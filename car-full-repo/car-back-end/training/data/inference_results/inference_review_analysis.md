# Inference Results Review: `inference_report_test_v2.jsonl`

## Summary
- **Total Records**: 37
- **Parse Success Rate**: 100% (37/37 records have `parse_ok: true`)
- **Stop Reason**: All records stopped at `end_marker_token_stop` (correct behavior)
- **Average Runtime**: ~8.5-11 seconds per inference
- **Average Generated Tokens**: ~210-270 tokens per output

## Overall Assessment

### ✅ **Strengths**

1. **Perfect JSON Parsing**: All 37 outputs are valid JSON with correct structure
2. **Consistent Format**: All outputs use the shortened key format correctly (`mk`, `md`, `tr`, `vt`, `cp`, `iu`, `pd`, `fa`, `oc`, `ps`, `lc`)
3. **Proper Stopping**: All generations correctly stop at `<END_JSON>` marker
4. **Schema Compliance**: All outputs maintain the required nested structure
5. **Literal Extraction**: Model correctly extracts exactly what's in the text without attempting semantic validation (intended behavior)

### ✅ **Correct Behaviors (Not Issues)**

The following are **intended behaviors** where the model correctly extracts literal text:

- **Vehicle Type Extraction**: Model extracts stated vehicle types (e.g., "coupe", "truck") even when they conflict with make/model specifications. This is correct - the model should extract what the user says, not validate against reality.
- **Powertrain Extraction**: Model extracts stated powertrains (e.g., "diesel" for Tesla) literally. This is correct - literal extraction is the goal.
- **Budget Strictness**: `max_strict: "false"` correctly appears when budget is not strict (e.g., "around $40k" vs "under $40k"). This is correct behavior.
- **Multiple Specifications**: Model extracts all stated specifications even when they seem incompatible (e.g., minivan + sedan model). This is correct - extract everything mentioned.

### ⚠️ **Actual Issues Identified**

#### Issue 1: Invalid Enum Value (Line 4) - **REAL ISSUE**

**Input**: "Show me good all-around options under $35k with reasonable mileage."

**Output**: 
```json
"mi": {
  "max": "unspecified",
  "qual": ["reasonable"]
}
```

**Problem**: 
- `"reasonable"` is not in the canonical vocabulary for mileage qualitative values
- Valid values are: `"very_low"`, `"low"`, `"moderate"`, `"low_or_moderate"`, `"high"`, `"does_not_matter"`, `"unspecified"`
- This will cause validation errors downstream

**Root Cause**: Model extracted "reasonable" literally from the text, but this value doesn't exist in the vocabulary. The model should map common terms like "reasonable" to canonical values (likely `"moderate"`).

**Impact**: **High** - Invalid enum value will break validation/query processing

**Recommendation**: 
1. Add vocabulary mapping for common terms like "reasonable" → "moderate"
2. Or add training examples that use canonical vocabulary terms instead of "reasonable"

#### Issue 2: Missing Make Extraction (Line 15) - **REAL ISSUE**

**Input**: "I want a minivan that's family focused, preferably **Toyota or Honda**, under $40k."

**Output**: 
```json
"mk": ["unspecified"]
```

**Problem**: 
- Model didn't extract either "Toyota" or "Honda" from the text
- The make field currently only accepts a single string value, but the text contains multiple makes ("Toyota or Honda")
- Model should extract at least one of the makes, or the training data should exclude such examples until multi-make support is added

**Root Cause**: 
- The make field schema likely only supports a single make value
- When multiple makes are mentioned with "or", the model doesn't know which to extract
- This example should have been excluded from the test set until multi-make support is implemented

**Impact**: **Medium** - Missing important constraint that user explicitly stated

**Recommendation**: 
1. Either update schema to support multiple makes in the array
2. Or exclude examples with multiple makes from training/test sets until support is added
3. Or train model to extract the first mentioned make when multiple are present

## Detailed Examples

### ✅ **Excellent Examples**

**Line 7 - Complex Query Handled Perfectly:**
- **Input**: Complex query with multiple constraints (location, year range, budget, features, exclusions)
- **Output**: Correctly extracted:
  - Make/Model: Toyota Prius ✅
  - Year range: 2022-2024 ✅
  - Location: North Las Vegas, NV, 25 miles ✅
  - Budget: $30k max ✅
  - Seating: 6 seats, 2 kids, 2 pets ✅
  - Features: All must-haves and nice-to-haves correctly categorized ✅
  - Exclusions: Correctly placed in `avoid` array ✅

**Line 9 - Simple Query Handled Perfectly:**
- **Input**: "Show me BMW X5 dual_clutch transmission cars within 75 miles, no tow package."
- **Output**: Correctly extracted:
  - Make/Model: BMW X5 ✅
  - Transmission: dual_clutch ✅
  - Location radius: 75 miles ✅
  - Avoid: tow_package ✅

**Line 6 - Literal Extraction Working as Intended:**
- **Input**: "2017–2018 Audi Q5 as my next **coupe**"
- **Output**: `"vt":{"inc":["coupe"]}`
- **Assessment**: ✅ Correct - Model extracted "coupe" exactly as stated, which is the intended behavior

**Line 14 - Literal Extraction Working as Intended:**
- **Input**: "2017+ Tesla Model Y... It should be **diesel-powered**"
- **Output**: `"pt":["diesel"]`
- **Assessment**: ✅ Correct - Model extracted "diesel" exactly as stated, which is the intended behavior

## Recommendations

### High Priority

1. **Fix Enum Vocabulary Mapping (Line 4)**:
   - Add mapping for "reasonable" → "moderate" (or other appropriate canonical value)
   - Or update training data to use canonical vocabulary terms instead of "reasonable"
   - Ensure all mileage qualitative values use canonical vocabulary

2. **Handle Multiple Makes (Line 15)**:
   - **Option A**: Update schema to support multiple makes in array: `"mk": ["Toyota", "Honda"]`
   - **Option B**: Train model to extract first mentioned make when multiple are present
   - **Option C**: Exclude examples with multiple makes from training/test sets until support is added

### Medium Priority

1. **Semantic Understanding Improvements**: 
   - These will be resolved with more training data as mentioned
   - Focus on improving extraction of implicit requirements and better tag extraction

## Conclusion

The model demonstrates **excellent structural consistency** and **strong literal extraction capabilities**. All outputs are valid JSON with correct schema structure. The model correctly extracts exactly what's stated in the text without attempting semantic validation, which is the intended behavior.

**Only 2 real issues identified:**
1. Invalid enum value "reasonable" for mileage (Line 4) - needs vocabulary mapping
2. Missing make extraction when multiple makes mentioned (Line 15) - needs schema/training update

**Overall Grade**: **A-**
- Structure: A+ (perfect)
- Consistency: A+ (perfect)
- Literal Extraction: A (excellent - working as intended)
- Vocabulary Compliance: B+ (one invalid enum value)
- Multi-value Handling: B (missing make extraction for multiple makes)

The model is performing very well for its intended purpose of literal extraction. The two identified issues are straightforward to address.

