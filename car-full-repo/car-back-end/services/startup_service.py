"""
Startup Service - Handles application startup logic
"""
from datetime import datetime
from flask import jsonify


class StartupService:
    """Service responsible for startup operations"""
    
    def __init__(self):
        self.name = "startup-service"
        self.initialized = False
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        @app.route('/')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'running',
                'service': self.name,
                'message': 'Startup service is active'
            })
        
        @app.route('/api/health')
        def api_health():
            """API health check endpoint for frontend"""
            return jsonify({
                'status': 'online',
                'backend': 'running',
                'timestamp': datetime.now().isoformat(),
                'message': 'Backend is live and connected!'
            })
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            # Add initialization logic here
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
