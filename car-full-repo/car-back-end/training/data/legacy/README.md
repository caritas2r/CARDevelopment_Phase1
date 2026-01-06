# Legacy Data Files

This directory contains older versions of training datasets and intermediate files from previous processing runs.

## Contents

### Old Training Datasets
- Various `train_*.jsonl`, `test_*.jsonl`, `validation_*.jsonl` files from previous versions
- Files with suffixes like `_template_free`, `_updated`, `_mapped`, `_min` represent different processing stages

### Source Data Files
- **`compressed_vehicle_prompts.csv`**: Original compressed prompts dataset
- **`compressed_vehicle_prompts_v2_schema_valid.csv`**: Validated version of compressed prompts
- **`post_mapping_dataset_extension_100_1.csv`**: Additional prompts added after initial mapping
- **`prompts.csv`**: Sample/example prompts file
- **`jsonl_ready_prompts.jsonl`**: Intermediate JSONL file from old conversion process

## Note

These files are kept for reference and historical purposes. The current active datasets are in the `active/` directory.

If you need to use any of these files, consider:
1. Checking if a newer version exists in `active/`
2. Understanding the processing differences (key mapping, format changes, etc.)
3. Re-processing through the current pipeline if needed

