# Utilities

This directory contains shared utility functions used across multiple frontend containers.

## Files

- `helpers.js` - Shared helper functions including:
  - `escapeHtml()` - Escapes HTML to prevent XSS attacks
  - `formatSqlQuery()` - Formats SQL queries for display

These utilities are imported by container files to avoid code duplication.

