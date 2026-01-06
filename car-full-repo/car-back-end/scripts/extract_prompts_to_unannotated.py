#!/usr/bin/env python3
"""
Extract prompts from annotated CSV files and append them to unannotated_nlp_prompts.csv.

This script:
1. Reads one or more annotated CSV files
2. Extracts just the prompt text
3. Finds the next available ID in unannotated_nlp_prompts.csv
4. Appends new rows with empty annotations
"""

import csv
import sys
from pathlib import Path
from typing import List, Tuple


def get_next_id(unannotated_path: Path) -> int:
    """Find the highest existing prompt ID and return the next one."""
    if not unannotated_path.exists():
        return 1
    
    max_id = 0
    with open(unannotated_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_str = row.get('id', '')
            if id_str.startswith('prompt_'):
                try:
                    id_num = int(id_str.replace('prompt_', ''))
                    max_id = max(max_id, id_num)
                except ValueError:
                    continue
    
    return max_id + 1


def extract_prompts_from_file(csv_path: Path) -> List[str]:
    """Extract prompt texts from an annotated CSV file."""
    prompts = []
    
    if not csv_path.exists():
        print(f"Warning: File not found: {csv_path}")
        return prompts
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompt = row.get('prompt', '').strip()
            if prompt:  # Only add non-empty prompts
                prompts.append(prompt)
    
    return prompts


def append_prompts_to_unannotated(
    unannotated_path: Path,
    prompts: List[str],
    start_id: int
) -> int:
    """Append prompts to unannotated CSV file. Returns number of prompts added."""
    
    # Ensure parent directory exists
    unannotated_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Append mode - if file doesn't exist, write header first
    file_exists = unannotated_path.exists()
    
    with open(unannotated_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['id', 'prompt', 'annotated_json', 'completion_status'])
        
        # Write each prompt with generated ID
        for i, prompt in enumerate(prompts):
            prompt_id = f'prompt_{start_id + i:03d}'
            writer.writerow([prompt_id, prompt, '', ''])
    
    return len(prompts)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python extract_prompts_to_unannotated.py <annotated_csv1> [annotated_csv2] ...")
        print("\nExample:")
        print("  python extract_prompts_to_unannotated.py post_mapping_dataset_extension_100_1.csv")
        sys.exit(1)
    
    # Get script directory and training directory
    script_dir = Path(__file__).parent
    training_dir = script_dir.parent / 'training'
    unannotated_path = training_dir / 'unannotated_nlp_prompts.csv'
    
    # Get next available ID
    next_id = get_next_id(unannotated_path)
    print(f"Next available ID: prompt_{next_id:03d}")
    print(f"Target file: {unannotated_path}")
    print("=" * 80)
    
    # Extract prompts from all input files
    all_prompts = []
    for csv_file_arg in sys.argv[1:]:
        csv_path = Path(csv_file_arg)
        
        # If relative path, try both script directory and training directory
        if not csv_path.is_absolute():
            if (training_dir / csv_path.name).exists():
                csv_path = training_dir / csv_path.name
            elif (script_dir / csv_path.name).exists():
                csv_path = script_dir / csv_path.name
            elif csv_path.exists():
                pass  # Use as-is
            else:
                print(f"Error: File not found: {csv_file_arg}")
                sys.exit(1)
        
        print(f"\nReading: {csv_path}")
        prompts = extract_prompts_from_file(csv_path)
        print(f"  Extracted {len(prompts)} prompts")
        all_prompts.extend(prompts)
    
    if not all_prompts:
        print("\nNo prompts found in input files!")
        sys.exit(1)
    
    print(f"\nTotal prompts to add: {len(all_prompts)}")
    
    # Confirm before appending
    response = input(f"\nAppend {len(all_prompts)} prompts to {unannotated_path}? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Append to unannotated CSV
    added_count = append_prompts_to_unannotated(unannotated_path, all_prompts, next_id)
    
    print(f"\n{'='*80}")
    print("SUCCESS")
    print(f"{'='*80}")
    print(f"Added {added_count} prompts to {unannotated_path}")
    print(f"New prompts have IDs: prompt_{next_id:03d} through prompt_{next_id + added_count - 1:03d}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

