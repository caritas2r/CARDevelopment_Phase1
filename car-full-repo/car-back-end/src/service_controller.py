"""
Service Controller - Manages and orchestrates all microservices
"""
from flask import Flask
from flask_cors import CORS


class ServiceController:
    """Manages all microservices in the application"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend requests
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
