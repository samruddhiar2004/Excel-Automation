import pandas as pd
import pytest
from src.validation.engine import ValidationEngine

def test_structure_validation_pass(default_config):
    validator = ValidationEngine(default_config)
    df = pd.DataFrame(columns=["Farmer ID", "Farmer Name", "Date", "Quantity", "Rate", "Amount"])
    is_valid, missing = validator.validate_structure(df, "test.xlsx")
    assert is_valid is True
    assert len(missing) == 0

def test_structure_validation_missing_columns(default_config):
    validator = ValidationEngine(default_config)
    df = pd.DataFrame(columns=["Farmer ID", "Farmer Name"])
    is_valid, missing = validator.validate_structure(df, "test.xlsx")
    assert is_valid is False
    assert "Date" in missing
    assert "Quantity" in missing

def test_row_validation_valid(default_config):
    validator = ValidationEngine(default_config)
    row = {
        "Farmer ID": "FRM-01",
        "Farmer Name": "Ramesh",
        "Date": "2026-10-01",
        "Quantity": "150",
        "Rate": 30.5,
        "Amount": 4575.0
    }
    is_valid, errors, norm = validator.validate_row(row, 2, "test.xlsx")
    assert is_valid is True
    assert len(errors) == 0
    assert norm["Quantity"] == 150.0

def test_row_validation_missing_fields(default_config):
    validator = ValidationEngine(default_config)
    row = {
        "Farmer ID": "",
        "Farmer Name": "Ramesh",
        "Date": None,
        "Quantity": 150,
        "Rate": 30.5,
        "Amount": 4575.0
    }
    is_valid, errors, _ = validator.validate_row(row, 2, "test.xlsx")
    assert is_valid is False
    error_fields = [e.field for e in errors]
    assert "Farmer ID" in error_fields
    assert "Date" in error_fields
    assert any(e.error_type == "Missing Field" for e in errors)

def test_row_validation_invalid_numeric(default_config):
    validator = ValidationEngine(default_config)
    row = {
        "Farmer ID": "FRM-01",
        "Farmer Name": "Ramesh",
        "Date": "2026-10-01",
        "Quantity": "INVALID_NUM",
        "Rate": -10.0,  # Violates min: 0 constraint
        "Amount": 100
    }
    is_valid, errors, _ = validator.validate_row(row, 3, "test.xlsx")
    assert is_valid is False
    err_types = [e.error_type for e in errors]
    assert "Invalid Data" in err_types

def test_row_validation_invalid_date(default_config):
    validator = ValidationEngine(default_config)
    row = {
        "Farmer ID": "FRM-01",
        "Farmer Name": "Ramesh",
        "Date": "2026-02-31", # Invalid date
        "Quantity": 100,
        "Rate": 25.0,
        "Amount": 2500
    }
    is_valid, errors, _ = validator.validate_row(row, 4, "test.xlsx")
    assert is_valid is False
    assert any(e.error_type == "Invalid Date" for e in errors)
