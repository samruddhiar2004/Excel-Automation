from datetime import datetime
from src.processing.processor import ProcessingResult

class SummaryReportGenerator:
    """Generates human-readable text summaries and audit reports for office staff."""

    @staticmethod
    def generate_text_summary(result: ProcessingResult) -> str:
        """Formats the exact summary matching required business report structure."""
        lines = []
        lines.append("==================================================")
        lines.append("       EXCEL DATA PROCESSING SUMMARY REPORT       ")
        lines.append("==================================================")
        lines.append(f"Processed at:          {result.processed_at}")
        lines.append(f"Files processed:       {result.files_processed}")
        lines.append(f"Total records:         {result.total_records:,}")
        lines.append("")
        lines.append(f"Valid records:         {result.valid_records:,}")
        lines.append(f"Invalid records:       {result.invalid_records:,}")
        lines.append(f"Duplicate records:     {result.duplicate_records:,}")
        lines.append("--------------------------------------------------")
        lines.append("FILE BREAKDOWN:")
        for stat in result.file_stats:
            lines.append(
                f" - {stat.file_name:<25} | "
                f"Rows: {stat.rows_detected:<5} | "
                f"Valid: {stat.valid:<5} | "
                f"Invalid: {stat.invalid:<5} | "
                f"Duplicates: {stat.duplicates:<5} | "
                f"[{stat.status}]"
            )
        
        # Categorized error summary
        if result.errors:
            lines.append("--------------------------------------------------")
            lines.append("ERROR BREAKDOWN BY TYPE:")
            error_types = {}
            for err in result.errors:
                error_types[err.error_type] = error_types.get(err.error_type, 0) + 1
            for err_type, count in sorted(error_types.items()):
                lines.append(f" - {err_type:<20}: {count:,}")

        lines.append("==================================================")
        lines.append("Processing completed successfully.")
        lines.append("==================================================")
        return "\n".join(lines)
