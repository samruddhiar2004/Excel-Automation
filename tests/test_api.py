from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.ui.server import app

client = TestClient(app)

def test_api_serve_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "Excel Data Processing Assistant" in response.text

def test_api_config_endpoints():
    get_res = client.get("/api/config")
    assert get_res.status_code == 200
    config_json = get_res.json()
    assert "required_columns" in config_json
    assert "Farmer ID" in config_json["required_columns"]

def test_api_process_and_downloads(samples_dir):
    valid_file = samples_dir / "01_valid_data.xlsx"
    with open(valid_file, "rb") as f:
        response = client.post(
            "/api/process",
            files={"files": ("01_valid_data.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["files_processed"] == 1
    assert data["valid_records"] == 7
    assert data["invalid_records"] == 0

    session_id = data["session_id"]

    # Test master download
    master_res = client.get(f"/api/download/{session_id}/master")
    assert master_res.status_code == 200
    assert "spreadsheetml" in master_res.headers["content-type"]

    # Test errors download
    errors_res = client.get(f"/api/download/{session_id}/errors")
    assert errors_res.status_code == 200

    # Test summary download
    summary_res = client.get(f"/api/download/{session_id}/summary")
    assert summary_res.status_code == 200
    assert "EXCEL DATA PROCESSING SUMMARY REPORT" in summary_res.text
