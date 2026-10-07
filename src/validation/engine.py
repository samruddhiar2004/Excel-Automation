from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
import math
import pandas as pd
from src.config.schema import ValidationRule
from src.validation.models import RecordError, ValidationResult
from src.logger import logger

class ValidationEngine:
    """Validates Excel dataset structure, required fields, and data types."""

    def __init__(self, config: ValidationRule):
        self.config = config

    def validate_structure(self, df: pd.DataFrame, file_name: str) -> Tuple[bool, List[str]]:
        """Verifies if the DataFrame contains all required columns."""
        existing_cols = {str(c).strip().lower(): str(c) for c in df.columns}
        missing_cols = []

        for req in self.config.required_columns:
            if req.strip().lower() not in existing_cols:
                missing_cols.append(req)

        if missing_cols:
            err_msg = f"Missing required column(s): {', '.join(missing_cols)}"
            logger.warning(f"Structural validation failed for '{file_name}': {err_msg}")
            return False, missing_cols

        return True, []

    def _is_blank(self, val: Any) -> bool:
        """Determines if a cell value is missing/blank."""
        if val is None:
            return True
        if isinstance(val, float) and (math.isnan(val) or pd.isna(val)):
            return True
        if pd.isna(val):
            return True
        if isinstance(val, str) and not val.strip():
            return True
        return False

    def _validate_numeric(
        self, val: Any, field_name: str
    ) -> Tuple[bool, Optional[float], Optional[str]]:
        """Validates that a value is numeric and satisfies configured constraints."""
        try:
            # Handle string formatted numbers with commas (e.g. "1,250.00")
            if isinstance(val, str):
                cleaned_val = val.strip().replace(",", "")
                num_val = float(cleaned_val)
            else:
                num_val = float(val)

            if math.isnan(num_val) or math.isinf(num_val):
                return False, None, f"{field_name} is not a valid number"

            # Check constraints
            constraints = self.config.numeric_constraints.get(field_name, {})
            min_val = constraints.get("min")
            if min_val is not None and num_val < min_val:
                return False, None, f"{field_name} must be >= {min_val} (got {num_val})"

            return True, num_val, None

        except (ValueError, TypeError):
            return False, None, f"{field_name} is not numeric ('{val}')"

    def _validate_date(self, val: Any, field_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validates date value and converts it to normalized YYYY-MM-DD string."""
        if isinstance(val, (datetime, pd.Timestamp)):
            return True, val.strftime("%Y-%m-%d"), None
        elif isinstance(val, date):
            return True, val.strftime("%Y-%m-%d"), None

        val_str = str(val).strip()
        
        # Try configured date formats
        for fmt in self.config.date_formats:
            try:
                parsed_dt = datetime.strptime(val_str, fmt)
                return True, parsed_dt.strftime("%Y-%m-%d"), None
            except (ValueError, TypeError):
                continue

        # Try pandas fallback
        try:
            parsed = pd.to_datetime(val_str, errors="raise")
            return True, parsed.strftime("%Y-%m-%d"), None
        except Exception:
            pass

        return False, None, f"Date format is invalid ('{val_str}')"

    def validate_row(
        self,
        row: Dict[str, Any],
        row_num: int,
        file_name: str
    ) -> Tuple[bool, List[RecordError], Dict[str, Any]]:
        """
        Validates a single data row.
        Returns: (is_valid, list_of_errors, normalized_row)
        """
        errors: List[RecordError] = []
        normalized_row = dict(row)

        # 1. Check required fields for blanks
        for req_col in self.config.required_columns:
            val = row.get(req_col)
            if self._is_blank(val):
                errors.append(RecordError(
                    file=file_name,
                    row=row_num,
                    error_type="Missing Field",
                    field=req_col,
                    description=f"{req_col} is empty",
                    raw_value="" if val is None else str(val),
                    row_data=row
                ))

        # 2. Check data types for non-blank fields
        for field, expected_type in self.config.type_rules.items():
            if field not in row:
                continue
            val = row.get(field)
            if self._is_blank(val):
                # Missing check already flagged if required, skip type checking on blanks
                continue

            if expected_type == "numeric":
                is_num, num_val, err_msg = self._validate_numeric(val, field)
                if not is_num:
                    errors.append(RecordError(
                        file=file_name,
                        row=row_num,
                        error_type="Invalid Data",
                        field=field,
                        description=err_msg or f"{field} is not numeric",
                        raw_value=str(val),
                        row_data=row
                    ))
                else:
                    normalized_row[field] = num_val

            elif expected_type == "date":
                is_dt, dt_str, err_msg = self._validate_date(val, field)
                if not is_dt:
                    errors.append(RecordError(
                        file=file_name,
                        row=row_num,
                        error_type="Invalid Date",
                        field=field,
                        description=err_msg or "Date format is invalid",
                        raw_value=str(val),
                        row_data=row
                    ))
                else:
                    normalized_row[field] = dt_str

            elif expected_type == "string":
                normalized_row[field] = str(val).strip()

        is_valid = len(errors) == 0
        return is_valid, errors, normalized_row

    def validate_dataframe(self, df: pd.DataFrame, file_name: str) -> ValidationResult:
        """Validates all rows in a DataFrame against configured rules."""
        result = ValidationResult(file_name=file_name)

        # Check structural columns first
        is_struct_valid, missing_cols = self.validate_structure(df, file_name)
        if not is_struct_valid:
            result.is_valid_structure = False
            result.structural_errors = [f"Missing required column: {c}" for c in missing_cols]
            # Record a file-level error
            result.errors.append(RecordError(
                file=file_name,
                row=1,
                error_type="Structural Error",
                field="Columns",
                description=f"Missing required columns: {', '.join(missing_cols)}"
            ))
            return result

        result.total_rows_inspected = len(df)

        for _, row_series in df.iterrows():
            row_dict = row_series.to_dict()
            row_num = int(row_dict.get("_excel_row_num", 0))

            is_valid, row_errors, norm_row = self.validate_row(row_dict, row_num, file_name)

            if is_valid:
                result.valid_rows.append(norm_row)
            else:
                result.errors.extend(row_errors)

        return result
