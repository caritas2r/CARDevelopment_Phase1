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
    
    def execute_query(self, sql_query: str, params: list = None):
        """
        Execute a SQL query and return results
        
        Args:
            sql_query: SQL query string
            params: List of parameters for parameterized query (optional)
        
        Returns:
            List of dictionaries representing query results, or empty list if no results
        
        Raises:
            Exception: If query execution fails
        """
        if params is None:
            params = []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            if rows:
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                return results
            return []
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
        finally:
            cursor.close()