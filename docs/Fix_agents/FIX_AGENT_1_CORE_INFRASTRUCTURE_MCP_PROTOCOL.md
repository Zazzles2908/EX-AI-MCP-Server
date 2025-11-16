# 🔧 FIX AGENT 1: CORE INFRASTRUCTURE & MCP PROTOCOL REMEDIATION

**Agent Type:** Senior Backend Engineer & Protocol Specialist  
**Priority:** P0 (Critical)  
**Estimated Time:** 2-3 weeks  
**Scope:** EX-AI-MCP-Server Core Infrastructure and MCP Protocol Compliance  

---

## 🎯 MISSION OBJECTIVE

Fix critical MCP STDIO bridge implementation issues, core system architecture problems, and protocol compliance violations to achieve full MCP specification compliance while maintaining production stability.

---

## 🚨 CRITICAL ISSUES IDENTIFIED

### 1. MCP STDIO BRIDGE LIFECYCLE BUG (P0-CRITICAL)
**Location:** `src/server.py`, `src/daemon/mcp_server.py`  
**Impact:** Process hangs, undefined client behavior, daemon instability

**Root Cause:** 
```python
# PROBLEMATIC CODE:
async def main():
    stdio_server = mcp.server.stdio(
        asyncio.get_event_loop()
    )
    async with stdio_server as (read_stream, write_stream):
        try:
            app = mcp.create_message_tool_session()
            await app.run(read_stream, write_stream)
            # This function is expected to BLOCK for session lifetime
            # BUT current code has error handling that expects it to return
```

**Required Fix:**
```python
# FIXED CODE:
async def main():
    stdio_server = mcp.server.stdio(
        asyncio.get_event_loop()
    )
    async with stdio_server as (read_stream, write_stream):
        try:
            app = mcp.create_message_tool_session()
            await app.run(read_stream, write_stream)
        except KeyboardInterrupt:
            logger.info("MCP server shutting down gracefully")
            break
        except Exception as e:
            logger.error(f"MCP server error: {e}")
            # CRITICAL: If run() returns unexpectedly, exit process
            logger.critical("MCP session ended unexpectedly - this should not happen")
            sys.exit(1)
```

### 2. JSON-RPC COMPLIANCE VIOLATIONS (P0-CRITICAL)
**Location:** `src/daemon/ws/request_router.py`, `src/daemon/ws/tool_executor.py`  
**Issues Found:**

#### Error Code Non-Compliance
```python
# PROBLEMATIC CODE:
return {"error": {"code": -32000, "message": "Server error"}}
# -32000 is NOT in JSON-RPC reserved range (-32768 to -32000)

# FIXED CODE:
return {"error": {"code": -32603, "message": "Server error"}}
# -32603 is in reserved range for server errors
```

#### ID Validation Failures
```python
# PROBLEMATIC CODE:
if request_id is None:
    return None  # Should reject with proper error

# FIXED CODE:
if request_id is None:
    return {
        "jsonrpc": "2.0",
        "id": null,
        "error": {
            "code": -32600,
            "message": "Invalid Request: missing id"
        }
    }
```

### 3. MESSAGE FRAMING VIOLATIONS (P1-HIGH)
**Location:** `src/daemon/ws/protocol_adapter.py`  
**Issue:** Embedded newlines in JSON messages violating stdio transport

```python
# PROBLEMATIC CODE:
async def send_message(ws, message):
    json_line = json.dumps(message) + "\n"
    # This creates embedded newlines in JSON content

# FIXED CODE:
async def send_message(ws, message):
    json_line = json.dumps(message)
    # Validate no newlines in content
    if "\\n" in json_line:
        json_line = json_line.replace("\\n", "\\\\n")
    await ws.send(json_line + "\n")
```

---

## 🏗️ ARCHITECTURE FIXES REQUIRED

### 1. PROTOCOL STANDARDIZATION
**Issue:** Inconsistent behavior between stdio and WebSocket transports

**Files to Fix:**
- `src/daemon/ws/protocol_adapter.py`
- `src/daemon/mcp_server.py`
- `src/server.py`

**Implementation Plan:**
```python
# Create unified protocol adapter
class MCPProtocolAdapter:
    """Unified adapter for both stdio and WebSocket transports"""
    
    def __init__(self, transport: str):
        self.transport = transport
        self.error_handler = JSONRPCErrorHandler()
    
    async def handle_request(self, request):
        """Process MCP requests with consistent error handling"""
        # Validate JSON-RPC structure
        if not self._validate_jsonrpc(request):
            return self.error_handler.invalid_request(request)
        
        # Apply transport-specific handling
        if self.transport == "stdio":
            return await self._handle_stdio_request(request)
        else:
            return await self._handle_ws_request(request)
    
    def _validate_jsonrpc(self, request):
        """Ensure JSON-RPC 2.0 compliance"""
        required_fields = ["jsonrpc", "method", "id"]
        return all(field in request for field in required_fields)
```

### 2. CONFIGURATION UNIFIED PATTERN
**Issue:** Multiple configuration loading patterns causing inconsistency

**Files to Fix:**
- `config/core.py`
- `config/operations.py`
- Various provider configs

**Implementation:**
```python
# config/unified_config.py
class UnifiedConfig:
    """Single source of truth for all configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config = self._load_config(config_path)
    
    def _load_config(self, path: Optional[str]) -> Dict:
        """Unified configuration loading"""
        config_files = [
            ".env",
            ".env.docker", 
            path or "config/defaults.yaml",
            "config/operations.py"
        ]
        
        merged_config = {}
        for config_file in config_files:
            if os.path.exists(config_file):
                if config_file.endswith('.env'):
                    merged_config.update(self._load_env_file(config_file))
                else:
                    merged_config.update(self._load_yaml_file(config_file))
        
        return merged_config
```

---

## 📋 DETAILED IMPLEMENTATION PLAN

### Phase 1: MCP STDIO Lifecycle Fix (Week 1)
**Day 1-2: Lifecycle Management**
1. Fix `src/server.py` main() function
2. Implement proper session persistence
3. Add error handling for unexpected returns
4. Test with raw stdio clients

**Day 3-4: JSON-RPC Compliance**
1. Update error codes to -32603 standard
2. Implement proper ID validation
3. Fix response structure requirements
4. Add JSON-RPC compliance tests

**Day 5-7: Message Framing**
1. Fix newline handling in stdio transport
2. Implement proper UTF-8 encoding
3. Add stdout/stderr discipline validation
4. Test raw MCP protocol compliance

### Phase 2: Architecture Standardization (Week 2)
**Day 8-10: Protocol Adapter**
1. Create unified MCPProtocolAdapter class
2. Implement transport-specific handlers
3. Add protocol compliance validation
4. Migrate existing adapters

**Day 11-12: Configuration Unification**
1. Create UnifiedConfig class
2. Migrate all configuration sources
3. Add configuration validation
4. Test configuration loading

**Day 13-14: Integration Testing**
1. Create MCP compliance test suite
2. Test both stdio and WebSocket transports
3. Validate end-to-end workflows
4. Performance testing

### Phase 3: Testing & Validation (Week 3)
**Day 15-17: Protocol Testing**
1. Create comprehensive MCP test harness
2. Test raw stdio communication
3. Validate JSON-RPC batch handling
4. Test capability negotiation

**Day 18-19: Integration Testing**
1. Test with external MCP clients
2. Validate tool execution workflows
3. Test error handling scenarios
4. Performance benchmarking

**Day 20-21: Documentation & Handover**
1. Update protocol documentation
2. Create deployment guides
3. Document API changes
4. Prepare for production rollout

---

## 🧪 VALIDATION REQUIREMENTS

### MCP Protocol Compliance Tests
```python
# tests/mcp/test_compliance.py
import pytest
import subprocess
import json

class TestMCPCompliance:
    
    def test_stdio_lifecycle(self):
        """Test MCP stdio session persistence"""
        process = subprocess.Popen(
            ["python", "-m", "exai_mcp_server", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize request
        initialize_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client"}
            }
        }
        
        process.stdin.write(json.dumps(initialize_req) + "\n")
        process.stdin.flush()
        
        # Verify response
        response = json.loads(process.stdout.readline())
        assert response["id"] == 1
        assert response["result"]["protocolVersion"] == "2024-11-05"
        
        # Process should NOT terminate immediately
        assert process.poll() is None, "MCP server should persist session"
        
        process.terminate()
    
    def test_jsonrpc_error_codes(self):
        """Test JSON-RPC compliance for error codes"""
        pass  # Detailed implementation needed
    
    def test_message_framing(self):
        """Test stdio message framing with newlines"""
        pass  # Detailed implementation needed
```

### Transport Compatibility Tests
```python
class TestTransportCompatibility:
    
    async def test_stdio_ws_parity(self):
        """Ensure stdio and WebSocket transports behave identically"""
        pass
    
    async def test_capability_consistency(self):
        """Test capability advertisement across transports"""
        pass
```

---

## 📚 REFERENCE DOCUMENTATION

### MCP Specification References
- **Base Protocol:** https://modelcontextprotocol.io/basic/lifecycle
- **JSON-RPC 2.0:** https://www.jsonrpc.org/specification
- **Transport Specs:** https://modelcontextprotocol.io/basic/transports
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk

### Key MCP Requirements
1. **Session Persistence:** `app.run()` MUST block for session lifetime
2. **JSON-RPC Errors:** Use codes in range -32768 to -32000
3. **ID Handling:** Reject missing IDs with -32600 error
4. **Message Framing:** Newline-delimited JSON for stdio
5. **Capability Negotiation:** Consistent across transports

---

## 🎯 SUCCESS CRITERIA

### Technical Compliance
- [ ] MCP protocol compliance score >95%
- [ ] JSON-RPC 2.0 compliance score >98%
- [ ] STDIO transport compliance score >98%
- [ ] WebSocket transport compliance score >98%
- [ ] Zero lifecycle hanging issues
- [ ] 100% error code compliance

### Integration Quality
- [ ] Both transports behave identically
- [ ] Consistent capability advertisement
- [ ] Unified configuration loading
- [ ] Comprehensive error handling
- [ ] Production-ready stability

### Testing Coverage
- [ ] MCP compliance test suite >90%
- [ ] Integration test coverage >85%
- [ ] Transport compatibility tests
- [ ] Performance benchmarks validated
- [ ] External client compatibility tested

---

## 🚀 DEPLOYMENT CONSIDERATIONS

### Backward Compatibility
- Maintain existing API interfaces
- Provide migration helpers for configuration
- Support legacy clients during transition

### Monitoring & Observability
- Add MCP protocol compliance metrics
- Implement session lifecycle monitoring
- Track error rate and types
- Monitor transport performance

### Rollback Strategy
- Keep previous version tag available
- Document rollback procedures
- Test rollback process thoroughly
- Monitor for issues post-deployment

---

## 📞 ESCALATION PROCEDURES

If issues arise during implementation:

1. **Protocol Violations:** Immediately stop and fix
2. **Livelock/Crash:** Rollback to previous version
3. **Performance Regression:** Profile and optimize
4. **Client Compatibility:** Document workarounds

**Contact:** Senior Protocol Engineer for MCP-specific issues  
**Escalation Path:** Protocol Team Lead → Architecture Review Board

---

**FIX AGENT 1 DELIVERABLES:**
- MCP protocol compliance (95%+)
- JSON-RPC 2.0 compliance (98%+)
- Unified architecture implementation
- Comprehensive test suite
- Production deployment readiness

**Ready for implementation when P0 issues are resolved!**
