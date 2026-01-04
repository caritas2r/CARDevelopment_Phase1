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

---

# Training Data Preparation

Once you have annotated your prompts, you need to prepare the data for model training. This section covers converting the CSV to JSONL format and splitting it into train/validation/test sets.

## Overview

The training data preparation pipeline consists of two steps:

1. **Convert CSV to JSONL**: Convert `annotated_nlp_prompts.csv` to `jsonl_ready_prompts.jsonl` format
2. **Split Dataset**: Split the JSONL file into training, validation, and test sets

## Step 1: Convert CSV to JSONL

The `csv_to_jsonl.py` script converts the annotated CSV file into JSONL format suitable for training frameworks like axolotl.

### Usage

```bash
cd car-back-end/training
python csv_to_jsonl.py
```

This will:
- Read `annotated_nlp_prompts.csv`
- Convert each completed row to JSONL format: `{"prompt": "...", "completion": "{...full schema json...}"}`
- Output `jsonl_ready_prompts.jsonl`

### Output Format

Each line in the JSONL file follows this structure:
```json
{"prompt": "I'm looking for an SUV under $30k", "completion": "{\"make\": [...], \"vehicle_type\": {...}, ...}"}
```

Only rows marked as `complete` are included in the output.

## Step 2: Split Dataset

The `split_jsonl.py` script randomly splits the JSONL file into training, validation, and test sets.

### Default Split

The default configuration splits the dataset as follows:
- **Training set**: 180 rows → `train.jsonl`
- **Validation set**: 20 rows → `validation.jsonl`
- **Test set**: 20 rows → `test.jsonl`
- **Total**: 220 rows

### Usage

```bash
cd car-back-end/training
python split_jsonl.py
```

This will:
- Read `jsonl_ready_prompts.jsonl`
- Randomly shuffle the data
- Split into train/validation/test sets
- Output three JSONL files

### Custom Split Sizes

You can customize the split sizes:

```bash
python split_jsonl.py --train-size 150 --val-size 35 --test-size 35
```

## Reproducibility with Random Seeds

### Seed 42 for Reproducibility

The `split_jsonl.py` script uses **random seed 42** by default to ensure reproducible results. This means:

- **Same seed = Same split**: Running the script multiple times with the same seed will always produce the same train/validation/test split
- **Reproducible experiments**: You can share your exact dataset splits with others, enabling reproducible research and consistent model comparisons
- **Version control friendly**: The same seed ensures your dataset splits remain consistent across different runs and environments

### Why Seed 42?

Seed 42 is a common default in machine learning (popularized by "The Hitchhiker's Guide to the Galaxy"). It provides a good balance between randomness and reproducibility. Using a fixed seed ensures:

- Consistent dataset splits across team members
- Reproducible model training results
- Easier debugging and comparison of different model configurations

### Adjusting the Seed for Flexibility

If you need different dataset splits (for example, to test model robustness or explore different data distributions), you can change the random seed:

```bash
# Use a different seed
python split_jsonl.py --seed 123

# Use another seed for a different split
python split_jsonl.py --seed 999

# Use current timestamp for a truly random split each time
python split_jsonl.py --seed $(date +%s)  # Linux/Mac
python split_jsonl.py --seed $((Get-Date).Ticks)  # PowerShell (Windows)
```

### When to Change the Seed

Consider changing the seed when:

1. **Testing model robustness**: Train on multiple different splits to ensure your model performs consistently
2. **Cross-validation**: Create multiple folds for k-fold cross-validation
3. **Data exploration**: Explore how different data distributions affect model performance
4. **A/B testing**: Compare training strategies with different data splits

### Maintaining Reproducibility

**Important**: For production training and experiments, always use seed 42 (or document your seed choice) to ensure:

- Results can be reproduced by others
- Model performance comparisons are valid
- Your training pipeline is deterministic

## Complete Training Data Pipeline

Here's the complete workflow:

```bash
cd car-back-end/training

# Step 1: Convert CSV to JSONL
python csv_to_jsonl.py

# Step 2: Split into train/validation/test (using seed 42)
python split_jsonl.py

# Result: Three files ready for training
# - train.jsonl (180 rows)
# - validation.jsonl (20 rows)
# - test.jsonl (20 rows)
```

## File Structure

After running the preparation scripts, your training directory will contain:

```
training/
├── annotated_nlp_prompts.csv      # Original annotated CSV (never modified)
├── jsonl_ready_prompts.jsonl      # Converted JSONL format (220 rows)
├── train.jsonl                    # Training set (180 rows)
├── validation.jsonl               # Validation set (20 rows)
└── test.jsonl                     # Test set (20 rows)
```

## Scripts Reference

- `csv_to_jsonl.py`: Converts CSV to JSONL format
  - Options: `--csv`, `--output`
- `split_jsonl.py`: Splits JSONL into train/val/test sets
  - Options: `--input`, `--train-size`, `--val-size`, `--test-size`, `--seed`, `--output-dir`

For detailed usage information, run any script with `--help`:
```bash
python csv_to_jsonl.py --help
python split_jsonl.py --help
```


