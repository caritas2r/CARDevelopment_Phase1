"""
Query Service - Orchestrates natural language query processing pipeline
"""
from flask import jsonify, request
from services.output_quality_service import OutputQualityService


class QueryService:
    """Service responsible for orchestrating the query processing pipeline"""
    
    def __init__(self, inference_service=None, key_mapping_service=None, json_converter_service=None, database_query_service=None, mock_nlp_trip_service=None, mock_query_service=None):
        """
        Initialize the query service
        
        Args:
            inference_service: InferenceService instance (required)
            key_mapping_service: KeyMappingService instance (required)
            json_converter_service: JsonInputConverterService instance (required)
            database_query_service: DatabaseQueryService instance (required)
            mock_nlp_trip_service: MockNlpTripService instance (optional, deprecated - set to None to use real inference)
        """
        """
        Initialize the query service
        
        Args:
            inference_service: InferenceService instance
            key_mapping_service: KeyMappingService instance (converts shortened keys to full keys)
            json_converter_service: JsonInputConverterService instance
            database_query_service: DatabaseQueryService instance
            mock_nlp_trip_service: MockNlpTripService instance (optional, for PoC)
        """
        self.name = "query-service"
        self.initialized = False
        self.inference_service = inference_service
        self.key_mapping_service = key_mapping_service
        self.json_converter_service = json_converter_service
        self.database_query_service = database_query_service
        self.mock_nlp_trip_service = mock_nlp_trip_service
        self.mock_query_service = mock_query_service
        
        # Only initialize quality service if not in mock mode
        if mock_query_service is None:
            self.quality_service = OutputQualityService()
            self.quality_service.initialize()
        else:
            self.quality_service = None
    
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
                
                # Check if we're in mock mode
                if self.mock_query_service is not None:
                    # Mock mode: Use MockQueryService (no inference, no database)
                    try:
                        result = self.mock_query_service.process_query(query_text)
                        return jsonify(result), 200
                    except ValueError as e:
                        return jsonify({
                            'success': False,
                            'error': str(e),
                            'error_type': 'validation'
                        }), 400
                
                # Normal mode: Full query processing pipeline
                # 1. Process through inference service (NLP -> JSON with shortened keys)
                # 2. Expand shortened keys to full keys (mk -> make, md -> model, etc.)
                # 3. Convert JSON to SQL
                # 4. Execute query
                # 5. Format and return results
                
                # Step 1: Process through inference service
                json_with_short_keys = self.inference_service.process_query(query_text)
                
                # Step 1.5: Check output quality (only if quality service is available)
                if self.quality_service:
                    is_acceptable, quality_warnings = self.quality_service.check_output_quality(
                        json_with_short_keys, query_text
                    )
                    if quality_warnings:
                        print(f"[{self.name}] Quality warnings: {', '.join(quality_warnings)}")
                else:
                    quality_warnings = []
                    is_acceptable = True
                
                # Extract specified fields (non-unspecified) from the JSON
                specified_fields = self.inference_service._extract_specified_fields(json_with_short_keys)
                
                # Step 2: Expand shortened keys to full keys for SQL conversion
                json_with_full_keys = self.key_mapping_service.expand_shortened_keys(json_with_short_keys)
                
                # Step 2.5: Validate JSON structure against schema
                try:
                    self.json_converter_service.validate_json_structure(json_with_full_keys)
                    print(f"[{self.name}] JSON structure validated against schema")
                except ValueError as e:
                    print(f"[{self.name}] WARNING: Schema validation failed: {e}")
                    # Continue anyway - let SQL conversion handle it, but log the issue
                
                # Step 3: Convert JSON to SQL
                sql_query, sql_params = self.json_converter_service.convert_to_sql(json_with_full_keys)
                
                # Step 4: Execute query against database
                print(f"[{self.name}] Executing SQL query: {sql_query[:200]}...")  # Log first 200 chars
                print(f"[{self.name}] SQL parameters: {sql_params}")
                results = self.database_query_service.execute_query(sql_query, sql_params)
                print(f"[{self.name}] Query executed successfully. Found {len(results)} results.")
                
                # Step 5: Format and return results
                response_data = {
                    'success': True,
                    'query': query_text,
                    'extracted_fields': specified_fields,
                    'sql_query': sql_query,
                    'sql_params': sql_params,
                    'results': results,
                    'result_count': len(results) if results else 0,
                    'quality_warnings': quality_warnings if quality_warnings else [],
                    'quality_acceptable': is_acceptable
                }
                
                print(f"[{self.name}] Returning response with {len(results)} results to frontend")
                if results and len(results) > 0:
                    print(f"[{self.name}] Sample result keys: {list(results[0].keys())}")
                    print(f"[{self.name}] Sample result - Make: {results[0].get('make')}, Model: {results[0].get('model')}, Features: {len(results[0].get('features', []))}, Use Cases: {len(results[0].get('use_case_tags', []))}")
                
                return jsonify(response_data), 200
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_type': 'internal_error'
                }), 500
        
        @app.route('/api/query/feedback', methods=['POST'])
        def feedback_endpoint():
            """
            Store unsatisfactory query for later training
            
            Expected request body:
            {
                "query": "original query text",
                "extracted_fields": {...},
                "sql_query": "...",
                "reason": "optional reason why unsatisfactory"
            }
            
            Returns:
                JSON response confirming storage
            """
            try:
                data = request.get_json()
                
                if not data or 'query' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing required field: query',
                        'error_type': 'validation'
                    }), 400
                
                # Store the feedback query
                # For now, we'll save to a CSV file similar to the training data structure
                import csv
                import os
                from datetime import datetime
                from pathlib import Path
                
                # Create feedback directory if it doesn't exist
                feedback_dir = Path(__file__).parent.parent / 'training' / 'data' / 'feedback'
                feedback_dir.mkdir(parents=True, exist_ok=True)
                
                feedback_file = feedback_dir / 'unsatisfactory_queries.csv'
                
                # Check if file exists to write header
                file_exists = feedback_file.exists()
                
                with open(feedback_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header if new file
                    if not file_exists:
                        writer.writerow([
                            'timestamp', 'query', 'extracted_fields', 'sql_query', 
                            'sql_params', 'reason'
                        ])
                    
                    # Write feedback data
                    import json
                    writer.writerow([
                        datetime.now().isoformat(),
                        data.get('query', ''),
                        json.dumps(data.get('extracted_fields', {})),
                        data.get('sql_query', ''),
                        json.dumps(data.get('sql_params', [])),
                        data.get('reason', '')
                    ])
                
                print(f"[{self.name}] Stored unsatisfactory query feedback")
                
                return jsonify({
                    'success': True,
                    'message': 'Feedback stored successfully'
                }), 200
                
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

