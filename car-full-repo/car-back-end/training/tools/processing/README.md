# Data Processing Scripts

This directory contains scripts for converting and transforming training data.

## Files

- **`csv_to_template_free_mapped.py`**: Converts annotated CSV to template-free segments JSONL format with key mapping
- **`apply_key_mapping.py`**: Applies key shortening mapping to JSON in existing JSONL files
- **`prepare_training_data_v2.py`**: Complete pipeline - converts CSV to mapped JSONL and splits into train/test/validation sets (80/10/10)
- **`minify_jsonls_no_newlines.py`**: Minifies JSONL files by removing newlines from JSON payloads

## Usage

### Convert CSV to JSONL with mapping:
```bash
python tools/processing/csv_to_template_free_mapped.py --input data/active/annotated_nlp_prompts.csv
```

### Prepare complete training dataset (recommended):
```bash
python tools/processing/prepare_training_data_v2.py
```

This will:
- Read `data/active/annotated_nlp_prompts.csv`
- Convert to template-free segments format with key mapping
- Split into 80/10/10 train/test/validation
- Output: `data/active/train_mapped_v2.jsonl`, `test_mapped_v2.jsonl`, `validation_mapped_v2.jsonl`

### Apply key mapping to existing JSONL:
```bash
python tools/processing/apply_key_mapping.py input.jsonl --output output.jsonl
```

## Key Mapping

Keys are shortened to reduce token usage:
- `make` → `mk`
- `model` → `md`
- `vehicle_type` → `vt`
- `features_amenities` → `fa`
- etc.

See `docs/key_mapping_schema.md` for the complete mapping.

