"""
Service Controller - Manages and orchestrates all microservices
"""
import os
from flask import Flask, request, Response
from flask_cors import CORS


class ServiceController:
    """Manages all microservices in the application"""
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # Configure CORS to properly handle preflight OPTIONS requests and all responses
        cors_origins = os.getenv('CORS_ORIGINS', '*')
        self.cors_origins = cors_origins
        
        if cors_origins == '*':
            # Allow all origins (development mode)
            self.allowed_origins = None  # None means allow all
            CORS(self.app, resources={
                r"/api/*": {
                    "origins": "*",
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"],
                    "supports_credentials": False
                }
            }, supports_credentials=False)
        else:
            # Allow specific origins (production mode)
            self.allowed_origins = [origin.strip() for origin in cors_origins.split(',')]
            CORS(self.app, resources={
                r"/api/*": {
                    "origins": self.allowed_origins,
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"],
                    "supports_credentials": False
                }
            }, supports_credentials=False)
        
        # Add explicit OPTIONS route handler for /api/* routes
        # This will catch OPTIONS requests before Flask-CORS processes them
        @self.app.route('/api/<path:path>', methods=['OPTIONS'])
        def handle_options(path):
            """Explicitly handle OPTIONS preflight requests for all /api/* routes"""
            origin = request.headers.get('Origin')
            print(f"[CORS] OPTIONS request to /api/{path} from origin: {origin}")
            
            if origin and (self.allowed_origins is None or origin in self.allowed_origins):
                # Create response with CORS headers
                response = Response()
                response.headers['Access-Control-Allow-Origin'] = '*' if self.allowed_origins is None else origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                response.headers['Access-Control-Max-Age'] = '3600'
                response.status_code = 200
                print(f"[CORS] Returning OPTIONS response with CORS headers")
                return response
            else:
                print(f"[CORS] OPTIONS request from disallowed origin: {origin}")
                return Response(status=403)
        
        # Also handle in before_request as backup
        @self.app.before_request
        def handle_preflight():
            if request.method == 'OPTIONS' and request.path.startswith('/api/'):
                origin = request.headers.get('Origin')
                # Always allow if origin is present (or if we allow all)
                if origin and (self.allowed_origins is None or origin in self.allowed_origins):
                    # Create a simple response with CORS headers
                    response = Response()
                    response.headers['Access-Control-Allow-Origin'] = '*' if self.allowed_origins is None else origin
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                    response.headers['Access-Control-Max-Age'] = '3600'
                    response.status_code = 200
                    print(f"[CORS] Handling OPTIONS preflight for {request.path} from origin {origin}")
                    return response
                elif origin:
                    print(f"[CORS] OPTIONS request from disallowed origin: {origin}")
        
        # Add after_request handler to ensure CORS headers on all responses (including errors)
        @self.app.after_request
        def after_request(response):
            # Ensure CORS headers are always present on all responses
            origin = request.headers.get('Origin')
            if origin and request.path.startswith('/api/'):
                # Check if origin is allowed
                if self.allowed_origins is None or origin in self.allowed_origins:
                    # Only add if not already present (to avoid duplicates)
                    if 'Access-Control-Allow-Origin' not in response.headers:
                        response.headers['Access-Control-Allow-Origin'] = '*' if self.allowed_origins is None else origin
                    if 'Access-Control-Allow-Methods' not in response.headers:
                        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                    if 'Access-Control-Allow-Headers' not in response.headers:
                        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                    if 'Access-Control-Max-Age' not in response.headers:
                        response.headers['Access-Control-Max-Age'] = '3600'
            return response
        
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
