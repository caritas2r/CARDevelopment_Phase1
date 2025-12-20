#!/usr/bin/env python3
"""
CSV Reset Script
Resets a CSV file by clearing all annotated_json values and setting completion_status to incomplete
"""
import sys
import csv
from pathlib import Path


def reset_csv(csv_path: Path):
    """
    Reset CSV file by clearing annotated_json and setting completion_status to incomplete
    
    Args:
        csv_path: Path to the CSV file to reset
    """
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Read all rows
    rows = []
    fieldnames = None
    
    print(f"Reading CSV file: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            print("Error: CSV file has no columns")
            sys.exit(1)
        
        for row in reader:
            rows.append(row)
    
    print(f"Found {len(rows)} rows")
    
    # Reset each row
    reset_count = 0
    for row in rows:
        # Clear annotated_json
        row['annotated_json'] = ''
        
        # Set completion_status to incomplete
        row['completion_status'] = 'incomplete'
        
        reset_count += 1
    
    # Write back to file
    print(f"Resetting {reset_count} rows...")
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Successfully reset {reset_count} rows in {csv_path}")
    print("All annotated_json fields cleared and completion_status set to 'incomplete'")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python reset_csv.py <csv_file> [--force]")
        print("\nExample:")
        print("  python reset_csv.py prompts.csv")
        print("  python reset_csv.py \"C:\\Users\\Sol\\Downloads\\vehicle_nlp_prompts.csv\" --force")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    force = '--force' in sys.argv or '-f' in sys.argv
    
    # Confirm before resetting (unless --force is used)
    if not force:
        print(f"\nWARNING: This will reset the CSV file: {csv_path}")
        print("All annotated_json values will be cleared and completion_status set to 'incomplete'")
        
        response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()
        
        if response not in ('yes', 'y'):
            print("Reset cancelled.")
            sys.exit(0)
    
    reset_csv(csv_path)


if __name__ == '__main__':
    main()


