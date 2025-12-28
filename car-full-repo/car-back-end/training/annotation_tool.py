#!/usr/bin/env python3
"""
Training Annotation Tool
Annotates NLP prompts with structured JSON schema values
"""
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Set, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.csv_manager import CSVManager
from training.schema_traverser import SchemaTraverser
from training.field_prompter import FieldPrompter

# Try to import tkinter for prompt window (optional - will work without it)
try:
    import tkinter as tk
    from tkinter import scrolledtext
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class PromptWindow:
    """
    Manages a separate window to display the NLP prompt text.
    Window automatically closes when annotation is complete.
    Uses subprocess to avoid threading issues with tkinter.
    """
    def __init__(self):
        self.process = None
        self.temp_file_path = None
    
    def _create_window_script(self, prompt_text: str) -> str:
        """Create a temporary Python script to show the window"""
        import tempfile
        import base64
        
        # Encode prompt text to avoid escaping issues
        prompt_encoded = base64.b64encode(prompt_text.encode('utf-8')).decode('ascii')
        
        # Get the training directory path for the close signal file
        training_dir = Path(__file__).parent
        
        script_content = f'''#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext
import base64
import sys
import os
from pathlib import Path

# Decode prompt text
prompt_text = base64.b64decode("{prompt_encoded}").decode('utf-8')

# Close signal file path
close_file = Path(r"{training_dir}") / ".prompt_window_close"

# Create window
root = tk.Tk()
root.title("NLP Prompt")
root.geometry("800x400")
root.resizable(True, True)

# Center window
root.update_idletasks()
width = 800
height = 400
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{{width}}x{{height}}+{{x}}+{{y}}')

# Create text widget
text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

text_widget = scrolledtext.ScrolledText(
    text_frame,
    wrap=tk.WORD,
    font=("Arial", 12),
    bg="white",
    fg="black",
    padx=10,
    pady=10
)
text_widget.pack(fill=tk.BOTH, expand=True)

# Insert prompt text
text_widget.insert("1.0", prompt_text)
text_widget.config(state=tk.DISABLED)

# Check for close signal file periodically
def check_close():
    if close_file.exists():
        try:
            close_file.unlink()
        except:
            pass
        root.quit()
        root.destroy()
        return
    root.after(100, check_close)

root.after(100, check_close)
root.mainloop()
'''
        
        # Create temporary script file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        temp_file.write(script_content)
        temp_file.close()
        
        return temp_file.name
    
    def show(self, prompt_text: str):
        """Show the prompt in a new window (non-blocking)"""
        if not TKINTER_AVAILABLE:
            return
        
        # Close existing window if any
        self.close()
        
        try:
            # Create script file
            script_path = self._create_window_script(prompt_text)
            self.temp_file_path = script_path
            
            # Launch in subprocess
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
        except Exception as e:
            print(f"Warning: Could not display prompt window: {e}")
            # Clean up temp file on error
            if self.temp_file_path and Path(self.temp_file_path).exists():
                try:
                    Path(self.temp_file_path).unlink()
                except:
                    pass
                self.temp_file_path = None
    
    def close(self):
        """Close the current prompt window"""
        if not TKINTER_AVAILABLE:
            return
        
        # Signal window to close by creating a marker file
        try:
            script_dir = Path(__file__).parent
            close_file = script_dir / ".prompt_window_close"
            close_file.touch()
            
            # Wait a moment for window to close
            import time
            time.sleep(0.2)
            
            # Clean up marker file
            if close_file.exists():
                close_file.unlink()
        except:
            pass
        
        # Terminate process if still running
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        
        # Clean up temp script file
        if self.temp_file_path is not None:
            try:
                if Path(self.temp_file_path).exists():
                    Path(self.temp_file_path).unlink()
            except:
                pass
            self.temp_file_path = None


class SchemaReferenceWindow:
    """
    Manages a separate window to display schema reference information.
    Shows all categories and their enum values with type information.
    Uses subprocess to avoid threading issues with tkinter.
    """
    def __init__(self):
        self.process = None
        self.temp_file_path = None
    
    def _create_reference_script(self, fields_info: list) -> str:
        """Create a temporary Python script to show the schema reference window"""
        import tempfile
        import base64
        
        # Encode fields info
        fields_info_json = json.dumps(fields_info, ensure_ascii=False)
        fields_info_encoded = base64.b64encode(fields_info_json.encode('utf-8')).decode('ascii')
        
        # Get the training directory path
        training_dir = Path(__file__).parent
        training_dir_str = str(training_dir)
        
        script_content = f'''#!/usr/bin/env python3
import tkinter as tk
from tkinter import scrolledtext
import base64
import json
import sys
from pathlib import Path
from collections import defaultdict

# Decode fields info
fields_info_json = base64.b64decode("{fields_info_encoded}").decode("utf-8")
fields_info = json.loads(fields_info_json)

# Close signal file path
close_file = Path(r"{training_dir_str}") / ".schema_reference_close"

# Organize fields by category, preserving order they appear in schema
categories = defaultdict(list)
category_order = []  # Track order of first appearance
for field in fields_info:
    path = field.get('path', [])
    field_type = field.get('type', '')
    enum_values = field.get('enum_values', [])
    nullable = field.get('nullable', False)
    required = field.get('required', False)
    
    if not path:
        continue
    
    # Use first part of path as category, or "root" for top-level
    if len(path) == 1:
        category = "root"
    else:
        category = path[0]
    
    # Track order of first appearance
    if category not in category_order:
        category_order.append(category)
    
    categories[category].append({{
        'name': field.get('name', '.'.join(path)),
        'path': path,
        'type': field_type,
        'enum_values': enum_values,
        'nullable': nullable,
        'required': required
    }})

# Create window
root = tk.Tk()
root.title("Schema Reference - Enum Values")
root.geometry("1000x700")
root.resizable(True, True)

# Center window
root.update_idletasks()
width = 1000
height = 700
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{{width}}x{{height}}+{{x}}+{{y}}')

# Create main frame with scrollbar
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

text_widget = scrolledtext.ScrolledText(
    main_frame,
    wrap=tk.WORD,
    font=("Consolas", 10),
    bg="#1e1e1e",
    fg="#d4d4d4",
    padx=10,
    pady=10
)
text_widget.pack(fill=tk.BOTH, expand=True)

# Configure tag for category headers (red, larger font, bold)
text_widget.tag_config("category_header", foreground="#ff4444", font=("Consolas", 16, "bold"))

# Insert header
text_widget.insert("end", "=" * 80 + "\\n")
text_widget.insert("end", "SCHEMA REFERENCE - ENUM VALUES AND TYPES\\n")
text_widget.insert("end", "=" * 80 + "\\n\\n")

# Use categories in order they appear in schema (not alphabetized)
for category in category_order:
    # Insert category header separator
    text_widget.insert("end", "=" * 80 + "\\n")
    
    # Insert category name with red tag
    start_pos = text_widget.index("end")  # Position before inserting
    text_widget.insert("end", f"CATEGORY: {{category.upper()}}\\n")
    end_pos = text_widget.index("end-1c")  # Position at end of line (before newline)
    # Apply red tag to category name line (excluding the newline)
    text_widget.tag_add("category_header", start_pos, end_pos)
    
    # Insert category header separator
    text_widget.insert("end", "=" * 80 + "\\n\\n")
    
    fields = categories[category]
    # Sort fields by name
    fields.sort(key=lambda x: x['name'])
    
    for field in fields:
        field_name = field['name']
        field_type = field['type']
        enum_values = field['enum_values']
        path_str = '.'.join(field['path'])
        
        text_widget.insert("end", f"Field: {{field_name}}\\n")
        text_widget.insert("end", f"  Path: {{path_str}}\\n")
        text_widget.insert("end", f"  Type: {{field_type}}\\n")
        
        if enum_values:
            # Determine value type
            has_strings = any(isinstance(v, str) for v in enum_values)
            has_integers = any(isinstance(v, int) for v in enum_values)
            
            if field_type == 'array_enum':
                text_widget.insert("end", f"  Format: ARRAY of values (use JSON array: [value1, value2])\\n")
            else:
                text_widget.insert("end", f"  Format: SINGLE value\\n")
            
            if has_strings and has_integers:
                value_type = "STRING or INTEGER"
            elif has_strings:
                value_type = "STRING"
            elif has_integers:
                value_type = "INTEGER"
            else:
                value_type = "MIXED"
            
            text_widget.insert("end", f"  Value Type: {{value_type}}\\n")
            text_widget.insert("end", f"  Valid Values:\\n")
            
            for i, val in enumerate(enum_values, 1):
                val_type = "STRING" if isinstance(val, str) else "INTEGER"
                text_widget.insert("end", f"    {{i:2d}}. {{val}} ({{val_type}})\\n")
        else:
            if field_type == 'string':
                text_widget.insert("end", f"  Format: STRING (free text)\\n")
            elif field_type in ('integer', 'number'):
                text_widget.insert("end", f"  Format: NUMBER (integer or decimal)\\n")
            elif field_type == 'boolean':
                text_widget.insert("end", f"  Format: BOOLEAN (true/false)\\n")
            elif field_type == 'integer_or_unspecified':
                text_widget.insert("end", f"  Format: INTEGER or STRING 'unspecified'\\n")
            else:
                text_widget.insert("end", f"  Format: {{field_type}}\\n")
        
        text_widget.insert("end", "\\n")
    
    text_widget.insert("end", "\\n")

text_widget.config(state=tk.DISABLED)  # Make read-only

# Check for close signal file periodically
def check_close():
    if close_file.exists():
        try:
            close_file.unlink()
        except:
            pass
        root.quit()
        root.destroy()
        return
    root.after(100, check_close)

root.after(100, check_close)
root.mainloop()
'''
        
        # Create temporary script file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
        temp_file.write(script_content)
        temp_file.close()
        
        return temp_file.name
    
    def show(self, fields_info: list):
        """Show the schema reference window (non-blocking)"""
        if not TKINTER_AVAILABLE:
            return
        
        # Close existing window if any
        self.close()
        
        try:
            # Create script file
            script_path = self._create_reference_script(fields_info)
            self.temp_file_path = script_path
            
            # Launch in subprocess - capture stderr to see errors
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=0  # Don't use CREATE_NO_WINDOW to see errors
            )
            
            # Check for immediate errors
            import time
            time.sleep(0.2)
            if self.process.poll() is not None:
                # Process exited immediately - there was an error
                stderr = self.process.stderr.read() if self.process.stderr else b''
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                print(f"Error: Schema reference script crashed immediately:")
                print(f"  {error_msg}")
                print(f"  Script path: {script_path}")
        except Exception as e:
            print(f"Warning: Could not display schema reference window: {e}")
            if self.temp_file_path and Path(self.temp_file_path).exists():
                try:
                    Path(self.temp_file_path).unlink()
                except:
                    pass
                self.temp_file_path = None
    
    def close(self):
        """Close the current schema reference window"""
        if not TKINTER_AVAILABLE:
            return
        
        # Signal window to close by creating a marker file
        try:
            script_dir = Path(__file__).parent
            close_file = script_dir / ".schema_reference_close"
            close_file.touch()
            
            # Wait a moment for window to close
            import time
            time.sleep(0.2)
            
            # Clean up marker file
            if close_file.exists():
                close_file.unlink()
        except:
            pass
        
        # Terminate process if still running
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        
        # Clean up temp script file
        if self.temp_file_path is not None:
            try:
                if Path(self.temp_file_path).exists():
                    Path(self.temp_file_path).unlink()
            except:
                pass
            self.temp_file_path = None


# Global window instances
_prompt_window = PromptWindow() if TKINTER_AVAILABLE else None
_schema_reference_window = SchemaReferenceWindow() if TKINTER_AVAILABLE else None


def set_nested_value(obj: dict, path: list, value: Any, field_type: str = None):
    """
    Set a value in a nested dictionary using a path
    
    Args:
        obj: Dictionary to modify
        path: List of keys (e.g., ['vehicle_type', 'include_body_styles'])
        value: Value to set
        field_type: Optional field type hint (for enum conversion)
    """
    # Convert enum values to strings if they're integers
    # This ensures consistency - all enum values in JSON are strings
    if field_type in ('enum', 'array_enum'):
        if isinstance(value, int):
            # Enum value is an integer, convert to string
            value = str(value)
        elif isinstance(value, list):
            # For array enums, convert any integer values to strings
            value = [str(v) if isinstance(v, int) else v for v in value]
    
    current = obj
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def get_default_value_for_field(field: dict) -> Any:
    """
    Get the default "unspecified" value for a field based on its type
    
    Args:
        field: Field definition from schema traverser
    
    Returns:
        Default value (usually "unspecified" or ["unspecified"])
    """
    field_type = field.get('type', '')
    field_name = field.get('name', '')
    
    # Check if field supports "unspecified"
    enum_values = field.get('enum_values', [])
    has_unspecified = "unspecified" in enum_values
    
    if field_type == 'enum':
        return "unspecified" if has_unspecified else None
    elif field_type == 'array_enum':
        return ["unspecified"] if has_unspecified else []
    elif field_type in ('integer', 'number'):
        # Check if field supports unspecified
        is_budget_year_radius = any(x in field_name for x in ['budget.min', 'budget.max', 'year.min', 'year.max', 'radius_miles', 'mileage.max', 'number_of_owners', 'currency', 'seating_capacity', 'kid_count', 'pet_count'])
        return "unspecified" if is_budget_year_radius else None
    elif field_type == 'string':
        return "unspecified"
    elif field_type == 'array_string' or (field_type == 'array' and (field_name == 'make' or field_name == 'model')):
        # Make and model are now arrays - return array with unspecified
        return ["unspecified"]
    elif field_type == 'boolean':
        # Check if boolean supports unspecified
        supports_unspecified = any(x in field_name for x in ['wants_hatch_access', 'wants_fold_flat_seats', 'strict_max'])
        return "unspecified" if supports_unspecified else None
    elif field_type == 'integer_or_unspecified':
        return "unspecified"
    
    return None


def initialize_json_with_defaults(fields: list, prompt_text: str) -> dict:
    """
    Initialize a JSON object with default "unspecified" values for all fields
    
    Args:
        fields: List of field definitions from schema traverser
        prompt_text: The NLP prompt text
    
    Returns:
        Initialized JSON object with defaults
    """
    annotated = {'query_text': prompt_text}
    
    for field in fields:
        field_name = field.get('name', '')
        field_path = field.get('path', [])
        field_type = field.get('type', '')
        
        # Skip query_text since it's already set
        if field_name == 'query_text':
            continue
        
        # Get default value
        default_value = get_default_value_for_field(field)
        
        if default_value is not None:
            # Pass field_type for enum conversion
            set_nested_value(annotated, field_path, default_value, field_type=field_type)
    
    return annotated


def annotate_prompt(prompt_text: str, fields: list, existing_json: dict = None) -> dict:
    """
    Annotate a single prompt by iterating through all fields.
    Supports dual-mode: JSON editor window OR step-by-step prompts.
    Whichever completes first is used.
    
    Args:
        prompt_text: The NLP prompt text
        fields: List of field definitions from schema traverser
        existing_json: Existing JSON to resume from (optional)
    
    Returns:
        Annotated JSON object
    """
    # Initialize with defaults if no existing JSON
    if existing_json:
        annotated = existing_json.copy()
        # Ensure query_text is set
        if 'query_text' not in annotated:
            annotated['query_text'] = prompt_text
    else:
        # Initialize with "unspecified" defaults for all fields
        annotated = initialize_json_with_defaults(fields, prompt_text)
    
    # Show prompt in separate window
    if _prompt_window is not None:
        _prompt_window.show(prompt_text)
    
    print(f"\n{'='*60}")
    print("NLP Prompt:")
    print(f"{'='*60}")
    print(prompt_text)
    print(f"{'='*60}\n")
    
    # Iterate through each field (step-by-step mode)
    for idx, field in enumerate(fields, 1):
        field_name = field['name']
        field_type = field['type']
        field_path = field['path']
        nullable = field.get('nullable', False)
        required = field.get('required', False)
        
        # Skip query_text since it's auto-set from prompt
        if field_name == 'query_text':
            continue
        
        # Only skip if resuming from existing annotation (not just defaults)
        # For new annotations, always prompt even if field has default "unspecified"
        if existing_json is not None:
            # Resume mode: skip fields that were already explicitly set
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
        
        # Prompt based on field type
        if field_type == 'enum':
            enum_values = field.get('enum_values', [])
            value = FieldPrompter.prompt_enum(field_name, enum_values, nullable, required)
            set_nested_value(annotated, field_path, value, field_type='enum')
        
        elif field_type == 'array_enum':
            enum_values = field.get('enum_values', [])
            value = FieldPrompter.prompt_array_enum(field_name, enum_values, nullable, required)
            set_nested_value(annotated, field_path, value, field_type='array_enum')
        
        elif field_type == 'array_string' or (field_type == 'array' and (field_name == 'make' or field_name == 'model')):
            # For make and model arrays, prompt for comma-separated values
            value = FieldPrompter.prompt_array_string(field_name, nullable, required)
            if value is None:
                value = ["unspecified"]
            set_nested_value(annotated, field_path, value, field_type='array_string')
        
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
    
    # Close prompt window
    if _prompt_window is not None:
        _prompt_window.close()
    
    # Note: Schema reference window stays open throughout the session
    # It will only close when the program is terminated (e.g., Ctrl+C)
    
    return annotated


def get_processed_ids(annotated_csv_path: Path) -> Set[str]:
    """
    Get set of IDs that have already been processed (completed) in the annotated CSV
    
    Args:
        annotated_csv_path: Path to annotated_nlp_prompts.csv
    
    Returns:
        Set of ID strings that are marked as complete in the annotated file
    """
    processed_ids = set()
    
    if not annotated_csv_path.exists():
        return processed_ids
    
    try:
        manager = CSVManager(annotated_csv_path)
        rows = manager.load()
        # Only count rows that are actually marked as complete
        completed_statuses = ('true', '1', 'yes', 'completed', 'complete')
        for row in rows:
            row_id = row.get('id', '').strip()
            completion_status = row.get('completion_status', '').strip().lower()
            # Only add IDs that are marked as complete
            if row_id and completion_status in completed_statuses:
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
        # Schema reference window will be opened once inside process_prompts
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
    # Show schema reference window once at the start of the session (if not already shown)
    if _schema_reference_window is not None:
        # Only show if window is not already open (check if process is running)
        if _schema_reference_window.process is None or _schema_reference_window.process.poll() is not None:
            print("Opening schema reference window (will stay open for the session)...")
            _schema_reference_window.show(fields)
    
    while True:
        result = csv_manager.find_next_incomplete()
        
        if result is None:
            # Close prompt window if still open
            if _prompt_window is not None:
                _prompt_window.close()
            # Note: Schema reference window stays open even after all prompts are completed
            # It will only close when the program is terminated (e.g., Ctrl+C)
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
            
            # Close prompt window before showing completion
            if _prompt_window is not None:
                _prompt_window.close()
                # Give window time to close
                import time
                time.sleep(0.2)
            
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
                            # Close prompt window
                            if _prompt_window is not None:
                                _prompt_window.close()
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
                            # Close prompt window
                            if _prompt_window is not None:
                                _prompt_window.close()
                            print("\nSaved. Exiting...")
                            return
                        
                        else:
                            print("Invalid selection. Please enter 1 or 2.")
        
        except KeyboardInterrupt:
            # Close prompt window if still open
            if _prompt_window is not None:
                _prompt_window.close()
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

