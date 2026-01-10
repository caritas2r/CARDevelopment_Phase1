# Documentation

This directory contains documentation files for the training pipeline.

## Files

- **`key_mapping_schema.md`**: Complete documentation of key mapping from full keys to shortened keys
- **`feature_analysis_summary.md`**: Analysis summary of features in the dataset

## Key Mapping

The key mapping reduces token usage by shortening JSON keys:
- Top-level keys: `make` → `mk`, `model` → `md`, etc.
- Nested keys: `include_body_styles` → `inc`, `must_have` → `must`, etc.

See `key_mapping_schema.md` for the complete mapping table.

