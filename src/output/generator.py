from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import io
import pandas as pd
from src.excel.writer import ExcelWriter
from src.processing.processor import ProcessingResult
from src.reports.summary import SummaryReportGenerator
from src.logger import logger

class OutputGenerator:
    """Manages the generation and export of Master Dataset, Error Report, and Summary files."""

    def __init__(self, output_dir: Union[str, Path] = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_all(
        self, result: ProcessingResult, prefix: str = ""
    ) -> Dict[str, Path]:
        """
        Saves all 3 output files to disk and returns a dictionary of generated file paths:
        - master_dataset.xlsx
        - error_report.xlsx
        - processing_summary.txt
        """
        prefix_str = f"{prefix}_" if prefix else ""
        master_path = self.output_dir / f"{prefix_str}master_dataset.xlsx"
        error_path = self.output_dir / f"{prefix_str}error_report.xlsx"
        summary_path = self.output_dir / f"{prefix_str}processing_summary.txt"

        # 1. Master Excel
        ExcelWriter.write_dataframe(
            df=result.master_df,
            sheet_title="Master Dataset",
            output_path=master_path,
            header_color="1E3A8A"
        )

        # 2. Error Report Excel
        ExcelWriter.write_error_report(
            errors_df=result.errors_df,
            output_path=error_path
        )

        # 3. Text Summary
        summary_text = SummaryReportGenerator.generate_text_summary(result)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        logger.info(f"Generated outputs in '{self.output_dir}':")
        logger.info(f" - Master Dataset: {master_path.name}")
        logger.info(f" - Error Report: {error_path.name}")
        logger.info(f" - Processing Summary: {summary_path.name}")

        return {
            "master_dataset": master_path,
            "error_report": error_path,
            "processing_summary": summary_path
        }

    @staticmethod
    def get_master_stream(result: ProcessingResult) -> io.BytesIO:
        """Returns in-memory stream of master dataset."""
        return ExcelWriter.write_dataframe(
            df=result.master_df,
            sheet_title="Master Dataset",
            header_color="1E3A8A"
        )

    @staticmethod
    def get_error_stream(result: ProcessingResult) -> io.BytesIO:
        """Returns in-memory stream of error report."""
        return ExcelWriter.write_error_report(errors_df=result.errors_df)

    @staticmethod
    def get_summary_stream(result: ProcessingResult) -> io.BytesIO:
        """Returns in-memory stream of processing summary text."""
        text = SummaryReportGenerator.generate_text_summary(result)
        return io.BytesIO(text.encode("utf-8"))
