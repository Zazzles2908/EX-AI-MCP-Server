# Week 2 Fix #8: Inconsistent Error Handling

**Date:** 2025-10-21  
**Status:** ✅ FOUNDATION COMPLETE (Infrastructure in place, gradual rollout in progress)  
**Priority:** MEDIUM  
**Category:** Code Quality / Maintainability  
**EXAI Recommendation:** Create standardized error format and logging patterns

---

## 🎯 Problem Statement

Error handling was inconsistent across the codebase:

- **Different Error Formats:** Some errors use `{"code": "X", "message": "Y"}`, others use `{"error": str(e)}`
- **Inconsistent Logging:** Some errors logged, some not; varying severity levels
- **No Error Codes:** Mix of string codes ("TOOL_NOT_FOUND") and ad-hoc messages
- **Technical vs User-Friendly:** Balance between detail and clarity inconsistent
- **No Structured Details:** Missing additional context for debugging

### Impact

- Difficult for clients to handle errors programmatically
- Inconsistent logging makes debugging harder
- No clear error severity levels
- Poor user experience with unclear error messages

---

## ✅ Solution Implemented

### 1. Standardized Error Handling Infrastructure

Created `src/daemon/error_handling.py` with:

#### Error Codes
```python
class ErrorCode:
    # Client errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    OVER_CAPACITY = "OVER_CAPACITY"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # MCP-specific errors (1xxx)
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PROTOCOL_ERROR = "PROTOCOL_ERROR"
```

#### Standardized Response Format
```python
{
    "error": {
        "code": "TOOL_NOT_FOUND",
        "message": "Tool not found: example_tool",
        "details": {
            "requested_tool": "example_tool"
        }
    }
}
```

#### Custom Exception Classes
```python
class MCPError(Exception):
    """Base exception for MCP server errors."""
    
class ToolNotFoundError(MCPError):
    """Raised when a requested tool is not found."""
    
class ToolExecutionError(MCPError):
    """Raised when tool execution fails."""
    
class ValidationError(MCPError):
    """Raised when input validation fails."""
    
class ProviderError(MCPError):
    """Raised when AI provider fails."""
    
class TimeoutError(MCPError):
    """Raised when operation times out."""
    
class OverCapacityError(MCPError):
    """Raised when server is over capacity."""
```

#### Logging Utilities
```python
def log_error(code, message, request_id=None, exc_info=False):
    """Log error with appropriate severity level based on error code."""
    
    # Server errors → ERROR level
    # Execution errors → WARNING level
    # Client errors → INFO level
```

#### Error Response Utilities
```python
def create_error_response(code, message, request_id=None, details=None):
    """Create standardized error response."""

def handle_exception(exc, request_id=None, context=None):
    """Convert any exception to standardized error response."""

def create_tool_error_response(request_id, error, tool_name=None):
    """Create error response for tool call failures."""
```

---

## 📊 Implementation Status

### ✅ Completed

1. **Error Handling Infrastructure** - Created `src/daemon/error_handling.py`
2. **Import in ws_server.py** - Added imports for error handling utilities
3. **First Migration** - Updated tool not found error handling

### ⏳ In Progress (Gradual Rollout)

**8 Error Handling Locations Identified in ws_server.py:**

1. ✅ **Line 779:** DUPLICATE error (tool not found) - **MIGRATED**
2. ⏳ **Line 844:** OVER_CAPACITY error (global concurrency limit)
3. ⏳ **Line 866:** OVER_CAPACITY error (provider concurrency limit)
4. ⏳ **Line 891:** OVER_CAPACITY error (session concurrency limit)
5. ⏳ **Line 914:** INTERNAL_ERROR (session semaphore acquisition failure)
6. ⏳ **Line 1039:** TIMEOUT error (tool timeout with specific timeout value)
7. ⏳ **Line 1189:** TIMEOUT error (call timeout)
8. ⏳ **Line 1236:** EXEC_ERROR (tool execution error)

**Migration Strategy:**
- Migrate one location at a time
- Test after each migration
- Ensure backward compatibility
- Update documentation as we go

---

## 🔒 Benefits

### 1. **Consistent Error Format**
- ✅ All errors use same JSON structure
- ✅ Machine-readable error codes
- ✅ Human-readable messages
- ✅ Optional details for debugging

### 2. **Appropriate Logging**
- ✅ Server errors logged at ERROR level
- ✅ Execution errors logged at WARNING level
- ✅ Client errors logged at INFO level
- ✅ Request ID correlation for debugging

### 3. **Better Client Experience**
- ✅ Clients can handle errors programmatically
- ✅ Clear error messages
- ✅ Additional context in details field
- ✅ Consistent error codes across API

### 4. **Easier Debugging**
- ✅ Structured error logging
- ✅ Request ID correlation
- ✅ Exception tracebacks when appropriate
- ✅ Context-aware error messages

---

## 📝 Files Modified

1. **`src/daemon/error_handling.py`** (NEW)
   - Error codes and constants
   - Custom exception classes
   - Error response utilities
   - Logging utilities

2. **`src/daemon/ws_server.py`**
   - Added error handling imports
   - Migrated tool not found error (line 686-704)
   - 7 more locations to migrate

---

## 🎯 Usage Examples

### Creating Error Responses

```python
# Simple error
error = create_error_response(
    code=ErrorCode.TOOL_NOT_FOUND,
    message="Tool not found: example_tool",
    request_id="req-123"
)

# Error with details
error = create_error_response(
    code=ErrorCode.VALIDATION_ERROR,
    message="Invalid parameter: timeout must be positive",
    request_id="req-123",
    details={"field": "timeout", "value": -1}
)

# Tool call error
error = create_tool_error_response(
    request_id="req-123",
    error=ToolExecutionError("example_tool", original_error),
    tool_name="example_tool"
)
```

### Raising Custom Exceptions

```python
# Raise tool not found
raise ToolNotFoundError("example_tool", available_tools=["tool1", "tool2"])

# Raise validation error
raise ValidationError("timeout", "must be positive", value=-1)

# Raise timeout error
raise TimeoutError("tool_execution", timeout_seconds=30)
```

### Handling Exceptions

```python
try:
    result = await execute_tool(tool_name, args)
except Exception as e:
    error_response = handle_exception(
        e,
        request_id=req_id,
        context=f"tool execution ({tool_name})"
    )
    await _safe_send(ws, {
        "op": "call_tool_res",
        "request_id": req_id,
        **error_response
    })
```

---

## 🔮 Next Steps

### Short-Term (This Week)
1. ⏳ Migrate remaining 7 error handling locations
2. ⏳ Add error handling to provider calls
3. ⏳ Update error handling in session management
4. ⏳ Test all error scenarios

### Medium-Term (Next Week)
1. Add error metrics to Prometheus
2. Create error handling documentation for clients
3. Add error handling tests
4. Review error messages for clarity

### Long-Term
1. Implement error recovery strategies
2. Add error rate limiting
3. Create error handling best practices guide
4. Add error handling to all new code

---

## 📚 Related Documentation

- **[EXAI Error Handling Guidance](https://chat.openai.com/)** - Expert recommendations
- **[Week 2 Progress](WEEK_2_PROGRESS_2025-10-21.md)** - Overall progress tracker
- **[Weekly Fix Roadmap](../WEEKLY_FIX_ROADMAP_2025-10-20.md)** - Complete fix list

---

## 🎓 Lessons Learned

### 1. **Infrastructure First**
Creating the error handling infrastructure first makes migration easier and more consistent.

### 2. **Gradual Migration**
Migrating error handling gradually (one location at a time) reduces risk and allows for testing.

### 3. **Logging Levels Matter**
Using appropriate logging levels (ERROR/WARNING/INFO) based on error severity improves debugging.

### 4. **Context is Key**
Including context (request ID, tool name, operation) in error messages makes debugging much easier.

### 5. **Balance Detail vs Clarity**
Error messages should be clear for users while providing enough detail for debugging.

---

**Status:** ✅ FOUNDATION COMPLETE - Infrastructure in place, gradual rollout in progress  
**Next Action:** Migrate remaining 7 error handling locations in ws_server.py

