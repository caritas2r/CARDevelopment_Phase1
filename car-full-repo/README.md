# Car Management System

A full-stack application with a Python Flask backend and a lightweight frontend for managing car data.

## Project Structure

```
car-full-repo/
├── car-back-end/                    # Flask API backend (microservices architecture)
│   ├── app.py                       # Application entry point
│   ├── requirements.txt
│   ├── README.md
│   ├── src/                         # Source code
│   │   ├── __init__.py
│   │   └── service_controller.py    # Service controller that manages all microservices
│   ├── services/                    # Microservices
│   │   ├── __init__.py
│   │   ├── startup_service.py       # Startup service (health checks)
│   │   ├── database_connection_service.py  # Database connection management
│   │   └── database_query_service.py       # Database query management (CRUD)
│   └── utils/                       # Utility scripts
│       ├── __init__.py
│       └── database_setup_script.py # Database setup script
│
└── car-front-end/                   # Lightweight frontend
    ├── index.html                   # Main HTML file
    ├── app.js                       # App entry point (routing)
    ├── README.md
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

## Technology Stack

- **Backend:** 
  - Python, Flask, Flask-CORS
  - SQLite (local database)
  - Microservices architecture with service controller
- **Frontend:** 
  - HTML5, CSS3, Vanilla JavaScript (ES6 modules)
  - Container-based architecture

## Features

- Microservices architecture with service controller
- Database connection management service
- Database query management service (ready for CRUD)
- Database setup script with initialization tracking
- Frontend-backend connection testing
- Health check endpoints
- CORS enabled for cross-origin requests
- Container-based frontend architecture

## Architecture

### Backend
The backend follows a microservices architecture:
- **Service Controller**: Manages and orchestrates all microservices
- **Services**: Individual microservices (startup, database connection, database query)
- **Utils**: Utility scripts for database setup and other tasks

### Frontend
The frontend uses a container-based architecture:
- **app.js**: Entry point that handles routing
- **Containers**: Page-level components (home-page, etc.)
- Each container has its own logic (`index.js`) and styles (`style.css`)

## Database

The application uses SQLite for local development:
- Database file: `car-back-end/data/car_database.db`
- Database setup runs automatically on first startup
- Connection service manages database connections
- Query service ready for CRUD operations
