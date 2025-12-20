# Training Annotation Tool

A CLI tool for annotating NLP prompts with structured JSON schema values for training an NLP model.

## Overview

This tool helps you create training data by:
1. Loading prompts from a CSV file
2. Iterating through the Vehicle Selection V1 JSON schema recursively
3. Prompting you to select enum values or enter data for each field
4. Saving annotated JSON back to the CSV file

## CSV Format

The CSV file must have the following columns:
- `id`: Unique identifier for the row (optional but recommended)
- `prompt`: The NLP query text
- `annotated_json`: The annotated JSON (initially empty)
- `completion_status`: `complete` or `incomplete` (initially `incomplete`)

Example:
```csv
id,prompt,annotated_json,completion_status
1,"I need an SUV for my family of 5, under $30k",,incomplete
2,"Looking for a sedan with good gas mileage",,incomplete
```

The tool preserves all columns (including `id`) when saving updates.

## Usage

### Basic Usage

```bash
cd car-back-end
python training/annotation_tool.py training/prompts.csv
```

### With Custom Schema

```bash
python training/annotation_tool.py training/prompts.csv schemas/vehicle_selection_v1_schema.json
```

## How It Works

1. **Load CSV**: The tool loads your CSV file and finds the first row with `completion_status != true`
2. **Display Prompt**: Shows the NLP prompt text
3. **Traverse Schema**: Recursively walks through the JSON schema from top to bottom
4. **Field Annotation**: For each field:
   - Shows field name and type
   - For enums: Displays numbered list of options
   - For arrays: Allows multiple selections
   - Validates input strictly (only accepts valid enum values)
5. **Save Progress**: After completing all fields, asks:
   - Continue to next prompt (saves and moves on)
   - Save and exit (saves and quits)

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
- Plain string fields (`make`, `model`): Enter text value (no "unspecified" option)
- String with unspecified (`trim`): Enter text value or 'unspecified'

### Boolean Fields with "unspecified"
- Fields like `wants_hatch_access`, `wants_fold_flat_seats`, `strict_max`
- Select 1 for "true", 2 for "false", 3 for "unspecified"

## Resuming Work

If you interrupt the tool (Ctrl+C), it will save your current progress. When you run it again, it will:
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
├── annotation_tool.py      # Main script
├── csv_manager.py          # CSV loading/updating
├── schema_traverser.py     # Recursive schema traversal
├── field_prompter.py       # User input prompting
├── prompts.csv             # Sample CSV file
└── README.md               # This file
```

## Validation

The tool performs strict validation:
- **Enum fields**: Only accepts values from the schema's enum list (including "unspecified")
- **Array enum fields**: Validates each selected value
- **Invalid input**: Shows error message and re-prompts
- **Required fields**: Must be filled (cannot skip)
- **Vehicle type validation**: At least one of `include_body_styles` or `exclude_body_styles` must have actual values (not just "unspecified")
- **Integer/number fields**: Validates numeric format or "unspecified"
- **String fields**: Validates based on field type (plain string vs. string with unspecified)

## Display of Completed JSON

After completing all fields for a prompt, the tool displays the completed JSON before prompting to save/quit or continue to the next prompt. This allows you to review the annotation before proceeding.

## Supported Field Types

The tool supports all field types from the Vehicle Selection V1 schema:
- **Enums**: Single selection with "unspecified" option
- **Array enums**: Multiple selections (body styles, powertrain types, features, use cases)
- **Integers/Numbers**: With "unspecified" option for fields like budget, year, mileage, number_of_owners
- **Strings**: Plain strings (make, model) or strings with "unspecified" (trim)
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


