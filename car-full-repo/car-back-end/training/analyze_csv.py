#!/usr/bin/env python3
"""Quick script to analyze the generated CSV"""
import csv
from pathlib import Path

csv_path = Path(__file__).parent / 'unannotated_nlp_prompts.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print("=" * 80)
print("CSV ANALYSIS RESULTS")
print("=" * 80)
print(f"\nTotal rows: {len(rows)}")
print(f"First ID: {rows[0]['id']}")
print(f"Last ID: {rows[-1]['id']}")

# Check for empty fields
empty_json = sum(1 for r in rows if not r['annotated_json'].strip())
empty_status = sum(1 for r in rows if not r['completion_status'].strip())
print(f"\nEmpty annotated_json: {empty_json} (expected: all)")
print(f"Empty completion_status: {empty_status} (expected: all)")

# Check prompt lengths
prompt_lengths = [len(r['prompt']) for r in rows]
print(f"\nPrompt length statistics:")
print(f"  Min: {min(prompt_lengths)} chars")
print(f"  Max: {max(prompt_lengths)} chars")
print(f"  Avg: {sum(prompt_lengths) // len(prompt_lengths)} chars")

# Sample rows at different positions
print(f"\n{'=' * 80}")
print("SAMPLE ROWS")
print("=" * 80)
for idx in [0, 1, 10, 100, 500, 846]:
    row = rows[idx]
    print(f"\nRow {idx+1} ({row['id']}):")
    print(f"  Length: {len(row['prompt'])} chars")
    preview = row['prompt'][:120] + "..." if len(row['prompt']) > 120 else row['prompt']
    print(f"  Preview: {preview}")
    print(f"  Annotated JSON: '{row['annotated_json']}'")
    print(f"  Completion Status: '{row['completion_status']}'")

# Check for any issues
print(f"\n{'=' * 80}")
print("VALIDATION CHECKS")
print("=" * 80)

# Check ID sequence
ids = [r['id'] for r in rows]
expected_ids = [f"prompt_{i+1:03d}" for i in range(len(rows))]
if ids == expected_ids:
    print("[OK] ID sequence is correct")
else:
    print("[ERROR] ID sequence has issues")
    print(f"  First mismatch at index {next((i for i, (a, b) in enumerate(zip(ids, expected_ids)) if a != b), None)}")

# Check for duplicate prompts
prompts = [r['prompt'] for r in rows]
unique_prompts = set(prompts)
if len(prompts) == len(unique_prompts):
    print("[OK] No duplicate prompts found")
else:
    duplicates = len(prompts) - len(unique_prompts)
    print(f"[WARNING] Found {duplicates} duplicate prompt(s)")

# Check for empty prompts
empty_prompts = [i for i, p in enumerate(prompts) if not p.strip()]
if not empty_prompts:
    print("[OK] No empty prompts found")
else:
    print(f"[ERROR] Found {len(empty_prompts)} empty prompt(s) at indices: {empty_prompts[:10]}")

print("\n" + "=" * 80)

