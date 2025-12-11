# Car Backend API

A Flask-based REST API backend with microservices architecture.

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

## Architecture

The backend follows a microservices architecture with a service controller:
- **Service Controller**: Manages and orchestrates all microservices
- **Startup Service**: Handles application startup logic and health checks
- **Database Connection Service**: Manages database connections and setup
- **Database Query Service**: Service for database query management

## Database

The application uses SQLite for local development:
- Database file: `data/car_database.db`
- Database setup runs automatically on first startup
- Connection service manages a single persistent database connection
