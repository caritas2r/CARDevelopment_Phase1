# Services

This directory contains all microservices that make up the application backend.

## Core Services

- `startup_service.py` - Handles application startup logic and health check endpoints
- `database_connection_service.py` - Manages database connections and initialization
- `database_query_service.py` - Handles database query execution

## Query Processing Services

- `query_service.py` - Orchestrates the natural language query processing pipeline
- `inference_service.py` - Processes natural language queries through inference model (NLP to JSON)
- `key_mapping_service.py` - Converts shortened keys to full keys in JSON output
- `json_input_converter_service.py` - Converts structured JSON query to SQL queries

## Mock Services

- `mock_query_service.py` - Mock query service for testing without inference (used with `--noinference` flag)
- `mock_nlp_trip_service.py` - Mock NLP service for PoC demonstrations

## Supporting Services

- `output_quality_service.py` - Validates and checks quality of inference output
- `payment_service.py` - Handles Stripe payment processing

## Service Pattern

All services follow a consistent pattern:
- Implement a `register(app)` method to add routes/functionality to the Flask app
- Optionally implement an `initialize()` method for startup logic
- Services are registered with the `ServiceController` in `app.py`

## Documentation

- `QUERY_FEEDBACK.md` - Documentation for the query feedback system
- `OUTPUT_QUALITY_SERVICE.md` - Documentation for the output quality service

