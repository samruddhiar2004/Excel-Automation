from pathlib import Path
from datetime import datetime, timedelta
import random
import pandas as pd
import openpyxl

SAMPLES_DIR = Path("samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

def generate_samples():
    print(f"Generating sample test files in '{SAMPLES_DIR}'...")

    # 1. Completely Valid Data
    valid_data = [
        {"Farmer ID": f"FRM-{1000+i}", "Farmer Name": f"Farmer {i}", "Date": f"2026-10-0{i+1}", 
         "Quantity": 150 + i * 10, "Rate": 25.50, "Amount": (150 + i * 10) * 25.50, "Invoice Number": f"INV-2026-00{i}"}
        for i in range(1, 8)
    ]
    pd.DataFrame(valid_data).to_excel(SAMPLES_DIR / "01_valid_data.xlsx", index=False)

    # 2. Missing Fields
    missing_data = [
        {"Farmer ID": "FRM-2001", "Farmer Name": "Rajesh Kumar", "Date": "2026-10-01", "Quantity": 200, "Rate": 30.0, "Amount": 6000.0, "Invoice Number": "INV-2001"},
        {"Farmer ID": "", "Farmer Name": "Sunita Devi", "Date": "2026-10-01", "Quantity": 180, "Rate": 30.0, "Amount": 5400.0, "Invoice Number": "INV-2002"}, # Missing Farmer ID
        {"Farmer ID": "FRM-2003", "Farmer Name": "Amit Patel", "Date": None, "Quantity": 150, "Rate": 28.0, "Amount": 4200.0, "Invoice Number": "INV-2003"}, # Missing Date
        {"Farmer ID": "FRM-2004", "Farmer Name": "Vikram Singh", "Date": "2026-10-02", "Quantity": None, "Rate": 29.0, "Amount": 0.0, "Invoice Number": "INV-2004"}, # Missing Quantity
        {"Farmer ID": "FRM-2005", "Farmer Name": "", "Date": "2026-10-02", "Quantity": 120, "Rate": 29.0, "Amount": 3480.0, "Invoice Number": "INV-2005"}, # Missing Farmer Name
    ]
    pd.DataFrame(missing_data).to_excel(SAMPLES_DIR / "02_missing_fields.xlsx", index=False)

    # 3. Duplicate Records
    dup_data = [
        {"Farmer ID": "FRM-3001", "Farmer Name": "Ramesh Rao", "Date": "2026-10-03", "Quantity": 100, "Rate": 25.0, "Amount": 2500.0, "Invoice Number": "INV-3001"},
        {"Farmer ID": "FRM-3002", "Farmer Name": "Suresh Babu", "Date": "2026-10-03", "Quantity": 120, "Rate": 25.0, "Amount": 3000.0, "Invoice Number": "INV-3002"},
        {"Farmer ID": "FRM-3001", "Farmer Name": "Ramesh Rao", "Date": "2026-10-03", "Quantity": 100, "Rate": 25.0, "Amount": 2500.0, "Invoice Number": "INV-3001"}, # Exact Duplicate
        {"Farmer ID": "FRM-3001", "Farmer Name": "Ramesh Rao", "Date": "2026-10-03", "Quantity": 150, "Rate": 25.0, "Amount": 3750.0, "Invoice Number": "INV-3001"}, # Duplicate key with different qty
    ]
    pd.DataFrame(dup_data).to_excel(SAMPLES_DIR / "03_duplicates.xlsx", index=False)

    # 4. Invalid Dates
    invalid_date_data = [
        {"Farmer ID": "FRM-4001", "Farmer Name": "Anand Mohan", "Date": "2026-10-01", "Quantity": 90, "Rate": 32.0, "Amount": 2880.0, "Invoice Number": "INV-4001"},
        {"Farmer ID": "FRM-4002", "Farmer Name": "Deepak Joshi", "Date": "2026-02-31", "Quantity": 110, "Rate": 32.0, "Amount": 3520.0, "Invoice Number": "INV-4002"}, # Invalid Feb 31
        {"Farmer ID": "FRM-4003", "Farmer Name": "Pooja Sharma", "Date": "not_a_date", "Quantity": 95, "Rate": 32.0, "Amount": 3040.0, "Invoice Number": "INV-4003"}, # Gibberish date
    ]
    pd.DataFrame(invalid_date_data).to_excel(SAMPLES_DIR / "04_invalid_dates.xlsx", index=False)

    # 5. Invalid Numeric Values
    invalid_num_data = [
        {"Farmer ID": "FRM-5001", "Farmer Name": "Manoj Tiwari", "Date": "2026-10-04", "Quantity": 100, "Rate": 35.0, "Amount": 3500.0, "Invoice Number": "INV-5001"},
        {"Farmer ID": "FRM-5002", "Farmer Name": "Prakash Ray", "Date": "2026-10-04", "Quantity": "Ten", "Rate": 35.0, "Amount": 3500.0, "Invoice Number": "INV-5002"}, # Text quantity
        {"Farmer ID": "FRM-5003", "Farmer Name": "Gopal Das", "Date": "2026-10-04", "Quantity": 80, "Rate": "FREE", "Amount": 0.0, "Invoice Number": "INV-5003"}, # Text rate
        {"Farmer ID": "FRM-5004", "Farmer Name": "Harish Seth", "Date": "2026-10-04", "Quantity": -50, "Rate": 35.0, "Amount": -1750.0, "Invoice Number": "INV-5004"}, # Negative quantity
    ]
    pd.DataFrame(invalid_num_data).to_excel(SAMPLES_DIR / "05_invalid_numbers.xlsx", index=False)

    # 6. Empty Excel File (0 data rows)
    wb = openpyxl.Workbook()
    wb.save(SAMPLES_DIR / "06_empty_file.xlsx")

    # 7. Incorrect Column Names (Missing required columns)
    wrong_cols_data = [
        {"Vendor ID": "V-101", "Vendor Name": "Agri Traders", "Transaction Date": "2026-10-05", "Total Kilos": 500, "Price": 22.0}
    ]
    pd.DataFrame(wrong_cols_data).to_excel(SAMPLES_DIR / "07_incorrect_columns.xlsx", index=False)

    # 8. Multi-file Batch Testing
    batch1 = [
        {"Farmer ID": "FRM-8001", "Farmer Name": "Devendra", "Date": "2026-10-05", "Quantity": 100, "Rate": 25.0, "Amount": 2500.0, "Invoice Number": "BATCH-1"},
        {"Farmer ID": "FRM-8002", "Farmer Name": "Kavita", "Date": "2026-10-05", "Quantity": 120, "Rate": 25.0, "Amount": 3000.0, "Invoice Number": "BATCH-2"}
    ]
    batch2 = [
        {"Farmer ID": "FRM-8002", "Farmer Name": "Kavita", "Date": "2026-10-05", "Quantity": 120, "Rate": 25.0, "Amount": 3000.0, "Invoice Number": "BATCH-2"}, # Duplicate of batch 1
        {"Farmer ID": "FRM-8003", "Farmer Name": "Naveen", "Date": "2026-10-05", "Quantity": 140, "Rate": 25.0, "Amount": 3500.0, "Invoice Number": "BATCH-3"}
    ]
    pd.DataFrame(batch1).to_excel(SAMPLES_DIR / "08_multi_batch_part1.xlsx", index=False)
    pd.DataFrame(batch2).to_excel(SAMPLES_DIR / "08_multi_batch_part2.xlsx", index=False)

    # 9. Large Dataset (1,500 records)
    print("Generating large dataset (1,500 records)...")
    large_data = []
    start_date = datetime(2026, 9, 1)
    for i in range(1, 1501):
        dt = (start_date + timedelta(days=(i % 30))).strftime("%Y-%m-%d")
        qty = round(random.uniform(50, 500), 1)
        rate = round(random.uniform(20, 60), 2)
        large_data.append({
            "Farmer ID": f"FRM-LG-{i:04d}",
            "Farmer Name": f"Farmer Name {i}",
            "Date": dt,
            "Quantity": qty,
            "Rate": rate,
            "Amount": round(qty * rate, 2),
            "Invoice Number": f"INV-LG-{i:05d}"
        })
    pd.DataFrame(large_data).to_excel(SAMPLES_DIR / "09_large_dataset.xlsx", index=False)

    print("All sample files generated successfully!")

if __name__ == "__main__":
    generate_samples()
