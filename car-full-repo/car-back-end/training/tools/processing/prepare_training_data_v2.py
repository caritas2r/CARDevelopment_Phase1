#!/usr/bin/env python3
"""
prepare_training_data_v2.py

Complete pipeline to convert annotated CSV to training-ready JSONL files with 80/10/10 split.

Process:
1. Read annotated_nlp_prompts.csv
2. Convert to template-free segments JSONL format with key mapping
3. Randomly split into 80% train, 10% test, 10% validation
4. Output: train_mapped_v2.jsonl, test_mapped_v2.jsonl, validation_mapped_v2.jsonl
"""

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

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


def convert_csv_to_jsonl(
    csv_path: Path,
    completion_status: str = "complete"
) -> List[Dict[str, Any]]:
    """
    Convert annotated CSV to list of JSONL entries (template-free segments format).
    
    Args:
        csv_path: Path to annotated_nlp_prompts.csv
        completion_status: Status to filter by (default: "complete")
    
    Returns:
        List of JSONL entry dictionaries
    """
    jsonl_entries = []
    errors = []
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}", file=sys.stderr)
        return jsonl_entries
    
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        
        # Validate required columns
        required_columns = {"id", "prompt", "annotated_json", "completion_status"}
        if not required_columns.issubset(reader.fieldnames or []):
            missing = required_columns - set(reader.fieldnames or [])
            print(f"Error: Missing required columns: {missing}", file=sys.stderr)
            return jsonl_entries
        
        for row_idx, row in enumerate(reader, start=1):
            row_id = row.get("id", "").strip()
            prompt = row.get("prompt", "").strip()
            annotated_json_str = row.get("annotated_json", "").strip()
            status = row.get("completion_status", "").strip().lower()
            
            # Check completion status
            if status not in (completion_status.lower(), "true"):
                continue
            
            # Validate required fields
            if not row_id:
                errors.append(f"Row {row_idx}: Missing id")
                continue
            
            if not prompt:
                errors.append(f"Row {row_idx} ({row_id}): Missing prompt")
                continue
            
            if not annotated_json_str:
                errors.append(f"Row {row_idx} ({row_id}): Missing annotated_json")
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
                
                jsonl_entries.append(jsonl_entry)
                
            except json.JSONDecodeError as e:
                errors.append(f"Row {row_idx} ({row_id}): Invalid JSON in annotated_json: {e}")
            except Exception as e:
                errors.append(f"Row {row_idx} ({row_id}): Error: {e}")
    
    if errors:
        print(f"\nWarnings: {len(errors)} errors encountered during conversion:")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    return jsonl_entries


def split_jsonl_entries(
    entries: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    test_ratio: float = 0.1,
    val_ratio: float = 0.1,
    seed: int = 42
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split JSONL entries into train, test, and validation sets.
    
    Args:
        entries: List of JSONL entry dictionaries
        train_ratio: Proportion for training set (default: 0.8)
        test_ratio: Proportion for test set (default: 0.1)
        val_ratio: Proportion for validation set (default: 0.1)
        seed: Random seed for reproducibility (default: 42)
    
    Returns:
        Tuple of (train_entries, test_entries, val_entries)
    """
    # Validate ratios sum to 1.0
    if abs(train_ratio + test_ratio + val_ratio - 1.0) > 0.001:
        raise ValueError(f"Ratios must sum to 1.0, got {train_ratio + test_ratio + val_ratio}")
    
    # Shuffle with seed for reproducibility
    random.seed(seed)
    shuffled = entries.copy()
    random.shuffle(shuffled)
    
    total = len(shuffled)
    train_size = int(total * train_ratio)
    test_size = int(total * test_ratio)
    
    train_entries = shuffled[:train_size]
    test_entries = shuffled[train_size:train_size + test_size]
    val_entries = shuffled[train_size + test_size:]
    
    return train_entries, test_entries, val_entries


def write_jsonl(entries: List[Dict[str, Any]], output_path: Path) -> None:
    """Write JSONL entries to file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert annotated CSV to training-ready JSONL files with 80/10/10 split"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="annotated_nlp_prompts.csv",
        help="Input CSV file (default: annotated_nlp_prompts.csv)"
    )
    parser.add_argument(
        "--output-dir",
        "-d",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--train-output",
        default="train_mapped_v2.jsonl",
        help="Training set output file (default: train_mapped_v2.jsonl)"
    )
    parser.add_argument(
        "--test-output",
        default="test_mapped_v2.jsonl",
        help="Test set output file (default: test_mapped_v2.jsonl)"
    )
    parser.add_argument(
        "--val-output",
        default="validation_mapped_v2.jsonl",
        help="Validation set output file (default: validation_mapped_v2.jsonl)"
    )
    parser.add_argument(
        "--status",
        "-s",
        default="complete",
        help="Completion status to filter by (default: complete)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for splitting (default: 42)"
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Training set ratio (default: 0.8)"
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.1,
        help="Test set ratio (default: 0.1)"
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="Validation set ratio (default: 0.1)"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    csv_path = script_dir / args.input
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_path = output_dir / args.train_output
    test_path = output_dir / args.test_output
    val_path = output_dir / args.val_output
    
    print("=" * 80)
    print("TRAINING DATA PREPARATION V2")
    print("=" * 80)
    print(f"\nInput CSV: {csv_path}")
    print(f"Output directory: {output_dir}")
    print(f"Filtering by completion_status: {args.status}")
    print(f"Random seed: {args.seed}")
    print(f"Split ratios: Train={args.train_ratio:.0%}, Test={args.test_ratio:.0%}, Val={args.val_ratio:.0%}")
    print("=" * 80)
    
    # Step 1: Convert CSV to JSONL entries
    print("\n[Step 1] Converting CSV to JSONL format...")
    jsonl_entries = convert_csv_to_jsonl(csv_path, args.status)
    print(f"  Converted {len(jsonl_entries)} entries")
    
    if not jsonl_entries:
        print("\nError: No entries to process. Exiting.")
        sys.exit(1)
    
    # Step 2: Split into train/test/validation
    print(f"\n[Step 2] Splitting into train/test/validation sets...")
    train_entries, test_entries, val_entries = split_jsonl_entries(
        jsonl_entries,
        train_ratio=args.train_ratio,
        test_ratio=args.test_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed
    )
    
    print(f"  Training set: {len(train_entries)} entries ({len(train_entries)/len(jsonl_entries):.1%})")
    print(f"  Test set: {len(test_entries)} entries ({len(test_entries)/len(jsonl_entries):.1%})")
    print(f"  Validation set: {len(val_entries)} entries ({len(val_entries)/len(jsonl_entries):.1%})")
    
    # Step 3: Write output files
    print(f"\n[Step 3] Writing output files...")
    write_jsonl(train_entries, train_path)
    print(f"  Written: {train_path}")
    
    write_jsonl(test_entries, test_path)
    print(f"  Written: {test_path}")
    
    write_jsonl(val_entries, val_path)
    print(f"  Written: {val_path}")
    
    print("\n" + "=" * 80)
    print("SUCCESS")
    print("=" * 80)
    print(f"\nTotal entries processed: {len(jsonl_entries)}")
    print(f"Training set: {len(train_entries)} entries -> {train_path}")
    print(f"Test set: {len(test_entries)} entries -> {test_path}")
    print(f"Validation set: {len(val_entries)} entries -> {val_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()

