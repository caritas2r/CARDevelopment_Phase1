"""
Database Connection Service - Manages database connections and setup
"""
import sqlite3
import os
from flask import jsonify
from utils.database_setup_script import DB_SETUP_RUN, db_setup


class DatabaseConnectionService:
    """Service responsible for managing database connections"""
    
    def __init__(self, db_path='data/car_database.db'):
        """
        Initialize the database connection service
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.name = "database-connection-service"
        self.initialized = False
        self.db_path = db_path
        self.connection = None
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        @app.route('/api/db/health')
        def db_health_check():
            """Database health check endpoint"""
            try:
                if self.connection is None:
                    return jsonify({
                        'status': 'disconnected',
                        'database': 'not connected'
                    }), 503
                
                # Perform a simple query to check connection
                cursor = self.connection.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                
                return jsonify({
                    'status': 'connected',
                    'database': 'healthy',
                    'path': self.db_path
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'database': 'unhealthy',
                    'error': str(e)
                }), 503
    
    def create_database(self):
        """
        Create the database file and directory if they don't exist
        """
        # Create data directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create database connection (this creates the file if it doesn't exist)
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.close()
            print(f"[{self.name}] Database created at {self.db_path}")
        else:
            print(f"[{self.name}] Database already exists at {self.db_path}")
    
    def get_connection(self):
        """
        Get or create a database connection
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute('PRAGMA foreign_keys = ON')
            # Set row factory for easier access
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            
            # Check if database setup needs to run
            if not DB_SETUP_RUN:
                db_setup(self)
            else:
                print(f"[{self.name}] Database setup already completed")
            
            # Get initial connection
            self.get_connection()
            
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
            print(f"[{self.name}] Database ready at {self.db_path}")
