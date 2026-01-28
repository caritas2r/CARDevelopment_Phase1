"""
Application Entry Point
"""
import sys
from src.service_controller import ServiceController
from services.startup_service import StartupService
from services.database_connection_service import DatabaseConnectionService
from services.database_query_service import DatabaseQueryService
from services.inference_service import InferenceService
from services.json_input_converter_service import JsonInputConverterService
from services.key_mapping_service import KeyMappingService
from services.query_service import QueryService
from services.mock_nlp_trip_service import MockNlpTripService
from services.mock_query_service import MockQueryService
from services.payment_service import PaymentService


def create_app(use_mock_query_service=False):
    """
    Create and configure the Flask application
    
    Args:
        use_mock_query_service: If True, use MockQueryService instead of inference pipeline
    """
    # Initialize service controller
    controller = ServiceController()
    
    # Register core services
    startup_service = StartupService()
    controller.register_service(startup_service)
    
    if use_mock_query_service:
        # Mock mode: Use MockQueryService (no inference, no database)
        print("=" * 60)
        print("MOCK MODE: Using MockQueryService (no inference/database)")
        print("=" * 60)
        print("Frontend should send only 'pass', 'fail', or 'insufficient'")
        print("See README-NOINFERENCE.md for usage instructions")
        print("=" * 60)
        
        mock_query_service = MockQueryService()
        controller.register_service(mock_query_service)
        
        # Even in mock mode, we want database for feedback storage
        db_connection_service = DatabaseConnectionService()
        controller.register_service(db_connection_service)
        
        # QueryService with mock_query_service parameter
        query_service = QueryService(mock_query_service=mock_query_service, database_connection_service=db_connection_service)
        controller.register_service(query_service)
    else:
        # Normal mode: Use full inference pipeline
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
            database_connection_service=db_connection_service,  # Needed for feedback endpoint
            mock_nlp_trip_service=None  # Set to None to use real inference service
        )
        controller.register_service(query_service)
    
    # Register payment service (available in both mock and normal modes)
    payment_service = PaymentService()
    controller.register_service(payment_service)
    
    # Initialize all services
    controller.initialize_all_services()
    
    return controller.get_app()


def main():
    """Main entry point"""
    import os
    
    # Check for --noinference flag
    use_mock = '--noinference' in sys.argv
    
    # Get port from command line --port argument or PORT env var, default to 5000
    port = 5000
    if '--port' in sys.argv:
        port_idx = sys.argv.index('--port')
        if port_idx + 1 < len(sys.argv):
            try:
                port = int(sys.argv[port_idx + 1])
            except (ValueError, IndexError):
                pass
    elif 'PORT' in os.environ:
        try:
            port = int(os.environ['PORT'])
        except ValueError:
            pass
    
    if use_mock:
        print("\n[APP] Starting in MOCK mode (--noinference flag detected)")
        print("[APP] Inference and database services disabled")
        print("[APP] MockQueryService will be used instead\n")
    
    app = create_app(use_mock_query_service=use_mock)
    print(f"\n[APP] Starting Flask server on port {port}\n")
    # Disable debug mode in production (use FLASK_ENV=production)
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()