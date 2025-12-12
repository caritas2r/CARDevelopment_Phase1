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
8. **`preference_signals`** (object): Reliability and safety priorities
9. **`location_constraints`** (object, optional): Geographic constraints

## Canonical Vocabularies

All enum values are defined in `vehicle_selection_v1_vocab.py`. These should be used consistently during:
- Training data generation
- Model inference
- Validation

### Key Vocabularies

- **Body Styles**: sedan, coupe, hatchback, wagon, suv, crossover, van, truck
- **Use Cases**: family, animals, commute, cargo, travel, work_light
- **Features**: backup_camera, blind_spot_monitoring, adaptive_cruise_control, apple_carplay, android_auto, heated_seats, leather_seats, sunroof, third_row_seating
- **Powertrain Types**: gas, hybrid, plug_in_hybrid, electric, diesel, unspecified
- **Drivetrains**: AWD, 4WD, FWD, RWD, unspecified

## Usage for Training

When creating training examples, ensure:

1. **All required fields are present** (even if null/empty)
2. **Enum values match canonical vocabulary** exactly
3. **Structure matches schema** (use validator to check)
4. **Query text is preserved** in `query_text` field

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
    "powertrain_type": "unspecified",
    "fuel_economy_priority": null
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
      "max": null,
      "qualitative": null
    }
  },
  "preference_signals": {
    "reliability_maintenance_priority": "unspecified",
    "safety_priority": "unspecified"
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

