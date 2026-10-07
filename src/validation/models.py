from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class RecordError(BaseModel):
    """Represents a validation error for a specific row in an Excel file."""
    file: str
    row: int
    error_type: str  # "Missing Field", "Invalid Data", "Invalid Date", "Duplicate", "Structural Error"
    field: str
    description: str
    raw_value: Optional[str] = None
    row_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "File": self.file,
            "Row": self.row,
            "Error Type": self.error_type,
            "Field": self.field,
            "Description": self.description,
            "Raw Value": self.raw_value or ""
        }

class ValidationResult(BaseModel):
    """Holds the result of validating an entire file."""
    file_name: str
    is_valid_structure: bool = True
    structural_errors: List[str] = Field(default_factory=list)
    valid_rows: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[RecordError] = Field(default_factory=list)
    total_rows_inspected: int = 0
