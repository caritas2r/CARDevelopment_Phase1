"""
Database Connection Service - Manages database connections and setup
PostgreSQL/Supabase version
"""
import psycopg2
import os
from flask import jsonify


class DatabaseConnectionService:
    """Service responsible for managing database connections"""
    
    def __init__(self, db_path=None):
        """
        Initialize the database connection service
        
        Args:
            db_path: Deprecated - kept for compatibility. Use DATABASE_URL env var instead.
        """
        self.name = "database-connection-service"
        self.initialized = False
        self.database_url = os.getenv('DATABASE_URL')
        self.connection = None
        
        if not self.database_url:
            raise RuntimeError("DATABASE_URL environment variable is required for PostgreSQL connection")
    
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
                cursor.close()
                
                return jsonify({
                    'status': 'connected',
                    'database': 'healthy',
                    'type': 'PostgreSQL'
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
                
                # Get connection with retry
                conn = None
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        refresh = (attempt > 0)
                        conn = self.get_connection(refresh=refresh)
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            return jsonify({
                                "status": "error",
                                "message": "Database connection error",
                                "error": str(e)
                            }), 503
                        print(f"[db_schema] Connection error on attempt {attempt + 1}, retrying...")
                        continue
                
                if conn is None:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to get database connection after retries",
                        "error": "Connection is None"
                    }), 503
                
                # Get all user tables (PostgreSQL information_schema)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                
                schema = {
                    "database_type": "PostgreSQL",
                    "tables": []
                }
                
                for t in tables:
                    table_name = t[0] if isinstance(t, (tuple, list)) else t
                    
                    if not table_name or not isinstance(table_name, str):
                        continue
                    
                    # Get table columns
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default, 
                               CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_pk
                        FROM information_schema.columns c
                        LEFT JOIN (
                            SELECT ku.table_name, ku.column_name
                            FROM information_schema.table_constraints tc
                            JOIN information_schema.key_column_usage ku
                                ON tc.constraint_name = ku.constraint_name
                            WHERE tc.constraint_type = 'PRIMARY KEY'
                        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
                        WHERE c.table_name = %s
                        ORDER BY c.ordinal_position;
                    """, (table_name,))
                    columns = cursor.fetchall()
                    
                    # Get table indexes
                    cursor.execute("""
                        SELECT i.indexname, i.indexdef
                        FROM pg_indexes i
                        WHERE i.schemaname = 'public' AND i.tablename = %s;
                    """, (table_name,))
                    indexes = cursor.fetchall()
                    
                    # Get foreign keys
                    cursor.execute("""
                        SELECT
                            tc.constraint_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name,
                            rc.update_rule,
                            rc.delete_rule
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                        JOIN information_schema.referential_constraints AS rc
                            ON rc.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
                    """, (table_name,))
                    fks = cursor.fetchall()
                    
                    # Process columns
                    column_list = []
                    for c in columns:
                        column_list.append({
                            "name": c[0],
                            "type": c[1],
                            "notnull": c[2] == 'NO',
                            "default": c[3],
                            "pk": c[4],
                        })
                    
                    # Process indexes
                    index_details = []
                    for idx in indexes:
                        index_details.append({
                            "name": idx[0],
                            "definition": idx[1]
                        })
                    
                    # Process foreign keys
                    fk_list = []
                    for fk in fks:
                        fk_list.append({
                            "constraint_name": fk[0],
                            "column": fk[1],
                            "foreign_table": fk[2],
                            "foreign_column": fk[3],
                            "on_update": fk[4],
                            "on_delete": fk[5],
                        })
                    
                    schema["tables"].append({
                        "name": table_name,
                        "columns": column_list,
                        "indexes": index_details,
                        "foreign_keys": fk_list,
                    })
                
                cursor.close()
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
    
    def get_connection(self, refresh=False):
        """
        Get or create a database connection
        
        Args:
            refresh: If True, close existing connection and create a new one
        
        Returns:
            psycopg2.connection: Database connection object
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
                cursor = self.connection.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                cursor.close()
                return self.connection
            except (psycopg2.Error, psycopg2.OperationalError):
                # Connection is stale, close it and create a new one
                print(f"[{self.name}] Connection is stale, refreshing...")
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
        
        # Create new connection
        try:
            self.connection = psycopg2.connect(self.database_url)
            print(f"[{self.name}] Connected to PostgreSQL database")
            return self.connection
        except psycopg2.Error as e:
            print(f"[{self.name}] ERROR: Failed to connect to database: {e}")
            raise RuntimeError(f"Failed to connect to PostgreSQL database: {e}")
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize(self):
        """
        Initialize the service.
        Establishes connection to PostgreSQL database.
        """
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            
            if not self.database_url:
                raise RuntimeError("DATABASE_URL environment variable is required")
            
            # Get initial connection
            conn = self.get_connection()
            
            # Test connection
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()[0]
            cursor.close()
            print(f"[{self.name}] PostgreSQL version: {version[:50]}...")
            
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
            print(f"[{self.name}] Database ready (PostgreSQL)")
