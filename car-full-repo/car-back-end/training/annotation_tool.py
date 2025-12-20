#!/usr/bin/env python3
"""
Training Annotation Tool
Annotates NLP prompts with structured JSON schema values
"""
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Set, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.csv_manager import CSVManager
from training.schema_traverser import SchemaTraverser
from training.field_prompter import FieldPrompter


def set_nested_value(obj: dict, path: list, value: Any):
    """
    Set a value in a nested dictionary using a path
    
    Args:
        obj: Dictionary to modify
        path: List of keys (e.g., ['vehicle_type', 'include_body_styles'])
        value: Value to set
    """
    current = obj
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def annotate_prompt(prompt_text: str, fields: list, existing_json: dict = None) -> dict:
    """
    Annotate a single prompt by iterating through all fields
    
    Args:
        prompt_text: The NLP prompt text
        fields: List of field definitions from schema traverser
        existing_json: Existing JSON to resume from (optional)
    
    Returns:
        Annotated JSON object
    """
    annotated = existing_json.copy() if existing_json else {}
    
    # Set query_text if not already set
    if 'query_text' not in annotated:
        annotated['query_text'] = prompt_text
    
    print(f"\n{'='*60}")
    print("NLP Prompt:")
    print(f"{'='*60}")
    print(prompt_text)
    print(f"{'='*60}\n")
    
    # Iterate through each field
    for idx, field in enumerate(fields, 1):
        field_name = field['name']
        field_type = field['type']
        field_path = field['path']
        nullable = field.get('nullable', False)
        required = field.get('required', False)
        
        # Skip query_text since it's auto-set from prompt
        if field_name == 'query_text':
            continue
        
        # Skip if already annotated (for resume)
        current_value = annotated
        for key in field_path:
            if key in current_value:
                current_value = current_value[key]
            else:
                current_value = None
                break
        
        if current_value is not None:
            print(f"\n=== Field: {field_name} ===")
            print(f"Already annotated: {current_value}")
            print("Skipping...")
            continue
        
        # Special message for vehicle_type arrays
        if field_name in ('vehicle_type.include_body_styles', 'vehicle_type.exclude_body_styles'):
            if 'vehicle_type' not in annotated or not annotated.get('vehicle_type'):
                print("\n" + "="*60)
                print("IMPORTANT: vehicle_type requirement")
                print("="*60)
                print("At least ONE of 'include_body_styles' or 'exclude_body_styles' must have values.")
                print("You cannot leave both arrays empty.")
                print("="*60 + "\n")
        
        # Prompt based on field type
        if field_type == 'enum':
            enum_values = field.get('enum_values', [])
            value = FieldPrompter.prompt_enum(field_name, enum_values, nullable, required)
            set_nested_value(annotated, field_path, value)
        
        elif field_type == 'array_enum':
            enum_values = field.get('enum_values', [])
            value = FieldPrompter.prompt_array_enum(field_name, enum_values, nullable, required)
            set_nested_value(annotated, field_path, value)
            
            # Validate vehicle_type immediately after both arrays are set
            if field_name in ('vehicle_type.include_body_styles', 'vehicle_type.exclude_body_styles'):
                vehicle_type = annotated.get('vehicle_type', {})
                include = vehicle_type.get('include_body_styles')
                exclude = vehicle_type.get('exclude_body_styles')
                
                # Only validate if both arrays have been set (keys exist in dict)
                if 'include_body_styles' in vehicle_type and 'exclude_body_styles' in vehicle_type:
                    # Filter out 'unspecified' from arrays for validation
                    include_filtered = [x for x in include if x != 'unspecified'] if include else []
                    exclude_filtered = [x for x in exclude if x != 'unspecified'] if exclude else []
                    
                    if len(include_filtered) == 0 and len(exclude_filtered) == 0:
                        print("\n" + "="*60)
                        print("VALIDATION ERROR: vehicle_type")
                        print("="*60)
                        print("At least one of 'include_body_styles' or 'exclude_body_styles' must have values.")
                        print("You cannot leave both arrays empty or only have 'unspecified'.")
                        print("Please select at least one actual body style (not 'unspecified') in one of the arrays.")
                        print("="*60)
                        raise ValueError("vehicle_type must have at least one non-empty array with actual body styles")
        
        elif field_type in ('integer', 'number'):
            value = FieldPrompter.prompt_number(field_name, nullable, required)
            set_nested_value(annotated, field_path, value)
        
        elif field_type == 'string':
            value = FieldPrompter.prompt_string(field_name, nullable, required)
            set_nested_value(annotated, field_path, value)
        
        elif field_type == 'boolean':
            value = FieldPrompter.prompt_boolean(field_name, nullable, required)
            set_nested_value(annotated, field_path, value)
        
        elif field_type == 'integer_or_unspecified':
            value = FieldPrompter.prompt_integer_or_unspecified(field_name, required)
            set_nested_value(annotated, field_path, value)
        
        else:
            print(f"\n=== Field: {field_name} ===")
            print(f"Warning: Unsupported field type '{field_type}'. Skipping...")
    
    # Final validation: vehicle_type must have at least one non-empty array
    if 'vehicle_type' in annotated:
        vehicle_type = annotated['vehicle_type']
        include = vehicle_type.get('include_body_styles', [])
        exclude = vehicle_type.get('exclude_body_styles', [])
        
        # Filter out 'unspecified' from arrays for validation
        include_filtered = [x for x in include if x != 'unspecified'] if include else []
        exclude_filtered = [x for x in exclude if x != 'unspecified'] if exclude else []
        
        if len(include_filtered) == 0 and len(exclude_filtered) == 0:
            print("\n" + "="*60)
            print("VALIDATION ERROR: vehicle_type")
            print("="*60)
            print("At least one of 'include_body_styles' or 'exclude_body_styles' must have values.")
            print("You cannot leave both arrays empty or only have 'unspecified'.")
            print("Please go back and add at least one body style to one of the arrays.")
            print("="*60)
            raise ValueError("vehicle_type must have at least one non-empty array")
    
    return annotated


def get_processed_ids(annotated_csv_path: Path) -> Set[str]:
    """
    Get set of IDs that have already been processed in the annotated CSV
    
    Args:
        annotated_csv_path: Path to annotated_nlp_prompts.csv
    
    Returns:
        Set of ID strings that are already in the annotated file
    """
    processed_ids = set()
    
    if not annotated_csv_path.exists():
        return processed_ids
    
    try:
        manager = CSVManager(annotated_csv_path)
        rows = manager.load()
        for row in rows:
            row_id = row.get('id', '').strip()
            if row_id:
                processed_ids.add(row_id)
    except Exception as e:
        print(f"Warning: Could not read annotated CSV to check processed IDs: {e}")
    
    return processed_ids


def filter_unprocessed_rows(csv_manager: CSVManager, processed_ids: Set[str]) -> None:
    """
    Filter out rows that have already been processed from the CSV manager
    
    Args:
        csv_manager: CSVManager instance with loaded rows
        processed_ids: Set of IDs that have already been processed
    """
    if not processed_ids:
        return
    
    # Filter out rows with IDs that are already processed
    original_count = len(csv_manager.rows)
    csv_manager.rows = [
        row for row in csv_manager.rows
        if row.get('id', '').strip() not in processed_ids
    ]
    
    removed_count = original_count - len(csv_manager.rows)
    if removed_count > 0:
        print(f"Note: Skipping {removed_count} row(s) that have already been processed.")


def append_to_annotated_csv(annotated_csv_path: Path, row_data: dict) -> None:
    """
    Append a completed row to the annotated CSV file
    
    Args:
        annotated_csv_path: Path to annotated_nlp_prompts.csv
        row_data: Dictionary with id, prompt, annotated_json, completion_status
    """
    # Ensure the file exists with headers if it's new
    if not annotated_csv_path.exists():
        with open(annotated_csv_path, 'w', encoding='utf-8', newline='') as f:
            import csv
            writer = csv.DictWriter(f, fieldnames=['id', 'prompt', 'annotated_json', 'completion_status'])
            writer.writeheader()
    
    # Append the row
    with open(annotated_csv_path, 'a', encoding='utf-8', newline='') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=['id', 'prompt', 'annotated_json', 'completion_status'])
        writer.writerow(row_data)


def process_with_temp_file(unannotated_path: Path, annotated_path: Path, schema_path: Path, test_mode: bool = False):
    """
    Process annotations using temporary file workflow (unannotated → temp → annotated)
    
    Args:
        unannotated_path: Path to unannotated_nlp_prompts.csv
        annotated_path: Path to annotated_nlp_prompts.csv
        schema_path: Path to schema JSON file
        test_mode: Whether to run in test mode
    """
    # Get IDs that have already been processed
    print("Checking for already processed prompts...")
    processed_ids = get_processed_ids(annotated_path)
    if processed_ids:
        print(f"Found {len(processed_ids)} already processed prompt(s).")
    
    # Create temporary file from unannotated CSV
    print(f"\nLoading unannotated prompts from: {unannotated_path}")
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    try:
        # Copy unannotated CSV to temp file
        shutil.copy2(unannotated_path, temp_path)
        print(f"Created temporary working file: {temp_path}")
        
        # Initialize components
        csv_manager = CSVManager(temp_path)
        schema_traverser = SchemaTraverser(schema_path)
        
        # Load CSV and filter out already processed rows
        csv_manager.load()
        filter_unprocessed_rows(csv_manager, processed_ids)
        
        if not csv_manager.rows:
            print("\nNo unprocessed prompts found. All prompts have been annotated!")
            return
        
        # Get schema fields
        print("Loading schema...")
        fields = schema_traverser.get_fields()
        print(f"Found {len(fields)} fields to annotate")
        print(f"\nFound {len(csv_manager.rows)} unprocessed prompt(s) to annotate.")
        
        # Process prompts (reuse the main processing loop)
        process_prompts(csv_manager, fields, test_mode, annotated_path, use_temp_workflow=True)
        
        print(f"\n{'='*60}")
        print("Session Complete!")
        print(f"{'='*60}")
        print(f"All completed annotations have been saved to: {annotated_path}")
        print(f"The original unannotated file was not modified: {unannotated_path}")
        print(f"Temporary file will be cleaned up: {temp_path}")
    
    finally:
        # Clean up temporary file
        try:
            if temp_path.exists():
                temp_path.unlink()
                print(f"\nCleaned up temporary file.")
        except Exception as e:
            print(f"\nWarning: Could not delete temporary file {temp_path}: {e}")


def process_prompts(csv_manager: CSVManager, fields: list, test_mode: bool, 
                    annotated_path: Optional[Path] = None, use_temp_workflow: bool = False):
    """
    Main processing loop for annotating prompts
    
    Args:
        csv_manager: CSVManager instance with loaded rows
        fields: List of field definitions from schema
        test_mode: Whether to run in test mode
        annotated_path: Path to annotated CSV (only used in temp workflow)
        use_temp_workflow: If True, append to annotated_path instead of saving to csv_manager's file
    """
    while True:
        result = csv_manager.find_next_incomplete()
        
        if result is None:
            print("\nAll prompts have been completed!")
            break
        
        row_index, row = result
        prompt_text = row.get('prompt', '').strip()
        row_id = row.get('id', '').strip() or str(row_index + 1)
        
        if not prompt_text:
            print(f"\nWarning: Row {row_index + 1} (ID: {row_id}) has empty prompt. Skipping.")
            continue
        
        # Get existing JSON if any (for resume)
        existing_json = csv_manager.get_annotated_json(row_index)
        
        # Display row ID
        print(f"\n{'='*60}")
        print(f"Processing Row {row_index + 1} (ID: {row_id})")
        print(f"{'='*60}")
        
        # Annotate the prompt
        try:
            annotated_json = annotate_prompt(prompt_text, fields, existing_json)
            
            # Show completion
            print(f"\n{'='*60}")
            print("Annotation Complete!")
            print(f"{'='*60}")
            
            # Display the completed JSON
            print("\nCompleted JSON:")
            print("-" * 60)
            print(json.dumps(annotated_json, indent=2, ensure_ascii=False))
            print("-" * 60)
            
            # Handle saving based on workflow type
            if use_temp_workflow:
                # Prepare row data for annotated CSV
                row_data = {
                    'id': row_id,
                    'prompt': prompt_text,
                    'annotated_json': json.dumps(annotated_json, indent=2),
                    'completion_status': 'complete'
                }
                
                if test_mode:
                    append_to_annotated_csv(annotated_path, row_data)
                    csv_manager.update_row(row_index, annotated_json, completed=True)
                    csv_manager.save()
                    print("\n[TEST MODE] Saved to annotated CSV. Moving to next prompt...\n")
                else:
                    while True:
                        choice = input("\nOptions:\n  1. Continue to next prompt\n  2. Save and exit\n\nEnter selection (1 or 2): ").strip()
                        
                        if choice == '1':
                            append_to_annotated_csv(annotated_path, row_data)
                            csv_manager.update_row(row_index, annotated_json, completed=True)
                            csv_manager.save()
                            print("\nSaved to annotated CSV. Moving to next prompt...\n")
                            break
                        
                        elif choice == '2':
                            append_to_annotated_csv(annotated_path, row_data)
                            csv_manager.update_row(row_index, annotated_json, completed=True)
                            csv_manager.save()
                            print("\nSaved to annotated CSV. Exiting...")
                            return
                        
                        else:
                            print("Invalid selection. Please enter 1 or 2.")
            else:
                # Direct workflow: save to the CSV file directly
                if test_mode:
                    csv_manager.update_row(row_index, annotated_json, completed=True)
                    csv_manager.save()
                    print("\n[TEST MODE] Saved. Moving to next prompt...\n")
                else:
                    while True:
                        choice = input("\nOptions:\n  1. Continue to next prompt\n  2. Save and exit\n\nEnter selection (1 or 2): ").strip()
                        
                        if choice == '1':
                            csv_manager.update_row(row_index, annotated_json, completed=True)
                            csv_manager.save()
                            print("\nSaved. Moving to next prompt...\n")
                            break
                        
                        elif choice == '2':
                            csv_manager.update_row(row_index, annotated_json, completed=True)
                            csv_manager.save()
                            print("\nSaved. Exiting...")
                            return
                        
                        else:
                            print("Invalid selection. Please enter 1 or 2.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            # Save current progress
            if 'annotated_json' in locals():
                if use_temp_workflow:
                    # In temp workflow, save to temp file only (not to annotated CSV)
                    csv_manager.update_row(row_index, annotated_json, completed=False)
                    csv_manager.save()
                    print("Progress saved to temporary file.")
                else:
                    csv_manager.update_row(row_index, annotated_json, completed=False)
                    csv_manager.save()
                    print("Progress saved.")
            sys.exit(0)
        
        except EOFError:
            print("\n\nError: No input available (non-interactive mode).")
            print("This tool requires interactive input. Please run it in a terminal.")
            print(f"\nSkipping row {row_index + 1} (ID: {row_id})...")
            continue
        
        except Exception as e:
            print(f"\nError during annotation: {e}")
            import traceback
            traceback.print_exc()
            print(f"\nSkipping row {row_index + 1} (ID: {row_id})...")
            continue


def main():
    """Main entry point"""
    # Check for test mode flag
    test_mode = '--test' in sys.argv or '--auto' in sys.argv
    if test_mode:
        sys.argv = [arg for arg in sys.argv if arg not in ('--test', '--auto')]
        FieldPrompter.test_mode = True
        print("TEST MODE ENABLED: Random enum selections will be made automatically")
    
    # Check for direct mode flag (backward compatibility)
    direct_mode = '--direct' in sys.argv
    if direct_mode:
        sys.argv = [arg for arg in sys.argv if arg != '--direct']
    
    # Determine workflow:
    # - If no CSV provided: use new workflow (unannotated → annotated) [DEFAULT]
    # - If CSV provided: use old workflow (direct CSV editing) [BACKWARD COMPATIBLE]
    if len(sys.argv) < 2:
        # New workflow: use unannotated_nlp_prompts.csv → annotated_nlp_prompts.csv
        training_dir = Path(__file__).parent
        unannotated_path = training_dir / 'unannotated_nlp_prompts.csv'
        annotated_path = training_dir / 'annotated_nlp_prompts.csv'
        schema_path = Path(__file__).parent.parent / 'schemas' / 'vehicle_selection_v1_schema.json'
        
        # Validate paths
        if not unannotated_path.exists():
            print(f"Error: Unannotated CSV file not found: {unannotated_path}")
            print("\nPlease create unannotated_nlp_prompts.csv in the training directory, or")
            print("use the direct mode: python annotation_tool.py <csv_file>")
            sys.exit(1)
        
        if not schema_path.exists():
            print(f"Error: Schema file not found: {schema_path}")
            sys.exit(1)
        
        # Use new workflow
        process_with_temp_file(unannotated_path, annotated_path, schema_path, test_mode)
        return
    
    # Old workflow: direct CSV editing (backward compatibility)
    csv_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else Path(__file__).parent.parent / 'schemas' / 'vehicle_selection_v1_schema.json'
    
    # Validate paths
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}")
        sys.exit(1)
    
    # Initialize components
    csv_manager = CSVManager(csv_path)
    schema_traverser = SchemaTraverser(schema_path)
    
    # Load CSV and find next incomplete row
    print("Loading CSV file...")
    csv_manager.load()
    
    # Get schema fields
    print("Loading schema...")
    fields = schema_traverser.get_fields()
    print(f"Found {len(fields)} fields to annotate")
    
    # Process prompts using direct workflow
    process_prompts(csv_manager, fields, test_mode, use_temp_workflow=False)


if __name__ == '__main__':
    main()

