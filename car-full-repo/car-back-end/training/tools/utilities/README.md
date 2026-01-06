# Utility Scripts

This directory contains utility scripts for data management and analysis.

## Files

- **`import_prompts.py`**: Import prompts from text files into CSV format
- **`reset_csv.py`**: Reset annotated CSV by clearing all annotations and setting status to incomplete
- **`analyze_csv.py`**: Quick analysis script for CSV files (row counts, prompt lengths, etc.)
- **`prompt_viewer.py`**: View prompts from CSV or JSONL files

## Usage

### Import prompts:
```bash
python tools/utilities/import_prompts.py --input prompts.txt --output data/active/unannotated_nlp_prompts.csv
```

### Reset annotations:
```bash
python tools/utilities/reset_csv.py data/active/annotated_nlp_prompts.csv
```

### Analyze CSV:
```bash
python tools/utilities/analyze_csv.py
```

### View prompts:
```bash
python tools/utilities/prompt_viewer.py data/active/annotated_nlp_prompts.csv
```

