# Known Issue: toolcall_log_tail Abstract Class

**Status:** Known Issue - Safe to Ignore  
**Severity:** Low  
**Impact:** Tool count shows 29 instead of 30

## Problem

The `toolcall_log_tail` tool fails to load during tool registry initialization with the following error:

```
Can't instantiate abstract class ToolcallLogTail without an implementation for abstract method 'get_system_prompt'
```

## Root Cause

The `ToolcallLogTail` class in `tools/diagnostics/toolcall_log_tail.py` inherits from an abstract base class but does not implement the required `get_system_prompt()` abstract method.

## Impact

- Tool is skipped at load time
- Tool count is 29 instead of 30
- No functional impact - tool was diagnostic-only
- System operates normally

## Workaround

None needed. The tool is diagnostic-only and not required for production operation.

## Fix

To fix this issue, implement the missing abstract method in `tools/diagnostics/toolcall_log_tail.py`:

```python
def get_system_prompt(self) -> str:
    """Return system prompt for this tool."""
    return "Tool for tailing MCP tool call logs"
```

## Related

- Tool registry: `tools/registry.py`
- Error handling: Tool registry silently skips tools that fail to instantiate
- See `ToolRegistry._load_tool()` for error handling logic

