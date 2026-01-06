# Training Data Pipeline

This directory contains the complete pipeline for annotating NLP prompts and preparing training data for the vehicle selection model.

## Directory Structure

```
training/
├── tools/                    # Scripts and utilities
│   ├── annotation/          # Annotation tool and core modules
│   ├── processing/          # Data conversion and transformation scripts
│   ├── utilities/           # Utility scripts (import, reset, analyze, view)
│   └── inference/           # Model inference and testing scripts
├── data/                    # Data files
│   ├── active/             # Current working datasets
│   ├── legacy/             # Older versions and intermediate files
│   └── inference_results/  # Model inference results
├── config/                  # Training configuration files
├── docs/                    # Documentation files
└── raw_training_text/      # Raw text files for prompt import
```

## Quick Start

### 1. Annotate Prompts

```bash
cd car-back-end/training
python tools/annotation/annotation_tool.py
```

This will:
- Load prompts from `data/active/unannotated_nlp_prompts.csv`
- Guide you through annotating each prompt
- Save completed annotations to `data/active/annotated_nlp_prompts.csv`

### 2. Prepare Training Data

```bash
cd car-back-end/training
python tools/processing/prepare_training_data_v2.py
```

This will:
- Convert annotated CSV to JSONL format with key mapping
- Split into 80/10/10 train/test/validation sets
- Output: `data/active/train_mapped_v2.jsonl`, `test_mapped_v2.jsonl`, `validation_mapped_v2.jsonl`

### 3. Train Model

Use the config files in `config/` with your training framework (e.g., Axolotl).

## Workflow Overview

1. **Annotation**: Use `tools/annotation/annotation_tool.py` to annotate prompts
2. **Conversion**: Use `tools/processing/prepare_training_data_v2.py` to convert to training format
3. **Training**: Use files in `data/active/` with training configs in `config/`
4. **Inference**: Use `tools/inference/` scripts to test trained models

## Key Concepts

### Annotation Format
- **CSV**: Full JSON with full key names (`make`, `model`, `vehicle_type`, etc.)
- **JSONL**: Shortened keys (`mk`, `md`, `vt`, etc.) with minified JSON

### Key Mapping
Keys are shortened to reduce token usage. See `docs/key_mapping_schema.md` for complete mapping.

### Template-Free Segments Format
Training data uses a segments format:
```json
{
  "segments": [
    {"label": false, "text": "prompt text\n"},
    {"label": true, "text": "{\"mk\":[...],\"vt\":{...}}<END_JSON>"}
  ]
}
```

## Documentation

- **Annotation Tool**: See `tools/annotation/README.md`
- **Data Processing**: See `tools/processing/README.md`
- **Utilities**: See `tools/utilities/README.md`
- **Inference**: See `tools/inference/README.md`
- **Active Data**: See `data/active/README.md`
- **Legacy Data**: See `data/legacy/README.md`
- **Configuration**: See `config/README.md`
- **Documentation**: See `docs/README.md`

## Current Status

- **Annotated Prompts**: 367 (target: 600-800)
- **Training Data**: `train_mapped_v2.jsonl` (293 entries)
- **Test Data**: `test_mapped_v2.jsonl` (36 entries)
- **Validation Data**: `validation_mapped_v2.jsonl` (38 entries)

## File Locations

### Active Files (Current Work)
- Annotations: `data/active/annotated_nlp_prompts.csv`
- Unannotated: `data/active/unannotated_nlp_prompts.csv`
- Training sets: `data/active/train_mapped_v2.jsonl`, `test_mapped_v2.jsonl`, `validation_mapped_v2.jsonl`

### Legacy Files (Reference Only)
- Old training datasets: `data/legacy/`
- Old source files: `data/legacy/`
