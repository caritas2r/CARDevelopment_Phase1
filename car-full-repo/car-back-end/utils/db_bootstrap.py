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
        'panoramic_roof','panoramic_sunroof','memory_seats','keyless_entry',
        'bluetooth','rear_entertainment_system','sliding_doors'
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

-- Flagged prompts table - stores rejected/flagged queries for review
CREATE TABLE IF NOT EXISTS flagged_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_text TEXT NOT NULL,
    flagged_annotation TEXT,
    flagged_query TEXT,
    flag_reason TEXT,
    query_status TEXT
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


# Expected schema definition - single source of truth for all tables and columns
# Format: {table_name: {column_name: (type, nullable)}}
EXPECTED_SCHEMA = {
    'vehicles': {
        'vehicle_id': ('TEXT', False),
        'make': ('TEXT', False),
        'model': ('TEXT', False),
        'trim': ('TEXT', True),
        'year': ('INTEGER', False),
        'price': ('INTEGER', False),
        'currency': ('INTEGER', False),
        'mileage': ('INTEGER', False),
        'body_style': ('TEXT', True),
        'transmission': ('TEXT', True),
        'drivetrain': ('TEXT', True),
        'seating_capacity': ('INTEGER', True),
        'color': ('TEXT', True),
        'cargo_space': ('TEXT', True),
        'has_hatch_access': ('BOOLEAN', True),
        'has_fold_flat_seats': ('BOOLEAN', True),
        'fuel_economy': ('TEXT', True),
        'reliability': ('TEXT', True),
        'city': ('TEXT', True),
        'state_region': ('TEXT', True),
        'zip_code': ('TEXT', True),
        'number_of_owners': ('INTEGER', True)
    },
    'vehicle_features': {
        'vehicle_id': ('TEXT', False),
        'feature_tag': ('TEXT', False)
    },
    'vehicle_use_case_tags': {
        'vehicle_id': ('TEXT', False),
        'use_case_tag': ('TEXT', False)
    },
    'vehicle_powertrain_types': {
        'vehicle_id': ('TEXT', False),
        'powertrain_type': ('TEXT', False)
    },
    'search_requests': {
        'request_id': ('INTEGER', False),
        'created_at': ('TEXT', False),
        'query_text': ('TEXT', True),
        'selection_json_raw': ('TEXT', False),
        'selection_json_normalized': ('TEXT', False)
    },
    'flagged_prompts': {
        'id': ('INTEGER', False),
        'prompt_text': ('TEXT', False),
        'flagged_annotation': ('TEXT', True),
        'flagged_query': ('TEXT', True),
        'flag_reason': ('TEXT', True),
        'query_status': ('TEXT', True)  # 'pass', 'fail', or 'insufficient'
    }
}

# Tables that can be dropped and recreated if schema changes (data loss acceptable)
RECREATE_TABLES = {'flagged_prompts'}

# SQL definitions for recreatable tables (used when schema doesn't match)
RECREATABLE_TABLE_DEFINITIONS = {
    'flagged_prompts': """
        CREATE TABLE flagged_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_text TEXT NOT NULL,
            flagged_annotation TEXT,
            flagged_query TEXT,
            flag_reason TEXT,
            query_status TEXT
        )
    """
}


def _get_table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    """Get the set of column names for a table"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
        return {col[1] for col in columns if col[1]}
    except sqlite3.Error:
        return set()


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def _add_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_type: str, nullable: bool = True) -> None:
    """Add a column to a table if it doesn't exist"""
    cursor = conn.cursor()
    try:
        # SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
        # So we check if column exists first
        existing_columns = _get_table_columns(conn, table_name)
        if column_name not in existing_columns:
            not_null_clause = " NOT NULL" if not nullable else ""
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{not_null_clause}")
            conn.commit()
            print(f"[db_bootstrap] Added column {column_name} to table {table_name}")
    except sqlite3.Error as e:
        # Column might already exist, or other error
        print(f"[db_bootstrap] Warning: Could not add column {column_name} to {table_name}: {e}")


def _recreate_table(conn: sqlite3.Connection, table_name: str) -> None:
    """Drop and recreate a table with the expected schema"""
    if table_name not in RECREATABLE_TABLE_DEFINITIONS:
        print(f"[db_bootstrap] ERROR: No definition found for recreatable table {table_name}")
        return
    
    cursor = conn.cursor()
    
    # Drop existing table
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    print(f"[db_bootstrap] Dropped table {table_name}")
    
    # Recreate with correct schema
    create_sql = RECREATABLE_TABLE_DEFINITIONS[table_name]
    cursor.execute(create_sql)
    conn.commit()
    print(f"[db_bootstrap] Recreated table {table_name} with correct schema")


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Comprehensive schema validation and migration system - ensures all tables and columns match expected schema.
    - Checks all tables exist
    - Checks all columns exist in each table
    - Adds missing columns (for tables with data we care about)
    - Drops and recreates tables in RECREATE_TABLES if schema doesn't match
    """
    cursor = conn.cursor()
    
    print(f"[db_bootstrap] Validating database schema...")
    
    # Check each expected table
    for table_name, expected_schema in EXPECTED_SCHEMA.items():
        table_exists = _table_exists(conn, table_name)
        
        if not table_exists:
            print(f"[db_bootstrap] Table {table_name} does not exist - will be created by schema script")
            continue
        
        # Get existing columns
        existing_columns = _get_table_columns(conn, table_name)
        expected_columns_set = set(expected_schema.keys())
        
        # Check if schema matches
        if existing_columns == expected_columns_set:
            print(f"[db_bootstrap] Table {table_name} schema is correct")
            continue
        
        # Schema doesn't match
        missing_columns = expected_columns_set - existing_columns
        extra_columns = existing_columns - expected_columns_set
        
        if missing_columns:
            print(f"[db_bootstrap] Table {table_name} missing columns: {missing_columns}")
        if extra_columns:
            print(f"[db_bootstrap] Table {table_name} has extra columns: {extra_columns}")
        
        # For tables that can be recreated (data loss acceptable)
        if table_name in RECREATE_TABLES:
            print(f"[db_bootstrap] Recreating table {table_name} to match expected schema...")
            _recreate_table(conn, table_name)
        else:
            # For other tables, add missing columns
            # Note: We can't easily remove extra columns in SQLite without recreating the table
            # This is a limitation we accept for the lightweight migration system
            if missing_columns:
                print(f"[db_bootstrap] Adding missing columns to table {table_name}...")
                # Add each missing column with correct type and nullability
                for col_name in missing_columns:
                    col_type, nullable = expected_schema[col_name]
                    _add_column(conn, table_name, col_name, col_type, nullable)
    
    print(f"[db_bootstrap] Schema validation complete")


def ensure_db_and_schema(db_path: Path | str, connection: Optional[sqlite3.Connection] = None, drop_existing: bool = False) -> None:
    """
    Safe to run on every app start.
    
    Responsibilities:
    - Create SQLite database file if missing
    - Create tables and indexes if missing
    - Ensure schema is up to date (migrate if needed)
    - Lightweight EF Core-like migration system
    
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
            DROP TABLE IF EXISTS flagged_prompts;
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
        
        # Run migrations to ensure schema is up to date
        _migrate_schema(conn)
        
        print(f"[db_bootstrap] Database schema ensured and migrated at {db_path.resolve()}")
    except sqlite3.Error as e:
        print(f"[db_bootstrap] ERROR: Failed to create/migrate schema: {e}")
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

