# Car Backend API

A Flask-based REST API backend with microservices architecture for vehicle selection and query processing.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - API health check (frontend connection test)
- `GET /api/db/health` - Database health check
- `POST /api/query/v1` - Process natural language vehicle queries (returns structured JSON)

## Architecture

The backend follows a microservices architecture with a service controller:

### Core Services
- **Service Controller**: Manages and orchestrates all microservices
- **Startup Service**: Handles application startup logic and health checks
- **Database Connection Service**: Manages database connections and setup
- **Database Query Service**: Service for database query management

### Query Processing Services
- **Query Service**: Orchestrates the natural language query processing pipeline
- **Inference Service**: Processes natural language queries through inference model (NLP to JSON)
- **JSON Input Converter Service**: Converts structured JSON query to SQL

### Utilities
- **Schema Validator**: Validates JSON output against Vehicle Selection V1 schema
- **Database Setup Script**: Handles database initialization
- **Database Bootstrap**: Creates database schema using PoC pattern (idempotent, safe to run on every startup)
- **Database Inspector**: Utility script to inspect database structure and contents

## Project Structure

```
car-back-end/
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/
│   └── car_database.db            # SQLite database (gitignored)
├── schemas/                        # Vehicle Selection V1 schema definitions
│   ├── __init__.py
│   ├── README.md                   # Schema documentation
│   ├── vehicle_selection_v1_schema.json  # JSON Schema (Draft-07)
│   ├── vehicle_selection_v1_vocab.py     # Canonical vocabularies
│   └── training_example.json      # Example training data
├── services/                       # Microservices
│   ├── __init__.py
│   ├── startup_service.py         # Startup and health checks
│   ├── database_connection_service.py
│   ├── database_query_service.py
│   ├── query_service.py           # Query orchestration
│   ├── inference_service.py       # NLP to JSON conversion
│   └── json_input_converter_service.py  # JSON to SQL conversion
├── src/
│   ├── __init__.py
│   └── service_controller.py      # Service controller
└── utils/                          # Utility scripts
    ├── __init__.py
    ├── database_setup_script.py    # Database setup script
    ├── db_bootstrap.py              # Database schema bootstrap (PoC pattern)
    ├── DB_BOOTSTRAP_README.md       # Database bootstrap documentation
    ├── inspect_database.py          # Database inspection utility
    └── schema_validator.py         # Schema validation utility
```

## Vehicle Selection V1 Schema

The backend uses a structured schema for vehicle selection queries. See `schemas/README.md` for detailed documentation.

### Key Features
- **Structured JSON Output**: Natural language queries are converted to structured JSON
- **Schema Validation**: All outputs are validated against Vehicle Selection V1 schema
- **Canonical Vocabularies**: Consistent enum values for training and inference

### Example Query

**Input:**
```json
{
  "query": "I need an SUV for my family of 5, under $30k, with AWD and backup camera"
}
```

**Output:** (Structured JSON conforming to Vehicle Selection V1 schema)
See `schemas/training_example.json` for a complete example.

## Database

The application uses SQLite for local development:
- Database file: `data/car_database.db` (gitignored)
- Database setup runs automatically on first startup
- Database schema is created using the bootstrap pattern (idempotent, safe to run on every startup)
- Schema includes three tables:
  - `vehicles`: Main vehicle inventory table with all vehicle attributes (make, model, year, body_style, price, currency, transmission, drivetrain, powertrain_type, seating_capacity, mileage, location)
  - `vehicle_features`: Junction table for vehicle features (many-to-many relationship)
  - `query_history`: Stores processed NLP queries and their Vehicle Selection V1 JSON representations
- Connection service manages a single persistent database connection
- See `utils/DB_BOOTSTRAP_README.md` for detailed database schema documentation
- Use `python utils/inspect_database.py` to inspect the database structure

## Dependencies

- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - CORS support
- python-dotenv 1.0.0 - Environment variable management
- jsonschema 4.20.0 - JSON schema validation
