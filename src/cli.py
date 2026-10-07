import argparse
import sys
from pathlib import Path
from src.config.schema import load_config
from src.input.loader import FileInputSource
from src.output.generator import OutputGenerator
from src.processing.processor import DataProcessor
from src.reports.summary import SummaryReportGenerator
from src.logger import logger

def main():
    parser = argparse.ArgumentParser(
        description="Office Work Automation - Excel Data Processing Assistant (CLI)"
    )
    parser.add_argument(
        "--files", "-f", nargs="+", help="Path(s) to input .xlsx file(s)"
    )
    parser.add_argument(
        "--input-dir", "-i", help="Directory containing .xlsx files to process"
    )
    parser.add_argument(
        "--output-dir", "-o", default="output", help="Directory to save generated outputs"
    )
    parser.add_argument(
        "--config", "-c", help="Path to custom JSON configuration file"
    )

    args = parser.parse_args()

    # Determine files to process
    file_paths = []
    if args.files:
        file_paths.extend([Path(f) for f in args.files])
    elif args.input_dir:
        input_path = Path(args.input_dir)
        if not input_path.exists():
            print(f"Error: Input directory '{args.input_dir}' does not exist.")
            sys.exit(1)
        file_paths.extend(list(input_path.glob("*.xlsx")))
    else:
        print("Please provide --files or --input-dir.")
        parser.print_help()
        sys.exit(1)

    if not file_paths:
        print("No .xlsx files found to process.")
        sys.exit(1)

    # Load configuration
    config = load_config(args.config)
    config.output_dir = args.output_dir

    print(f"\nProcessing {len(file_paths)} Excel file(s)...")
    source = FileInputSource(file_paths)
    processor = DataProcessor(config=config)
    result = processor.process_inputs(source)

    # Generate and save outputs
    generator = OutputGenerator(output_dir=args.output_dir)
    saved_files = generator.save_all(result)

    # Print summary to terminal
    print("\n" + SummaryReportGenerator.generate_text_summary(result))
    print("\nOutputs saved to:")
    for name, p in saved_files.items():
        print(f"  {name}: {p}")

if __name__ == "__main__":
    main()
