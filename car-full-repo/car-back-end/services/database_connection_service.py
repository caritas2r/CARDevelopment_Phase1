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
        
        @app.route('/api/db/schema')
        def db_schema():
            """Database schema introspection endpoint"""
            try:
                # Check if service is initialized
                if not self.initialized:
                    return jsonify({
                        "status": "error",
                        "message": "Database connection service not initialized",
                        "error": "Service not ready"
                    }), 503
                
                # Get connection (will create if needed, and auto-create database if missing)
                # Try to get connection, with retry on failure
                conn = None
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        # On retry, refresh the connection
                        refresh = (attempt > 0)
                        conn = self.get_connection(refresh=refresh)
                        break
                    except RuntimeError as e:
                        # Database doesn't exist and couldn't be created
                        if attempt == max_retries - 1:
                            return jsonify({
                                "status": "error",
                                "message": "Database not found and could not be created",
                                "error": str(e),
                                "database_path": self.db_path
                            }), 404
                        # Retry - maybe database was just created
                        continue
                    except (sqlite3.Error, sqlite3.OperationalError) as e:
                        # Database connection error
                        if attempt == max_retries - 1:
                            return jsonify({
                                "status": "error",
                                "message": "Database connection error",
                                "error": str(e),
                                "database_path": self.db_path
                            }), 503
                        # Retry with fresh connection
                        print(f"[db_schema] Connection error on attempt {attempt + 1}, retrying...")
                        continue
                    except Exception as e:
                        # Other unexpected errors
                        return jsonify({
                            "status": "error",
                            "message": "Failed to get database connection",
                            "error": str(e),
                            "database_path": self.db_path
                        }), 503
                
                if conn is None:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to get database connection after retries",
                        "error": "Connection is None",
                        "database_path": self.db_path
                    }), 503
                
                # Get all user tables (exclude sqlite internal tables)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                      AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                """)
                tables = cursor.fetchall()
                
                schema = {
                    "database_path": self.db_path,
                    "tables": []
                }
                
                for t in tables:
                    # Extract table name (should be a tuple from fetchall)
                    if not isinstance(t, (tuple, list)) or len(t) == 0:
                        continue  # Skip invalid table entries
                    
                    table_name = t[0]
                    
                    # Safety check: table name must be a non-empty string
                    if not table_name or not isinstance(table_name, str):
                        continue
                    
                    # Safety check: validate table name contains only safe characters
                    # SQLite table names should only contain alphanumeric, underscore, and dollar sign
                    if not all(c.isalnum() or c in ('_', '$') for c in table_name):
                        continue  # Skip invalid table names
                    
                    # Get table columns
                    cursor.execute(f"PRAGMA table_info('{table_name}')")
                    columns = cursor.fetchall()
                    # Get table indexes
                    cursor.execute(f"PRAGMA index_list('{table_name}')")
                    indexes = cursor.fetchall()
                    # Get foreign keys
                    cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
                    fks = cursor.fetchall()
                    
                    # Get index details
                    index_details = []
                    for idx in indexes:
                        # PRAGMA index_list returns: (seq, name, unique, origin, partial)
                        # idx[0] = seq, idx[1] = name, idx[2] = unique (0 or 1)
                        if not isinstance(idx, (tuple, list)) or len(idx) < 2:
                            continue  # Skip invalid index entries
                        
                        idx_name = idx[1]
                        
                        # Safety check: index name must be a non-empty string
                        if not idx_name or not isinstance(idx_name, str):
                            continue
                        
                        # Safety check: validate index name
                        if not all(c.isalnum() or c in ('_', '$') for c in idx_name):
                            continue  # Skip invalid index names
                        
                        cursor.execute(f"PRAGMA index_info('{idx_name}')")
                        idx_info = cursor.fetchall()
                        
                        # Extract column names from index info
                        # PRAGMA index_info returns: (seqno, cid, name)
                        # Note: name can be None for expression-based indexes
                        idx_columns = []
                        for ii in idx_info:
                            if isinstance(ii, (tuple, list)) and len(ii) > 2:
                                col_name = ii[2]  # Column name is at index 2
                                if col_name and isinstance(col_name, str):
                                    idx_columns.append(col_name)
                        
                        index_details.append({
                            "name": idx_name,
                            "unique": bool(idx[2]) if isinstance(idx, (tuple, list)) and len(idx) > 2 else False,
                            "columns": idx_columns
                        })
                    
                    # Process columns
                    # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
                    column_list = []
                    for c in columns:
                        if isinstance(c, (tuple, list)) and len(c) >= 6:
                            column_list.append({
                                "cid": c[0],
                                "name": c[1],
                                "type": c[2],
                                "notnull": bool(c[3]),
                                "default": c[4],
                                "pk": bool(c[5]),
                            })
                    
                    # Process foreign keys
                    # PRAGMA foreign_key_list returns: (id, seq, table, from, to, on_update, on_delete, match)
                    fk_list = []
                    for fk in fks:
                        if isinstance(fk, (tuple, list)) and len(fk) >= 8:
                            fk_list.append({
                                "id": fk[0],
                                "seq": fk[1],
                                "table": fk[2],
                                "from": fk[3],
                                "to": fk[4],
                                "on_update": fk[5],
                                "on_delete": fk[6],
                                "match": fk[7],
                            })
                    
                    schema["tables"].append({
                        "name": table_name,
                        "columns": column_list,
                        "indexes": index_details,
                        "foreign_keys": fk_list,
                    })
                
                return jsonify(schema)
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"[db_schema] Error: {str(e)}")
                print(f"[db_schema] Traceback: {error_trace}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to introspect database schema",
                    "error": str(e),
                }), 500
    
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
    
    def get_connection(self, refresh=False):
        """
        Get or create a database connection
        
        Args:
            refresh: If True, close existing connection and create a new one
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        # Refresh connection if requested
        if refresh and self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        
        # Check if connection exists and is still valid
        if self.connection is not None:
            try:
                # Test if connection is still alive
                self.connection.execute('SELECT 1')
                return self.connection
            except (sqlite3.Error, sqlite3.ProgrammingError):
                # Connection is stale, close it and create a new one
                print(f"[{self.name}] Connection is stale, refreshing...")
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
        
        # Create new connection
        if not os.path.exists(self.db_path):
            # Try to create database if it doesn't exist
            print(f"[{self.name}] Database not found at {self.db_path}, attempting to create...")
            try:
                self.create_database()
            except Exception as e:
                raise RuntimeError(f"Database file does not exist at {self.db_path} and could not be created: {e}")
        
        self.connection = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.connection.execute('PRAGMA foreign_keys = ON')
        # Don't set row_factory to Row for PRAGMA commands - they work better with tuples
        # self.connection.row_factory = sqlite3.Row
        
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
