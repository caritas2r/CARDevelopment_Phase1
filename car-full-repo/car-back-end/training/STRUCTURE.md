# Training Directory Structure

## Overview

The training directory has been organized into a clean, logical structure with nested folders and documentation.

## Directory Tree

```
training/
├── README.md                    # Main documentation
├── STRUCTURE.md                 # This file
│
├── tools/                       # All scripts organized by function
│   ├── annotation/             # Annotation tool and core modules
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── annotation_tool.py
│   │   ├── csv_manager.py
│   │   ├── field_prompter.py
│   │   └── schema_traverser.py
│   │
│   ├── processing/             # Data conversion and transformation
│   │   ├── README.md
│   │   ├── apply_key_mapping.py
│   │   ├── csv_to_template_free_mapped.py
│   │   ├── minify_jsonls_no_newlines.py
│   │   └── prepare_training_data_v2.py
│   │
│   ├── utilities/              # Utility scripts
│   │   ├── README.md
│   │   ├── analyze_csv.py
│   │   ├── import_prompts.py
│   │   ├── prompt_viewer.py
│   │   └── reset_csv.py
│   │
│   └── inference/              # Model inference scripts
│       └── README.md
│
├── data/                        # All data files
│   ├── active/                 # Current working datasets
│   │   ├── README.md
│   │   ├── annotated_nlp_prompts.csv
│   │   ├── unannotated_nlp_prompts.csv
│   │   ├── train_mapped_v2.jsonl
│   │   ├── test_mapped_v2.jsonl
│   │   └── validation_mapped_v2.jsonl
│   │
│   ├── legacy/                 # Older versions and intermediate files
│   │   ├── README.md
│   │   └── [22 legacy files: old JSONL, CSV files]
│   │
│   └── inference_results/      # Model inference results
│       ├── README.md
│       ├── inference_results_test.jsonl
│       ├── inference_report_test.jsonl
│       ├── test_predictions.jsonl
│       └── formatted_prediction_results.csv
│
├── config/                      # Training configuration files
│   ├── README.md
│   ├── qwen25_3b_preprocess.yml
│   └── qwen25_3b_qlora_v2.yml
│
├── docs/                        # Documentation files
│   ├── README.md
│   ├── key_mapping_schema.md
│   └── feature_analysis_summary.md
│
└── raw_training_text/           # Raw text files for import
    └── README.md
```

## Key Locations

### Active Work Files
- **Annotations**: `data/active/annotated_nlp_prompts.csv`
- **Unannotated**: `data/active/unannotated_nlp_prompts.csv`
- **Training Data**: `data/active/train_mapped_v2.jsonl`, `test_mapped_v2.jsonl`, `validation_mapped_v2.jsonl`

### Main Scripts
- **Annotation**: `tools/annotation/annotation_tool.py`
- **Data Prep**: `tools/processing/prepare_training_data_v2.py`
- **Utilities**: `tools/utilities/`

### Configuration
- **Training Configs**: `config/qwen25_3b_*.yml`

## Usage

All scripts should be run from the `training/` directory:

```bash
cd car-back-end/training
python tools/annotation/annotation_tool.py
python tools/processing/prepare_training_data_v2.py
```

