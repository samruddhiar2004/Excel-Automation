from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field

from src.config.schema import ValidationRule, load_config
from src.excel.reader import ExcelReader, ExcelReadResult
from src.input.loader import BaseInputSource, FileInputSource, InputItem
from src.logger import logger
from src.processing.duplicate import DuplicateDetector
from src.validation.engine import ValidationEngine
from src.validation.models import RecordError

class FileProcessingStat(BaseModel):
    file_name: str
    rows_detected: int = 0
    valid: int = 0
    invalid: int = 0
    duplicates: int = 0
    status: str = "Success" # "Success", "Failed", "Empty", "Structural Error"
    message: Optional[str] = None

class ProcessingResult(BaseModel):
    processed_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    files_processed: int = 0
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    duplicate_records: int = 0
    file_stats: List[FileProcessingStat] = Field(default_factory=list)
    errors: List[RecordError] = Field(default_factory=list)
    master_records: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def master_df(self) -> pd.DataFrame:
        """Returns clean pandas DataFrame of master dataset."""
        if not self.master_records:
            return pd.DataFrame()
        df = pd.DataFrame(self.master_records)
        # Drop internal tracking columns
        for col in ["_excel_row_num", "_source_file"]:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        return df

    @property
    def errors_df(self) -> pd.DataFrame:
        """Returns pandas DataFrame for the error report."""
        if not self.errors:
            # Return empty DataFrame with defined columns
            return pd.DataFrame(columns=["Row", "Error Type", "Field", "Description", "File", "Raw Value"])
        
        rows = []
        for err in self.errors:
            rows.append({
                "Row": err.row,
                "Error Type": err.error_type,
                "Field": err.field,
                "Description": err.description,
                "File": err.file,
                "Raw Value": err.raw_value or ""
            })
        return pd.DataFrame(rows)

class DataProcessor:
    """Core processor coordinating input reading, validation, deduplication, and master dataset compilation."""

    def __init__(self, config: Optional[ValidationRule] = None):
        self.config = config or load_config()
        self.validator = ValidationEngine(self.config)
        self.duplicate_detector = DuplicateDetector(self.config.duplicate_keys)

    def process_inputs(self, input_source: BaseInputSource) -> ProcessingResult:
        """Processes all items from the input source."""
        inputs = input_source.get_inputs()
        result = ProcessingResult()
        result.files_processed = len(inputs)

        logger.info(f"Starting processing run for {len(inputs)} file(s)")

        for item in inputs:
            file_stat = self._process_single_input(item, result)
            result.file_stats.append(file_stat)

        # Aggregate overall summary
        result.total_records = sum(stat.rows_detected for stat in result.file_stats)
        result.valid_records = len(result.master_records)
        result.duplicate_records = sum(stat.duplicates for stat in result.file_stats)
        result.invalid_records = len(result.errors) - result.duplicate_records

        logger.info(
            f"Run Complete: Files: {result.files_processed} | "
            f"Total Rows: {result.total_records} | "
            f"Valid: {result.valid_records} | "
            f"Invalid: {result.invalid_records} | "
            f"Duplicates: {result.duplicate_records}"
        )

        return result

    def _process_single_input(self, item: InputItem, result: ProcessingResult) -> FileProcessingStat:
        """Processes a single Excel input item."""
        file_name = item.source_name
        logger.info(f"--- Processing file: {file_name} ---")

        # 1. Read Excel
        read_res = ExcelReader.read(item.get_stream(), file_name=file_name)
        if not read_res.success:
            logger.warning(f"File {file_name} could not be parsed: {read_res.error_message}")
            err = RecordError(
                file=file_name,
                row=1,
                error_type="Read Error",
                field="File",
                description=read_res.error_message or "Failed to read file",
                raw_value=""
            )
            result.errors.append(err)
            return FileProcessingStat(
                file_name=file_name,
                rows_detected=0,
                status="Empty" if read_res.is_empty else "Failed",
                message=read_res.error_message
            )

        df = read_res.df
        rows_detected = len(df)

        # 2. Validate Structure
        is_struct_valid, missing_cols = self.validator.validate_structure(df, file_name)
        if not is_struct_valid:
            logger.warning(f"File {file_name} failed structure check: Missing {missing_cols}")
            for col in missing_cols:
                result.errors.append(RecordError(
                    file=file_name,
                    row=1,
                    error_type="Missing Column",
                    field=col,
                    description=f"Required column '{col}' is missing",
                    raw_value=""
                ))
            return FileProcessingStat(
                file_name=file_name,
                rows_detected=rows_detected,
                invalid=rows_detected,
                status="Structural Error",
                message=f"Missing columns: {', '.join(missing_cols)}"
            )

        # 3. Validate Data Rows & Duplicate Detection
        file_valid_count = 0
        file_invalid_count = 0
        file_duplicate_count = 0

        for _, row_series in df.iterrows():
            row_dict = row_series.to_dict()
            row_num = int(row_dict.get("_excel_row_num", 0))

            is_valid, row_errors, norm_row = self.validator.validate_row(row_dict, row_num, file_name)

            if not is_valid:
                file_invalid_count += 1
                result.errors.extend(row_errors)
                continue

            # Check duplicate
            is_dup, dup_error = self.duplicate_detector.check_and_register(norm_row, row_num, file_name)
            if is_dup and dup_error:
                file_duplicate_count += 1
                result.errors.append(dup_error)
            else:
                file_valid_count += 1
                result.master_records.append(norm_row)

        logger.info(
            f"File: {file_name}\n"
            f"Rows detected: {rows_detected}\n"
            f"Valid: {file_valid_count}\n"
            f"Invalid: {file_invalid_count}\n"
            f"Duplicates: {file_duplicate_count}\n"
            f"Processing completed."
        )

        return FileProcessingStat(
            file_name=file_name,
            rows_detected=rows_detected,
            valid=file_valid_count,
            invalid=file_invalid_count,
            duplicates=file_duplicate_count,
            status="Success"
        )
