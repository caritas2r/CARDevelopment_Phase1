# JSON Schema to Database Field Mapping

This document maps fields from the Vehicle Selection V1 JSON schema to the corresponding database fields in the `vehicles` inventory table and related junction tables.

## Value Conversion Rules

- **"unspecified" → NULL**: All JSON schema fields that contain the string `"unspecified"` should be converted to `NULL` when storing in the database. The database does not use sentinel values; unknown/missing data is represented as `NULL`.
- **Enum values**: JSON enum values map directly to database enum values (excluding "unspecified" which becomes NULL).

## Field Mappings

### Identity Fields

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| N/A | `vehicles` | `vehicle_id` | Primary key, generated/assigned separately |
| N/A | `vehicles` | `make` | Required (NOT NULL) |
| N/A | `vehicles` | `model` | Required (NOT NULL) |
| N/A | `vehicles` | `trim` | Optional |

### Vehicle Type

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `vehicle_type.include_body_styles[]` | `vehicles` | `body_style` | Array → single value. If multiple body styles in array, store first or most relevant. "unspecified" → NULL |
| `vehicle_type.exclude_body_styles[]` | N/A | N/A | Used for query filtering, not stored in inventory |

### Capacity & Practicality

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `capacity_practicality.min_seating_capacity` | `vehicles` | `seating_capacity` | Integer or "unspecified". "unspecified" → NULL. Used in queries as `seating_capacity >= min_seating_capacity` |
| `capacity_practicality.kid_count` | N/A | N/A | Used for query logic, not stored in inventory |
| `capacity_practicality.pet_count` | N/A | N/A | Used for query logic, not stored in inventory |
| `capacity_practicality.cargo_priority` | `vehicles` | `cargo_space` | Maps priority level to space level: "low" → "low", "medium" → "medium", "high" → "high", "unspecified" → NULL |
| `capacity_practicality.cargo_flexibility.wants_hatch_access` | `vehicles` | `has_hatch_access` | Boolean enum: "true" → 1, "false" → 0, "unspecified" → NULL |
| `capacity_practicality.cargo_flexibility.wants_fold_flat_seats` | `vehicles` | `has_fold_flat_seats` | Boolean enum: "true" → 1, "false" → 0, "unspecified" → NULL |

### Intended Use

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `intended_use.use_case_tags[]` | `vehicle_use_case_tags` | `use_case_tag` | Many-to-many relationship. Array of tags → multiple rows. "unspecified" → skip (don't create row) |

### Powertrain & Drivability

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `powertrain_drivability.transmission` | `vehicles` | `transmission` | Direct match. "unspecified" → NULL |
| `powertrain_drivability.drivetrain` | `vehicles` | `drivetrain` | Direct match. "unspecified" → NULL |
| `powertrain_drivability.powertrain_type[]` | `vehicle_powertrain_types` (junction table) | `powertrain_type` | Array → many-to-many relationship. Array of types → multiple rows. "unspecified" → skip (don't create row). **Note: Junction table needs to be created in database schema.** |
| `powertrain_drivability.fuel_economy_priority` | `vehicles` | `fuel_economy` | Maps priority level to economy level: "low" → "low", "medium" → "medium", "high" → "high", "unspecified" → NULL |

### Features & Amenities

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `features_amenities.must_have[]` | `vehicle_features` | `feature_tag` | Many-to-many relationship. Array of tags → multiple rows. "unspecified" → skip |
| `features_amenities.nice_to_have[]` | `vehicle_features` | `feature_tag` | Many-to-many relationship. Array of tags → multiple rows. "unspecified" → skip |
| `features_amenities.avoid[]` | N/A | N/A | Used for query filtering (exclusion), not stored in inventory |

### Preference Signals

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `preference_signals.reliability_maintenance_priority` | `vehicles` | `reliability` | Maps priority to reliability level: "low_cost" → "low", "balanced" → "medium", "performance_first" → "high", "unspecified" → NULL |
| `preference_signals.color` | `vehicles` | `color` | Direct match. "unspecified" → NULL |

### Ownership Constraints

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `ownership_constraints.budget.currency` | `vehicles` | `currency` | Integer (ISO 4217 code). "unspecified" → NULL. Default: 840 (USD) |
| `ownership_constraints.budget.min` | `vehicles` | `price` | Used in queries as `price >= budget.min`. "unspecified" → not applied |
| `ownership_constraints.budget.max` | `vehicles` | `price` | Used in queries as `price <= budget.max` (or `price < budget.max` if `strict_max` is true). "unspecified" → not applied |
| `ownership_constraints.budget.strict_max` | N/A | N/A | Used for query logic (affects comparison operator), not stored in inventory |
| `ownership_constraints.year.min` | `vehicles` | `year` | Used in queries as `year >= year.min`. "unspecified" → not applied |
| `ownership_constraints.year.max` | `vehicles` | `year` | Used in queries as `year <= year.max`. "unspecified" → not applied |
| `ownership_constraints.mileage.max` | `vehicles` | `mileage` | Used in queries as `mileage <= mileage.max`. "unspecified" → not applied |
| `ownership_constraints.mileage.qualitative` | N/A | N/A | Used for query logic (qualitative mileage filtering). "unspecified" → not applied |
| `ownership_constraints.number_of_owners` | `vehicles` | `number_of_owners` | Direct match. Integer (0 or higher) or "unspecified". "unspecified" → NULL |

### Location Constraints

| JSON Schema Path | Database Table | Database Field | Notes |
|-----------------|----------------|----------------|-------|
| `location_constraints.city` | `vehicles` | `city` | Direct match. "unspecified" → NULL |
| `location_constraints.state_region` | `vehicles` | `state_region` | Direct match. "unspecified" → NULL |
| `location_constraints.radius_miles` | N/A | N/A | Used for query logic (distance calculation), not stored in inventory |
| N/A | `vehicles` | `zip_code` | Additional location field in database (not in JSON schema) |

## Query-Only Fields

The following JSON schema fields are used for querying/filtering but are not stored in the inventory database:

- `vehicle_type.exclude_body_styles[]` - Used to exclude body styles in queries
- `capacity_practicality.kid_count` - Used for query logic
- `capacity_practicality.pet_count` - Used for query logic
- `ownership_constraints.budget.strict_max` - Affects query comparison operator
- `ownership_constraints.year.min` / `year.max` - Used in WHERE clause comparisons
- `ownership_constraints.mileage.max` - Used in WHERE clause comparisons
- `ownership_constraints.mileage.qualitative` - Used for qualitative mileage filtering (low, moderate, high, very_low, very_high, does_not_matter)
- `location_constraints.radius_miles` - Used for distance-based filtering
- `features_amenities.avoid[]` - Used to exclude features in queries

## Required Fields in Database

The following fields are required (NOT NULL) in the `vehicles` table for transactional listings:

- `make`
- `model`
- `year`
- `price`
- `currency` (defaults to 840 if not specified)
- `mileage`

All other fields are nullable to allow for incomplete data.

## Junction Tables

### `vehicle_features`
- Maps many-to-many relationship between vehicles and feature tags
- Primary key: (`vehicle_id`, `feature_tag`)
- Foreign key: `vehicle_id` → `vehicles(vehicle_id)`

### `vehicle_use_case_tags`
- Maps many-to-many relationship between vehicles and use case tags
- Primary key: (`vehicle_id`, `use_case_tag`)
- Foreign key: `vehicle_id` → `vehicles(vehicle_id)`

### `vehicle_powertrain_types` (to be created)
- Maps many-to-many relationship between vehicles and powertrain types
- Primary key: (`vehicle_id`, `powertrain_type`)
- Foreign key: `vehicle_id` → `vehicles(vehicle_id)`
- **Note: This junction table needs to be added to the database schema to support multiple powertrain types per vehicle.**

## Notes

1. **Array to Single Value**: Some JSON schema fields are arrays (e.g., `include_body_styles[]`), but the database stores a single value. The conversion logic should select the most appropriate value (e.g., first item, most specific, etc.).

2. **Priority to Descriptive Mapping**: Some JSON schema fields use priority levels ("low", "medium", "high") while the database uses descriptive levels (e.g., "low", "medium", "high", "unknown"). The mapping is direct for these cases.

3. **Boolean Enums**: JSON schema uses string enums for booleans ("true", "false", "unspecified"), while the database uses BOOLEAN type (1, 0, NULL).

4. **Currency**: JSON schema allows integer or "unspecified" for currency. The database stores ISO 4217 numeric codes (e.g., 840 for USD). "unspecified" becomes NULL, but for PoC, currency defaults to 840 (USD).

5. **Query vs. Storage**: Many JSON schema fields are used for querying/filtering but are not stored in the inventory. The inventory represents actual vehicle properties, while the JSON schema represents user query criteria.

