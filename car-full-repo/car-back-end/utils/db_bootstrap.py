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
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Vehicles table - stores vehicle inventory that can be queried
-- This table stores actual vehicle inventory data, so most fields are required
-- Only fields that may legitimately be unknown (like mileage for new vehicles) are nullable
CREATE TABLE IF NOT EXISTS vehicles (
    id TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    body_style TEXT NOT NULL CHECK(body_style IN ('sedan', 'coupe', 'hatchback', 'wagon', 'suv', 'crossover', 'van', 'truck')),
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    mileage INTEGER,  -- Nullable: new vehicles may not have mileage yet
    transmission TEXT NOT NULL CHECK(transmission IN ('automatic', 'manual', 'other', 'unspecified')) DEFAULT 'unspecified',
    drivetrain TEXT NOT NULL CHECK(drivetrain IN ('AWD', '4WD', 'FWD', 'RWD', 'unspecified')) DEFAULT 'unspecified',
    powertrain_type TEXT NOT NULL CHECK(powertrain_type IN ('gas', 'hybrid', 'plug_in_hybrid', 'electric', 'diesel', 'unspecified')) DEFAULT 'unspecified',
    seating_capacity INTEGER NOT NULL,
    city TEXT,  -- Nullable: location may not always be known
    state_region TEXT,  -- Nullable: location may not always be known
    created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Vehicle features junction table (many-to-many)
CREATE TABLE IF NOT EXISTS vehicle_features (
    vehicle_id TEXT NOT NULL,
    feature_tag TEXT NOT NULL CHECK(feature_tag IN (
        'backup_camera', 'blind_spot_monitoring', 'adaptive_cruise_control',
        'apple_carplay', 'android_auto', 'heated_seats', 'leather_seats',
        'sunroof', 'third_row_seating'
    )),
    PRIMARY KEY (vehicle_id, feature_tag),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

-- Query history table - stores processed queries for analytics
CREATE TABLE IF NOT EXISTS query_history (
    id TEXT PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_json TEXT NOT NULL,  -- JSON string of the Vehicle Selection V1 structure
    result_count INTEGER,
    created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS ix_vehicles_body_style ON vehicles(body_style);
CREATE INDEX IF NOT EXISTS ix_vehicles_make_model_year ON vehicles(make, model, year);
CREATE INDEX IF NOT EXISTS ix_vehicles_price ON vehicles(price);
CREATE INDEX IF NOT EXISTS ix_vehicles_year ON vehicles(year);
CREATE INDEX IF NOT EXISTS ix_vehicles_mileage ON vehicles(mileage);
CREATE INDEX IF NOT EXISTS ix_vehicles_drivetrain ON vehicles(drivetrain);
CREATE INDEX IF NOT EXISTS ix_vehicles_powertrain_type ON vehicles(powertrain_type);
CREATE INDEX IF NOT EXISTS ix_vehicles_seating_capacity ON vehicles(seating_capacity);
CREATE INDEX IF NOT EXISTS ix_vehicles_location ON vehicles(city, state_region);
CREATE INDEX IF NOT EXISTS ix_vehicle_features_vehicle_id ON vehicle_features(vehicle_id);
CREATE INDEX IF NOT EXISTS ix_vehicle_features_feature_tag ON vehicle_features(feature_tag);
CREATE INDEX IF NOT EXISTS ix_query_history_created_at ON query_history(created_at_utc);
"""


def ensure_db_and_schema(db_path: Path | str, connection: Optional[sqlite3.Connection] = None) -> None:
    """
    Safe to run on every app start.
    
    Responsibilities:
    - Create SQLite database file if missing
    - Create tables and indexes if missing
    - Perform no data mutation
    
    Args:
        db_path: Path to the database file
        connection: Optional existing database connection. If provided, uses it instead of creating a new one.
    
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
    ensure_db_and_schema(test_db_path)
    print(f"DB initialized at: {test_db_path.resolve()}")

