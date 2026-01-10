# Data Directory

This directory contains application data files.

## Files

- `car_database.db` - SQLite database file (gitignored)
  - Contains all application data including vehicles, search requests, and flagged prompts
  - Automatically created on first application startup
  - Schema is managed by `utils/db_bootstrap.py`

The database file is excluded from version control via `.gitignore`.

