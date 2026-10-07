import pytest
from src.config.schema import ValidationRule
from src.input.loader import FileInputSource
from src.processing.processor import DataProcessor

def test_processor_valid_data(default_config, samples_dir):
    source = FileInputSource([samples_dir / "01_valid_data.xlsx"])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    assert result.files_processed == 1
    assert result.total_records == 7
    assert result.valid_records == 7
    assert result.invalid_records == 0
    assert result.duplicate_records == 0
    assert len(result.master_df) == 7
    assert result.errors_df.empty or len(result.errors_df) == 0

def test_processor_duplicate_detection(default_config, samples_dir):
    source = FileInputSource([samples_dir / "03_duplicates.xlsx"])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    assert result.files_processed == 1
    assert result.total_records == 4
    assert result.valid_records == 2
    assert result.duplicate_records == 2
    assert len(result.master_df) == 2

def test_processor_idempotency(default_config, samples_dir):
    """Processing the exact same file twice should yield the same master dataset without duplicating."""
    file_path = samples_dir / "01_valid_data.xlsx"
    source = FileInputSource([file_path, file_path])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    assert result.files_processed == 2
    assert result.total_records == 14
    assert result.valid_records == 7
    assert result.duplicate_records == 7
    assert len(result.master_df) == 7

def test_processor_multi_file_batch(default_config, samples_dir):
    batch1 = samples_dir / "08_multi_batch_part1.xlsx"
    batch2 = samples_dir / "08_multi_batch_part2.xlsx"
    source = FileInputSource([batch1, batch2])
    processor = DataProcessor(config=default_config)
    result = processor.process_inputs(source)

    assert result.files_processed == 2
    # Batch 1 has 2 rows (both unique). Batch 2 has 2 rows (1 duplicate of batch 1, 1 unique).
    # Total rows = 4. Valid = 3. Duplicate = 1.
    assert result.total_records == 4
    assert result.valid_records == 3
    assert result.duplicate_records == 1
