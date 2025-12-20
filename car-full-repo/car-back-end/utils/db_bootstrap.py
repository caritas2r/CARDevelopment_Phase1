"""
Database Bootstrap - Creates database schema following PoC pattern
Based on Vehicle Selection V1 schema requirements
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

# Schema SQL for vehicle inventory table
# This table structure supports querying based on Vehicle Selection V1 criteria
# Key decisions:
#   - Inventory DB stores NO 'unspecified' sentinel values; unknown = NULL
#   - Transactional listings: year, mileage, price, currency are required
#   - USD-only PoC: currency is stored as INTEGER (ISO 4217 numeric code), default 840
#   - price is stored as INTEGER for straightforward numeric comparisons (<=, >=)
#   - Booleans: SQLite stores booleans as integers under the hood; we use BOOLEAN with CHECKs
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Vehicles table - stores vehicle inventory that can be queried
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,

    -- Identity
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    trim TEXT,

    -- Transactional listing essentials (required)
    year INTEGER NOT NULL,
    price INTEGER NOT NULL,      -- store whole dollars for PoC comparisons
    currency INTEGER NOT NULL DEFAULT 840,  -- USD (ISO 4217 numeric); PoC assumes USD
    mileage INTEGER NOT NULL,

    -- Core vehicle descriptors (nullable if unknown)
    body_style TEXT CHECK(body_style IN ('sedan','coupe','hatchback','wagon','suv','crossover','van','truck','convertible','minivan')),
    transmission TEXT CHECK(transmission IN ('automatic','manual','other','cvt','dual_clutch')),
    drivetrain TEXT CHECK(drivetrain IN ('AWD','4WD','FWD','RWD')),

    seating_capacity INTEGER,

    color TEXT CHECK(color IN (
        'black','white','silver','gray','grey','red','blue','green','brown',
        'beige','tan','gold','orange','yellow','purple','burgundy','maroon',
        'navy','teal','pink'
    )),

    -- New descriptors to support schema + inference (nullable if unknown)
    -- cargo_space recommended values: none|low|medium|high|unknown
    cargo_space TEXT CHECK(cargo_space IN ('none','low','medium','high','unknown')),

    -- Booleans: store as 1/0/NULL, declared BOOLEAN for readability + enforced by CHECK
    has_hatch_access BOOLEAN CHECK(has_hatch_access IN (0,1) OR has_hatch_access IS NULL),
    has_fold_flat_seats BOOLEAN CHECK(has_fold_flat_seats IN (0,1) OR has_fold_flat_seats IS NULL),

    -- recommended values: low|medium|high|unknown
    fuel_economy TEXT CHECK(fuel_economy IN ('low','medium','high','unknown')),
    reliability TEXT CHECK(reliability IN ('low','medium','high','unknown')),

    -- Location (zip_code as TEXT to preserve leading zeros)
    city TEXT,
    state_region TEXT,
    zip_code TEXT,

    -- Ownership history
    number_of_owners INTEGER
);

-- Vehicle features junction table (many-to-many)
CREATE TABLE IF NOT EXISTS vehicle_features (
    vehicle_id TEXT NOT NULL,
    feature_tag TEXT NOT NULL CHECK(feature_tag IN (
        'backup_camera','blind_spot_monitoring','adaptive_cruise_control',
        'apple_carplay','android_auto','heated_seats','leather_seats',
        'sunroof','third_row_seating','lane_keep_assist','lane_departure_warning',
        'front_parking_sensors','rear_parking_sensors','remote_start',
        'heated_steering_wheel','ventilated_seats','wireless_charging',
        'premium_audio','built_in_navigation','roof_rack','tow_package',
        'panoramic_roof','memory_seats','keyless_entry'
    )),
    PRIMARY KEY (vehicle_id, feature_tag),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Vehicle use case tags junction table (many-to-many)
CREATE TABLE IF NOT EXISTS vehicle_use_case_tags (
    vehicle_id TEXT NOT NULL,
    use_case_tag TEXT NOT NULL CHECK(use_case_tag IN (
        'family','animals','commute','cargo','travel','work_light',
        'pleasure','performance','rideshare','towing','off_road','luxury','budget_value'
    )),
    PRIMARY KEY (vehicle_id, use_case_tag),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Vehicle powertrain types junction table (many-to-many)
CREATE TABLE IF NOT EXISTS vehicle_powertrain_types (
    vehicle_id TEXT NOT NULL,
    powertrain_type TEXT NOT NULL CHECK(powertrain_type IN (
        'gas','hybrid','plug_in_hybrid','electric','diesel','mild_hybrid'
    )),
    PRIMARY KEY (vehicle_id, powertrain_type),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Search requests table - stores processed queries for analytics
CREATE TABLE IF NOT EXISTS search_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    query_text TEXT,
    selection_json_raw TEXT NOT NULL,
    selection_json_normalized TEXT NOT NULL
);

-- Indexes for common filters
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_year ON vehicles(make, model, year);
CREATE INDEX IF NOT EXISTS idx_vehicles_year ON vehicles(year);
CREATE INDEX IF NOT EXISTS idx_vehicles_price ON vehicles(price);
CREATE INDEX IF NOT EXISTS idx_vehicles_mileage ON vehicles(mileage);
CREATE INDEX IF NOT EXISTS idx_vehicles_body_style ON vehicles(body_style);
CREATE INDEX IF NOT EXISTS idx_vehicles_transmission ON vehicles(transmission);
CREATE INDEX IF NOT EXISTS idx_vehicles_drivetrain ON vehicles(drivetrain);
CREATE INDEX IF NOT EXISTS idx_vehicles_seating_capacity ON vehicles(seating_capacity);
CREATE INDEX IF NOT EXISTS idx_vehicles_color ON vehicles(color);
CREATE INDEX IF NOT EXISTS idx_vehicles_cargo_space ON vehicles(cargo_space);
CREATE INDEX IF NOT EXISTS idx_vehicles_fuel_economy ON vehicles(fuel_economy);
CREATE INDEX IF NOT EXISTS idx_vehicles_reliability ON vehicles(reliability);
CREATE INDEX IF NOT EXISTS idx_vehicles_location ON vehicles(state_region, city, zip_code);
CREATE INDEX IF NOT EXISTS idx_vehicle_features_tag ON vehicle_features(feature_tag, vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_use_case_tags_tag ON vehicle_use_case_tags(use_case_tag, vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_powertrain_types_tag ON vehicle_powertrain_types(powertrain_type, vehicle_id);
"""


def ensure_db_and_schema(db_path: Path | str, connection: Optional[sqlite3.Connection] = None, drop_existing: bool = False) -> None:
    """
    Safe to run on every app start.
    
    Responsibilities:
    - Create SQLite database file if missing
    - Create tables and indexes if missing
    - Perform no data mutation
    
    Args:
        db_path: Path to the database file
        connection: Optional existing database connection. If provided, uses it instead of creating a new one.
        drop_existing: If True, drop existing tables before recreating (useful for schema updates)
    
    Returns:
        None
    """
    if isinstance(db_path, str):
        db_path = Path(db_path)
    
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use provided connection or create a new one
    if connection is not None:
        conn = connection
        should_close = False
    else:
        conn = sqlite3.connect(db_path)
        should_close = True
    
    try:
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Drop existing tables if requested
        if drop_existing:
            drop_sql = """
            DROP TABLE IF EXISTS search_requests;
            DROP TABLE IF EXISTS vehicle_powertrain_types;
            DROP TABLE IF EXISTS vehicle_use_case_tags;
            DROP TABLE IF EXISTS vehicle_features;
            DROP TABLE IF EXISTS vehicles;
            """
            conn.executescript(drop_sql)
            conn.commit()
            print(f"[db_bootstrap] Dropped existing tables")
        
        # Execute schema creation (idempotent with IF NOT EXISTS)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        
        print(f"[db_bootstrap] Database schema ensured at {db_path.resolve()}")
    except sqlite3.Error as e:
        print(f"[db_bootstrap] ERROR: Failed to create schema: {e}")
        raise
    finally:
        if should_close:
            conn.close()


def seed_data(connection: sqlite3.Connection) -> None:
    """
    Placeholder for future data seeding.
    Intentionally a no-op for PoC.
    
    Args:
        connection: Database connection
    """
    pass


if __name__ == "__main__":
    # Test the bootstrap
    test_db_path = Path("data/car_database.db")
    ensure_db_and_schema(test_db_path, drop_existing=True)
    print(f"DB initialized at: {test_db_path.resolve()}")

