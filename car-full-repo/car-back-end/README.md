# Car Backend API

A Flask-based REST API for managing car data.

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
- `GET /api/cars` - Get all cars
- `POST /api/cars` - Add a new car (requires: make, model, year)
- `GET /api/cars/<id>` - Get a specific car
- `DELETE /api/cars/<id>` - Delete a car

## Example Request

```bash
curl -X POST http://localhost:5000/api/cars \
  -H "Content-Type: application/json" \
  -d '{"make": "Toyota", "model": "Camry", "year": 2023, "color": "Blue"}'
```
