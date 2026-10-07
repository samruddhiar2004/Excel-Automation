import io
import pandas as pd
import pytest
from src.excel.reader import ExcelReader

def test_reader_valid_file(samples_dir):
    file_path = samples_dir / "01_valid_data.xlsx"
    result = ExcelReader.read(file_path, file_name="01_valid_data.xlsx")
    assert result.success is True
    assert result.total_rows == 7
    assert "_excel_row_num" in result.df.columns
    # Excel header is row 1, first data row must be 2
    assert result.df["_excel_row_num"].iloc[0] == 2
    assert result.df["_excel_row_num"].iloc[-1] == 8

def test_reader_empty_file(samples_dir):
    file_path = samples_dir / "06_empty_file.xlsx"
    result = ExcelReader.read(file_path, file_name="06_empty_file.xlsx")
    assert result.success is False
    assert result.is_empty is True

def test_reader_nonexistent_file():
    result = ExcelReader.read("non_existent_file.xlsx", file_name="non_existent_file.xlsx")
    assert result.success is False
    assert "empty" in result.error_message.lower() or "failed" in result.error_message.lower()

def test_reader_bytes_io():
    df = pd.DataFrame([{"A": 1, "B": 2}])
    stream = io.BytesIO()
    df.to_excel(stream, index=False)
    stream.seek(0)

    result = ExcelReader.read(stream, file_name="in_memory.xlsx")
    assert result.success is True
    assert result.total_rows == 1
    assert result.df["_excel_row_num"].iloc[0] == 2
