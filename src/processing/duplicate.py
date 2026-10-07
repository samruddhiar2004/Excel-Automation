from typing import Any, Dict, List, Optional, Set, Tuple
from src.validation.models import RecordError

class DuplicateDetector:
    """
    Detects duplicates across records using configurable composite keys.
    Maintains a registry of seen records to ensure idempotency across multiple files
    and duplicate file submissions.
    """

    def __init__(self, key_columns: List[str]):
        self.key_columns = key_columns
        # Map: composite_key -> dict(file=..., row=...)
        self.seen_keys: Dict[str, Dict[str, Any]] = {}

    def _generate_composite_key(self, row: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Generates a normalized composite key from the configured key columns."""
        active_keys = [k for k in self.key_columns if k in row]
        if not active_keys:
            # Fallback if none of configured duplicate keys are in the row:
            # use all non-internal columns
            active_keys = [k for k in row.keys() if not k.startswith("_")]

        parts = []
        for k in active_keys:
            val = str(row.get(k, "")).strip().lower()
            parts.append(f"{k}:{val}")

        return "|".join(parts), active_keys

    def check_and_register(
        self,
        row: Dict[str, Any],
        row_num: int,
        file_name: str
    ) -> Tuple[bool, Optional[RecordError]]:
        """
        Checks if the row is a duplicate.
        Returns: (is_duplicate, RecordError if duplicate else None)
        """
        comp_key, active_keys = self._generate_composite_key(row)
        
        if comp_key in self.seen_keys:
            prior = self.seen_keys[comp_key]
            keys_label = " + ".join(active_keys)
            error = RecordError(
                file=file_name,
                row=row_num,
                error_type="Duplicate",
                field=keys_label,
                description=(
                    f"Duplicate record matching {prior['file']} (row {prior['row']}) "
                    f"on key [{keys_label}]"
                ),
                raw_value=comp_key,
                row_data=row
            )
            return True, error

        # Register this key
        self.seen_keys[comp_key] = {
            "file": file_name,
            "row": row_num
        }
        return False, None

    def reset(self):
        """Clears the seen keys registry."""
        self.seen_keys.clear()
