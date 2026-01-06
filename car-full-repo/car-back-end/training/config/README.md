# Configuration Files

This directory contains configuration files for model training and preprocessing.

## Files

- **`qwen25_3b_preprocess.yml`**: Preprocessing configuration for Qwen 2.5 3B model
- **`qwen25_3b_qlora_v2.yml`**: QLoRA training configuration for Qwen 2.5 3B model (version 2)

## Usage

These YAML files are used by training frameworks (e.g., Axolotl) to configure:
- Model architecture and parameters
- Training hyperparameters
- Data loading and preprocessing
- LoRA/QLoRA adapter settings

## Training

To use these configs, reference them in your training command:

```bash
# Example with Axolotl
axolotl train config/qwen25_3b_qlora_v2.yml
```

