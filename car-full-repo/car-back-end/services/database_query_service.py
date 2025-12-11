"""
Database Query Service - Manages CRUD operations and database queries
"""


class DatabaseQueryService:
    """Service responsible for managing database queries and CRUD operations"""
    
    def __init__(self, connection_service):
        """
        Initialize the database query service
        
        Args:
            connection_service: DatabaseConnectionService instance
        """
        self.name = "database-query-service"
        self.initialized = False
        self.connection_service = connection_service
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        # No routes needed yet - this service will be used for CRUD operations
        pass
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            # Service initialization logic will go here
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
    
    def get_connection(self):
        """
        Get database connection from connection service
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        return self.connection_service.get_connection()
