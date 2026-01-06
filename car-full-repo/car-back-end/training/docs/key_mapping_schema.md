# Key Mapping Schema

This document defines the shortened key names used in the training data to reduce token usage while maintaining readability and avoiding ambiguity.

## Top-Level Keys

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `make` | `mk` | Vehicle manufacturer |
| `model` | `md` | Vehicle model |
| `trim` | `tr` | Vehicle trim level |
| `vehicle_type` | `vt` | Vehicle body type and style preferences |
| `capacity_practicality` | `cp` | Seating, cargo, and practicality requirements |
| `intended_use` | `iu` | Primary use cases for the vehicle |
| `powertrain_drivability` | `pd` | Engine, transmission, and drivetrain preferences |
| `features_amenities` | `fa` | Desired and avoided features |
| `ownership_constraints` | `oc` | Budget, year, mileage, and ownership constraints |
| `preference_signals` | `ps` | Reliability, maintenance, and color preferences |
| `location_constraints` | `lc` | Geographic search constraints |

## Nested Keys

### vehicle_type (vt)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `include_body_styles` | `inc` | Body styles to include in search |
| `exclude_body_styles` | `exc` | Body styles to exclude from search |

### capacity_practicality (cp)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `min_seating_capacity` | `seat_min` | Minimum number of seats required |
| `kid_count` | `kids` | Number of children |
| `pet_count` | `pets` | Number of pets |
| `cargo_priority` | `cargo_pri` | Priority level for cargo space |
| `cargo_flexibility` | `cargo_fx` | Cargo flexibility requirements |

### cargo_flexibility (cargo_fx)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `wants_hatch_access` | `hatch` | Preference for hatchback access |
| `wants_fold_flat_seats` | `foldflat` | Preference for fold-flat seats |

### intended_use (iu)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `use_case_tags` | `tags` | List of use case tags (e.g., commute, family, travel) |

### powertrain_drivability (pd)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `transmission` | `tx` | Transmission type preference |
| `drivetrain` | `dt` | Drivetrain preference (FWD, RWD, AWD, 4WD) |
| `powertrain_type` | `pt` | Powertrain type (gas, electric, hybrid, etc.) |
| `fuel_economy_priority` | `fe_pri` | Priority level for fuel economy |

### features_amenities (fa)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `must_have` | `must` | Required features |
| `nice_to_have` | `nice` | Desired but not required features |
| `avoid` | `avoid` | Features to avoid (unchanged) |

### ownership_constraints (oc)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `budget` | `bud` | Budget constraints |

#### budget (bud)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `currency` | `cur` | Currency code (ISO 4217 numeric) |
| `min` | `min` | Minimum budget (unchanged) |
| `max` | `max` | Maximum budget (unchanged) |
| `strict_max` | `max_strict` | Whether maximum budget is strict |

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `year` | `yr` | Year constraints |
| `mileage` | `mi` | Mileage constraints |
| `number_of_owners` | `owners` | Maximum number of previous owners |

#### year (yr)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `min` | `min` | Minimum year (unchanged) |
| `max` | `max` | Maximum year (unchanged) |

#### mileage (mi)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `max` | `max` | Maximum mileage (unchanged) |
| `qualitative` | `qual` | Qualitative mileage descriptors |

### preference_signals (ps)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `reliability_maintenance_priority` | `rel_pri` | Priority for reliability and maintenance |
| `color` | `clr` | Preferred exterior colors |

### location_constraints (lc)

| Original Key | Shortened Key | Description |
|-------------|---------------|-------------|
| `city` | `cty` | City name |
| `state_region` | `st` | State or region code |
| `radius_miles` | `rad` | Search radius in miles |

## Usage

This key mapping is applied to all JSON payloads in the `label: true` segments of the training data files:
- `train_template_free_updated.jsonl`
- `validation_template_free_updated.jsonl`
- `test_template_free_updated.jsonl`

The mapping reduces token usage significantly while maintaining code readability and avoiding ambiguous abbreviations.

