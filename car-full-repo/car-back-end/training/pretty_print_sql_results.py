"""
Pretty Print SQL Results

Reads SQL results JSONL file and outputs a human-readable format with SQL queries.

Usage:
    python pretty_print_sql_results.py <input_jsonl_file> [--output <output_file>]
    
Example:
    python pretty_print_sql_results.py sql_results_test.jsonl --output sql_queries.txt
"""

import json
import sys
import argparse
from pathlib import Path


def format_sql_result(record: dict, separator: str = "=" * 64) -> str:
    """
    Format a single SQL result record for human reading.
    
    Args:
        record: SQL result record dictionary
        separator: Separator string to use between records
        
    Returns:
        Formatted string representation
    """
    lines = []
    lines.append(separator)
    lines.append(f"Record #{record.get('source_line_index', '?')}")
    lines.append(separator)
    lines.append("")
    lines.append("INPUT TEXT:")
    lines.append("-" * 64)
    lines.append(record.get('input_text', 'N/A'))
    lines.append("")
    
    if record.get('conversion_success'):
        lines.append("SQL QUERY:")
        lines.append("-" * 64)
        sql_query = record.get('sql_query', 'N/A')
        lines.append(sql_query)
        lines.append("")
        
        lines.append("SQL PARAMETERS:")
        lines.append("-" * 64)
        sql_params = record.get('sql_params', [])
        if sql_params:
            for i, param in enumerate(sql_params, 1):
                lines.append(f"  {i}. {param!r}")
        else:
            lines.append("  (none)")
        lines.append("")
        
        # Show a formatted version with parameters substituted (for readability)
        if sql_query and sql_params:
            lines.append("FORMATTED QUERY (for reference only):")
            lines.append("-" * 64)
            formatted = sql_query
            for param in sql_params:
                # Simple substitution - replace first ? with parameter
                if isinstance(param, str):
                    formatted = formatted.replace('?', f"'{param}'", 1)
                else:
                    formatted = formatted.replace('?', str(param), 1)
            lines.append(formatted)
            lines.append("")
    else:
        lines.append("CONVERSION FAILED:")
        lines.append("-" * 64)
        lines.append(record.get('conversion_error', 'Unknown error'))
        lines.append("")
    
    lines.append(separator)
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Pretty print SQL results from JSONL file'
    )
    parser.add_argument(
        'input_file',
        help='Path to input JSONL file with SQL results'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Path to output text file (default: stdout)',
        default=None
    )
    parser.add_argument(
        '--separator',
        '-s',
        help='Separator string (default: 64 equals signs)',
        default="=" * 64
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load results
    print(f"Loading results from {args.input_file}...", file=sys.stderr)
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num}: {e}", file=sys.stderr)
                continue
    
    print(f"Loaded {len(records)} records", file=sys.stderr)
    
    # Format and output
    output_lines = []
    output_lines.append("SQL QUERY RESULTS")
    output_lines.append("=" * 64)
    output_lines.append("")
    output_lines.append(f"Total Records: {len(records)}")
    output_lines.append(f"Successful: {sum(1 for r in records if r.get('conversion_success'))}")
    output_lines.append(f"Failed: {sum(1 for r in records if not r.get('conversion_success'))}")
    output_lines.append("")
    output_lines.append("=" * 64)
    output_lines.append("")
    
    for record in records:
        output_lines.append(format_sql_result(record, args.separator))
    
    # Write output
    output_text = "\n".join(output_lines)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == '__main__':
    main()

