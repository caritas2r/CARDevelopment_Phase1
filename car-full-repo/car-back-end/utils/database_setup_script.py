"""
Database Setup Script - Handles initial database setup
"""
DB_SETUP_RUN = False


def db_setup(connection_service):
    """
    Set up the database by calling create_database on the connection service.
    Sets DB_SETUP_RUN to True after execution.
    
    Args:
        connection_service: DatabaseConnectionService instance with create_database method
    """
    global DB_SETUP_RUN
    
    if not DB_SETUP_RUN:
        print("[database_setup_script] Running database setup...")
        connection_service.create_database()
        DB_SETUP_RUN = True
        print("[database_setup_script] Database setup completed")
    else:
        print("[database_setup_script] Database setup already run, skipping...")
