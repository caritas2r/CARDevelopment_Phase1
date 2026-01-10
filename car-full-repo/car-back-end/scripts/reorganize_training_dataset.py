#!/usr/bin/env python3
"""
Reorganize the training dataset by:
1. Extracting prompts from vehicle_prompts_200.csv (no annotations)
2. Extracting prompts from post_mapping_dataset_extension_100_1.csv (no annotations)
3. Keeping rows 1-220 unchanged (already annotated)
4. Deleting rows 300-500
5. Randomizing and re-indexing rows 221+ with new prompts mixed in
"""

import csv
import random
import sys
from pathlib import Path
from typing import List, Tuple


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
            if prompt:
                prompts.append(prompt)
    
    return prompts


def read_unannotated_csv(csv_path: Path) -> List[Tuple[str, str]]:
    """Read unannotated CSV and return list of (id, prompt) tuples."""
    rows = []
    
    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        return rows
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = row.get('id', '').strip()
            prompt = row.get('prompt', '').strip()
            rows.append((row_id, prompt))
    
    return rows


def write_unannotated_csv(csv_path: Path, rows: List[Tuple[str, str]]):
    """Write unannotated CSV with (id, prompt) tuples."""
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'prompt', 'annotated_json', 'completion_status'])
        
        for row_id, prompt in rows:
            writer.writerow([row_id, prompt, '', ''])


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    training_dir = script_dir.parent / 'training'
    
    # File paths
    unannotated_path = training_dir / 'unannotated_nlp_prompts.csv'
    vehicle_200_path = Path(r'c:\Users\Sol\Downloads\vehicle_prompts_200.csv')
    post_mapping_path = training_dir / 'post_mapping_dataset_extension_100_1.csv'
    
    print("=" * 80)
    print("Reorganizing Training Dataset")
    print("=" * 80)
    
    # Step 1: Read current unannotated CSV
    print("\n1. Reading current unannotated_nlp_prompts.csv...")
    current_rows = read_unannotated_csv(unannotated_path)
    print(f"   Found {len(current_rows)} rows")
    
    if len(current_rows) < 220:
        print(f"Error: Need at least 220 rows, but found {len(current_rows)}")
        sys.exit(1)
    
    # Step 2: Extract prompts from new files
    print("\n2. Extracting prompts from new files...")
    
    vehicle_200_prompts = extract_prompts_from_file(vehicle_200_path)
    print(f"   Extracted {len(vehicle_200_prompts)} prompts from vehicle_prompts_200.csv")
    
    post_mapping_prompts = extract_prompts_from_file(post_mapping_path)
    print(f"   Extracted {len(post_mapping_prompts)} prompts from post_mapping_dataset_extension_100_1.csv")
    
    # Step 3: Keep rows 1-220 unchanged
    print("\n3. Preserving rows 1-220 (already annotated)...")
    preserved_rows = current_rows[:220]
    print(f"   Preserved {len(preserved_rows)} rows")
    
    # Step 4: Get rows 221-299 and 501-end (skip 300-500)
    print("\n4. Extracting rows 221-299 and 501+ (removing 300-500)...")
    rows_221_299 = current_rows[220:299]  # Index 220-298 (rows 221-299)
    rows_501_end = current_rows[500:] if len(current_rows) > 500 else []  # Index 500+ (rows 501+)
    
    print(f"   Extracted {len(rows_221_299)} rows from range 221-299")
    print(f"   Extracted {len(rows_501_end)} rows from range 501+")
    print(f"   Deleted {min(500, len(current_rows)) - 299} rows (300-500)")
    
    # Step 5: Extract prompts from the existing rows (221-299 and 501+)
    existing_prompts_221_plus = [prompt for _, prompt in rows_221_299] + [prompt for _, prompt in rows_501_end]
    
    # Step 6: Combine all prompts for rows 221+
    print("\n5. Combining all prompts for rows 221+...")
    all_prompts_221_plus = (
        existing_prompts_221_plus +
        vehicle_200_prompts +
        post_mapping_prompts
    )
    print(f"   Total prompts to randomize: {len(all_prompts_221_plus)}")
    print(f"     - Existing prompts (221-299, 501+): {len(existing_prompts_221_plus)}")
    print(f"     - New from vehicle_prompts_200.csv: {len(vehicle_200_prompts)}")
    print(f"     - New from post_mapping_dataset_extension_100_1.csv: {len(post_mapping_prompts)}")
    
    # Step 7: Randomize
    print("\n6. Randomizing prompts...")
    random.seed(42)  # For reproducibility
    random.shuffle(all_prompts_221_plus)
    print(f"   Randomized {len(all_prompts_221_plus)} prompts")
    
    # Step 8: Re-index starting at prompt_221
    print("\n7. Re-indexing starting at prompt_221...")
    reindexed_rows = []
    for i, prompt in enumerate(all_prompts_221_plus):
        new_id = f'prompt_{221 + i:03d}'
        reindexed_rows.append((new_id, prompt))
    
    print(f"   Created {len(reindexed_rows)} rows with IDs prompt_221 through prompt_{220 + len(reindexed_rows):03d}")
    
    # Step 9: Combine preserved rows (1-220) with reindexed rows (221+)
    print("\n8. Combining preserved and reindexed rows...")
    final_rows = preserved_rows + reindexed_rows
    print(f"   Final dataset size: {len(final_rows)} rows")
    
    # Step 10: Write back
    print("\n9. Writing updated dataset...")
    write_unannotated_csv(unannotated_path, final_rows)
    print(f"   Wrote to: {unannotated_path}")
    
    print("\n" + "=" * 80)
    print("SUCCESS")
    print("=" * 80)
    print(f"[OK] Preserved rows 1-220 (unchanged)")
    print(f"[OK] Deleted rows 300-500")
    print(f"[OK] Randomized and re-indexed rows 221+ ({len(reindexed_rows)} rows)")
    print(f"[OK] Mixed new prompts into existing dataset to avoid clumping")
    print("=" * 80)


if __name__ == "__main__":
    main()

