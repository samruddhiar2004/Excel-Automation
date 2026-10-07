from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple, Union
import io
import pandas as pd
from src.logger import logger

class ExcelReadResult:
    """Container for data read from an Excel file."""
    def __init__(
        self,
        file_name: str,
        df: Optional[pd.DataFrame] = None,
        sheet_name: str = "",
        total_rows: int = 0,
        is_empty: bool = False,
        error_message: Optional[str] = None
    ):
        self.file_name = file_name
        self.df = df if df is not None else pd.DataFrame()
        self.sheet_name = sheet_name
        self.total_rows = total_rows
        self.is_empty = is_empty
        self.error_message = error_message

    @property
    def success(self) -> bool:
        return self.error_message is None and not self.is_empty

class ExcelReader:
    """Reads Excel (.xlsx) files with robust edge-case handling."""

    @staticmethod
    def read(
        file_source: Union[str, Path, BinaryIO, io.BytesIO],
        file_name: str,
        sheet_name: Optional[str] = None
    ) -> ExcelReadResult:
        """
        Reads an Excel file and returns an ExcelReadResult.
        Preserves 1-based Excel row numbering (row 1 = header, row 2 = first data row).
        """
        logger.info(f"Reading Excel file: {file_name}")
        try:
            # Check empty stream/file
            if isinstance(file_source, (str, Path)):
                path = Path(file_source)
                if not path.exists() or path.stat().st_size == 0:
                    return ExcelReadResult(
                        file_name=file_name,
                        is_empty=True,
                        error_message="File is empty (0 bytes)."
                    )
            elif isinstance(file_source, (io.BytesIO, io.BufferedReader)):
                current_pos = file_source.tell()
                file_source.seek(0, io.SEEK_END)
                size = file_source.tell()
                file_source.seek(current_pos)
                if size == 0:
                    return ExcelReadResult(
                        file_name=file_name,
                        is_empty=True,
                        error_message="File is empty (0 bytes)."
                    )

            # Read file with pandas using openpyxl engine
            # dtype=object to prevent premature type conversion / data loss
            excel_file = pd.ExcelFile(file_source, engine="openpyxl")
            sheets = excel_file.sheet_names
            if not sheets:
                return ExcelReadResult(
                    file_name=file_name,
                    is_empty=True,
                    error_message="Workbook contains no worksheets."
                )

            target_sheet = sheet_name if sheet_name and sheet_name in sheets else sheets[0]
            df = excel_file.parse(sheet_name=target_sheet, dtype=object)

            if df.empty or len(df.columns) == 0:
                return ExcelReadResult(
                    file_name=file_name,
                    sheet_name=target_sheet,
                    is_empty=True,
                    error_message="Worksheet is empty or has no data."
                )

            # Clean column names (strip leading/trailing whitespace, keep as strings)
            df.columns = [str(col).strip() for col in df.columns]

            # Excel row calculation:
            # Header is row 1. First row of data in df is row 2.
            # Record original Excel row number (1-based index)
            df["_excel_row_num"] = [i + 2 for i in range(len(df))]
            df["_source_file"] = file_name

            logger.info(f"Successfully read {len(df)} rows from '{file_name}' (sheet: '{target_sheet}')")
            return ExcelReadResult(
                file_name=file_name,
                df=df,
                sheet_name=target_sheet,
                total_rows=len(df),
                is_empty=False
            )

        except Exception as e:
            logger.error(f"Error reading Excel file '{file_name}': {str(e)}")
            return ExcelReadResult(
                file_name=file_name,
                is_empty=True,
                error_message=f"Failed to read Excel file: {str(e)}"
            )
