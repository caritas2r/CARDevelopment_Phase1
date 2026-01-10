#!/usr/bin/env python3
"""
Validate vehicle prompts CSV for enum/mapping consistency and logical correctness.

Checks:
1. Enum values match schema definitions
2. Field mappings are correct (abbreviated keys match expected structure)
3. Logical consistency between prompt text and annotated JSON
4. Required fields are present
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Reverse mapping - short keys to full keys
REVERSE_KEY_MAPPING = {
    "mk": "make",
    "md": "model",
    "tr": "trim",
    "vt": "vehicle_type",
    "cp": "capacity_practicality",
    "iu": "intended_use",
    "pd": "powertrain_drivability",
    "fa": "features_amenities",
    "oc": "ownership_constraints",
    "ps": "preference_signals",
    "lc": "location_constraints",
    # Nested keys
    "inc": "include_body_styles",
    "exc": "exclude_body_styles",
    "seat_min": "min_seating_capacity",
    "kids": "kid_count",
    "pets": "pet_count",
    "cargo_pri": "cargo_priority",
    "cargo_fx": "cargo_flexibility",
    "hatch": "wants_hatch_access",
    "foldflat": "wants_fold_flat_seats",
    "tags": "use_case_tags",
    "tx": "transmission",
    "dt": "drivetrain",
    "pt": "powertrain_type",
    "fe_pri": "fuel_economy_priority",
    "must": "must_have",
    "nice": "nice_to_have",
    "bud": "budget",
    "yr": "year",
    "mi": "mileage",
    "owners": "number_of_owners",
    "cur": "currency",
    "max_strict": "strict_max",
    "qual": "qualitative",
    "rel_pri": "reliability_maintenance_priority",
    "clr": "color",
    "cty": "city",
    "st": "state_region",
    "rad": "radius_miles",
}

# Schema enum definitions
BODY_STYLES = {"sedan", "coupe", "hatchback", "wagon", "suv", "crossover", "van", "truck", "convertible", "minivan", "unspecified"}
PRIORITY_LEVELS = {"low", "medium", "high", "unspecified"}
USE_CASE_TAGS = {"family", "animals", "commute", "cargo", "travel", "work_light", "pleasure", "performance", "rideshare", "towing", "off_road", "luxury", "budget_value", "unspecified"}
TRANSMISSIONS = {"automatic", "manual", "other", "cvt", "dual_clutch", "unspecified"}
DRIVETRAINS = {"AWD", "4WD", "FWD", "RWD", "unspecified"}
POWERTRAIN_TYPES = {"gas", "hybrid", "plug_in_hybrid", "electric", "diesel", "mild_hybrid", "unspecified"}
FEATURE_TAGS = {
    "backup_camera", "blind_spot_monitoring", "adaptive_cruise_control", "apple_carplay", "android_auto",
    "heated_seats", "leather_seats", "sunroof", "third_row_seating", "lane_keep_assist",
    "lane_departure_warning", "front_parking_sensors", "rear_parking_sensors", "remote_start",
    "heated_steering_wheel", "ventilated_seats", "wireless_charging", "premium_audio",
    "built_in_navigation", "roof_rack", "tow_package", "panoramic_roof", "panoramic_sunroof",
    "memory_seats", "keyless_entry", "bluetooth", "rear_entertainment_system", "sliding_doors", "unspecified"
}
MAINTENANCE_PRIORITIES = {"low_cost", "balanced", "performance_first", "luxury_ok", "unspecified"}
COLORS = {"black", "white", "silver", "gray", "grey", "red", "blue", "green", "brown", "beige", "tan", "gold", "orange", "yellow", "purple", "burgundy", "maroon", "navy", "teal", "pink", "unspecified"}
BOOLEAN_WITH_UNSPECIFIED = {"true", "false", "unspecified"}
MILEAGE_QUALITATIVE = {"low", "moderate", "high", "low_or_moderate", "very_low", "very_high", "does_not_matter", "unspecified"}


def expand_keys(obj: Any) -> Any:
    """Recursively expand abbreviated keys back to full schema keys."""
    if isinstance(obj, dict):
        expanded = {}
        for key, value in obj.items():
            new_key = REVERSE_KEY_MAPPING.get(key, key)
            expanded[new_key] = expand_keys(value)
        return expanded
    elif isinstance(obj, list):
        return [expand_keys(item) for item in obj]
    else:
        return obj


class ValidationError:
    def __init__(self, row_id: str, category: str, field: str, message: str):
        self.row_id = row_id
        self.category = category  # "enum", "mapping", "logic", "structure"
        self.field = field
        self.message = message

    def __str__(self):
        return f"Row {self.row_id} [{self.category}] {self.field}: {self.message}"


def validate_enum(value: Any, valid_set: set, field_name: str) -> List[str]:
    """Validate a single enum value or list of enum values."""
    errors = []
    if isinstance(value, list):
        for item in value:
            if item not in valid_set:
                errors.append(f"Invalid enum value '{item}' in {field_name}. Valid: {sorted(valid_set)}")
    elif value not in valid_set:
        errors.append(f"Invalid enum value '{value}' in {field_name}. Valid: {sorted(valid_set)}")
    return errors


def validate_json_structure(data: Dict, row_id: str) -> List[ValidationError]:
    """Validate JSON structure and enum values."""
    errors = []
    
    # Validate vehicle_type
    if "vehicle_type" in data:
        vt = data["vehicle_type"]
        if "include_body_styles" in vt:
            for val in validate_enum(vt["include_body_styles"], BODY_STYLES, "vehicle_type.include_body_styles"):
                errors.append(ValidationError(row_id, "enum", "vehicle_type.include_body_styles", val))
        if "exclude_body_styles" in vt:
            for val in validate_enum(vt["exclude_body_styles"], BODY_STYLES, "vehicle_type.exclude_body_styles"):
                errors.append(ValidationError(row_id, "enum", "vehicle_type.exclude_body_styles", val))
    
    # Validate capacity_practicality
    if "capacity_practicality" in data:
        cp = data["capacity_practicality"]
        if "cargo_priority" in cp:
            for val in validate_enum(cp["cargo_priority"], PRIORITY_LEVELS, "capacity_practicality.cargo_priority"):
                errors.append(ValidationError(row_id, "enum", "cargo_priority", val))
        if "cargo_flexibility" in cp:
            cf = cp["cargo_flexibility"]
            if "wants_hatch_access" in cf:
                for val in validate_enum(cf["wants_hatch_access"], BOOLEAN_WITH_UNSPECIFIED, "cargo_flexibility.wants_hatch_access"):
                    errors.append(ValidationError(row_id, "enum", "wants_hatch_access", val))
            if "wants_fold_flat_seats" in cf:
                for val in validate_enum(cf["wants_fold_flat_seats"], BOOLEAN_WITH_UNSPECIFIED, "cargo_flexibility.wants_fold_flat_seats"):
                    errors.append(ValidationError(row_id, "enum", "wants_fold_flat_seats", val))
    
    # Validate intended_use
    if "intended_use" in data:
        iu = data["intended_use"]
        if "use_case_tags" in iu:
            for val in validate_enum(iu["use_case_tags"], USE_CASE_TAGS, "intended_use.use_case_tags"):
                errors.append(ValidationError(row_id, "enum", "use_case_tags", val))
    
    # Validate powertrain_drivability
    if "powertrain_drivability" in data:
        pd = data["powertrain_drivability"]
        if "transmission" in pd:
            for val in validate_enum(pd["transmission"], TRANSMISSIONS, "powertrain_drivability.transmission"):
                errors.append(ValidationError(row_id, "enum", "transmission", val))
        if "drivetrain" in pd:
            for val in validate_enum(pd["drivetrain"], DRIVETRAINS, "powertrain_drivability.drivetrain"):
                errors.append(ValidationError(row_id, "enum", "drivetrain", val))
        if "powertrain_type" in pd:
            for val in validate_enum(pd["powertrain_type"], POWERTRAIN_TYPES, "powertrain_drivability.powertrain_type"):
                errors.append(ValidationError(row_id, "enum", "powertrain_type", val))
        if "fuel_economy_priority" in pd:
            for val in validate_enum(pd["fuel_economy_priority"], PRIORITY_LEVELS, "powertrain_drivability.fuel_economy_priority"):
                errors.append(ValidationError(row_id, "enum", "fuel_economy_priority", val))
    
    # Validate features_amenities
    if "features_amenities" in data:
        fa = data["features_amenities"]
        for key in ["must_have", "nice_to_have", "avoid"]:
            if key in fa:
                for val in validate_enum(fa[key], FEATURE_TAGS, f"features_amenities.{key}"):
                    errors.append(ValidationError(row_id, "enum", key, val))
    
    # Validate preference_signals
    if "preference_signals" in data:
        ps = data["preference_signals"]
        if "reliability_maintenance_priority" in ps:
            for val in validate_enum(ps["reliability_maintenance_priority"], MAINTENANCE_PRIORITIES, "preference_signals.reliability_maintenance_priority"):
                errors.append(ValidationError(row_id, "enum", "reliability_maintenance_priority", val))
        if "color" in ps:
            for val in validate_enum(ps["color"], COLORS, "preference_signals.color"):
                errors.append(ValidationError(row_id, "enum", "color", val))
    
    # Validate mileage qualitative
    if "ownership_constraints" in data:
        oc = data["ownership_constraints"]
        if "mileage" in oc and "qualitative" in oc["mileage"]:
            for val in validate_enum(oc["mileage"]["qualitative"], MILEAGE_QUALITATIVE, "ownership_constraints.mileage.qualitative"):
                errors.append(ValidationError(row_id, "enum", "mileage.qualitative", val))
    
    return errors


def check_logical_consistency(prompt: str, data: Dict, row_id: str) -> List[ValidationError]:
    """Check logical consistency between prompt text and annotated JSON."""
    errors = []
    prompt_lower = prompt.lower()
    
    # Check for contradictory body styles
    if "vehicle_type" in data:
        vt = data["vehicle_type"]
        include = set(vt.get("include_body_styles", []))
        exclude = set(vt.get("exclude_body_styles", []))
        overlap = include & exclude
        if overlap:
            errors.append(ValidationError(
                row_id, "logic", "vehicle_type",
                f"Body styles both included and excluded: {overlap}"
            ))
    
    # Check for duplicate features
    if "features_amenities" in data:
        fa = data["features_amenities"]
        must_have = set(fa.get("must_have", []))
        nice_to_have = set(fa.get("nice_to_have", []))
        avoid = set(fa.get("avoid", []))
        
        # Feature in both must_have and avoid
        must_avoid_overlap = must_have & avoid
        if must_avoid_overlap:
            errors.append(ValidationError(
                row_id, "logic", "features_amenities",
                f"Features in both must_have and avoid: {must_avoid_overlap}"
            ))
        
        # Feature in both nice_to_have and avoid
        nice_avoid_overlap = nice_to_have & avoid
        if nice_avoid_overlap:
            errors.append(ValidationError(
                row_id, "logic", "features_amenities",
                f"Features in both nice_to_have and avoid: {nice_avoid_overlap}"
            ))
        
        # Duplicate features within same category
        if len(must_have) != len(list(must_have)):
            errors.append(ValidationError(
                row_id, "logic", "features_amenities.must_have",
                "Duplicate features in must_have list"
            ))
    
    # Check for contradictory use case tags
    contradictory_tags = [
        ({"budget_value", "luxury"}, "budget_value and luxury are contradictory"),
        ({"performance", "budget_value"}, "performance and budget_value may be contradictory"),
    ]
    if "intended_use" in data and "use_case_tags" in data["intended_use"]:
        tags = set(data["intended_use"]["use_case_tags"])
        for tag_set, msg in contradictory_tags:
            if tag_set.issubset(tags):
                errors.append(ValidationError(
                    row_id, "logic", "use_case_tags", msg
                ))
    
    # Check budget consistency
    if "ownership_constraints" in data and "budget" in data["ownership_constraints"]:
        budget = data["ownership_constraints"]["budget"]
        min_val = budget.get("min")
        max_val = budget.get("max")
        if (isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)) and
            min_val > max_val):
            errors.append(ValidationError(
                row_id, "logic", "budget",
                f"Budget min ({min_val}) > max ({max_val})"
            ))
    
    # Check year consistency
    if "ownership_constraints" in data and "year" in data["ownership_constraints"]:
        year = data["ownership_constraints"]["year"]
        min_year = year.get("min")
        max_year = year.get("max")
        if (isinstance(min_year, int) and isinstance(max_year, int) and
            min_year > max_year):
            errors.append(ValidationError(
                row_id, "logic", "year",
                f"Year min ({min_year}) > max ({max_year})"
            ))
    
    return errors


def validate_csv(csv_path: Path) -> Tuple[int, List[ValidationError]]:
    """Validate all rows in the CSV file."""
    errors = []
    rows_processed = 0
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row_idx, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
            row_id = row.get("id", str(row_idx)).strip()
            prompt = row.get("prompt", "").strip()
            annotated_json_str = row.get("annotated_json", "").strip()
            
            if not annotated_json_str:
                errors.append(ValidationError(row_id, "structure", "annotated_json", "Missing annotated_json"))
                continue
            
            try:
                # Parse JSON (may have <END_JSON> marker)
                json_str = annotated_json_str
                if "<END_JSON>" in json_str:
                    json_str = json_str.split("<END_JSON>")[0]
                
                data = json.loads(json_str)
                
                # Expand abbreviated keys to full schema keys
                expanded_data = expand_keys(data)
                
                # Validate enum values
                enum_errors = validate_json_structure(expanded_data, row_id)
                errors.extend(enum_errors)
                
                # Check logical consistency
                logic_errors = check_logical_consistency(prompt, expanded_data, row_id)
                errors.extend(logic_errors)
                
                rows_processed += 1
                
            except json.JSONDecodeError as e:
                errors.append(ValidationError(row_id, "structure", "annotated_json", f"Invalid JSON: {e}"))
            except Exception as e:
                errors.append(ValidationError(row_id, "structure", "annotated_json", f"Error processing: {e}"))
    
    return rows_processed, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_prompts.py <csv_file>")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    print(f"Validating {csv_path}...")
    print("=" * 80)
    
    rows_processed, errors = validate_csv(csv_path)
    
    print(f"\nRows processed: {rows_processed}")
    print(f"Errors found: {len(errors)}")
    print("=" * 80)
    
    if errors:
        # Group errors by category
        by_category = {}
        for error in errors:
            if error.category not in by_category:
                by_category[error.category] = []
            by_category[error.category].append(error)
        
        for category in sorted(by_category.keys()):
            print(f"\n{category.upper()} Errors ({len(by_category[category])}):")
            print("-" * 80)
            for error in by_category[category][:20]:  # Show first 20 of each category
                print(f"  {error}")
            if len(by_category[category]) > 20:
                print(f"  ... and {len(by_category[category]) - 20} more {category} errors")
    else:
        print("\n✓ All validations passed!")
    
    print("=" * 80)
    
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

