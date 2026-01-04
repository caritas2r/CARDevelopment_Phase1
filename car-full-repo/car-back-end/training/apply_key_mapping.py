#!/usr/bin/env python3
"""
apply_key_mapping.py

Apply key shortening mapping to JSON in label:true "text" segments inside template-free segments JSONL.

This script transforms all keys in the JSON payload according to the key_mapping_schema.md
to reduce token usage while maintaining readability.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

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


def _apply_key_mapping_to_text(txt: str, line_no: int, seg_idx: int) -> Tuple[str, bool]:
    """
    Given a segment text, strip END_MARKER if present, parse JSON, apply key mapping,
    re-dump minified, then append END_MARKER with no whitespace/newlines.

    Returns: (new_text, changed?)
    """
    if txt is None:
        return txt, False

    original = txt

    # Remove everything after the first END_MARKER if present
    if END_MARKER in txt:
        txt = txt.split(END_MARKER, 1)[0]

    txt_stripped = txt.strip()
    if not txt_stripped:
        return original, False

    try:
        obj = json.loads(txt_stripped)
    except json.JSONDecodeError as e:
        print(
            f"Warning: line {line_no} seg {seg_idx}: label:true text is not valid JSON: {e}",
            file=sys.stderr,
        )
        return original, False

    # Apply key transformation
    transformed_obj = transform_keys(obj)
    
    # Minify and add END_MARKER
    minified = json.dumps(transformed_obj, ensure_ascii=False, separators=(",", ":"))
    new_text = minified + END_MARKER

    return new_text, (new_text != original)


def process_file(in_path: Path, out_path: Path, in_place: bool) -> None:
    """
    Process a JSONL file and write results to out_path.
    If in_place=True, we write to a temp file then replace the original.
    """
    tmp_path = out_path
    if in_place:
        tmp_path = in_path.with_suffix(in_path.suffix + ".tmp")

    total_lines = 0
    total_json_lines = 0
    segments_transformed = 0
    lines_with_changes = 0
    skipped_invalid_json_lines = 0

    with in_path.open("r", encoding="utf-8") as f_in, tmp_path.open("w", encoding="utf-8") as f_out:
        for line_no, line in enumerate(f_in, start=1):
            total_lines += 1
            line = line.rstrip("\n")
            if not line.strip():
                # Strict JSONL: skip empty lines
                continue

            try:
                ex: Dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as e:
                skipped_invalid_json_lines += 1
                print(f"Warning: line {line_no}: invalid JSONL line: {e}", file=sys.stderr)
                # Preserve the raw line to avoid data loss
                f_out.write(line + "\n")
                continue

            total_json_lines += 1
            segs = ex.get("segments", [])
            changed_this_line = False

            for seg_idx, seg in enumerate(segs):
                if seg.get("label") is True and "text" in seg:
                    new_text, changed = _apply_key_mapping_to_text(
                        seg.get("text"), line_no=line_no, seg_idx=seg_idx
                    )
                    if changed:
                        seg["text"] = new_text
                        segments_transformed += 1
                        changed_this_line = True

            if changed_this_line:
                lines_with_changes += 1

            f_out.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # If in-place, atomically replace original
    if in_place:
        tmp_path.replace(in_path)
        final_out = in_path
    else:
        final_out = out_path

    print(f"{in_path} -> {final_out}")
    print(f"  Total lines read:              {total_lines}")
    print(f"  JSON records processed:        {total_json_lines}")
    print(f"  Lines with any changes:        {lines_with_changes}")
    print(f"  label:true segments transformed: {segments_transformed}")
    if skipped_invalid_json_lines:
        print(f"  Invalid JSONL lines preserved: {skipped_invalid_json_lines}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply key mapping to label:true JSON text segments in template-free segments JSONL files."
    )
    parser.add_argument("files", nargs="+", help="Input JSONL file(s) to process")
    parser.add_argument(
        "--in-place",
        "-i",
        action="store_true",
        help="Overwrite input files in place (safe temp write then replace).",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (only valid when processing a single input file).",
    )
    parser.add_argument(
        "--suffix",
        default="_mapped",
        help="Suffix used when generating output paths (default: _mapped). Ignored with --in-place or --output.",
    )
    args = parser.parse_args()

    if args.output and len(args.files) != 1:
        parser.error("--output can only be used with a single input file")

    for file_str in args.files:
        in_path = Path(file_str)
        if not in_path.exists():
            print(f"Error: file not found: {in_path}", file=sys.stderr)
            continue

        if args.in_place:
            out_path = in_path  # not used directly; we write temp then replace
        elif args.output:
            out_path = Path(args.output)
        else:
            out_path = in_path.with_name(in_path.stem + args.suffix + in_path.suffix)

        process_file(in_path=in_path, out_path=out_path, in_place=args.in_place)
        print()


if __name__ == "__main__":
    main()

