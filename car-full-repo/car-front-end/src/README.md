# Source Code

This directory contains all frontend source code.

## Structure

- `containers/` - Page-level components (home, query, results, payment, db-schema)
- `utils/` - Shared utility functions

## Containers

Each container represents a page in the application:
- Contains its own `index.js` for page logic
- Contains its own `style.css` for page-specific styles
- Exposes a render function to `app.js` for routing

## Utils

- `helpers.js` - Shared utility functions used across multiple containers (e.g., HTML escaping, SQL formatting)

