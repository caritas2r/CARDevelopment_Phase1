"""
Database Setup Script - Handles initial database setup
"""
DB_SETUP_RUN = False


def db_setup(connection_service):
    """
    Set up the database by calling create_database on the connection service.
    Checks if database exists before attempting to create one.
    Sets DB_SETUP_RUN to True after execution.
    
    Args:
        connection_service: DatabaseConnectionService instance with create_database method
    
    Returns:
        bool: True if database was created, False if it already existed
    """
    global DB_SETUP_RUN
    
    if not DB_SETUP_RUN:
        print("[database_setup_script] Running database setup...")
        
        # Check if database already exists
        if connection_service.database_exists():
            print("[database_setup_script] Database already exists, skipping creation")
            DB_SETUP_RUN = True
            return False
        
        # Create database if it doesn't exist
        created = connection_service.create_database()
        DB_SETUP_RUN = True
        
        if created:
            print("[database_setup_script] Database setup completed - new database created")
        else:
            print("[database_setup_script] Database setup completed - database already existed")
        
        return created
    else:
        print("[database_setup_script] Database setup already run, skipping...")
        return False
