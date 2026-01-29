"""
Query Service - Orchestrates natural language query processing pipeline
"""
from flask import jsonify, request
from services.output_quality_service import OutputQualityService


class QueryService:
    """Service responsible for orchestrating the query processing pipeline"""
    
    def __init__(self, inference_service=None, key_mapping_service=None, json_converter_service=None, database_query_service=None, mock_nlp_trip_service=None, mock_query_service=None, database_connection_service=None):
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
        self.database_connection_service = database_connection_service
        
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
            print(f"[{self.name}] POST /api/query/v1 received")
            print(f"[{self.name}] Request headers: {dict(request.headers)}")
            try:
                # Get request data
                data = request.get_json()
                print(f"[{self.name}] Request body: {data}")
                
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
                
                # Step 4: Execute query against database with result limiting
                MAX_RESULTS = 100  # Maximum results to return to prevent performance/storage issues
                print(f"[{self.name}] Executing SQL query: {sql_query[:200]}...")  # Log first 200 chars
                print(f"[{self.name}] SQL parameters: {sql_params}")
                
                # Get total count first (for the full query without LIMIT)
                # Use connection directly for COUNT query (doesn't need enrichment)
                conn = self.database_query_service.get_connection()
                cursor = conn.cursor()
                try:
                    count_query = sql_query.replace('SELECT *', 'SELECT COUNT(*)', 1)
                    params_tuple = tuple(sql_params) if sql_params else ()
                    cursor.execute(count_query, params_tuple)
                    count_row = cursor.fetchone()
                    total_result_count = count_row[0] if count_row else 0
                finally:
                    cursor.close()
                
                # Execute query with LIMIT
                limited_sql_query = f"{sql_query} LIMIT {MAX_RESULTS}"
                results = self.database_query_service.execute_query(limited_sql_query, sql_params)
                results_truncated = total_result_count > MAX_RESULTS
                
                print(f"[{self.name}] Query executed successfully. Found {total_result_count} total results, returning {len(results)} results.")
                if results_truncated:
                    print(f"[{self.name}] WARNING: Results truncated - {total_result_count} total results, but only returning first {MAX_RESULTS}")
                
                # Step 5: Format and return results
                response_data = {
                    'success': True,
                    'query': query_text,
                    'extracted_fields': specified_fields,
                    'sql_query': sql_query,
                    'sql_params': sql_params,
                    'results': results,
                    'result_count': len(results) if results else 0,
                    'total_result_count': total_result_count,  # Total matches found
                    'results_truncated': results_truncated,  # Flag indicating if results were limited
                    'max_results': MAX_RESULTS if results_truncated else None,  # Max limit if truncated
                    'quality_warnings': quality_warnings if quality_warnings else [],
                    'quality_acceptable': is_acceptable
                }
                
                print(f"[{self.name}] Returning response with {len(results)} results to frontend")
                if results and len(results) > 0:
                    print(f"[{self.name}] Sample result keys: {list(results[0].keys())}")
                    print(f"[{self.name}] Sample result - Make: {results[0].get('make')}, Model: {results[0].get('model')}, Features: {len(results[0].get('features', []))}, Use Cases: {len(results[0].get('use_case_tags', []))}")
                
                return jsonify(response_data), 200
                
            except ValueError as e:
                # Check if this is the "inconclusive search results" error
                error_message = str(e)
                if "Inconclusive search results" in error_message or "inconclusive" in error_message.lower():
                    return jsonify({
                        'success': False,
                        'error': error_message,
                        'error_type': 'insufficient_criteria',
                        'query': query_text,
                        'extracted_fields': {},
                        'sql_query': '',
                        'sql_params': [],
                        'results': [],
                        'result_count': 0
                    }), 400
                else:
                    # Other ValueError cases
                    return jsonify({
                        'success': False,
                        'error': error_message,
                        'error_type': 'validation_error',
                        'query': query_text
                    }), 400
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_type': 'internal_error',
                    'query': query_text
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
                
                # Store the feedback query in the database
                import json
                
                if not self.database_connection_service:
                    return jsonify({
                        'success': False,
                        'error': 'Database connection service not available',
                        'error_type': 'service_unavailable'
                    }), 503
                
                # Get database connection
                conn = self.database_connection_service.get_connection()
                
                # Prepare data for insertion
                prompt_text = data.get('query', '')
                
                # Handle extracted_fields - save even if empty dict (use None only if missing)
                extracted_fields = data.get('extracted_fields')
                if extracted_fields is not None:
                    flagged_annotation = json.dumps(extracted_fields) if extracted_fields else None
                else:
                    flagged_annotation = None
                
                # Handle sql_query - save empty string if present, use None only if missing
                flagged_query = data.get('sql_query')
                if flagged_query == '':  # Empty string is a valid value to save
                    flagged_query = ''
                elif not flagged_query:  # None or missing
                    flagged_query = None
                
                # Handle flag_reason - save empty string if present, use None only if missing
                flag_reason = data.get('reason')
                if flag_reason == '':  # Empty string is a valid value to save
                    flag_reason = ''
                elif not flag_reason:  # None or missing
                    flag_reason = None
                
                # Determine query_status based on prompt_text or response data
                # Check if it's a mock query (pass/fail/insufficient) or derive from response
                query_status = None
                prompt_lower = prompt_text.lower().strip()
                if prompt_lower in ['pass', 'fail', 'insufficient']:
                    # Mock mode: use the literal prompt text as status
                    query_status = prompt_lower
                elif data.get('success') is False:
                    # Query failed to process (parsing error, inference error, etc.)
                    query_status = 'fail'
                elif data.get('success') is True and data.get('result_count', 0) == 0:
                    # Query processed successfully but found no results (e.g., searching for McLaren P1 that doesn't exist)
                    query_status = 'insufficient'
                elif data.get('success') is True and data.get('result_count', 0) > 0:
                    # Query processed successfully and found results
                    query_status = 'pass'
                elif flagged_query and flagged_annotation:
                    # Fallback: If we have SQL query and extracted fields but no explicit status, assume it's a successful query
                    query_status = 'pass'
                # If we still don't know, leave it NULL
                
                # Insert into flagged_prompts table
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO flagged_prompts (prompt_text, flagged_annotation, flagged_query, flag_reason, query_status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (prompt_text, flagged_annotation, flagged_query, flag_reason, query_status))
                
                # Get the inserted ID (PostgreSQL uses RETURNING clause)
                flagged_id = cursor.fetchone()[0]
                
                # Commit the transaction
                conn.commit()
                
                print(f"[{self.name}] Stored flagged prompt in database with ID: {flagged_id}")
                
                return jsonify({
                    'success': True,
                    'message': 'Feedback stored successfully',
                    'flagged_id': flagged_id
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

