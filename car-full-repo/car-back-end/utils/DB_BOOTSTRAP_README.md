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
   - Most fields are **NOT NULL** because vehicles in inventory should have complete information
   - Fields align with Vehicle Selection V1 query criteria for matching:
     - `body_style`: Matches schema enum (sedan, coupe, hatchback, wagon, suv, crossover, van, truck) - **NOT NULL**
     - `transmission`: Matches schema enum (automatic, manual, other, unspecified) - **NOT NULL** (defaults to 'unspecified')
     - `drivetrain`: Matches schema enum (AWD, 4WD, FWD, RWD, unspecified) - **NOT NULL** (defaults to 'unspecified')
     - `powertrain_type`: Matches schema enum (gas, hybrid, plug_in_hybrid, electric, diesel, unspecified) - **NOT NULL** (defaults to 'unspecified')
     - `seating_capacity`: Supports `capacity_practicality.min_seating_capacity` queries - **NOT NULL**
     - `price` (REAL): Numeric price value - **NOT NULL** (required for inventory)
     - `currency` (TEXT): Currency code (e.g., "USD", "EUR", "GBP") - **NOT NULL** (defaults to 'USD')
     - `year`: Supports `ownership_constraints.year` queries - **NOT NULL** (core identifier)
     - `mileage`: Supports `ownership_constraints.mileage` queries - **nullable** (new vehicles may not have mileage)
     - `city`, `state_region`: Supports `location_constraints` queries - **nullable** (location may not always be known)
   - **Note on currency/price**: Currency is stored as a TEXT string (ISO currency codes like "USD"), while price is stored as a REAL number. This allows for proper currency handling and potential future currency conversion features.

2. **`vehicle_features`** - Junction table for vehicle features
   - Many-to-many relationship between vehicles and features
   - Supports `features_amenities` queries (must_have, nice_to_have, avoid)
   - Feature tags match schema enum:
     - backup_camera, blind_spot_monitoring, adaptive_cruise_control
     - apple_carplay, android_auto, heated_seats, leather_seats
     - sunroof, third_row_seating

3. **`query_history`** - Query analytics table
   - Stores processed NLP queries and their Vehicle Selection V1 JSON representations
   - Useful for analytics and improving query processing

### Indexes

Indexes are created for common query patterns:
- Body style, make/model/year combinations
- Price, year, mileage (for constraint queries)
- Drivetrain, powertrain type (for powertrain queries)
- Seating capacity (for capacity queries)
- Location (city, state_region)
- Feature lookups (vehicle_id, feature_tag)

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

1. **Multiple tables**: Three tables instead of one (vehicles, vehicle_features, query_history)
2. **Junction table**: Many-to-many relationship for features
3. **Comprehensive indexes**: Multiple indexes for query performance
4. **CHECK constraints**: Enforces enum values from Vehicle Selection V1 schema
5. **Foreign keys**: CASCADE delete for vehicle_features
6. **Connection reuse**: Optional connection parameter to avoid unnecessary connections

## Future Enhancements

- **Data seeding**: The `seed_data()` function is stubbed for future use
- **Migrations**: For production, consider a migration framework (Alembic, etc.)
- **Additional tables**: May need tables for dealers, inventory sources, etc.

## Notes

- The schema uses `TEXT` for IDs (flexible for UUIDs or other formats)
- Timestamps use ISO 8601 format with UTC timezone
- All enum values match the Vehicle Selection V1 schema exactly
- The schema is designed to be queryable by the `DatabaseQueryService` based on Vehicle Selection V1 criteria
- **Nullable fields**: Only fields that may legitimately be unknown are nullable:
  - `mileage`: New vehicles may not have mileage yet
  - `city`, `state_region`: Location may not always be known or relevant
- **NOT NULL fields**: Vehicle inventory should have complete information (make, model, year, body_style, price, currency, transmission, drivetrain, powertrain_type, seating_capacity)
- **Currency design**: Currency is stored as TEXT (ISO codes like "USD", "EUR") while price is REAL. This separation allows for:
  - Proper currency identification
  - Future currency conversion capabilities
  - Handling cases where price exists but currency is unspecified (defaults can be handled in application logic)

