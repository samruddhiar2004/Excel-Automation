import io
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.config.schema import ValidationRule, load_config
from src.input.loader import UploadedStreamInputSource
from src.output.generator import OutputGenerator
from src.processing.processor import DataProcessor, ProcessingResult
from src.reports.summary import SummaryReportGenerator
from src.logger import logger

app = FastAPI(title="Excel Data Processing Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active configuration in memory
current_config: ValidationRule = load_config()

# Cache for recent processing sessions (in-memory for quick download)
# session_id -> { "result": ProcessingResult, "created_at": ... }
session_cache: Dict[str, ProcessingResult] = {}

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Index file not found</h1>", status_code=404)
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/api/config")
async def get_config():
    """Returns active validation & duplicate detection configuration."""
    return current_config.model_dump()

@app.post("/api/config")
async def update_config(config_data: ValidationRule):
    """Updates active validation rules."""
    global current_config
    current_config = config_data
    logger.info("Updated active validation configuration.")
    return {"message": "Configuration updated successfully", "config": current_config.model_dump()}

@app.post("/api/process")
async def process_files(files: List[UploadFile] = File(...)):
    """Processes uploaded Excel files and returns summary, metrics, and previews."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    logger.info(f"Received {len(files)} files for processing via Web API.")

    uploads = []
    for file in files:
        if not file.filename.lower().endswith((".xlsx", ".xls")):
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a supported format. Please upload .xlsx files."
            )
        content = await file.read()
        uploads.append((file.filename, content))

    try:
        source = UploadedStreamInputSource(uploads)
        processor = DataProcessor(config=current_config)
        result = processor.process_inputs(source)

        session_id = str(uuid.uuid4())
        session_cache[session_id] = result

        # Also save to disk output folder automatically
        generator = OutputGenerator(output_dir=current_config.output_dir)
        generator.save_all(result, prefix=session_id[:8])

        # Prepare master preview (first 50 rows)
        master_preview = []
        if not result.master_df.empty:
            master_preview = result.master_df.head(50).fillna("").to_dict(orient="records")

        # Prepare error preview (first 100 errors)
        errors_preview = [err.to_dict() for err in result.errors[:100]]

        summary_text = SummaryReportGenerator.generate_text_summary(result)

        return {
            "session_id": session_id,
            "processed_at": result.processed_at,
            "files_processed": result.files_processed,
            "total_records": result.total_records,
            "valid_records": result.valid_records,
            "invalid_records": result.invalid_records,
            "duplicate_records": result.duplicate_records,
            "file_stats": [stat.model_dump() for stat in result.file_stats],
            "master_preview": master_preview,
            "errors_preview": errors_preview,
            "summary_text": summary_text
        }

    except Exception as e:
        logger.exception("Processing error occurred:")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/download/{session_id}/master")
async def download_master(session_id: str):
    """Downloads the consolidated Master Excel file for a session."""
    if session_id not in session_cache:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    result = session_cache[session_id]
    stream = OutputGenerator.get_master_stream(result)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=master_dataset_{session_id[:8]}.xlsx"}
    )

@app.get("/api/download/{session_id}/errors")
async def download_errors(session_id: str):
    """Downloads the Error Report Excel file for a session."""
    if session_id not in session_cache:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    result = session_cache[session_id]
    stream = OutputGenerator.get_error_stream(result)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=error_report_{session_id[:8]}.xlsx"}
    )

@app.get("/api/download/{session_id}/summary")
async def download_summary(session_id: str):
    """Downloads the Processing Summary text file for a session."""
    if session_id not in session_cache:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    result = session_cache[session_id]
    stream = OutputGenerator.get_summary_stream(result)
    return StreamingResponse(
        stream,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=processing_summary_{session_id[:8]}.txt"}
    )
