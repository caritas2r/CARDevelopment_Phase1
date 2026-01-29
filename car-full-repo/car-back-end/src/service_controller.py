"""
Service Controller - Manages and orchestrates all microservices
"""
import os
from flask import Flask
from flask_cors import CORS


class ServiceController:
    """Manages all microservices in the application"""
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # Configure CORS to properly handle preflight OPTIONS requests
        cors_origins = os.getenv('CORS_ORIGINS', '*')
        if cors_origins == '*':
            # Allow all origins (development mode)
            CORS(self.app, resources={
                r"/api/*": {
                    "origins": "*",
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"]
                }
            })
        else:
            # Allow specific origins (production mode)
            origins = [origin.strip() for origin in cors_origins.split(',')]
            CORS(self.app, resources={
                r"/api/*": {
                    "origins": origins,
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"]
                }
            })
        
        self.services = []
    
    def register_service(self, service):
        """
        Register a service with the controller
        
        Args:
            service: Service instance that implements a register() method
        """
        if hasattr(service, 'register'):
            service.register(self.app)
            self.services.append(service)
        else:
            raise ValueError(f"Service {service} does not implement a register() method")
    
    def initialize_all_services(self):
        """Initialize all registered services"""
        for service in self.services:
            if hasattr(service, 'initialize'):
                service.initialize()
    
    def get_app(self):
        """Get the Flask application instance"""
        return self.app
    
    def run(self, **kwargs):
        """Run the Flask application"""
        self.initialize_all_services()
        self.app.run(**kwargs)
