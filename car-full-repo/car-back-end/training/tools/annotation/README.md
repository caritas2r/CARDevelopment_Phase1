# Annotation Tools

This directory contains the core annotation tool and its supporting modules.

## Files

- **`annotation_tool.py`**: Main CLI tool for annotating NLP prompts with structured JSON schema values
- **`csv_manager.py`**: Utility class for managing CSV file operations (load, save, update, remove rows)
- **`field_prompter.py`**: Handles user input prompting for different field types (enums, arrays, integers, etc.)
- **`schema_traverser.py`**: Recursively traverses the JSON schema to generate field definitions

## Usage

Run the annotation tool from the parent directory:

```bash
cd car-back-end/training
python tools/annotation/annotation_tool.py
```

Or use the main entry point:

```bash
python -m training.tools.annotation.annotation_tool
```

## Workflow

1. Loads prompts from `data/active/unannotated_nlp_prompts.csv`
2. Iterates through the Vehicle Selection V1 JSON schema recursively
3. Prompts user to select enum values or enter data for each field
4. Saves annotated JSON to `data/active/annotated_nlp_prompts.csv`

See the main `README.md` in the training directory for detailed documentation.

