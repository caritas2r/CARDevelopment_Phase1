#!/usr/bin/env python3
"""
test_pipeline.py

Test the full NLP-to-SQL pipeline:
1. Load sample JSON with shortened keys (simulating model inference output)
2. Expand shortened keys to full keys
3. Convert JSON to SQL
4. Execute query (optional - can just print SQL)

This validates that the key mapping and SQL conversion work correctly.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.insert(0, str(Path(__file__).parent))

from services.key_mapping_service import KeyMappingService
from services.json_input_converter_service import JsonInputConverterService
from services.database_connection_service import DatabaseConnectionService
from services.database_query_service import DatabaseQueryService


def load_sample_from_jsonl(jsonl_path: Path, line_index: int = 0):
    """
    Load a sample JSON from the test JSONL file.
    Extracts the JSON from the label:true segment.
    
    Args:
        jsonl_path: Path to JSONL file
        line_index: Which line to load (0-based)
    
    Returns:
        Dictionary with shortened keys (simulating model output)
    """
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if line_index >= len(lines):
            raise ValueError(f"Line index {line_index} out of range (file has {len(lines)} lines)")
        
        line = lines[line_index].strip()
        data = json.loads(line)
        
        # Extract the JSON from label:true segment
        segments = data.get('segments', [])
        for seg in segments:
            if seg.get('label') is True:
                text = seg.get('text', '')
                # Remove END_MARKER if present
                if '<END_JSON>' in text:
                    text = text.split('<END_JSON>')[0]
                # Parse the JSON
                return json.loads(text)
        
        raise ValueError("No label:true segment found in line")


def test_pipeline(jsonl_path: Path, line_index: int = 0, execute_query: bool = False):
    """
    Test the full pipeline on a sample from the JSONL file.
    
    Args:
        jsonl_path: Path to test JSONL file
        line_index: Which line to test (0-based)
        execute_query: Whether to actually execute the SQL query
    """
    print("=" * 80)
    print("TESTING NLP-TO-SQL PIPELINE")
    print("=" * 80)
    
    # Step 1: Load sample JSON with shortened keys (simulating model inference)
    print(f"\n[Step 1] Loading sample from {jsonl_path} (line {line_index})...")
    try:
        json_with_short_keys = load_sample_from_jsonl(jsonl_path, line_index)
        print("✓ Loaded JSON with shortened keys:")
        print(json.dumps(json_with_short_keys, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"✗ Failed to load sample: {e}")
        return False
    
    # Step 2: Expand shortened keys to full keys
    print(f"\n[Step 2] Expanding shortened keys to full keys...")
    try:
        key_mapping_service = KeyMappingService()
        key_mapping_service.initialize()
        json_with_full_keys = key_mapping_service.expand_shortened_keys(json_with_short_keys)
        print("✓ Expanded to full keys:")
        print(json.dumps(json_with_full_keys, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"✗ Key mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Convert JSON to SQL
    print(f"\n[Step 3] Converting JSON to SQL...")
    try:
        json_converter_service = JsonInputConverterService()
        json_converter_service.initialize()
        
        # Validate JSON structure first
        json_converter_service.validate_json_structure(json_with_full_keys)
        print("✓ JSON structure validated")
        
        # Convert to SQL
        sql_query, sql_params = json_converter_service.convert_to_sql(json_with_full_keys)
        print("✓ Generated SQL query:")
        print(f"  SQL: {sql_query}")
        print(f"  Parameters: {sql_params}")
    except Exception as e:
        print(f"✗ SQL conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Execute query (optional)
    if execute_query:
        print(f"\n[Step 4] Executing SQL query...")
        try:
            db_connection_service = DatabaseConnectionService()
            db_connection_service.initialize()
            db_query_service = DatabaseQueryService(db_connection_service)
            db_query_service.initialize()
            
            results = db_query_service.execute_query(sql_query, sql_params)
            print(f"✓ Query executed successfully")
            print(f"  Results: {len(results)} rows")
            if results:
                print("  First result:")
                print(json.dumps(results[0], indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"\n[Step 4] Skipping query execution (use --execute to run queries)")
    
    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test the NLP-to-SQL pipeline with sample data"
    )
    parser.add_argument(
        "--file",
        "-f",
        default="training/data/active/test_mapped_v2.jsonl",
        help="Path to test JSONL file (default: training/data/active/test_mapped_v2.jsonl)"
    )
    parser.add_argument(
        "--line",
        "-l",
        type=int,
        default=0,
        help="Line index to test (0-based, default: 0)"
    )
    parser.add_argument(
        "--execute",
        "-e",
        action="store_true",
        help="Actually execute the SQL query (requires database)"
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Test all lines in the file"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    jsonl_path = script_dir / args.file
    
    if not jsonl_path.exists():
        print(f"Error: File not found: {jsonl_path}")
        sys.exit(1)
    
    if args.all:
        # Test all lines
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        
        print(f"Testing all {total_lines} lines in {jsonl_path}...\n")
        success_count = 0
        for i in range(total_lines):
            print(f"\n{'='*80}")
            print(f"Testing line {i}/{total_lines-1}")
            print(f"{'='*80}")
            if test_pipeline(jsonl_path, i, args.execute):
                success_count += 1
            else:
                print(f"Line {i} failed!")
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {success_count}/{total_lines} lines passed")
        print(f"{'='*80}")
    else:
        # Test single line
        success = test_pipeline(jsonl_path, args.line, args.execute)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

