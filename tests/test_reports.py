from pathlib import Path
import pytest
from src.input.loader import FileInputSource
from src.output.generator import OutputGenerator
from src.processing.processor import DataProcessor
from src.reports.summary import SummaryReportGenerator

def test_summary_report_text_generation(default_config, samples_dir):
    source = FileInputSource([samples_dir / "01_valid_data.xlsx"])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    summary_text = SummaryReportGenerator.generate_text_summary(result)
    assert "EXCEL DATA PROCESSING SUMMARY REPORT" in summary_text
    assert "Files processed:       1" in summary_text
    assert "Valid records:         7" in summary_text
    assert "Processing completed successfully." in summary_text

def test_output_generator_save_all(default_config, samples_dir, tmp_path):
    source = FileInputSource([samples_dir / "01_valid_data.xlsx", samples_dir / "02_missing_fields.xlsx"])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    generator = OutputGenerator(output_dir=tmp_path)
    saved = generator.save_all(result, prefix="test")

    assert saved["master_dataset"].exists()
    assert saved["error_report"].exists()
    assert saved["processing_summary"].exists()
    assert saved["master_dataset"].stat().st_size > 0
    assert saved["error_report"].stat().st_size > 0
