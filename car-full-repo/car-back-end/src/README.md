# Source Code

This directory contains core application infrastructure.

## Files

- `service_controller.py` - Service controller that manages and orchestrates all microservices in the application

## Service Controller

The `ServiceController` class:
- Manages the Flask application instance
- Registers and initializes all microservices
- Provides CORS support for frontend requests
- Handles service lifecycle (registration, initialization, execution)

Services are registered with the controller and must implement a `register(app)` method to add routes and functionality to the Flask app.

