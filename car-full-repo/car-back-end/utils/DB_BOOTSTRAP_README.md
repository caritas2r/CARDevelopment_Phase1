# Database Bootstrap Implementation

This document describes the database bootstrap implementation based on the PoC pattern, adapted for the Vehicle Selection V1 schema requirements.

## Overview

The `db_bootstrap.py` module follows the minimal, proof-of-concept database bootstrap pattern:
- **Idempotent**: Safe to run on every app start using `CREATE TABLE IF NOT EXISTS`
- **No data mutation**: Only creates schema, never modifies existing data
- **SQLite auto-creation**: SQLite creates the database file automatically when connecting
- **Foreign key support**: Enables foreign key constraints via `PRAGMA foreign_keys = ON`

## Schema Design

The database schema is designed to support querying vehicles based on the Vehicle Selection V1 JSON schema criteria:

### Tables

1. **`vehicles`** - Main vehicle inventory table
   - Stores actual vehicle inventory data (not query criteria)
   - Required fields (NOT NULL): make, model, year, price, currency, mileage
   - Most other fields are nullable to allow for incomplete data
   - Fields align with Vehicle Selection V1 query criteria for matching:
     - Identity: `make`, `model`, `trim` (make/model required, trim optional)
     - Transactional: `year`, `price`, `currency` (INTEGER, ISO 4217 numeric code, default 840 for USD), `mileage`
     - Descriptors: `body_style`, `transmission`, `drivetrain`, `seating_capacity`, `color`, `cargo_space`
     - Features: `has_hatch_access`, `has_fold_flat_seats`, `fuel_economy`, `reliability`
     - Location: `city`, `state_region`, `zip_code`
     - Ownership: `number_of_owners`
     - **Note**: `powertrain_type` is NOT in this table - use `vehicle_powertrain_types` junction table
   - **Note on currency/price**: Currency is stored as INTEGER (ISO 4217 numeric codes like 840 for USD), while price is stored as INTEGER (whole dollars). This allows for proper currency handling and potential future currency conversion features.

2. **`vehicle_features`** - Junction table for vehicle features
   - Many-to-many relationship between vehicles and features
   - Supports `features_amenities` queries (must_have, nice_to_have, avoid)
   - Feature tags match schema enum:
     - backup_camera, blind_spot_monitoring, adaptive_cruise_control
     - apple_carplay, android_auto, heated_seats, leather_seats
     - sunroof, third_row_seating
   - Primary key: (vehicle_id, feature_tag)
   - Foreign key: vehicle_id → vehicles(vehicle_id) ON DELETE CASCADE

3. **`vehicle_use_case_tags`** - Junction table for use case tags
   - Many-to-many relationship between vehicles and use case tags
   - Supports `intended_use.use_case_tags` queries
   - Use case tags match schema enum:
     - family, animals, commute, cargo, travel, work_light, pleasure, performance
   - Primary key: (vehicle_id, use_case_tag)
   - Foreign key: vehicle_id → vehicles(vehicle_id) ON DELETE CASCADE

4. **`vehicle_powertrain_types`** - Junction table for powertrain types
   - Many-to-many relationship between vehicles and powertrain types
   - Supports `powertrain_drivability.powertrain_type[]` queries (array field)
   - Powertrain types match schema enum:
     - gas, hybrid, plug_in_hybrid, electric, diesel
   - **Note**: Vehicles can have multiple powertrain types (e.g., a plug-in hybrid has both "hybrid" and "plug_in_hybrid")
   - Primary key: (vehicle_id, powertrain_type)
   - Foreign key: vehicle_id → vehicles(vehicle_id) ON DELETE CASCADE

5. **`search_requests`** - Query analytics table
   - Stores processed NLP queries and their Vehicle Selection V1 JSON representations
   - Useful for analytics and improving query processing
   - Fields: request_id (AUTOINCREMENT), created_at, query_text, selection_json_raw, selection_json_normalized

### Indexes

Indexes are created for common query patterns:
- Body style, make/model/year combinations
- Price, year, mileage (for constraint queries)
- Drivetrain (for drivetrain queries)
- Seating capacity (for capacity queries)
- Location (city, state_region)
- Feature lookups (vehicle_id, feature_tag)
- Use case tag lookups (vehicle_id, use_case_tag)
- Powertrain type lookups (vehicle_id, powertrain_type)

## Integration

The bootstrap is integrated into the `DatabaseConnectionService`:

1. **During database creation** (`create_database()`):
   - Calls `ensure_db_and_schema()` to create the schema
   - Even if database exists, verifies schema is up to date

2. **During service initialization** (`initialize()`):
   - After database setup, ensures schema is current
   - Uses existing connection to avoid unnecessary reconnections

## Usage

### Standalone Testing

```bash
python utils/db_bootstrap.py
```

This will create/update the database schema at `data/car_database.db`.

### Programmatic Usage

```python
from utils.db_bootstrap import ensure_db_and_schema
from pathlib import Path

# With new connection (creates file if needed)
ensure_db_and_schema(Path("data/car_database.db"))

# With existing connection
import sqlite3
conn = sqlite3.connect("data/car_database.db")
ensure_db_and_schema(Path("data/car_database.db"), connection=conn)
```

## Verification

Use the inspection utility to verify the schema:

```bash
python utils/inspect_database.py
```

This will show:
- Database path and existence
- All tables and their columns
- Row counts for each table
- Database file size

## Differences from PoC

The implementation extends the PoC pattern with:

1. **Multiple tables**: Five tables (vehicles, vehicle_features, vehicle_use_case_tags, vehicle_powertrain_types, search_requests)
2. **Junction tables**: Many-to-many relationships for features, use case tags, and powertrain types
3. **Comprehensive indexes**: Multiple indexes for query performance
4. **CHECK constraints**: Enforces enum values from Vehicle Selection V1 schema
5. **Foreign keys**: CASCADE delete for all junction tables
6. **Connection reuse**: Optional connection parameter to avoid unnecessary connections
7. **Powertrain types as array**: Powertrain types are stored in a junction table to support multiple types per vehicle

## Future Enhancements

- **Data seeding**: The `seed_data()` function is stubbed for future use
- **Migrations**: For production, consider a migration framework (Alembic, etc.)
- **Additional tables**: May need tables for dealers, inventory sources, etc.

## Notes

- The schema uses `TEXT` for IDs (flexible for UUIDs or other formats)
- Timestamps use ISO 8601 format with UTC timezone
- All enum values match the Vehicle Selection V1 schema exactly (excluding "unspecified" which becomes NULL in DB)
- The schema is designed to be queryable by the `DatabaseQueryService` based on Vehicle Selection V1 criteria
- **Nullable fields**: Most fields are nullable except required transactional fields (make, model, year, price, currency, mileage)
- **NOT NULL fields**: Only core transactional fields are required: make, model, year, price, currency, mileage
- **Currency design**: Currency is stored as INTEGER (ISO 4217 numeric codes like 840 for USD) while price is INTEGER (whole dollars). This separation allows for:
  - Proper currency identification
  - Future currency conversion capabilities
  - Handling cases where price exists but currency is unspecified (defaults to 840 for USD)
- **Powertrain types**: Stored in `vehicle_powertrain_types` junction table to support multiple types per vehicle (e.g., plug-in hybrid = hybrid + plug_in_hybrid)
- **"unspecified" → NULL**: JSON schema uses "unspecified" as sentinel value, but database stores NULL for unknown values

