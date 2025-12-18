#!/usr/bin/env python3
"""
Training Annotation Tool
Annotates NLP prompts with structured JSON schema values
"""
import sys
import json
from pathlib import Path
from typing import Any

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


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python annotation_tool.py <csv_file> [schema_file] [--test]")
        print("\nExample:")
        print("  python annotation_tool.py prompts.csv")
        print("  python annotation_tool.py prompts.csv schemas/vehicle_selection_v1_schema.json")
        print("  python annotation_tool.py prompts.csv --test  # Test mode with random enum selections")
        sys.exit(1)
    
    # Check for test mode flag
    test_mode = '--test' in sys.argv or '--auto' in sys.argv
    if test_mode:
        sys.argv = [arg for arg in sys.argv if arg not in ('--test', '--auto')]
        FieldPrompter.test_mode = True
        print("TEST MODE ENABLED: Random enum selections will be made automatically")
    
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
    
    # Process prompts
    while True:
        result = csv_manager.find_next_incomplete()
        
        if result is None:
            print("\nAll prompts have been completed!")
            break
        
        row_index, row = result
        prompt_text = row.get('prompt', '').strip()
        row_id = row.get('id', str(row_index + 1))
        
        if not prompt_text:
            print(f"\nWarning: Row {row_index + 1} (ID: {row_id}) has empty prompt. Marking as completed.")
            csv_manager.update_row(row_index, {}, completed=True)
            csv_manager.save()
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
            
            # Ask to continue or save and exit (skip in test mode)
            if FieldPrompter.test_mode:
                # In test mode, automatically continue to next prompt
                csv_manager.update_row(row_index, annotated_json, completed=True)
                csv_manager.save()
                print("\n[TEST MODE] Saved. Moving to next prompt...\n")
            else:
                while True:
                    choice = input("\nOptions:\n  1. Continue to next prompt\n  2. Save and exit\n\nEnter selection (1 or 2): ").strip()
                    
                    if choice == '1':
                        # Update CSV and continue
                        csv_manager.update_row(row_index, annotated_json, completed=True)
                        csv_manager.save()
                        print("\nSaved. Moving to next prompt...\n")
                        break
                    
                    elif choice == '2':
                        # Update CSV and exit
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
                csv_manager.update_row(row_index, annotated_json, completed=False)
                csv_manager.save()
                print("Progress saved.")
            sys.exit(0)
        
        except EOFError:
            print("\n\nError: No input available (non-interactive mode).")
            print("This tool requires interactive input. Please run it in a terminal.")
            print(f"\nSkipping row {row_index + 1} (ID: {row_id})...")
            # Mark as incomplete and move on to prevent infinite loop
            csv_manager.update_row(row_index, {}, completed=False)
            csv_manager.save()
            continue
        
        except Exception as e:
            print(f"\nError during annotation: {e}")
            import traceback
            traceback.print_exc()
            print(f"\nSkipping row {row_index + 1} (ID: {row_id})...")
            # Mark as incomplete to prevent infinite loop on same error
            try:
                partial_json = annotated_json if 'annotated_json' in locals() else {}
                csv_manager.update_row(row_index, partial_json, completed=False)
                csv_manager.save()
            except:
                pass  # If we can't save, at least continue
            continue


if __name__ == '__main__':
    main()

