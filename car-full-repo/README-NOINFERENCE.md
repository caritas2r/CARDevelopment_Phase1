# No Inference Mode (`--noinference` Flag)

## Overview

The `--noinference` flag allows you to run the application **without** requiring GPU inference capabilities or a database. This mode uses a `MockQueryService` that returns fake vehicle results for testing the frontend and application flow.

## Purpose

Use this mode when you want to:
- Test the frontend and UI without GPU hardware
- Run the app on a laptop without inference dependencies
- Test the application flow without setting up the full inference pipeline
- Develop frontend features without waiting for model loading

## Usage

### Starting the Application

**Windows:**
```batch
create-venv.bat --noinference
```

**PowerShell:**
```powershell
.\create-venv.bat --noinference
```

**Direct Python:**
```bash
cd car-back-end
python app.py --noinference
```

### What Gets Disabled

When using `--noinference`:
- ❌ Model inference service (no GPU/ML dependencies needed)
- ❌ Database connection and queries
- ❌ Inference model loading
- ❌ Schema validation pipeline
- ❌ Quality checks

### What Still Works

- ✅ Frontend UI and routing
- ✅ Query submission interface
- ✅ Results page rendering
- ✅ Paywall functionality
- ✅ All frontend features

## Frontend Query Format

**IMPORTANT:** In mock mode, the frontend must send **ONLY** one of these three exact string values:

### Accepted Values

1. **`"pass"`** - Returns 1-10 random fake vehicle results
   - Results are rendered exactly like normal results
   - Paywall functionality works normally
   - Uses values from JSON schema enums (makes, models, body styles, features, etc.)

2. **`"fail"`** - Returns empty results (no results found)
   - Triggers the "no results" UI path
   - Useful for testing empty state handling

3. **`"insufficient"`** - Returns an error message
   - Message: "Too many results found that match your criteria. Please refine your search..."
   - Useful for testing error handling and user feedback

### Example Frontend Query

```javascript
// In query-page/index.js or similar
const queryText = "pass";  // or "fail" or "insufficient"
```

## Response Formats

### "pass" Response

```json
{
  "success": true,
  "query": "pass",
  "extracted_fields": {...},
  "sql_query": "SELECT * FROM vehicles WHERE make IN ('Toyota', 'Honda') LIMIT 5",
  "sql_params": [],
  "results": [
    {
      "vehicle_id": "mock_vehicle_001",
      "make": "Toyota",
      "model": "Camry",
      "year": 2022,
      "price": 35000,
      ...
    },
    ...
  ],
  "result_count": 5,
  "quality_warnings": [],
  "quality_acceptable": true
}
```

### "fail" Response

```json
{
  "success": true,
  "query": "fail",
  "extracted_fields": {},
  "sql_query": "SELECT * FROM vehicles WHERE make = 'NonExistentMake'",
  "sql_params": [],
  "results": [],
  "result_count": 0,
  "quality_warnings": [],
  "quality_acceptable": true
}
```

### "insufficient" Response

```json
{
  "success": false,
  "query": "insufficient",
  "error": "Too many results found that match your criteria. Please refine your search by adding more specific constraints (e.g., make, model, year range, budget range).",
  "error_type": "insufficient_criteria",
  "extracted_fields": {},
  "sql_query": "",
  "sql_params": [],
  "results": [],
  "result_count": 0
}
```

## Mock Data Generation

The mock service generates fake vehicle data using:
- **Makes/Models**: Realistic combinations from the vocabulary
- **Body Styles**: Values from `BODY_STYLES` enum
- **Features**: Random selection from `FEATURE_TAGS`
- **Use Cases**: Random selection from `USE_CASE_TAGS`
- **Powertrains**: Random selection from `POWERTRAIN_TYPES` (array)
- **Transmissions**: Values from `TRANSMISSIONS` enum
- **Drivetrains**: Values from `DRIVETRAINS` enum
- **Colors**: Realistic color names
- **Other Fields**: Random realistic values (years, prices, mileage, etc.)

All values conform to the Vehicle Selection V1 schema enums.

## Requirements

**Minimal requirements when using `--noinference`:**
- Python 3.10+
- Flask (`pip install flask flask-cors`)

**Not required:**
- PyTorch
- Transformers library
- PEFT/accelerate
- CUDA/GPU
- Database file
- Model adapter directory

## Limitations

- **No real inference**: Cannot test actual NLP-to-SQL conversion
- **No real database**: Cannot test actual database queries
- **Fixed responses**: Only three response types (pass/fail/insufficient)
- **No schema validation**: Schema validation is skipped in mock mode
- **No quality checks**: Output quality checks are disabled

## Testing Different Scenarios

### Test Successful Query Flow
1. Send query: `"pass"`
2. Should see 1-10 random vehicle results
3. Test paywall functionality
4. Test result display formatting

### Test Empty Results
1. Send query: `"fail"`
2. Should see "no results" UI
3. Test empty state handling

### Test Error Handling
1. Send query: `"insufficient"`
2. Should see error message
3. Test error UI display

## Troubleshooting

### "Mock query service accepts only 'pass', 'fail', or 'insufficient'"

**Error:** You sent a different string value.

**Solution:** Make sure the frontend sends exactly one of: `"pass"`, `"fail"`, or `"insufficient"` (case-insensitive).

### "Flask not found"

**Error:** Python can't find Flask when starting in mock mode.

**Solution:** Install Flask manually:
```bash
pip install flask flask-cors
```

### Application doesn't start

**Error:** Backend fails to start even with `--noinference`.

**Solution:** Check that `app.py` is in the correct directory and Python is accessible. The flag should be passed as: `python app.py --noinference`

## Switching Back to Normal Mode

To use real inference again, simply run without the flag:

```batch
create-venv.bat
```

Or:
```bash
cd car-back-end
python app.py
```

Make sure you have:
- Model adapter directory configured
- Environment variables set (HF_BASE_MODEL_ID, LORA_ADAPTER_PATH)
- Inference dependencies installed
- Database file available
