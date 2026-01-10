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
            # Ensure connection service is initialized first
            if not self.connection_service.initialized:
                self.connection_service.initialize()
            # Verify we can get a connection
            try:
                conn = self.get_connection()
                # Test connection with a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                print(f"[{self.name}] Database connection verified")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize database query service: {str(e)}")
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
        Execute a SQL query and return results with junction table data enriched
        
        Args:
            sql_query: SQL query string
            params: List of parameters for parameterized query (optional)
        
        Returns:
            List of dictionaries representing query results with junction table data, or empty list if no results
        
        Raises:
            Exception: If query execution fails
        """
        if params is None:
            params = []
        
        # Ensure connection service is initialized
        if not self.connection_service.initialized:
            self.connection_service.initialize()
        
        # Get database connection
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Execute the query with parameters
            # SQLite accepts both list and tuple for params, but we'll use tuple for consistency
            params_tuple = tuple(params) if params else ()
            cursor.execute(sql_query, params_tuple)
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            if rows:
                # Get column names from cursor description
                columns = [description[0] for description in cursor.description]
                # Convert each row tuple to a dictionary
                results = [dict(zip(columns, row)) for row in rows]
                
                # Enrich results with junction table data (features, use_case_tags, powertrain_types)
                enriched_results = self._enrich_with_junction_data(conn, results)
                return enriched_results
            return []
        except Exception as e:
            # Enhanced error message with query details for debugging
            error_msg = f"Query execution failed: {str(e)}\nSQL: {sql_query}\nParams: {params}"
            print(f"[{self.name}] ERROR: {error_msg}")
            raise Exception(error_msg)
        finally:
            cursor.close()
    
    def _enrich_with_junction_data(self, conn, vehicles: list):
        """
        Enrich vehicle results with junction table data (features, use_case_tags, powertrain_types)
        
        Args:
            conn: Database connection
            vehicles: List of vehicle dictionaries from main query
        
        Returns:
            List of enriched vehicle dictionaries
        """
        if not vehicles:
            return vehicles
        
        cursor = conn.cursor()
        
        try:
            # Get all vehicle IDs
            vehicle_ids = [v.get('vehicle_id') for v in vehicles if v.get('vehicle_id')]
            
            if not vehicle_ids:
                return vehicles
            
            # Query features for all vehicles
            placeholders = ','.join(['?'] * len(vehicle_ids))
            cursor.execute(
                f"SELECT vehicle_id, feature_tag FROM vehicle_features WHERE vehicle_id IN ({placeholders})",
                vehicle_ids
            )
            features_rows = cursor.fetchall()
            
            # Query use case tags for all vehicles
            cursor.execute(
                f"SELECT vehicle_id, use_case_tag FROM vehicle_use_case_tags WHERE vehicle_id IN ({placeholders})",
                vehicle_ids
            )
            use_case_rows = cursor.fetchall()
            
            # Query powertrain types for all vehicles
            cursor.execute(
                f"SELECT vehicle_id, powertrain_type FROM vehicle_powertrain_types WHERE vehicle_id IN ({placeholders})",
                vehicle_ids
            )
            powertrain_rows = cursor.fetchall()
            
            # Build lookup dictionaries for efficient access
            features_by_vehicle = {}
            for vehicle_id, feature_tag in features_rows:
                if vehicle_id not in features_by_vehicle:
                    features_by_vehicle[vehicle_id] = []
                features_by_vehicle[vehicle_id].append(feature_tag)
            
            use_cases_by_vehicle = {}
            for vehicle_id, use_case_tag in use_case_rows:
                if vehicle_id not in use_cases_by_vehicle:
                    use_cases_by_vehicle[vehicle_id] = []
                use_cases_by_vehicle[vehicle_id].append(use_case_tag)
            
            powertrains_by_vehicle = {}
            for vehicle_id, powertrain_type in powertrain_rows:
                if vehicle_id not in powertrains_by_vehicle:
                    powertrains_by_vehicle[vehicle_id] = []
                powertrains_by_vehicle[vehicle_id].append(powertrain_type)
            
            # Enrich each vehicle with junction table data
            for vehicle in vehicles:
                vehicle_id = vehicle.get('vehicle_id')
                vehicle['features'] = features_by_vehicle.get(vehicle_id, [])
                vehicle['use_case_tags'] = use_cases_by_vehicle.get(vehicle_id, [])
                vehicle['powertrain_types'] = powertrains_by_vehicle.get(vehicle_id, [])
            
            return vehicles
            
        except Exception as e:
            print(f"[{self.name}] WARNING: Failed to enrich with junction data: {str(e)}")
            # Return vehicles without enrichment if junction query fails
            return vehicles
        finally:
            cursor.close()