# Vehicle Prompts Validation Report

**File:** `vehicle_prompts_100.csv`  
**Rows Processed:** 100  
**Total Errors Found:** 5  
**Status:** ⚠️ **Issues Found - Review Required**

## Summary

The validation script checked:
1. ✅ Enum value consistency (all enums valid)
2. ✅ Field mapping correctness (all abbreviated keys valid)
3. ⚠️ Logical consistency (5 issues found)
4. ✅ JSON structure (all valid)

## Issues Found

### 1. Logical Contradictions - Feature Conflicts (2 errors)

#### Row 59: Feature in both `nice_to_have` and `avoid`
**Prompt:** "I'd like third row seating, lane departure warning if possible; but skip third row seating."
- **Issue:** `third_row_seating` appears in both `nice_to_have` AND `avoid` lists
- **Fix:** Remove from one list based on user intent (likely remove from `avoid` since they said "I'd like")

#### Row 67: Feature in both `must_have` and `avoid`
**Prompt:** "it has to have third row seating; ... but skip third row seating, memory seats."
- **Issue:** `third_row_seating` appears in both `must_have` AND `avoid` lists
- **Fix:** This is clearly contradictory - likely remove from `avoid` since it's marked as "has to have"

### 2. Potentially Contradictory Use Case Tags (3 warnings)

#### Row 26: `budget_value` + `performance`
**Tags:** `["budget_value", "cargo", "performance"]`
- **Note:** May be contradictory - performance vehicles typically cost more. This could be valid if user wants "best performance for budget".

#### Row 33: `budget_value` + `performance`
**Tags:** `["budget_value", "performance", "off_road"]`
- **Note:** Same concern as above.

#### Row 63: `budget_value` + `performance`
**Tags:** `["performance", "work_light", "budget_value"]`
- **Note:** Same concern as above.

## Recommendations

1. **Rows 59 & 67:** These need immediate correction - a feature cannot be both required/desired AND avoided. Review the prompts and fix the annotations.

2. **Rows 26, 33, 63:** Review these to ensure the tags accurately reflect user intent. If the user genuinely wants performance on a budget, these may be valid. However, consider if one tag is more accurate than the other.

## Validation Details

### Enum Validation
- ✅ All body_style values valid
- ✅ All priority_level values valid
- ✅ All use_case_tag values valid
- ✅ All transmission values valid
- ✅ All drivetrain values valid
- ✅ All powertrain_type values valid
- ✅ All feature_tag values valid
- ✅ All maintenance_priority values valid
- ✅ All color values valid
- ✅ All boolean_with_unspecified values valid

### Structure Validation
- ✅ All JSON structures valid
- ✅ All abbreviated keys correctly mapped
- ✅ All required fields present

## Next Steps

1. Fix rows 59 and 67 (feature contradictions)
2. Review rows 26, 33, and 63 (potentially contradictory tags)
3. Re-run validation to confirm all issues resolved

