"""
Query Service - Orchestrates natural language query processing pipeline
"""
from flask import jsonify, request


class QueryService:
    """Service responsible for orchestrating the query processing pipeline"""
    
    def __init__(self, inference_service, json_converter_service, database_query_service, mock_nlp_trip_service=None):
        """
        Initialize the query service
        
        Args:
            inference_service: InferenceService instance
            json_converter_service: JsonInputConverterService instance
            database_query_service: DatabaseQueryService instance
            mock_nlp_trip_service: MockNlpTripService instance (optional, for PoC)
        """
        self.name = "query-service"
        self.initialized = False
        self.inference_service = inference_service
        self.json_converter_service = json_converter_service
        self.database_query_service = database_query_service
        self.mock_nlp_trip_service = mock_nlp_trip_service
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        @app.route('/api/query/v1', methods=['POST'])
        def query_endpoint():
            """
            Process natural language query and return database results
            
            Expected request body:
            {
                "query": "natural language text"
            }
            
            Returns:
                JSON response with query results or error
            """
            try:
                # Get request data
                data = request.get_json()
                
                if not data or 'query' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing required field: query',
                        'error_type': 'validation'
                    }), 400
                
                query_text = data['query']
                
                if not query_text or not isinstance(query_text, str):
                    return jsonify({
                        'success': False,
                        'error': 'Query must be a non-empty string',
                        'error_type': 'validation'
                    }), 400
                
                # PoC: Use mock service to return sample vehicle
                if self.mock_nlp_trip_service:
                    vehicle = self.mock_nlp_trip_service.get_sample_vehicle()
                    if vehicle:
                        return jsonify({
                            'success': True,
                            'query': query_text,
                            'results': [vehicle],
                            'result_count': 1,
                            'poc_mode': True
                        }), 200
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Sample vehicle not found in database',
                            'error_type': 'not_found'
                        }), 404
                
                # TODO: Implement full query processing pipeline:
                # 1. Process through inference service
                # 2. Convert JSON to SQL
                # 3. Execute query
                # 4. Format and return results
                
                return jsonify({
                    'success': False,
                    'error': 'Query processing not yet implemented',
                    'error_type': 'not_implemented'
                }), 501
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_type': 'internal_error'
                }), 500
    
    def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            print(f"[{self.name}] Initializing...")
            # Add initialization logic here
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")

