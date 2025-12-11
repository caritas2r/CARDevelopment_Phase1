"""
Application Entry Point
"""
from src.service_controller import ServiceController
from services.startup_service import StartupService
from services.database_connection_service import DatabaseConnectionService
from services.database_query_service import DatabaseQueryService


def create_app():
    """Create and configure the Flask application"""
    # Initialize service controller
    controller = ServiceController()
    
    # Register services
    startup_service = StartupService()
    controller.register_service(startup_service)
    
    # Register database services
    db_connection_service = DatabaseConnectionService()
    controller.register_service(db_connection_service)
    
    db_query_service = DatabaseQueryService(db_connection_service)
    controller.register_service(db_query_service)
    
    # Initialize all services
    controller.initialize_all_services()
    
    return controller.get_app()


def main():
    """Main entry point"""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()