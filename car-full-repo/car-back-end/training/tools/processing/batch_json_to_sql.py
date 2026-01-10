"""
Batch JSON to SQL Converter

One-off script to batch process inference results and convert them to SQL queries.
This is for review/testing purposes only - production workflow uses live prompts.

Prerequisites:
    Install dependencies: pip install -r requirements.txt

Usage:
    python batch_json_to_sql.py <input_jsonl_file> [--output <output_file>]
    
    Run from car-back-end/ directory:
    python training/batch_json_to_sql.py training/data/inference_results/inference_report_test_v2.jsonl --output training/sql_results.jsonl
    
Example:
    python training/batch_json_to_sql.py training/data/inference_results/inference_report_test_v2.jsonl --output training/sql_results.jsonl
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add car-back-end directory to path to import services
# Script can be run from training/ or car-back-end/ directory
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from services.key_mapping_service import KeyMappingService
from services.json_input_converter_service import JsonInputConverterService


def load_inference_results(jsonl_path: str) -> List[Dict[str, Any]]:
    """
    Load inference results from JSONL file.
    
    Args:
        jsonl_path: Path to JSONL file containing inference results
        
    Returns:
        List of inference result dictionaries
    """
    results = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                results.append(record)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num}: {e}", file=sys.stderr)
                continue
    return results


def process_inference_to_sql(
    inference_record: Dict[str, Any],
    key_mapping_service: KeyMappingService,
    json_converter_service: JsonInputConverterService
) -> Dict[str, Any]:
    """
    Process a single inference record: extract JSON, expand keys, convert to SQL.
    
    Args:
        inference_record: Single inference result record from JSONL
        key_mapping_service: Service for expanding shortened keys
        json_converter_service: Service for converting JSON to SQL
        
    Returns:
        Dictionary containing:
        - source_line_index: Original line index
        - input_text: Original user query
        - parsed_json_short: JSON with shortened keys (from model)
        - parsed_json_full: JSON with full keys (after expansion)
        - sql_query: Generated SQL query
        - sql_params: SQL parameters
        - conversion_success: Whether conversion succeeded
        - conversion_error: Error message if conversion failed
    """
    result = {
        'source_line_index': inference_record.get('source_line_index', -1),
        'input_text': inference_record.get('input_text', ''),
        'parsed_json_short': None,
        'parsed_json_full': None,
        'sql_query': None,
        'sql_params': None,
        'conversion_success': False,
        'conversion_error': None
    }
    
    # Extract parsed JSON (with shortened keys)
    parsed_json_short = inference_record.get('parsed_json')
    if not parsed_json_short:
        result['conversion_error'] = 'No parsed_json field in inference record'
        return result
    
    result['parsed_json_short'] = parsed_json_short
    
    try:
        # Step 1: Expand shortened keys to full keys
        parsed_json_full = key_mapping_service.expand_shortened_keys(parsed_json_short)
        result['parsed_json_full'] = parsed_json_full
        
        # Step 2: Convert JSON to SQL
        sql_query, sql_params = json_converter_service.convert_to_sql(parsed_json_full)
        result['sql_query'] = sql_query
        result['sql_params'] = sql_params
        result['conversion_success'] = True
        
    except Exception as e:
        result['conversion_error'] = str(e)
        result['conversion_success'] = False
    
    return result


def main():
    """Main entry point for batch processing"""
    parser = argparse.ArgumentParser(
        description='Batch process inference results and convert to SQL queries'
    )
    parser.add_argument(
        'input_file',
        help='Path to input JSONL file with inference results'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Path to output JSONL file (default: stdout)',
        default=None
    )
    parser.add_argument(
        '--pretty',
        '-p',
        action='store_true',
        help='Pretty print JSON output (for human reading)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize services
    print("Initializing services...", file=sys.stderr)
    key_mapping_service = KeyMappingService()
    key_mapping_service.initialize()
    
    json_converter_service = JsonInputConverterService()
    json_converter_service.initialize()
    
    # Load inference results
    print(f"Loading inference results from {args.input_file}...", file=sys.stderr)
    inference_results = load_inference_results(args.input_file)
    print(f"Loaded {len(inference_results)} inference results", file=sys.stderr)
    
    # Process each record
    print("Processing records...", file=sys.stderr)
    sql_results = []
    success_count = 0
    error_count = 0
    
    for i, inference_record in enumerate(inference_results, 1):
        result = process_inference_to_sql(
            inference_record,
            key_mapping_service,
            json_converter_service
        )
        sql_results.append(result)
        
        if result['conversion_success']:
            success_count += 1
        else:
            error_count += 1
            print(
                f"  Error processing record {i} (line {result['source_line_index']}): "
                f"{result['conversion_error']}",
                file=sys.stderr
            )
    
    print(f"\nProcessing complete:", file=sys.stderr)
    print(f"  Success: {success_count}", file=sys.stderr)
    print(f"  Errors: {error_count}", file=sys.stderr)
    
    # Output results
    output_file = open(args.output, 'w', encoding='utf-8') if args.output else sys.stdout
    
    try:
        if args.pretty:
            # Pretty print for human reading
            json.dump(sql_results, output_file, indent=2, ensure_ascii=False)
            output_file.write('\n')
        else:
            # JSONL format (one JSON object per line)
            for result in sql_results:
                json.dump(result, output_file, ensure_ascii=False)
                output_file.write('\n')
    finally:
        if args.output and output_file != sys.stdout:
            output_file.close()
            print(f"\nResults written to {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()

