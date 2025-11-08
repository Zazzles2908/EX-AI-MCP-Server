# Planner Tool Validation Fix Report

## Issue Summary

The planner tool was failing with a Pydantic validation error when called with legacy parameters (`task`, `deadline`) instead of the required workflow parameters (`step`, `step_number`, `total_steps`, `next_step_required`).

### Error Details

```
pydantic_core._pydantic_core.ValidationError: 4 validation errors for PlannerRequest
step - Field required
step_number - Field required
total_steps - Field required
next_step_required - Field required
```

### Root Cause

The `PlannerRequest` Pydantic model defines these required fields:
- `step: str`
- `step_number: int`
- `total_steps: int`
- `next_step_required: bool`

But the tool was being called with legacy parameters:
- `task: str` (should map to `step`)
- `deadline: str` (should map to `total_steps`)

The validation error occurred in `tools/workflow/orchestration.py` at line 75 where `self.get_workflow_request_model()(**arguments)` was called without parameter validation.

## Solution Implemented

### 1. Added Parameter Validation Method

Created `_validate_and_convert_parameters()` method in `OrchestrationMixin` class (`tools/workflow/orchestration.py`):

- **Location**: Lines 52-128 in `tools/workflow/orchestration.py`
- **Function**: Validates and converts parameters before creating the workflow request
- **Special handling**: For planner tool, converts legacy parameters to new format

### 2. Parameter Conversion Logic

The method performs the following conversions for the planner tool:

| Legacy Parameter | New Parameter | Value/Conversion |
|-----------------|---------------|------------------|
| `task` | `step` | Direct mapping |
| `deadline` | `total_steps` | Default to 1 (can be enhanced to parse date) |
| (missing) | `step_number` | Default to 1 |
| (missing) | `next_step_required` | Default to True |
| (missing) | `findings` | Default: "Legacy parameter conversion completed" |

### 3. Error Handling

The method provides clear error messages when parameters cannot be converted:

```
[planner] Missing required parameters: ['step', 'step_number', 'total_steps', 'next_step_required']

Expected parameters (new format):
  - step:str - The current planning step description
  - step_number:int - Current step number (starts at 1)
  - total_steps:int - Total estimated steps
  - next_step_required:bool - Whether another step is needed

Legacy parameters (deprecated):
  - task:str (converted to 'step')
  - deadline:str (converted to 'total_steps' defaulting to 1)

Received parameters: [...]

Please use the new parameter format or provide all required parameters.
```

## Testing

### Test Coverage

Created comprehensive test suite (`test_planner_fix.py`) that validates:

1. ✅ **Legacy parameters (task, deadline)**: Successfully converts to new format
2. ✅ **New parameters (step, step_number, total_steps, next_step_required)**: Validates correctly
3. ✅ **Partial legacy parameters (task only)**: Converts and adds defaults
4. ✅ **Empty parameters**: Correctly raises ValueError with helpful message
5. ✅ **Mixed parameters**: Handles correctly

### Test Results

```
============================================================
PLANNER TOOL PARAMETER VALIDATION TEST
============================================================

Test 1: Legacy parameters (task, deadline)
============================================================
[planner] Converting legacy parameters to new format
[planner] Converted deadline 'Today' to total_steps=1
[planner] Added default step_number=1
[planner] Added default next_step_required=True
[planner] Added default findings
[OK] SUCCESS: {'step': 'Optimize Qwen2.5', 'total_steps': 1, 'step_number': 1, 'next_step_required': True, 'findings': 'Legacy parameter conversion completed'}

Test 2: New parameters (step, step_number, total_steps, next_step_required)
============================================================
[OK] SUCCESS: (validates correctly)

Test 3: Partial legacy parameters (task only)
============================================================
[OK] SUCCESS: (converts and adds defaults)

Test 4: Empty parameters (should raise error)
============================================================
[OK] SUCCESS: Correctly raised ValueError for empty parameters

Test 5: Mixed parameters (task + step_number)
============================================================
[OK] SUCCESS: (handles correctly)

============================================================
ALL TESTS PASSED [OK]
============================================================
```

## Files Modified

1. **tools/workflow/orchestration.py** (Lines 52-128, 134-135)
   - Added `_validate_and_convert_parameters()` method
   - Modified `execute_workflow()` to call validation before creating request

## Benefits

1. **Backward Compatibility**: Legacy parameters (`task`, `deadline`) still work
2. **Clear Migration Path**: Detailed error messages guide users to new format
3. **Automatic Conversion**: Smart parameter conversion with sensible defaults
4. **Better UX**: Helpful error messages instead of cryptic Pydantic errors
5. **Extensible**: Easy to add similar validation for other workflow tools

## Recommendations

1. **Add deprecation warnings**: For future releases, add `warnings.warn()` when legacy parameters are detected
2. **Enhance deadline parsing**: Implement proper date parsing for `deadline` parameter to calculate `total_steps`
3. **Add similar validation**: Apply same pattern to other workflow tools that may have similar parameter issues
4. **Update documentation**: Document the parameter format in tool descriptions

## Verification

The fix has been tested and verified to:
- ✅ Convert legacy parameters correctly
- ✅ Validate new parameters properly
- ✅ Provide clear error messages
- ✅ Maintain backward compatibility
- ✅ Pass all test cases

## Resolution

**Status**: ✅ **FIXED**

The planner tool validation error has been resolved by adding parameter validation and conversion in the orchestration layer. The tool now gracefully handles both legacy and new parameter formats, providing clear error messages when validation fails.
