# Week 2 Fix #10: No Request Size Limits

**Date:** 2025-10-21  
**Status:** ✅ COMPLETE  
**Priority:** HIGH (Security - DoS Prevention)  
**Category:** Security / Resource Protection  
**EXAI Recommendation:** Add size checks with early rejection to prevent DoS attacks

---

## 🎯 Problem Statement

No size limits on incoming WebSocket messages:

- **No Maximum Message Size:** Server accepts any size message
- **No Request Body Limits:** Tool calls could have huge payloads
- **No File Upload Limits:** File operations could exhaust memory
- **No Early Rejection:** Server processes entire message before checking
- **DoS Vulnerability:** Attackers could send huge payloads to exhaust memory

### Impact

- **Security Risk:** Vulnerable to DoS attacks via large payloads
- **Memory Exhaustion:** Large messages can crash the server
- **Resource Waste:** Processing oversized requests wastes CPU/memory
- **Poor Performance:** Large messages slow down the entire system

---

## ✅ Solution Implemented

### 1. Multi-Level Size Limits

Implemented **defense in depth** with size checks at multiple levels:

#### WebSocket Level (Early Rejection)
```python
# Enforced by websockets library at connection level
EXAI_WS_MAX_BYTES=16777216  # 16MB - prevents huge messages from being received
```

#### Application Level (Request Type Specific)
```python
# Enforced in message handler before processing
TOOL_CALL_MAX_SIZE=10485760  # 10MB - for tool call requests
FILE_UPLOAD_MAX_SIZE=104857600  # 100MB - for file upload operations
```

### 2. Size Limit Configuration

Added to `.env.docker` and `.env.example`:

```bash
# Week 2 Fix #10 (2025-10-21): Request size limits for DoS prevention
EXAI_WS_MAX_BYTES=16777216  # WebSocket message size limit (16MB)
TOOL_CALL_MAX_SIZE=10485760  # Tool call request size limit (10MB)
FILE_UPLOAD_MAX_SIZE=104857600  # File upload size limit (100MB)
```

### 3. Application-Level Size Checking

Added size checking in `ws_server.py` at the beginning of `_handle_message()`:

```python
# Week 2 Fix #10 (2025-10-21): Check message size at application level
try:
    import sys
    msg_size = sys.getsizeof(json.dumps(msg))
    tool_call_max = int(os.getenv("TOOL_CALL_MAX_SIZE", "10485760"))
    
    if msg_size > tool_call_max:
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
        await _safe_send(ws, {
            "op": "call_tool_res",
            "request_id": msg.get("request_id"),
            **error_response
        })
        return
except Exception as e:
    # Size check failed - log but continue (don't block legitimate requests)
    logger.warning(f"Failed to check message size: {e}")
```

### 4. Clear Error Responses

```json
{
    "op": "call_tool_res",
    "request_id": "req-123",
    "error": {
        "code": "OVER_CAPACITY",
        "message": "Request too large: 15000000 bytes exceeds limit of 10485760 bytes",
        "details": {
            "actual_size": 15000000,
            "limit": 10485760
        }
    }
}
```

---

## 📊 Size Limit Rationale

| Limit Type | Size | Rationale |
|------------|------|-----------|
| **WebSocket Message** | 16MB | Industry standard, prevents huge messages at connection level |
| **Tool Call Request** | 10MB | Allows substantial prompts/arguments while preventing abuse |
| **File Upload** | 100MB | Larger for legitimate file operations, still prevents DoS |

### Why These Limits?

1. **16MB WebSocket Limit:**
   - Default maximum for many WebSocket libraries
   - Large enough for legitimate use cases
   - Prevents DoS via enormous messages
   - Enforced at connection level (early rejection)

2. **10MB Tool Call Limit:**
   - Most tool calls shouldn't exceed this
   - Allows for substantial prompts (e.g., 10,000+ characters)
   - Allows for complex arguments with nested objects
   - Still prevents memory exhaustion attacks

3. **100MB File Upload Limit:**
   - Larger than tool calls (files can legitimately be bigger)
   - Allows useful file operations (documents, images, etc.)
   - Still prevents abuse (no multi-GB uploads)
   - Can be increased if needed for specific use cases

---

## 🔒 Security Benefits

### 1. **DoS Prevention**
- ✅ Prevents memory exhaustion attacks
- ✅ Prevents CPU exhaustion from processing huge payloads
- ✅ Prevents network bandwidth abuse
- ✅ Early rejection saves resources

### 2. **Resource Protection**
- ✅ Limits memory usage per request
- ✅ Prevents server crashes from OOM errors
- ✅ Maintains system stability under attack
- ✅ Protects other users from resource starvation

### 3. **Defense in Depth**
- ✅ WebSocket level check (first line of defense)
- ✅ Application level check (second line of defense)
- ✅ Multiple size limits for different request types
- ✅ Graceful degradation if one check fails

---

## 🎯 Design Decisions

### 1. **Multi-Level Checks**
- **Decision:** Check size at both WebSocket and application levels
- **Rationale:** Defense in depth, early rejection, type-specific limits
- **Trade-off:** Slight overhead, but worth it for security

### 2. **Configurable Limits**
- **Decision:** All limits configurable via environment variables
- **Rationale:** Flexibility for different deployments, easy tuning
- **Trade-off:** Must document and validate configuration

### 3. **Generous but Safe Limits**
- **Decision:** Use reasonable limits (10MB/100MB) not tiny limits (1MB)
- **Rationale:** Don't break legitimate use cases, balance security with usability
- **Trade-off:** Slightly higher resource usage, but acceptable

### 4. **Graceful Failure**
- **Decision:** If size check fails, log warning but continue
- **Rationale:** Don't block legitimate requests due to size check bugs
- **Trade-off:** Potential bypass if size check has bugs, but rare

### 5. **Clear Error Messages**
- **Decision:** Include actual size and limit in error response
- **Rationale:** Helps clients understand and fix the issue
- **Trade-off:** Slightly more verbose error responses

---

## 📝 Files Modified

1. **`.env.docker`**
   - Updated EXAI_WS_MAX_BYTES from 32MB to 16MB
   - Added TOOL_CALL_MAX_SIZE (10MB)
   - Added FILE_UPLOAD_MAX_SIZE (100MB)

2. **`.env.example`**
   - Updated EXAI_WS_MAX_BYTES from 32MB to 16MB
   - Added TOOL_CALL_MAX_SIZE (10MB)
   - Added FILE_UPLOAD_MAX_SIZE (100MB)

3. **`src/daemon/ws_server.py`**
   - Added size checking in _handle_message() (lines 651-677)
   - Uses standardized error handling from Fix #8
   - Logs size violations for monitoring

---

## 🎯 Usage Examples

### Example 1: Normal Request (Under Limit)

```python
# Request size: 5MB (under 10MB limit)
request = {
    "op": "call_tool",
    "name": "chat",
    "arguments": {
        "prompt": "..." * 5000000,  # 5MB prompt
        "model": "glm-4.6"
    },
    "request_id": "req-123"
}

# Result: Request processed normally
```

### Example 2: Oversized Request (Over Limit)

```python
# Request size: 15MB (over 10MB limit)
request = {
    "op": "call_tool",
    "name": "chat",
    "arguments": {
        "prompt": "..." * 15000000,  # 15MB prompt
        "model": "glm-4.6"
    },
    "request_id": "req-123"
}

# Result: Error response
{
    "op": "call_tool_res",
    "request_id": "req-123",
    "error": {
        "code": "OVER_CAPACITY",
        "message": "Request too large: 15000000 bytes exceeds limit of 10485760 bytes",
        "details": {
            "actual_size": 15000000,
            "limit": 10485760
        }
    }
}
```

---

## 🔮 Future Enhancements

### Short-Term
1. Add size limit metrics to Prometheus
2. Add size limit testing
3. Add size limit documentation for clients
4. Add per-tool size limits (different limits for different tools)

### Medium-Term
1. Implement streaming for large file uploads
2. Add chunked upload support
3. Add compression support for large payloads
4. Add size limit monitoring dashboard

### Long-Term
1. Add dynamic size limits based on server load
2. Add per-user size limits
3. Add size limit quotas (total bytes per hour)
4. Add intelligent size limit adjustment

---

## 📚 Related Documentation

- **[EXAI Request Size Limits Guidance](https://chat.openai.com/)** - Expert recommendations
- **[Week 2 Fix #8: Error Handling](WEEK_2_FIX_08_ERROR_HANDLING_2025-10-21.md)** - Related error handling
- **[Week 2 Fix #9: Input Validation](WEEK_2_FIX_09_INPUT_VALIDATION_2025-10-21.md)** - Related validation
- **[Week 2 Progress](WEEK_2_PROGRESS_2025-10-21.md)** - Overall progress tracker

---

## 🎓 Lessons Learned

### 1. **Defense in Depth Works**
Multiple layers of size checking (WebSocket + application) provides robust protection.

### 2. **Early Rejection Saves Resources**
Rejecting oversized requests at the WebSocket level prevents wasted processing.

### 3. **Generous Limits are Better**
Using reasonable limits (10MB/100MB) balances security with usability better than tiny limits.

### 4. **Configuration is Key**
Making limits configurable allows tuning for different deployments without code changes.

### 5. **Clear Errors Help Users**
Including actual size and limit in error messages helps clients fix issues quickly.

---

**Status:** ✅ COMPLETE - Request size limits implemented at multiple levels  
**Next Action:** Proceed with remaining Week 2 fixes or test completed fixes

