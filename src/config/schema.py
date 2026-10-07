import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ValidationRule(BaseModel):
    required_columns: List[str] = Field(
        default_factory=lambda: [
            "Farmer ID",
            "Farmer Name",
            "Date",
            "Quantity",
            "Rate",
            "Amount"
        ]
    )
    duplicate_keys: List[str] = Field(
        default_factory=lambda: ["Farmer ID", "Date", "Invoice Number"]
    )
    type_rules: Dict[str, str] = Field(
        default_factory=lambda: {
            "Quantity": "numeric",
            "Rate": "numeric",
            "Amount": "numeric",
            "Date": "date",
            "Farmer ID": "string",
            "Farmer Name": "string"
        }
    )
    date_formats: List[str] = Field(
        default_factory=lambda: [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d"
        ]
    )
    numeric_constraints: Dict[str, Dict[str, Optional[float]]] = Field(
        default_factory=lambda: {
            "Quantity": {"min": 0.0},
            "Rate": {"min": 0.0},
            "Amount": {"min": 0.0}
        }
    )
    output_dir: str = "output"

def load_config(config_path: Optional[str | Path] = None) -> ValidationRule:
    """Loads configuration from JSON file or returns defaults."""
    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ValidationRule(**data)
    
    default_path = Path("config/default_config.json")
    if default_path.exists():
        with open(default_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ValidationRule(**data)
            
    return ValidationRule()
