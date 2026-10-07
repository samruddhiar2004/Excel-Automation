# Office Work Automation — Excel Data Processing Assistant (v1.0)

A lightweight, modular, and reliable automation tool designed to eliminate repetitive Excel data processing tasks for office workers.

---

## 🌟 Overview & Purpose

Employees in office environments frequently spend hours manually opening incoming vendor/partner Excel files, verifying required columns, searching for duplicate transactions, fixing invalid data types or missing fields, and copy-pasting clean records into master spreadsheets.

This application automates this entire pipeline into a single one-click workflow:
1. **Multi-File Ingestion**: Accepts one or more `.xlsx` files simultaneously.
2. **Structure & Column Validation**: Confirms all required columns exist before processing.
3. **Field & Type Validation**: Checks for missing fields, invalid dates, and non-numeric numbers.
4. **Intelligent Deduplication**: Detects duplicate records using configurable business keys.
5. **Idempotent Master Dataset**: Consolidates clean records without duplicating entries even if the same file is processed repeatedly.
6. **Segregated Error Report**: Generates a detailed audit spreadsheet pinpointing the exact file, row number, error type, and description for correction.
7. **Executive Summary & Audit Log**: Shows total records processed, valid rows, invalid rows, and duplicate rows.
8. **One-Click Downloads**: Download the clean Master Excel, Error Report, and Text Audit Report.

---

## 📐 Architecture & Modular Design

Built adhering to strict product principles:
- **No Over-Engineering**: No Kubernetes, microservices, complex workflow engines, or external cloud dependencies.
- **Future-Proof Interfaces**: Separated into independent layers ready for future extensions (Email attachments, PDF parsers, database storage, and notifications).

```
Excel Files (.xlsx)
        ↓
[Input Layer]          → /src/input       (Supports file paths and uploaded streams)
        ↓
[Excel Reader]         → /src/excel       (Openpyxl/Pandas, tracks 1-based Excel row numbers)
        ↓
[Validation Engine]    → /src/validation  (Configurable rules, data types, missing fields)
        ↓
[Duplicate Detector]   → /src/processing  (Composite business keys, idempotency registry)
        ↓
[Data Processor]       → /src/processing  (Orchestrator separating valid vs problematic rows)
        ↓
[Output Generator]     → /src/output      (Styled Excel workbooks & error reports)
        ↓
[Report Generator]     → /src/reports     (Audit summaries & executive metrics)
        ↓
[User Interface / API] → /src/ui          (FastAPI web server & responsive web frontend)
```

### Directory Structure

```
Agent02-Excel_Automation/
├── config/
│   └── default_config.json      # Configurable validation rules & duplicate keys
├── samples/
│   ├── generate_samples.py      # Generates realistic test data for all test cases
│   ├── 01_valid_data.xlsx
│   ├── 02_missing_fields.xlsx
│   ├── 03_duplicates.xlsx
│   ├── 04_invalid_dates.xlsx
│   ├── 05_invalid_numbers.xlsx
│   ├── 06_empty_file.xlsx
│   ├── 07_incorrect_columns.xlsx
│   ├── 08_multi_batch_part1.xlsx
│   ├── 08_multi_batch_part2.xlsx
│   └── 09_large_dataset.xlsx
├── src/
│   ├── config/                  # Configuration schema and loader
│   ├── input/                   # File input source abstraction
│   ├── excel/                   # Excel reader & styled Excel writer
│   ├── validation/              # Structural and row-level validation engine
│   ├── processing/              # Duplicate detection & master consolidation
│   ├── reports/                 # Summary text and audit report generator
│   ├── output/                  # Master dataset & error workbook exporter
│   ├── ui/
│   │   ├── static/              # HTML5, modern CSS, and JavaScript frontend
│   │   └── server.py            # FastAPI backend server
│   ├── cli.py                   # Command-line interface for batch tasks
│   └── logger.py                # Structured operational logging
├── tests/                       # Complete automated test suite (22 tests)
├── output/                      # Default export directory for generated results
├── run.py                       # Quick web app launcher
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## ⚙️ Configuration

Validation rules and duplicate keys are completely separated from core business logic in `config/default_config.json`:

```json
{
  "required_columns": [
    "Farmer ID",
    "Farmer Name",
    "Date",
    "Quantity",
    "Rate",
    "Amount"
  ],
  "duplicate_keys": [
    "Farmer ID",
    "Date",
    "Invoice Number"
  ],
  "type_rules": {
    "Quantity": "numeric",
    "Rate": "numeric",
    "Amount": "numeric",
    "Date": "date",
    "Farmer ID": "string",
    "Farmer Name": "string"
  },
  "date_formats": [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d"
  ],
  "numeric_constraints": {
    "Quantity": { "min": 0.0 },
    "Rate": { "min": 0.0 },
    "Amount": { "min": 0.0 }
  },
  "output_dir": "output"
}
```

*Note: You can also adjust these settings dynamically directly within the Web UI by clicking the "Rules Config" button.*

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Dependencies installed via:
  ```powershell
  python -m pip install -r requirements.txt
  ```

### 2. Launch the Web Interface
Run the application server:
```powershell
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

**Features in Web UI:**
- **Drag-and-Drop Dropzone**: Select single or multiple `.xlsx` files.
- **KPI Dashboards**: Instant cards displaying Files Processed, Total Records, Valid Records, Invalid Records, and Duplicate Records.
- **One-Click Downloads**:
  - `Download Master Excel (.xlsx)`: Corporate-styled clean dataset with freeze panes and auto-sized columns.
  - `Download Error Report (.xlsx)`: Segregated table with exact Excel row numbers, error types, and descriptions.
  - `Download Processing Report (.txt)`: Human-readable audit log.
- **Interactive Previews**:
  - File-by-file breakdown table.
  - Live data table preview of master records.
  - Error report preview with color-coded badges (`Missing Field`, `Duplicate`, `Invalid Data`, `Invalid Date`, `Missing Column`).
  - Terminal-style audit log.

---

## 💻 Command-Line Interface (CLI)

For batch processing or script automation, you can run the CLI directly:

### Process specific files:
```powershell
python -m src.cli --files samples/01_valid_data.xlsx samples/02_missing_fields.xlsx
```

### Process an entire folder:
```powershell
python -m src.cli --input-dir samples/ --output-dir output/
```

### Example CLI Output:
```
Processing 7 Excel file(s)...

==================================================
       EXCEL DATA PROCESSING SUMMARY REPORT       
==================================================
Processed at:          2026-10-07 10:57:45
Files processed:       7
Total records:         24

Valid records:         12
Invalid records:       17
Duplicate records:     2
--------------------------------------------------
FILE BREAKDOWN:
 - 01_valid_data.xlsx        | Rows: 7     | Valid: 7     | Invalid: 0     | Duplicates: 0     | [Success]
 - 02_missing_fields.xlsx    | Rows: 5     | Valid: 1     | Invalid: 4     | Duplicates: 0     | [Success]
 - 03_duplicates.xlsx        | Rows: 4     | Valid: 2     | Invalid: 0     | Duplicates: 2     | [Success]
 - 04_invalid_dates.xlsx     | Rows: 3     | Valid: 1     | Invalid: 2     | Duplicates: 0     | [Success]
 - 05_invalid_numbers.xlsx   | Rows: 4     | Valid: 1     | Invalid: 3     | Duplicates: 0     | [Success]
 - 06_empty_file.xlsx        | Rows: 0     | Valid: 0     | Invalid: 0     | Duplicates: 0     | [Empty]
 - 07_incorrect_columns.xlsx | Rows: 1     | Valid: 0     | Invalid: 1     | Duplicates: 0     | [Structural Error]
--------------------------------------------------
ERROR BREAKDOWN BY TYPE:
 - Duplicate           : 2
 - Invalid Data        : 4
 - Invalid Date        : 2
 - Missing Column      : 6
 - Missing Field       : 4
 - Read Error          : 1
==================================================
Processing completed successfully.
==================================================
```

---

## 🧪 Testing

The repository includes a comprehensive automated test suite and sample data generator.

### Run Sample Data Generation
```powershell
python samples/generate_samples.py
```
This generates 10 comprehensive edge-case scenarios:
1. `01_valid_data.xlsx`: Clean records matching all rules.
2. `02_missing_fields.xlsx`: Empty Farmer ID, Date, Quantity, etc.
3. `03_duplicates.xlsx`: Duplicate records on composite business keys.
4. `04_invalid_dates.xlsx`: Non-existent dates (e.g., Feb 31) and malformed strings.
5. `05_invalid_numbers.xlsx`: Strings in numeric columns and negative values.
6. `06_empty_file.xlsx`: Blank workbook with 0 rows.
7. `07_incorrect_columns.xlsx`: Wrong column headers.
8. `08_multi_batch_part1.xlsx` & `08_multi_batch_part2.xlsx`: Cross-file batch deduplication.
9. `09_large_dataset.xlsx`: 1,500 records benchmark.

### Run Automated Tests
```powershell
python -m pytest -v
```
All 22 unit, integration, and API tests pass covering:
- Excel reading & row tracking
- Structural column validation
- Missing field identification
- Numeric & date type checking
- Duplicate detection & idempotency
- Summary report generation
- Styled output generation
- FastAPI endpoints & file downloads

---

## 🔮 Roadmap for Future Automation
The codebase was designed specifically so the following modules can be added in subsequent milestones without refactoring core logic:
- **Email Ingestion Module** (`/src/input/email_source.py`): Automatically poll inbox for Excel attachments.
- **PDF Parser** (`/src/input/pdf_source.py`): Extract invoice tables into standard schema.
- **Database Connector** (`/src/output/db_sink.py`): Persist master dataset into PostgreSQL / SQLite.
- **Notification Webhook** (`/src/reports/notifier.py`): Send Slack or Teams summary notifications upon batch completion.
