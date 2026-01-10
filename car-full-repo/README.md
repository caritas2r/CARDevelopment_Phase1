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
│   │   ├── json_input_converter_service.py  # JSON to SQL conversion
│   │   └── mock_nlp_trip_service.py # Mock NLP service for PoC
│   ├── src/                         # Source code
│   │   ├── __init__.py
│   │   └── service_controller.py    # Service controller
│   ├── training/                    # Training data annotation pipeline
│   │   ├── __init__.py
│   │   ├── annotation_tool.py       # Interactive annotation tool
│   │   ├── csv_manager.py           # CSV file management
│   │   ├── field_prompter.py        # Field input prompting
│   │   ├── schema_traverser.py      # Schema traversal logic
│   │   ├── reset_csv.py             # CSV reset utility
│   │   ├── unannotated_nlp_prompts.csv  # Source prompts (input, never modified)
│   │   ├── annotated_nlp_prompts.csv    # Completed annotations (output)
│   │   ├── prompts.csv              # Sample prompts CSV (for direct mode)
│   │   └── README.md                # Training pipeline documentation
│   └── utils/                       # Utility scripts
│       ├── __init__.py
│       ├── database_setup_script.py # Database setup script
│       ├── db_bootstrap.py          # Database schema bootstrap (PoC pattern)
│       ├── DB_BOOTSTRAP_README.md   # Database bootstrap documentation
│       └── schema_validator.py      # Schema validation utility
│   ├── docs/                        # Documentation
│   │   ├── json_to_db_mapping.md    # JSON schema to database mapping
│   │   ├── end_to_end_pipeline.md   # End-to-end pipeline documentation
│   │   └── training_and_inference.md # Training and inference documentation
│
└── car-front-end/                   # Lightweight frontend
    ├── index.html                   # Main HTML file
    ├── app.js                       # App entry point (routing)
    ├── package.json                 # Node dependencies
    ├── README.md                    # Frontend documentation
    ├── dev-server.js                # Node.js dev server (no cache)
    ├── dev-server.py                # Python dev server (no cache)
    └── src/                         # Source code
        ├── containers/              # Page containers
        │   ├── home-page/           # Home page container
        │   │   ├── index.js         # Home page logic
        │   │   └── style.css        # Home page styles
        │   ├── query-page/          # Query page container
        │   │   ├── index.js         # Query page logic
        │   │   └── style.css        # Query page styles
        │   ├── results-page/        # Results page container
        │   │   ├── index.js         # Results page logic
        │   │   └── style.css        # Results page styles
        │   ├── payment-page/        # Payment page container
        │   │   ├── index.js         # Payment page logic
        │   │   └── style.css        # Payment page styles
        │   └── db-schema-page/      # Database schema page
        │       ├── index.js         # Schema page logic
        │       └── style.css         # Schema page styles
        └── utils/                   # Utility functions
            └── helpers.js           # Shared helper functions
```

## Quick Start

### Option 1: Use the Launcher Script with Inference (Recommended)

**Windows (Recommended):**
```bash
create-venv.bat
```

This script will automatically:
- Create/verify the inference virtual environment (`car_inference_env`)
- Install PyTorch (with GPU support if NVIDIA is detected, otherwise CPU)
- Install all ML inference dependencies (transformers, peft, accelerate, safetensors, etc.)
- Set up environment variables for model inference
- Start the backend server on port 5000 with full inference capabilities
- Start the frontend server on port 8000
- Open your browser to the frontend

**Mock Mode (No Inference):**
- Use `create-venv.bat --noinference` to run without GPU/model dependencies
- See `README-NOINFERENCE.md` for details

### Option 2: Manual Setup (Without Launcher Scripts)

#### Backend Setup with Inference

1. Navigate to the backend directory:
```bash
cd car-back-end
```

2. Create and activate the inference virtual environment:
```bash
python -m venv car_inference_env
# Windows:
car_inference_env\Scripts\activate
# macOS/Linux:
source car_inference_env/bin/activate
```

3. Install PyTorch (GPU if NVIDIA available, otherwise CPU):
```bash
# For GPU (NVIDIA):
pip install torch --index-url https://download.pytorch.org/whl/cu124

# For CPU:
pip install torch
```

4. Install inference dependencies:
```bash
pip install -r requirements.inference.txt
```

5. Set environment variables for model inference:
```bash
# Windows (Command Prompt):
set HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B
set LORA_ADAPTER_PATH=path\to\car-models\qwen25_3b_base_MAPPED_v2
set HF_HOME=path\to\repo\hf_cache

# Windows (PowerShell):
$env:HF_BASE_MODEL_ID = "Qwen/Qwen2.5-3B"
$env:LORA_ADAPTER_PATH = "path\to\car-models\qwen25_3b_base_MAPPED_v2"
$env:HF_HOME = "path\to\repo\hf_cache"

# macOS/Linux:
export HF_BASE_MODEL_ID=Qwen/Qwen2.5-3B
export LORA_ADAPTER_PATH=path/to/car-models/qwen25_3b_base_MAPPED_v2
export HF_HOME=path/to/repo/hf_cache
```

6. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000` with full inference support.

**Note:** For basic setup without inference (e.g., testing API endpoints only), you can use `requirements.txt` instead of `requirements.inference.txt`, but inference queries will not work.

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd car-front-end
```

2. Start a local server (choose one):

   **Python (recommended for development):**
   ```bash
   python dev-server.py
   ```
   This server sets no-cache headers automatically.

   **Node.js (recommended for development):**
   ```bash
   npm run dev
   # or
   node dev-server.js
   ```
   This also sets no-cache headers automatically.

   **Standard Python http.server:**
   ```bash
   python -m http.server 8000
   ```
   ⚠️ Note: May cache files during development.

3. Open `http://localhost:8000` in your browser

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - API health check (frontend connection test)
- `GET /api/db/health` - Database health check
- `GET /api/db/schema` - Get database schema information
- `GET /api/schema/v1` - Get Vehicle Selection V1 JSON schema
- `POST /api/query/v1` - Process natural language vehicle queries
  - Request body: `{ "query": "natural language text" }`
  - Returns: Vehicle data matching the query
- `POST /api/query/feedback` - Submit feedback for unsatisfactory queries
  - Request body: `{ "query": "...", "extracted_fields": {...}, "sql_query": "...", "reason": "..." }`
  - Stores feedback in `flagged_prompts` table
- `POST /api/payment/process` - Process payment via Stripe
  - Request body: `{ "amount": 999, "currency": "usd", "payment_method": "pm_card_visa" }`
  - Returns: Payment processing result

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
- Mock NLP service for PoC demonstrations
- Schema validation utility
- Database bootstrap with idempotent schema creation
- Training data annotation pipeline
- Health check endpoints
- CORS enabled for cross-origin requests

### Frontend
- Container-based frontend architecture
- IBM Carbon Design System v11 styling
- Hash-based routing (`#/`, `#/query`, `#/results`, `#/payment`, `#/db-schema`)
- Query submission interface with rotating placeholders
- Vehicle result display with paywall functionality
- Payment processing integration with Stripe (test mode)
- Database schema viewer
- Query feedback system for unsatisfactory results
- Responsive design

### Training Pipeline
- Interactive annotation tool for labeling NLP prompts
- Two-file workflow: `unannotated_nlp_prompts.csv` → `annotated_nlp_prompts.csv` (original file never modified)
- Automatic duplicate detection (by ID) - skips already processed prompts (only counts rows marked as "complete")
- CSV-based data management
- Schema-aware field prompting with default "unspecified" values (press Enter to accept)
- **Schema reference window** - displays all enum values and types (stays open throughout session)
- **Prompt window** - displays current NLP prompt (closes after each annotation)
- Support for arrays, enums, and complex nested structures
- Progress tracking and resume capability
- Temporary file workflow for safe processing

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
2. **Mock NLP Trip Service** (PoC): Returns sample vehicle data for demonstrations
3. **Inference Service**: Converts natural language to structured JSON (Vehicle Selection V1 schema) - for future ML integration
4. **JSON Input Converter Service**: Converts structured JSON to SQL - for future query generation
5. **Database Query Service**: Executes SQL queries

**Training Pipeline:**
1. **Annotation Tool**: Interactive CLI tool for labeling NLP prompts
2. **Schema Traverser**: Recursively extracts fields from JSON schema
3. **Field Prompter**: Handles user input for each field type
4. **CSV Manager**: Manages prompt data and annotations

**Supporting Components:**
- **Schemas**: Vehicle Selection V1 schema definitions and vocabularies
- **Schema Validator**: Validates JSON output against schema
- **Utils**: Utility scripts for database setup and validation

### Frontend
The frontend uses a container-based architecture:
- **app.js**: Entry point that handles hash-based routing (`#/`, `#/query`, `#/results`, `#/payment`, `#/db-schema`)
- **Containers**: Page-level components (home-page, query-page, results-page, payment-page, db-schema-page)
- Each container has its own logic (`index.js`) and styles (`style.css`)
- **Utils**: Shared utility functions in `src/utils/helpers.js`
- IBM Carbon Design System v11 for consistent styling
- Dynamic placeholder text rotation on query page
- Session storage for query results and payment state

## Database

The application uses SQLite for local development:
- Database file: `car-back-end/data/car_database.db` (gitignored)
- Database setup runs automatically on first startup
- Database schema is created using the bootstrap pattern (idempotent, safe to run on every startup)
- Schema includes the following tables:
  - `vehicles`: Main vehicle inventory table with all vehicle attributes
  - `vehicle_features`: Junction table for vehicle features (many-to-many)
  - `vehicle_use_case_tags`: Junction table for use case tags (many-to-many)
  - `vehicle_powertrain_types`: Junction table for powertrain types (many-to-many)
  - `search_requests`: Stores processed queries for analytics
- `flagged_prompts`: Stores user feedback for unsatisfactory queries
- Connection service manages a single persistent database connection
- Query service handles all database operations
- See `car-back-end/utils/DB_BOOTSTRAP_README.md` for detailed database schema documentation
- See `car-back-end/docs/json_to_db_mapping.md` for JSON schema to database field mappings

## Vehicle Selection V1 Schema

The system uses a structured schema for vehicle selection queries. This schema:
- Defines a frozen V1 contract for NLP-to-JSON translation
- Includes canonical vocabularies for consistent training
- Supports comprehensive vehicle selection criteria:
  - **Make and model** - **arrays of strings** (supports multiple makes/models)
  - Vehicle type (body styles) - arrays for include/exclude
  - Capacity and practicality (seating, cargo, kids, pets)
  - Intended use cases - array of tags
  - Powertrain and drivability - **powertrain_type is an array** (supports multiple selections like gas, hybrid, electric)
  - Features and amenities - arrays for must-have, nice-to-have, avoid
  - Ownership constraints (budget, year, mileage, number_of_owners)
  - Preference signals (reliability, **color as array**)
  - Location constraints
  - Trim (string field)

**Key Features:**
- Uses "unspecified" as sentinel value instead of null for enum fields
- Supports arrays for multi-select fields: **make, model, body styles, powertrain types, features, use cases, colors, mileage qualitative**
- Integer/number fields can be values or "unspecified"
- Boolean fields support "true", "false", or "unspecified"

See `car-back-end/schemas/README.md` for detailed schema documentation.
