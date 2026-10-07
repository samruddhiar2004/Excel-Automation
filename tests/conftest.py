import pytest
from pathlib import Path
from src.config.schema import ValidationRule

@pytest.fixture
def default_config() -> ValidationRule:
    return ValidationRule(
        required_columns=[
            "Farmer ID",
            "Farmer Name",
            "Date",
            "Quantity",
            "Rate",
            "Amount"
        ],
        duplicate_keys=["Farmer ID", "Date", "Invoice Number"],
        type_rules={
            "Quantity": "numeric",
            "Rate": "numeric",
            "Amount": "numeric",
            "Date": "date",
            "Farmer ID": "string",
            "Farmer Name": "string"
        },
        date_formats=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"],
        numeric_constraints={
            "Quantity": {"min": 0.0},
            "Rate": {"min": 0.0},
            "Amount": {"min": 0.0}
        },
        output_dir="output_test"
    )

@pytest.fixture
def samples_dir() -> Path:
    return Path("samples")
