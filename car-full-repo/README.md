# Car Management System

A full-stack application with a Python Flask backend and a lightweight frontend for managing car data.

## Project Structure

```
car-full-repo/
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
│
├── car-back-end/                    # Flask API backend (microservices architecture)
│   ├── app.py                       # Application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── README.md                    # Backend documentation
│   ├── data/                        # Data directory
│   │   └── car_database.db          # SQLite database (gitignored)
│   ├── schemas/                     # Vehicle Selection V1 schema
│   │   ├── __init__.py
│   │   ├── README.md                # Schema documentation
│   │   ├── vehicle_selection_v1_schema.json  # JSON Schema definition
│   │   ├── vehicle_selection_v1_vocab.py    # Canonical vocabularies
│   │   └── training_example.json   # Example training data
│   ├── services/                    # Microservices
│   │   ├── __init__.py
│   │   ├── startup_service.py       # Startup service (health checks)
│   │   ├── database_connection_service.py  # Database connection management
│   │   ├── database_query_service.py       # Database query management
│   │   ├── query_service.py         # Query orchestration
│   │   ├── inference_service.py     # NLP to JSON conversion
│   │   └── json_input_converter_service.py  # JSON to SQL conversion
│   ├── src/                         # Source code
│   │   ├── __init__.py
│   │   └── service_controller.py    # Service controller
│   └── utils/                       # Utility scripts
│       ├── __init__.py
│       ├── database_setup_script.py # Database setup script
│       ├── db_bootstrap.py          # Database schema bootstrap (PoC pattern)
│       ├── DB_BOOTSTRAP_README.md   # Database bootstrap documentation
│       ├── inspect_database.py      # Database inspection utility
│       └── schema_validator.py      # Schema validation utility
│
└── car-front-end/                   # Lightweight frontend
    ├── index.html                   # Main HTML file
    ├── app.js                       # App entry point (routing)
    ├── package.json                 # Node dependencies
    ├── README.md                    # Frontend documentation
    └── src/                         # Source code
        └── containers/              # Page containers
            └── home-page/           # Home page container
                ├── index.js         # Home page logic
                └── style.css        # Home page styles
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd car-back-end
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd car-front-end
```

2. Start a local server (choose one):

   **Python:**
   ```bash
   python -m http.server 8000
   ```

   **Node.js:**
   ```bash
   npx http-server -p 8000
   ```

3. Open `http://localhost:8000` in your browser

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - API health check (frontend connection test)
- `GET /api/db/health` - Database health check
- `POST /api/query/v1` - Process natural language vehicle queries
  - Request body: `{ "query": "natural language text" }`
  - Returns: Structured JSON conforming to Vehicle Selection V1 schema

## Technology Stack

- **Backend:** 
  - Python, Flask, Flask-CORS
  - SQLite (local database)
  - Microservices architecture with service controller
  - JSON Schema validation (jsonschema)
  - NLP to JSON translation pipeline
- **Frontend:** 
  - HTML5, CSS3, Vanilla JavaScript (ES6 modules)
  - Container-based architecture
  - IBM Carbon Design System v11

## Features

### Backend
- Microservices architecture with service controller
- Database connection management service
- Database query management service
- Natural language query processing pipeline
- Vehicle Selection V1 schema for structured queries
- Schema validation utility
- Database setup script with initialization tracking
- Health check endpoints
- CORS enabled for cross-origin requests

### Frontend
- Container-based frontend architecture
- IBM Carbon Design System v11 styling
- Responsive design

## Architecture

### Backend
The backend follows a microservices architecture:

**Core Services:**
- **Service Controller**: Manages and orchestrates all microservices
- **Startup Service**: Handles application startup and health checks
- **Database Connection Service**: Manages database connections
- **Database Query Service**: Handles database queries

**Query Processing Pipeline:**
1. **Query Service**: Receives natural language query, orchestrates processing
2. **Inference Service**: Converts natural language to structured JSON (Vehicle Selection V1 schema)
3. **JSON Input Converter Service**: Converts structured JSON to SQL
4. **Database Query Service**: Executes SQL queries

**Supporting Components:**
- **Schemas**: Vehicle Selection V1 schema definitions and vocabularies
- **Schema Validator**: Validates JSON output against schema
- **Utils**: Utility scripts for database setup and validation

### Frontend
The frontend uses a container-based architecture:
- **app.js**: Entry point that handles routing
- **Containers**: Page-level components (home-page, etc.)
- Each container has its own logic (`index.js`) and styles (`style.css`)
- IBM Carbon Design System v11 for consistent styling

## Database

The application uses SQLite for local development:
- Database file: `car-back-end/data/car_database.db` (gitignored)
- Database setup runs automatically on first startup
- Database schema is created using the bootstrap pattern (idempotent, safe to run on every startup)
- Schema includes three tables:
  - `vehicles`: Main vehicle inventory table with all vehicle attributes
  - `vehicle_features`: Junction table for vehicle features (many-to-many)
  - `query_history`: Stores processed queries for analytics
- Connection service manages a single persistent database connection
- Query service handles all database operations
- See `car-back-end/utils/DB_BOOTSTRAP_README.md` for detailed database schema documentation

## Vehicle Selection V1 Schema

The system uses a structured schema for vehicle selection queries. This schema:
- Defines a frozen V1 contract for NLP-to-JSON translation
- Includes canonical vocabularies for consistent training
- Supports comprehensive vehicle selection criteria:
  - Vehicle type (body styles)
  - Capacity and practicality
  - Intended use cases
  - Powertrain and drivability
  - Features and amenities
  - Ownership constraints (budget, year, mileage)
  - Preference signals (reliability, safety)
  - Location constraints

See `car-back-end/schemas/README.md` for detailed schema documentation.
