# Training and Inference Documentation

This document describes the key files used for training and running inference with the Qwen2.5-3B model for structured NLP-to-JSON conversion.

## Overview

The training and inference pipeline consists of three main components:

1. **qwen25_3b_qlora_v2.yml** - Training configuration file for Axolotl
2. **infer_simple_jsonl.py** - Inference script for running the trained model
3. **inference_report_test.jsonl** - Output file containing inference results and metrics

---

## qwen25_3b_qlora_v2.yml

**Location:** `car-back-end/training/qwen25_3b_qlora_v2.yml`

**Purpose:** Axolotl training configuration file that defines all parameters for fine-tuning the Qwen2.5-3B model using QLoRA (Quantized Low-Rank Adaptation).

### Key Configuration Sections

#### Model Configuration
- **Base Model:** `Qwen/Qwen2.5-3B` (3 billion parameter model)
- **Model Type:** `AutoModelForCausalLM`
- **Tokenizer Type:** `AutoTokenizer`

#### Template-Free Training
- **train_on_inputs:** `false` - Only trains on output tokens (label:true segments), not input prompts

#### Quantization (QLoRA)
- **load_in_4bit:** `true` - Uses 4-bit quantization to reduce memory usage
- **bnb_4bit_quant_type:** `nf4` - NormalFloat4 quantization
- **bnb_4bit_compute_dtype:** `float16` - Computation in float16
- **bnb_4bit_use_double_quant:** `true` - Double quantization for additional memory savings

#### Data Configuration
- **Training Data:** `./data/train_template_free_updated.jsonl`
- **Validation Data:** `./data/validation_template_free_updated.jsonl`
- **Dataset Type:** `input_output` - Template-free format with segments
- **Prepared Path:** `prepared/qwen25_3b_template_free_v1`

#### Output Configuration
- **Output Directory:** `outputs/qwen25_3b_base_template_free_json_qlora_v2_ENDJSON_REMOVEDESCAPES`
- **Save Total Limit:** `3` - Keeps only the last 3 checkpoints

#### Sequence Configuration
- **Sequence Length:** `2048` tokens
- **Sample Packing:** `false` - No packing of multiple examples

#### LoRA Adapter Configuration
- **Adapter Type:** `qlora`
- **LoRA Rank (r):** `16` - Low-rank dimension
- **LoRA Alpha:** `32` - Scaling factor (alpha/r = 2.0)
- **LoRA Dropout:** `0.05` - 5% dropout for regularization
- **Target:** `lora_target_linear: true` - Applies LoRA to linear layers

#### Training Hyperparameters
- **Micro Batch Size:** `1`
- **Gradient Accumulation Steps:** `16` - Effective batch size = 16
- **Number of Epochs:** `6`
- **Learning Rate:** `2e-4` (0.0002)
- **Warmup Ratio:** `0.03` - 3% of training steps for warmup
- **LR Scheduler:** `cosine` - Cosine annealing
- **Weight Decay:** `0.0` - No weight decay
- **Optimizer:** `paged_adamw_8bit` - Memory-efficient AdamW
- **Gradient Checkpointing:** `true` - Trades compute for memory

#### Precision Settings
- **FP16:** `true` - Mixed precision training
- **BF16:** `false`
- **TF32:** `true` - TensorFloat-32 for faster computation

#### Evaluation and Logging
- **Eval Steps:** `50` - Evaluate every 50 steps
- **Logging Steps:** `10` - Log metrics every 10 steps
- **Save Steps:** `50` - Save checkpoint every 50 steps

#### Stability Settings
- **Flash Attention:** `false` - Disabled for stability
- **XFormers Attention:** `false` - Disabled for stability

### Usage

This configuration file is used with Axolotl to train the model:

```bash
axolotl train qwen25_3b_qlora_v2.yml
```

---

## infer_simple_jsonl.py

**Location:** `car-back-end/training/infer_simple_jsonl.py`

**Purpose:** Token-efficient inference script that runs the trained model on test data and generates structured JSON output from natural language prompts.

### Key Features

1. **Efficient Generation:** Single `generate()` call per prompt
2. **Smart Stopping:** Stops when `<END_JSON>` marker is detected (handles whitespace variants)
3. **JSON Extraction:** Automatically extracts and parses the first JSON object from generated text
4. **Comprehensive Reporting:** Records metrics, timing, and parse status

### Configuration Constants

```python
BASE_MODEL_ID = "Qwen/Qwen2.5-3B"
ADAPTER_PATH = "outputs/qwen25_3b_base_template_free_json_qlora_v2_ENDJSON_REMOVEDESCAPES"
INPUT_JSONL = "data/test_template_free.jsonl"
OUTPUT_JSONL = "outputs/inference_report_test.jsonl"
END_MARKER = "<END_JSON>"
MAX_NEW_TOKENS = 512
REPETITION_PENALTY = 1.05
TORCH_DTYPE = torch.float16
```

### Key Functions

#### `iter_input_texts_from_segments(example)`
Extracts all text segments where `label: false` from the template-free JSONL format. These are the input prompts for inference.

#### `extract_first_json_object(text)`
Robustly extracts the first complete JSON object from generated text by:
- Finding the first `{`
- Tracking string state and escape sequences
- Matching braces to find the closing `}`

Returns a `JsonExtractResult` with the JSON text or an error message.

#### `StopOnAnyTokenSequence`
Custom stopping criteria that stops generation when any of the provided stop token sequences are detected. Handles variants like:
- `<END_JSON>`
- `\n<END_JSON>`
- ` <END_JSON>`
- `\r\n<END_JSON>`

This is more robust than simple token matching because whitespace can change tokenization.

#### `build_stop_sequences(tokenizer, marker)`
Creates multiple stop sequences for the END_MARKER with common whitespace prefixes to handle different tokenization scenarios.

#### `load_model_and_tokenizer()`
Loads the base model and applies the trained LoRA adapter:
1. Loads tokenizer from base model
2. Sets pad token if needed
3. Loads base model with 4-bit quantization
4. Applies PEFT adapter
5. Sets model to eval mode

### Main Workflow

1. **Load Model:** Loads base model and applies trained adapter
2. **Build Stop Sequences:** Creates stop sequences for END_MARKER detection
3. **Load Prompts:** Reads input JSONL and extracts all `label: false` text segments
4. **For Each Prompt:**
   - Tokenize the prompt
   - Run generation with stopping criteria
   - Measure runtime
   - Extract JSON from generated text
   - Parse JSON and validate
   - Write results to output JSONL

### Output Record Format

Each line in the output JSONL contains:

```json
{
  "source_line_index": 0,           // Line number in input file
  "segment_index": 0,               // Segment index within line
  "prompt_len_tokens": 16,          // Input prompt token count
  "generated_len_tokens": 210,      // Generated output token count
  "runtime_seconds": 10.918,        // Inference time in seconds
  "stop_reason": "end_marker_token_stop",  // Why generation stopped
  "parse_ok": true,                 // Whether JSON parsed successfully
  "input_text": "...",               // Original input prompt
  "raw_generated_text": "...",       // Full generated text (before extraction)
  "extracted_json_text": "...",      // Extracted JSON string
  "parse_error": null,               // Parse error if any
  "parsed_json": {...}               // Parsed JSON object (if successful)
}
```

### Stop Reasons

- **`end_marker_token_stop`:** Generation stopped when END_MARKER was detected
- **`cap`:** Generation stopped due to max_new_tokens limit

### Usage

```bash
cd car-back-end/training
python infer_simple_jsonl.py
```

The script will:
1. Load the model and adapter
2. Process all prompts from `INPUT_JSONL`
3. Write results to `OUTPUT_JSONL`
4. Print progress to stdout

---

## inference_report_test.jsonl

**Location:** `car-back-end/training/inference_report_test.jsonl`

**Purpose:** Output file containing detailed inference results, metrics, and parsed JSON outputs from running `infer_simple_jsonl.py` on test data.

### File Format

Each line is a JSON object containing one inference result. The file follows JSONL format (one JSON object per line).

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `source_line_index` | integer | Zero-based line number in the input JSONL file |
| `segment_index` | integer | Zero-based segment index within that line |
| `prompt_len_tokens` | integer | Number of tokens in the input prompt |
| `generated_len_tokens` | integer | Number of tokens generated (before stopping) |
| `runtime_seconds` | float | Time taken for inference in seconds |
| `stop_reason` | string | Reason generation stopped: `"end_marker_token_stop"` or `"cap"` |
| `parse_ok` | boolean | Whether the extracted JSON was successfully parsed |
| `input_text` | string | Original natural language input prompt |
| `raw_generated_text` | string | Complete generated text before JSON extraction |
| `extracted_json_text` | string | Extracted JSON string (first complete JSON object) |
| `parse_error` | string\|null | Error message if JSON parsing failed, null otherwise |
| `parsed_json` | object\|null | Parsed JSON object if successful, null otherwise |

### JSON Output Format

The `parsed_json` field contains structured vehicle selection data using shortened keys (see `key_mapping_schema.md`):

```json
{
  "mk": ["Toyota"],           // make
  "md": ["RAV4"],            // model
  "tr": "unspecified",       // trim
  "vt": {                    // vehicle_type
    "inc": ["suv"],          // include_body_styles
    "exc": ["hatchback"]     // exclude_body_styles
  },
  "cp": {...},               // capacity_practicality
  "iu": {...},               // intended_use
  "pd": {...},               // powertrain_drivability
  "fa": {...},               // features_amenities
  "oc": {...},               // ownership_constraints
  "ps": {...},               // preference_signals
  "lc": {...}                // location_constraints
}
```

### Typical Metrics

Based on current results:
- **Parse Success Rate:** ~100% (all entries parse successfully)
- **Stop at END_MARKER:** ~100% (most stop at marker, not token limit)
- **Generated Tokens:** 210-260 tokens per inference
- **Runtime:** ~9-12 seconds per inference (depends on hardware)
- **Format Compliance:** 100% (uses shortened keys, minified JSON)

### Analysis Use Cases

This file is useful for:
1. **Performance Analysis:** Token counts, runtime, stop reasons
2. **Quality Assessment:** Parse success rate, JSON structure validation
3. **Error Analysis:** Examining `parse_error` and `raw_generated_text` for failures
4. **Semantic Accuracy:** Comparing `parsed_json` with expected outputs
5. **Model Evaluation:** Tracking improvements across training iterations

### Example Analysis

To analyze the results:

```python
import json

parse_ok_count = 0
total_count = 0
total_tokens = 0

with open("inference_report_test.jsonl", "r") as f:
    for line in f:
        record = json.loads(line)
        total_count += 1
        if record["parse_ok"]:
            parse_ok_count += 1
        total_tokens += record["generated_len_tokens"]

print(f"Parse success rate: {parse_ok_count/total_count*100:.1f}%")
print(f"Average tokens: {total_tokens/total_count:.1f}")
```

---

## Workflow Summary

1. **Training:**
   - Prepare training data in template-free format with shortened keys
   - Run `axolotl train qwen25_3b_qlora_v2.yml`
   - Model checkpoints saved to `outputs/qwen25_3b_base_template_free_json_qlora_v2_ENDJSON_REMOVEDESCAPES`

2. **Inference:**
   - Prepare test data in same template-free format
   - Run `python infer_simple_jsonl.py`
   - Results written to `inference_report_test.jsonl`

3. **Analysis:**
   - Review `inference_report_test.jsonl` for metrics and quality
   - Check parse success rate, token efficiency, semantic accuracy
   - Iterate on training data or hyperparameters as needed

---

## Related Documentation

- **key_mapping_schema.md** - Documents the shortened key mappings used in training data
- **json_to_db_mapping.md** - Maps JSON schema fields to database columns

