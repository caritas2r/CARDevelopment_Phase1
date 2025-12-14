"""
Database Connection Service - Manages database connections and setup
"""
import sqlite3
import os
from pathlib import Path
from flask import jsonify
from utils.database_setup_script import DB_SETUP_RUN, db_setup
from utils.db_bootstrap import ensure_db_and_schema


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
    
    def database_exists(self):
        """
        Check if the database file exists and is a valid SQLite database
        
        Returns:
            bool: True if database exists and is valid, False otherwise
        """
        if not os.path.exists(self.db_path):
            return False
        
        # Verify it's a valid SQLite database by trying to open it
        try:
            test_conn = sqlite3.connect(self.db_path)
            # Try to query sqlite_master to verify it's a valid database
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
            return True
        except (sqlite3.Error, sqlite3.DatabaseError):
            # File exists but is not a valid SQLite database
            return False
    
    def create_database(self):
        """
        Create the database file, directory, and schema if they don't exist.
        Checks if database already exists before attempting to create one.
        Uses the bootstrap pattern to ensure schema is created.
        
        Returns:
            bool: True if database was created, False if it already existed
        """
        # Check if database already exists
        if self.database_exists():
            print(f"[{self.name}] Database already exists at {self.db_path}")
            # Even if database exists, ensure schema is up to date (idempotent)
            try:
                conn = sqlite3.connect(self.db_path)
                ensure_db_and_schema(self.db_path, connection=conn)
                conn.close()
            except sqlite3.Error as e:
                print(f"[{self.name}] WARNING: Could not verify schema: {e}")
            print(f"[{self.name}] Skipping database creation")
            return False
        
        # Create data directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"[{self.name}] Created data directory: {db_dir}")
        
        # Create database connection and schema (this creates the file if it doesn't exist)
        try:
            conn = sqlite3.connect(self.db_path)
            # Use bootstrap to create schema (idempotent)
            ensure_db_and_schema(self.db_path, connection=conn)
            conn.close()
            print(f"[{self.name}] Database and schema created successfully at {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"[{self.name}] ERROR: Failed to create database: {e}")
            raise
    
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
        """
        Initialize the service.
        Ensures database exists before establishing connection.
        """
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            
            # Check if database exists first
            if not self.database_exists():
                print(f"[{self.name}] Database not found. Will create during setup.")
            else:
                print(f"[{self.name}] Database found at {self.db_path}")
            
            # Check if database setup needs to run
            if not DB_SETUP_RUN:
                db_setup(self)
            else:
                print(f"[{self.name}] Database setup already completed")
            
            # Verify database exists before connecting
            if not self.database_exists():
                raise RuntimeError(f"Database does not exist at {self.db_path} and could not be created")
            
            # Get initial connection
            conn = self.get_connection()
            
            # Ensure schema is up to date (idempotent - safe to run every time)
            ensure_db_and_schema(self.db_path, connection=conn)
            
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
            print(f"[{self.name}] Database ready at {self.db_path}")
