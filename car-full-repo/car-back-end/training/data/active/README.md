# Active Data Files

This directory contains the current working datasets for annotation and training.

## Files

### Annotation Data
- **`unannotated_nlp_prompts.csv`**: Source prompts waiting to be annotated (never modified by annotation tool)
- **`annotated_nlp_prompts.csv`**: Completed annotations (output from annotation tool)

### Training Data (Current Version: v2)
- **`train_mapped_v2.jsonl`**: Training set (80% of annotated prompts)
- **`test_mapped_v2.jsonl`**: Test set (10% of annotated prompts)
- **`validation_mapped_v2.jsonl`**: Validation set (10% of annotated prompts)

## Format

### CSV Format
- Columns: `id`, `prompt`, `annotated_json`, `completion_status`
- `annotated_json` contains full JSON schema with full key names
- `completion_status` is `complete` or `incomplete`

### JSONL Format
- Template-free segments format
- Each line: `{"segments": [{"label": false, "text": "prompt\n"}, {"label": true, "text": "{...mapped json...}<END_JSON>"}]}`
- Keys are shortened (mk, md, vt, etc.)
- JSON is minified (no spaces/newlines)

## Generation

Training JSONL files are generated using:
```bash
python tools/processing/prepare_training_data_v2.py
```

This reads `annotated_nlp_prompts.csv` and outputs the three JSONL files.

