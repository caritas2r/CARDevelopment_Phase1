# Utilities

This directory contains utility scripts and modules for database management and schema validation.

## Files

- `db_bootstrap.py` - Database schema bootstrap system that creates and validates database schema on startup
- `database_setup_script.py` - Database setup script for initial database creation
- `schema_validator.py` - Validates JSON output against Vehicle Selection V1 schema

## Database Bootstrap

The `db_bootstrap.py` module implements a lightweight schema migration system:
- Validates database schema on every application startup
- Automatically adds missing columns to existing tables
- Drops and recreates tables that allow recreation (e.g., `flagged_prompts`) if schema doesn't match
- Ensures database schema always matches the expected structure

See `DB_BOOTSTRAP_README.md` for detailed documentation.

## Schema Validator

The `schema_validator.py` module provides validation for Vehicle Selection V1 schema:
- Validates JSON output from inference against the schema
- Used by `json_input_converter_service.py` to ensure valid input
- Supports Draft-07 JSON Schema validation

