import pytest
from src.processing.duplicate import DuplicateDetector

def test_duplicate_detector_unique_records():
    detector = DuplicateDetector(key_columns=["Farmer ID", "Date", "Invoice Number"])
    row1 = {"Farmer ID": "FRM-1", "Date": "2026-10-01", "Invoice Number": "INV-01"}
    row2 = {"Farmer ID": "FRM-2", "Date": "2026-10-01", "Invoice Number": "INV-02"}

    is_dup1, err1 = detector.check_and_register(row1, 2, "file1.xlsx")
    is_dup2, err2 = detector.check_and_register(row2, 3, "file1.xlsx")

    assert is_dup1 is False
    assert err1 is None
    assert is_dup2 is False
    assert err2 is None

def test_duplicate_detector_catches_duplicate():
    detector = DuplicateDetector(key_columns=["Farmer ID", "Date", "Invoice Number"])
    row1 = {"Farmer ID": "FRM-1", "Date": "2026-10-01", "Invoice Number": "INV-01"}
    row2 = {"Farmer ID": "FRM-1", "Date": "2026-10-01", "Invoice Number": "INV-01"} # duplicate

    detector.check_and_register(row1, 2, "file1.xlsx")
    is_dup, err = detector.check_and_register(row2, 5, "file2.xlsx")

    assert is_dup is True
    assert err is not None
    assert err.error_type == "Duplicate"
    assert "file1.xlsx" in err.description
    assert "row 2" in err.description

def test_duplicate_detector_case_insensitivity():
    detector = DuplicateDetector(key_columns=["Farmer ID", "Date"])
    row1 = {"Farmer ID": "FRM-1", "Date": "2026-10-01"}
    row2 = {"Farmer ID": "frm-1 ", "Date": " 2026-10-01"}

    detector.check_and_register(row1, 2, "file1.xlsx")
    is_dup, err = detector.check_and_register(row2, 3, "file1.xlsx")

    assert is_dup is True
