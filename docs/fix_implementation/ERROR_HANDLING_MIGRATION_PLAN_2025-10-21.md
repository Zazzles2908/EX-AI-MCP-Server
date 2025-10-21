# Error Handling Migration Plan
**Date:** 2025-10-21  
**Status:** 1/8 Complete (12.5%) | 7 Remaining

---

## Executive Summary

Complete migration of error handling in `ws_server.py` to use the standardized error handling infrastructure created in Week 2 Fix #8. This addresses the baseline fix priority and ensures consistent error responses across the entire system.

---

## Migration Status

### ✅ Completed (1/8)
1. **Line 686-725:** Tool not found error - MIGRATED ✅
   - Uses `create_error_response()` and `log_error()`
   - Proper error code: `ErrorCode.TOOL_NOT_FOUND`
   - Appropriate logging level: WARNING

### 🔄 Remaining (7/8)

#### Location 1: Global Concurrency Limit (Line 893)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "OVER_CAPACITY", "message": f"{capacity_type} concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.OVER_CAPACITY,
    message=f"{capacity_type} concurrency limit reached; retry soon",
    request_id=req_id,
    details={"retry_after": RETRY_AFTER_SECS, "capacity_type": capacity_type}
)
log_error(
    ErrorCode.OVER_CAPACITY,
    f"{capacity_type} concurrency limit reached",
    request_id=req_id
)
await _safe_send(ws, error_response)
```

**Complexity:** Low  
**Risk:** Low - straightforward replacement

---

#### Location 2: Provider Concurrency Limit (Line 915)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "OVER_CAPACITY", "message": f"{prov_key} concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.OVER_CAPACITY,
    message=f"{prov_key} concurrency limit reached; retry soon",
    request_id=req_id,
    details={"retry_after": RETRY_AFTER_SECS, "provider": prov_key}
)
log_error(
    ErrorCode.OVER_CAPACITY,
    f"Provider {prov_key} concurrency limit reached",
    request_id=req_id
)
await _safe_send(ws, error_response)
```

**Complexity:** Low  
**Risk:** Low - straightforward replacement

---

#### Location 3: Session Concurrency Limit (Line 940)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "OVER_CAPACITY", "message": "Session concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.OVER_CAPACITY,
    message="Session concurrency limit reached; retry soon",
    request_id=req_id,
    details={"retry_after": RETRY_AFTER_SECS, "session_id": session_id}
)
log_error(
    ErrorCode.OVER_CAPACITY,
    f"Session {session_id} concurrency limit reached",
    request_id=req_id
)
await _safe_send(ws, error_response)
```

**Complexity:** Low  
**Risk:** Low - straightforward replacement

---

#### Location 4: Tool Timeout (Progress Loop) (Line 1088)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "TIMEOUT", "message": f"call_tool exceeded {tool_timeout}s"}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.TIMEOUT,
    message=f"call_tool exceeded {tool_timeout}s",
    request_id=req_id,
    details={"timeout_seconds": tool_timeout, "tool_name": name}
)
log_error(
    ErrorCode.TIMEOUT,
    f"Tool '{name}' exceeded timeout of {tool_timeout}s",
    request_id=req_id
)
await _safe_send(ws, error_response)
```

**Complexity:** Low  
**Risk:** Low - straightforward replacement

---

#### Location 5: Call Timeout (Outer Exception Handler) (Line 1238)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "TIMEOUT", "message": f"call_tool exceeded {CALL_TIMEOUT}s"}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.TIMEOUT,
    message=f"call_tool exceeded {CALL_TIMEOUT}s",
    request_id=req_id,
    details={"timeout_seconds": CALL_TIMEOUT, "tool_name": name, "duration": latency_timeout}
)
log_error(
    ErrorCode.TIMEOUT,
    f"Tool '{name}' exceeded call timeout of {CALL_TIMEOUT}s (duration: {latency_timeout:.2f}s)",
    request_id=req_id
)
await _safe_send(ws, error_response)
```

**Complexity:** Low  
**Risk:** Low - straightforward replacement

---

#### Location 6: Tool Execution Error (Line 1285)
**Current Code:**
```python
await _safe_send(ws, {
    "op": "call_tool_res",
    "request_id": req_id,
    "error": {"code": "EXEC_ERROR", "message": str(e)}
})
```

**Migration Target:**
```python
error_response = create_error_response(
    code=ErrorCode.INTERNAL_ERROR,  # Note: EXEC_ERROR maps to INTERNAL_ERROR
    message=str(e),
    request_id=req_id,
    details={"tool_name": name, "error_type": type(e).__name__}
)
log_error(
    ErrorCode.INTERNAL_ERROR,
    f"Tool '{name}' execution failed: {str(e)}",
    request_id=req_id,
    exc_info=e
)
await _safe_send(ws, error_response)
```

**Complexity:** Medium  
**Risk:** Medium - Need to verify EXEC_ERROR → INTERNAL_ERROR mapping is correct

---

#### Location 7: Size Limit Validation (Line 660-669)
**Current Code:**
```python
error_response = create_error_response(
    code=ErrorCode.OVER_CAPACITY,
    message=f"Request too large: {msg_size} bytes exceeds limit of {tool_call_max} bytes",
    request_id=msg.get("request_id"),
    details={"actual_size": msg_size, "limit": tool_call_max}
)
log_error(
    ErrorCode.OVER_CAPACITY,
    f"Oversized request rejected: {msg_size} bytes (limit: {tool_call_max})",
    request_id=msg.get("request_id")
)
```

**Status:** ✅ ALREADY MIGRATED (Week 2 Fix #10)  
**Complexity:** N/A  
**Risk:** N/A

---

## Migration Sequence

### Phase 1: Simple Replacements (Locations 1-5)
**Estimated Time:** 30-45 minutes  
**Risk Level:** Low

1. Migrate Location 1 (Global concurrency)
2. Migrate Location 2 (Provider concurrency)
3. Migrate Location 3 (Session concurrency)
4. Migrate Location 4 (Tool timeout - progress loop)
5. Migrate Location 5 (Call timeout - outer handler)

**Testing After Phase 1:**
- Trigger each concurrency limit
- Trigger tool timeouts
- Verify error responses match expected format
- Check logs for appropriate severity levels

### Phase 2: Complex Replacement (Location 6)
**Estimated Time:** 15-20 minutes  
**Risk Level:** Medium

1. Verify EXEC_ERROR → INTERNAL_ERROR mapping
2. Migrate Location 6 (Tool execution error)
3. Add exc_info parameter for stack traces

**Testing After Phase 2:**
- Trigger tool execution errors
- Verify error responses include proper details
- Check logs include stack traces
- Confirm error code mapping is correct

---

## Testing Strategy

### Unit Testing
- Test each error location independently
- Verify error response format matches MCP protocol
- Check logging levels are appropriate
- Validate error details are included

### Integration Testing
- Trigger actual errors in running system
- Verify client receives proper error responses
- Check logs for consistency
- Validate retry_after hints work correctly

### Regression Testing
- Ensure existing error handling still works
- Verify no breaking changes to error format
- Check backward compatibility with clients

---

## Success Criteria

- ✅ All 7 locations migrated to standardized error handling
- ✅ Error responses follow consistent format
- ✅ Logging levels are appropriate (ERROR for server, WARNING for execution, INFO for client)
- ✅ Error details include relevant context
- ✅ No regressions in existing error handling
- ✅ All tests pass
- ✅ EXAI expert validation confirms migration is correct

---

## Risk Mitigation

### Risk 1: Breaking Changes to Error Format
**Mitigation:** 
- Maintain backward compatibility with existing error codes
- Test with actual clients before deployment
- Document any format changes

### Risk 2: Incorrect Error Code Mapping
**Mitigation:**
- Verify EXEC_ERROR → INTERNAL_ERROR mapping with EXAI
- Review error code semantics
- Test with actual error scenarios

### Risk 3: Missing Error Details
**Mitigation:**
- Include all relevant context in error details
- Review each error location for required information
- Test error responses for completeness

---

## Next Steps

1. **Immediate:** Begin Phase 1 migration (Locations 1-5)
2. **After Phase 1:** Test all concurrency and timeout errors
3. **After Testing:** Proceed to Phase 2 (Location 6)
4. **After Phase 2:** Comprehensive testing of all error scenarios
5. **Final:** EXAI expert validation of complete migration

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-21  
**Author:** AI Agent

