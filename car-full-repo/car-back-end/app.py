"""
Application Entry Point
"""
from src.service_controller import ServiceController
from services.startup_service import StartupService
from services.database_connection_service import DatabaseConnectionService
from services.database_query_service import DatabaseQueryService
from services.inference_service import InferenceService
from services.json_input_converter_service import JsonInputConverterService
from services.key_mapping_service import KeyMappingService
from services.query_service import QueryService
from services.mock_nlp_trip_service import MockNlpTripService


def create_app():
    """Create and configure the Flask application"""
    # Initialize service controller
    controller = ServiceController()
    
    # Register core services
    startup_service = StartupService()
    controller.register_service(startup_service)
    
    # Register database services
    db_connection_service = DatabaseConnectionService()
    controller.register_service(db_connection_service)
    
    db_query_service = DatabaseQueryService(db_connection_service)
    controller.register_service(db_query_service)
    
    # Register query processing services
    # These services form the NLP-to-SQL pipeline
    inference_service = InferenceService()
    controller.register_service(inference_service)
    
    json_converter_service = JsonInputConverterService()
    controller.register_service(json_converter_service)
    
    key_mapping_service = KeyMappingService()
    controller.register_service(key_mapping_service)
    
    # QueryService depends on the other services, so create it after they're instantiated
    query_service = QueryService(
        inference_service=inference_service,
        key_mapping_service=key_mapping_service,
        json_converter_service=json_converter_service,
        database_query_service=db_query_service,
        mock_nlp_trip_service=None  # Set to None to use real inference service
    )
    controller.register_service(query_service)
    
    # Initialize all services
    controller.initialize_all_services()
    
    return controller.get_app()


def main():
    """Main entry point"""
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()