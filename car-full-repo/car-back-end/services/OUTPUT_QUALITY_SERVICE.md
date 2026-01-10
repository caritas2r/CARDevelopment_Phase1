# Output Quality Service

## Overview

The `OutputQualityService` provides quality checks for model inference output to ensure the generated JSON meets certain standards before being processed further in the pipeline.

## Purpose

This service detects common issues with model output such as:
- Empty or malformed JSON structures
- All fields being "unspecified" (no constraints extracted)
- Missing critical fields
- Contradictory constraints (e.g., year_min > year_max, budget_min > budget_max)

## Usage

The service is automatically integrated into the query pipeline in `QueryService`. It runs after model inference and before SQL conversion.

### Integration in Query Pipeline

```python
# In query_service.py
is_acceptable, quality_warnings = self.quality_service.check_output_quality(
    json_with_short_keys, query_text
)
```

### Response Format

The service returns:
- `is_acceptable` (bool): `True` if output quality is acceptable, `False` if there are critical issues
- `warnings` (List[str]): List of warning messages describing any quality issues found

### Quality Checks

1. **Empty/Malformed Output Check**
   - Detects if output is `None`, empty, or not a dictionary
   - Critical issue - returns `is_acceptable = False`

2. **All Fields Unspecified Check**
   - Checks if all extractable fields are "unspecified" (no constraints extracted)
   - Critical issue - returns `is_acceptable = False`

3. **Missing Critical Fields Check**
   - Validates presence of critical fields: `make`, `model`, `vehicle_type`, `ownership_constraints`
   - Non-critical warning - logged but doesn't fail the request

4. **Contradictory Constraints Check**
   - Detects logical contradictions:
     - `year_min > year_max`
     - `budget_min > budget_max`
   - Non-critical warning - logged but doesn't fail the request

### API Response

Quality warnings are included in the API response:

```json
{
  "success": true,
  "query": "show me manual transmission cars",
  "extracted_fields": {...},
  "sql_query": "...",
  "sql_params": [...],
  "results": [...],
  "result_count": 5,
  "quality_warnings": [
    "Missing critical fields: make, model"
  ],
  "quality_acceptable": true
}
```

## Implementation Details

### `check_output_quality(json_output, original_query)`

Main method that performs all quality checks.

**Parameters:**
- `json_output` (Dict[str, Any]): The JSON output from model inference
- `original_query` (str): The original natural language query

**Returns:**
- `Tuple[bool, List[str]]`: `(is_acceptable, warnings)`

### Helper Methods

- `_all_fields_unspecified(json_output)`: Checks if all extractable fields are unspecified
- `_has_specified_value(value)`: Checks if a value is specified (not "unspecified", not empty, not None)
- `_check_contradictions(json_output)`: Detects contradictory constraints

## Notes

- The service does **not** detect semantic errors (e.g., wrong make/model names like "corvette" → "caddy")
- Schema validation is handled separately by `VehicleSelectionV1Validator`
- Quality warnings are logged but don't prevent request processing (except for critical issues like empty output)
