#!/usr/bin/env python3
"""
csv_to_template_free_mapped.py

Convert annotated CSV to template-free segments JSONL format with:
- Shortened keys (mk, md, vt, etc.)
- Minified JSON (no spaces, no newlines)
- END_MARKER appended
- Template-free segments format

This script reads annotated_nlp_prompts.csv and outputs training-ready JSONL files
that match the format of train_template_free_updated.jsonl (after mapping and minification).
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

END_MARKER = "<END_JSON>"

# Key mapping dictionary - maps original keys to shortened keys
KEY_MAPPING = {
    # Top-level keys
    "make": "mk",
    "model": "md",
    "trim": "tr",
    "vehicle_type": "vt",
    "capacity_practicality": "cp",
    "intended_use": "iu",
    "powertrain_drivability": "pd",
    "features_amenities": "fa",
    "ownership_constraints": "oc",
    "preference_signals": "ps",
    "location_constraints": "lc",
    # Nested keys - vehicle_type
    "include_body_styles": "inc",
    "exclude_body_styles": "exc",
    # Nested keys - capacity_practicality
    "min_seating_capacity": "seat_min",
    "kid_count": "kids",
    "pet_count": "pets",
    "cargo_priority": "cargo_pri",
    "cargo_flexibility": "cargo_fx",
    # Nested keys - cargo_flexibility
    "wants_hatch_access": "hatch",
    "wants_fold_flat_seats": "foldflat",
    # Nested keys - intended_use
    "use_case_tags": "tags",
    # Nested keys - powertrain_drivability
    "transmission": "tx",
    "drivetrain": "dt",
    "powertrain_type": "pt",
    "fuel_economy_priority": "fe_pri",
    # Nested keys - features_amenities
    "must_have": "must",
    "nice_to_have": "nice",
    # "avoid" stays the same
    # Nested keys - ownership_constraints
    "budget": "bud",
    "year": "yr",
    "mileage": "mi",
    "number_of_owners": "owners",
    # Nested keys - budget
    "currency": "cur",
    "strict_max": "max_strict",
    # "min" and "max" stay the same
    # Nested keys - mileage
    "qualitative": "qual",
    # Nested keys - preference_signals
    "reliability_maintenance_priority": "rel_pri",
    "color": "clr",
    # Nested keys - location_constraints
    "city": "cty",
    "state_region": "st",
    "radius_miles": "rad",
}


def transform_keys(obj: Any) -> Any:
    """
    Recursively transform keys in a JSON object according to KEY_MAPPING.
    
    Handles:
    - Dictionaries: transform keys and recurse into values
    - Lists: recurse into each element
    - Primitives: return as-is
    """
    if isinstance(obj, dict):
        transformed = {}
        for key, value in obj.items():
            # Skip query_text if present (not part of schema)
            if key == "query_text":
                continue
            # Map the key if it exists in KEY_MAPPING, otherwise keep original
            new_key = KEY_MAPPING.get(key, key)
            # Recursively transform the value
            transformed[new_key] = transform_keys(value)
        return transformed
    elif isinstance(obj, list):
        # Transform each element in the list
        return [transform_keys(item) for item in obj]
    else:
        # Primitives (str, int, float, bool, None) - return as-is
        return obj


def process_csv_to_jsonl(
    csv_path: Path,
    output_path: Path,
    completion_status: str = "complete"
) -> tuple[int, int, list[str]]:
    """
    Convert annotated CSV to template-free segments JSONL format.
    
    Args:
        csv_path: Path to annotated_nlp_prompts.csv
        output_path: Path to output JSONL file
        completion_status: Status to filter by (default: "complete")
    
    Returns:
        Tuple of (rows_processed, rows_skipped, errors)
    """
    rows_processed = 0
    rows_skipped = 0
    errors = []
    
    if not csv_path.exists():
        errors.append(f"CSV file not found: {csv_path}")
        return rows_processed, rows_skipped, errors
    
    with open(csv_path, "r", encoding="utf-8") as csv_file, \
         open(output_path, "w", encoding="utf-8") as jsonl_file:
        
        reader = csv.DictReader(csv_file)
        
        # Validate required columns
        required_columns = {"id", "prompt", "annotated_json", "completion_status"}
        if not required_columns.issubset(reader.fieldnames or []):
            missing = required_columns - set(reader.fieldnames or [])
            errors.append(f"Missing required columns: {missing}")
            return rows_processed, rows_skipped, errors
        
        for row_idx, row in enumerate(reader, start=1):
            row_id = row.get("id", "").strip()
            prompt = row.get("prompt", "").strip()
            annotated_json_str = row.get("annotated_json", "").strip()
            status = row.get("completion_status", "").strip().lower()
            
            # Check completion status
            if status not in (completion_status.lower(), "true"):
                rows_skipped += 1
                continue
            
            # Validate required fields
            if not row_id:
                errors.append(f"Row {row_idx}: Missing id")
                rows_skipped += 1
                continue
            
            if not prompt:
                errors.append(f"Row {row_idx} ({row_id}): Missing prompt")
                rows_skipped += 1
                continue
            
            if not annotated_json_str:
                errors.append(f"Row {row_idx} ({row_id}): Missing annotated_json")
                rows_skipped += 1
                continue
            
            try:
                # Parse the annotated JSON (may have formatting/indentation)
                annotated_json = json.loads(annotated_json_str)
                
                # Remove query_text if present (not part of output schema)
                if "query_text" in annotated_json:
                    del annotated_json["query_text"]
                
                # Apply key mapping (full keys -> short keys)
                mapped_json = transform_keys(annotated_json)
                
                # Minify JSON (no spaces, no newlines)
                minified_json = json.dumps(mapped_json, ensure_ascii=False, separators=(",", ":"))
                
                # Add END_MARKER
                json_text = minified_json + END_MARKER
                
                # Create template-free segments format
                # Ensure prompt ends with newline
                prompt_text = prompt if prompt.endswith("\n") else prompt + "\n"
                
                jsonl_entry = {
                    "segments": [
                        {"label": False, "text": prompt_text},
                        {"label": True, "text": json_text}
                    ]
                }
                
                # Write as a single line (JSONL format)
                jsonl_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")
                rows_processed += 1
                
            except json.JSONDecodeError as e:
                errors.append(f"Row {row_idx} ({row_id}): Invalid JSON in annotated_json: {e}")
                rows_skipped += 1
            except Exception as e:
                errors.append(f"Row {row_idx} ({row_id}): Error: {e}")
                rows_skipped += 1
    
    return rows_processed, rows_skipped, errors


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert annotated CSV to template-free segments JSONL with mapped keys and minified JSON"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="annotated_nlp_prompts.csv",
        help="Input CSV file (default: annotated_nlp_prompts.csv)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="train_template_free_mapped.jsonl",
        help="Output JSONL file (default: train_template_free_mapped.jsonl)"
    )
    parser.add_argument(
        "--status",
        "-s",
        default="complete",
        help="Completion status to filter by (default: complete)"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    csv_path = script_dir / args.input
    output_path = script_dir / args.output
    
    print(f"Converting {csv_path} to {output_path}...")
    print(f"Filtering by completion_status: {args.status}")
    print("=" * 60)
    
    rows_processed, rows_skipped, errors = process_csv_to_jsonl(
        csv_path, output_path, args.status
    )
    
    print(f"\n{'='*60}")
    print("CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Rows processed: {rows_processed}")
    print(f"Rows skipped: {rows_skipped}")
    
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    print(f"\nOutput written to: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

