# Training Annotation Tool

A CLI tool for annotating NLP prompts with structured JSON schema values for training an NLP model.

## Overview

This tool helps you create training data by:
1. Loading prompts from `unannotated_nlp_prompts.csv` (default workflow)
2. Iterating through the Vehicle Selection V1 JSON schema recursively
3. Prompting you to select enum values or enter data for each field
4. Saving annotated JSON to `annotated_nlp_prompts.csv` (original file is never modified)

## Workflow

The tool uses a **two-file workflow** by default to protect your source data:

- **Input**: `unannotated_nlp_prompts.csv` - Your source prompts (never modified)
- **Output**: `annotated_nlp_prompts.csv` - Completed annotations (accumulated results)
- **Temporary**: A temporary file is used during processing (automatically cleaned up)

This ensures:
- Your original unannotated prompts remain untouched
- Completed annotations are safely stored in a separate file
- You can run the tool multiple times - it automatically skips already-processed prompts (by ID)
- Incremental progress - you can add new prompts to the unannotated file and process them separately

## CSV Format

Both `unannotated_nlp_prompts.csv` and `annotated_nlp_prompts.csv` must have the following columns:
- `id`: Unique identifier for the row (required for duplicate detection)
- `prompt`: The NLP query text
- `annotated_json`: The annotated JSON (initially empty in unannotated file)
- `completion_status`: `complete` or `incomplete` (initially `incomplete`)

**unannotated_nlp_prompts.csv** example:
```csv
id,prompt,annotated_json,completion_status
1,"I need an SUV for my family of 5, under $30k",,
2,"Looking for a sedan with good gas mileage",,
```

**annotated_nlp_prompts.csv** (auto-generated):
```csv
id,prompt,annotated_json,completion_status
1,"I need an SUV for my family of 5, under $30k","{...}",complete
```

The tool preserves all columns (including `id`) when saving updates. The `id` field is critical for tracking which prompts have already been processed.

## Usage

### Default Workflow (Recommended)

Run without arguments to use the default workflow:

```bash
cd car-back-end
python training/annotation_tool.py
```

This will:
- Load prompts from `training/unannotated_nlp_prompts.csv`
- Save completed annotations to `training/annotated_nlp_prompts.csv`
- Automatically skip prompts that have already been processed (by ID)
- Never modify the original unannotated file

### With Custom Schema

```bash
python training/annotation_tool.py schemas/vehicle_selection_v1_schema.json
```

### Direct CSV Editing (Backward Compatibility)

If you want to edit a CSV file directly (old workflow):

```bash
python training/annotation_tool.py training/prompts.csv
python training/annotation_tool.py training/prompts.csv schemas/vehicle_selection_v1_schema.json
```

### Test Mode

Automatically select random enum values for testing:

```bash
python training/annotation_tool.py --test
```

## How It Works

### Default Workflow (Unannotated → Annotated)

1. **Check Processed IDs**: Reads `annotated_nlp_prompts.csv` to find already-processed prompt IDs (only counts rows marked as "complete")
2. **Load Unannotated CSV**: Loads `unannotated_nlp_prompts.csv` into a temporary file (original never modified)
3. **Filter Unprocessed**: Removes prompts that have already been processed (by ID)
4. **Open Windows**: 
   - Opens a **schema reference window** showing all enum values and types (stays open for entire session)
   - Opens a **prompt window** showing the current NLP prompt (closes after each annotation)
5. **Display Prompt**: Shows the NLP prompt text in both the prompt window and terminal
6. **Traverse Schema**: Recursively walks through the JSON schema from top to bottom
7. **Field Annotation**: For each field:
   - Shows field name and type
   - For enums: Displays numbered list of options
   - For arrays: Allows multiple selections
   - For make/model arrays: Enter comma-separated values
   - Press Enter to accept default "unspecified" values (speeds up annotation)
   - Validates input strictly (only accepts valid enum values)
8. **Save Progress**: After completing all fields:
   - Appends completed annotation to `annotated_nlp_prompts.csv`
   - Updates temporary file (for resume capability)
   - Closes prompt window and advances to next prompt
9. **Cleanup**: Automatically deletes temporary file when done. Schema reference window stays open until program termination (Ctrl+C)

### Direct CSV Workflow (Backward Compatibility)

When a CSV path is provided, the tool works directly on that file (old behavior):
1. Loads the specified CSV file
2. Processes prompts and saves directly to that file
3. No temporary file or duplicate checking

## Field Types

### Enum Fields
- Single enum: Select one option by number (1-indexed)
- Array of enum: Select multiple options (comma-separated numbers), type 'done' when finished
- All enum fields support "unspecified" option (use "unspecified" instead of null)

### Integer/Number Fields with "unspecified"
- Fields like `budget.min`, `budget.max`, `year.min`, `year.max`, `mileage.max`, `number_of_owners`
- Enter an integer/number value, or type 'unspecified'
- For `kid_count` and `pet_count`: 0 means "no kids/pets", type 'unspecified' for unspecified
- For `number_of_owners`: Enter 0 or higher, or 'unspecified'

### String Fields
- Array of strings (`make`, `model`): Enter comma-separated values (e.g., "Toyota, Honda" for multiple makes). Press Enter for default `["unspecified"]`
- String with unspecified (`trim`): Enter text value or 'unspecified'

### Boolean Fields with "unspecified"
- Fields like `wants_hatch_access`, `wants_fold_flat_seats`, `strict_max`
- Select 1 for "true", 2 for "false", 3 for "unspecified"

## Resuming Work

### Default Workflow

If you interrupt the tool (Ctrl+C), it will save your current progress to the temporary file. When you run it again:
- **Already completed prompts**: Automatically skipped (checked by ID in `annotated_nlp_prompts.csv`)
- **Partially completed prompts**: Resume from the first incomplete field (progress saved in temp file)
- **New prompts**: Processed from the beginning

### Direct CSV Workflow

If you interrupt the tool, it saves progress to the CSV file. When you run it again:
- Skip fields that are already annotated
- Resume from the first incomplete field

## Example Session

```
Loading CSV file...
Loading schema...
Found 23 fields to annotate

============================================================
Processing Row 1 (ID: 1)
============================================================

============================================================
NLP Prompt:
============================================================
I need an SUV for my family of 5, under $30k, with AWD and backup camera
============================================================

=== Field: query_text ===
Type: string
Enter value: I need an SUV for my family of 5, under $30k, with AWD and backup camera
Entered: I need an SUV for my family of 5, under $30k, with AWD and backup camera

=== Field: vehicle_type.include_body_styles ===
Type: array of enum
Select one or more options (comma-separated numbers, or 'done' when finished):
  1. sedan
  2. coupe
  3. hatchback
  4. wagon
  5. suv
  6. crossover
  7. van
  8. truck
Enter selection(s): 5
Added: suv
Enter selection(s): done
Selected: ['suv']

[... continues through all fields ...]

============================================================
Annotation Complete!
============================================================

Options:
  1. Continue to next prompt
  2. Save and exit

Enter selection (1 or 2): 1
```

## File Structure

```
training/
├── __init__.py
├── annotation_tool.py          # Main script
├── csv_manager.py              # CSV loading/updating
├── schema_traverser.py         # Recursive schema traversal
├── field_prompter.py           # User input prompting
├── unannotated_nlp_prompts.csv # Source prompts (input, never modified)
├── annotated_nlp_prompts.csv   # Completed annotations (output, auto-generated)
├── prompts.csv                  # Sample CSV file (for direct mode)
└── README.md                    # This file
```

## Validation

The tool performs strict validation:
- **Enum fields**: Only accepts values from the schema's enum list (including "unspecified")
- **Array enum fields**: Validates each selected value
- **Array string fields**: Accepts comma-separated values for make/model
- **Invalid input**: Shows error message and re-prompts
- **Required fields**: Must be filled (cannot skip)
- **Integer/number fields**: Validates numeric format or "unspecified"
- **String fields**: Validates based on field type

## Windows

The tool uses two separate windows to improve the annotation experience:

1. **Schema Reference Window**: 
   - Opens once at the start of the session
   - Displays all schema categories with their enum values and types
   - Shows whether values are strings or integers, and whether they're single values or arrays
   - Category headers are displayed in red, bold font for easy identification
   - **Stays open throughout the entire session** - only closes when the program is terminated (Ctrl+C)

2. **Prompt Window**:
   - Opens for each prompt
   - Displays the current NLP prompt text
   - Automatically closes when annotation is complete
   - Opens again with the next prompt

## Display of Completed JSON

After completing all fields for a prompt, the tool displays the completed JSON before prompting to save/quit or continue to the next prompt. This allows you to review the annotation before proceeding.

## Supported Field Types

The tool supports all field types from the Vehicle Selection V1 schema:
- **Enums**: Single selection with "unspecified" option (press Enter for default)
- **Array enums**: Multiple selections (body styles, powertrain types, features, use cases, colors, mileage qualitative)
- **Array strings**: Comma-separated values for make and model (e.g., "Toyota, Honda")
- **Integers/Numbers**: With "unspecified" option for fields like budget, year, mileage, number_of_owners (press Enter for default)
- **Strings**: Strings with "unspecified" (trim)
- **Booleans**: With "unspecified" option (wants_hatch_access, wants_fold_flat_seats, strict_max)
- **Nested objects**: Automatically traverses nested structures

## Notes

- The tool saves after each complete annotation (not incrementally during annotation)
- **Completed JSON is displayed** before prompting to save/quit or continue
- Progress is saved to the CSV file immediately when you choose "Continue" or "Save and exit"
- If interrupted, partial progress is saved for the current prompt
- The tool automatically finds the next incomplete prompt in the CSV
- All columns (including `id`) are preserved when saving updates
- Completion status uses `complete`/`incomplete` values (also accepts `true`/`false` for compatibility)
- Enum options are 1-indexed (first option is 1, not 0)
- For array fields, you can select multiple values by entering comma-separated numbers


