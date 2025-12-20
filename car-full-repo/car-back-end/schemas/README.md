# Vehicle Selection V1 Schema

This directory contains the **Vehicle Selection V1** schema, a frozen contract for NLP-to-JSON translation training.

## Overview

The Vehicle Selection V1 schema defines a structured format for representing natural language vehicle queries as JSON. This schema is designed specifically for training NLP models to convert user queries into structured vehicle selection criteria.

## Files

- **`vehicle_selection_v1_schema.json`**: JSON Schema (Draft-07) for validation
- **`vehicle_selection_v1_vocab.py`**: Canonical vocabulary definitions (Python constants)
- **`__init__.py`**: Package initialization

## Schema Structure

The schema requires the following top-level fields:

1. **`query_text`** (string): The original natural language query
2. **`vehicle_type`** (object): Body style preferences (include/exclude)
3. **`capacity_practicality`** (object): Seating, cargo, and practicality needs
4. **`intended_use`** (object): Use case tags (family, commute, cargo, etc.)
5. **`powertrain_drivability`** (object): Transmission, drivetrain, fuel type preferences
6. **`features_amenities`** (object): Must-have, nice-to-have, and avoid features
7. **`ownership_constraints`** (object): Budget, year, mileage constraints
8. **`preference_signals`** (object): Reliability and color preferences
9. **`location_constraints`** (object, optional): Geographic constraints

## Canonical Vocabularies

All enum values are defined in `vehicle_selection_v1_vocab.py`. These should be used consistently during:
- Training data generation
- Model inference
- Validation

### Key Vocabularies

- **Body Styles**: sedan, coupe, hatchback, wagon, suv, crossover, van, truck, convertible, minivan, unspecified
- **Use Cases**: family, animals, commute, cargo, travel, work_light, pleasure, performance, rideshare, towing, off_road, luxury, budget_value, unspecified
- **Features**: backup_camera, blind_spot_monitoring, adaptive_cruise_control, apple_carplay, android_auto, heated_seats, leather_seats, sunroof, third_row_seating, lane_keep_assist, lane_departure_warning, front_parking_sensors, rear_parking_sensors, remote_start, heated_steering_wheel, ventilated_seats, wireless_charging, premium_audio, built_in_navigation, roof_rack, tow_package, panoramic_roof, memory_seats, keyless_entry, unspecified
- **Powertrain Types**: gas, hybrid, plug_in_hybrid, electric, diesel, mild_hybrid, unspecified
  - **Note**: `powertrain_type` is an **array** - users can select multiple types (e.g., gas, hybrid, electric)
- **Transmission**: automatic, manual, other, cvt, dual_clutch, unspecified
- **Drivetrains**: AWD, 4WD, FWD, RWD, unspecified
- **Maintenance Priority**: low_cost, balanced, performance_first, luxury_ok, unspecified
- **Mileage Qualitative**: low, moderate, high, low_or_moderate, very_low, very_high, does_not_matter, unspecified
- **Colors**: black, white, silver, gray, grey, red, blue, green, brown, beige, tan, gold, orange, yellow, purple, burgundy, maroon, navy, teal, pink, unspecified

## Key Schema Features

- **"unspecified" sentinel**: All enum fields use "unspecified" instead of null to represent "not mentioned"
- **Array fields**: Several fields support multiple selections:
  - `vehicle_type.include_body_styles[]` - Array of body styles
  - `vehicle_type.exclude_body_styles[]` - Array of excluded body styles
  - `intended_use.use_case_tags[]` - Array of use case tags
  - `powertrain_drivability.powertrain_type[]` - **Array of powertrain types** (can select multiple: gas, hybrid, electric, etc.)
  - `features_amenities.must_have[]` - Array of required features
  - `features_amenities.nice_to_have[]` - Array of preferred features
  - `features_amenities.avoid[]` - Array of features to avoid
- **Integer/Number with unspecified**: Fields like `budget.min`, `budget.max`, `year.min`, `year.max`, `mileage.max`, `number_of_owners` can be integers/numbers or "unspecified"
- **Mileage qualitative**: The `mileage.qualitative` field supports qualitative mileage descriptions (low, moderate, high, very_low, very_high, does_not_matter, or unspecified)
- **Boolean with unspecified**: Fields like `wants_hatch_access`, `wants_fold_flat_seats`, `strict_max` support "true", "false", or "unspecified"
- **String fields**: `make` and `model` are plain strings (no enums), `trim` is a string with "unspecified" option

## Usage for Training

When creating training examples, ensure:

1. **All required fields are present** (even if "unspecified" or empty arrays)
2. **Enum values match canonical vocabulary** exactly
3. **Array fields are arrays** - use `[]` for empty arrays, `["value1", "value2"]` for multiple values
4. **Structure matches schema** (use validator to check)
5. **Query text is preserved** in `query_text` field
6. **Use "unspecified" not null** for enum fields where value is not mentioned

### Example Training Pair

**Input (Natural Language):**
```
"I need an SUV for my family of 5, under $30k, with AWD and backup camera"
```

**Output (JSON):**
```json
{
  "query_text": "I need an SUV for my family of 5, under $30k, with AWD and backup camera",
  "vehicle_type": {
    "include_body_styles": ["suv"],
    "exclude_body_styles": []
  },
  "capacity_practicality": {
    "min_seating_capacity": 5,
    "kid_count": null,
    "pet_count": null,
    "cargo_priority": null,
    "cargo_flexibility": {}
  },
  "intended_use": {
    "use_case_tags": ["family"]
  },
  "powertrain_drivability": {
    "transmission": "unspecified",
    "drivetrain": "AWD",
    "powertrain_type": ["unspecified"],
    "fuel_economy_priority": "unspecified"
  },
  "features_amenities": {
    "must_have": ["backup_camera"],
    "nice_to_have": [],
    "avoid": []
  },
  "ownership_constraints": {
    "budget": {
      "currency": "USD",
      "min": null,
      "max": 30000,
      "strict_max": true
    },
    "year": {
      "min": null,
      "max": null
    },
    "mileage": {
      "max": "unspecified",
      "qualitative": "unspecified"
    }
  },
  "preference_signals": {
    "reliability_maintenance_priority": "unspecified"
  },
  "location_constraints": null
}
```

## Validation

Use the `VehicleSelectionV1Validator` class from `utils/schema_validator.py` to validate training examples:

```python
from utils.schema_validator import VehicleSelectionV1Validator

validator = VehicleSelectionV1Validator()
is_valid, error = validator.validate(json_output)

if not is_valid:
    print(f"Validation error: {error}")
```

## Version

This is **V1** - a frozen contract. Do not modify this schema. For changes, create V2.

