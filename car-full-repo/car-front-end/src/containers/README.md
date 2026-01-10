# Containers

This directory contains page-level components for the frontend application.

## Pages

- `home-page/` - Home page with system status and navigation
- `query-page/` - Natural language query submission interface
- `results-page/` - Vehicle search results display with paywall functionality
- `payment-page/` - Payment processing page for unlocking full results
- `db-schema-page/` - Database schema viewer

## Container Pattern

Each container follows a consistent pattern:
- `index.js` - Contains page logic and render function
- `style.css` - Contains page-specific styles
- Exposes a render function (e.g., `renderQueryPage()`) that is called by `app.js` routing
- Uses IBM Carbon Design System v11 for styling

## Routing

Containers are registered in `app.js` and accessed via hash-based routing:
- `#/` - Home page
- `#/query` - Query page
- `#/results` - Results page
- `#/payment` - Payment page
- `#/db-schema` - Database schema page

