# EX-AI-MCP-Server Test Suite

## Overview

This directory contains comprehensive test suites for the EX-AI-MCP-Server, covering MCP protocol validation, system stability, performance benchmarks, and configuration validation.

## Quick Start

### Run All Tests
```bash
python tests/validation/comprehensive_system_test.py
```

### Run Individual Test Suites

#### MCP Protocol Tests
```bash
# Full MCP validation suite
python tests/protocol/mcp/mcp_comprehensive_test.py

# Kimi-specific tests
python tests/protocol/mcp/test_kimi_complete_mcp.py

# Proper MCP client
python tests/protocol/mcp/test_kimi_mcp_proper.py
```

#### Configuration Validation
```bash
# Validate all configuration fixes
python tests/validation/configuration_validation_test.py
```

#### Stability Tests
```bash
# Async event loop stability
python tests/protocol/mcp_async_stability_test.py

# Interactive protocol validator
python tests/validation/realtime_protocol_validator.py
```

#### Performance Benchmarks
```bash
# Routing performance benchmarks
python tests/benchmarks/routing_performance_bench.py
```

## Expected Results

### Configuration Validation
```
Total Validations: 5
Passed: 5
Failed: 0
Success Rate: 100.0%

✅ ALL CONFIGURATION VALIDATIONS PASSED!
```

### MCP Protocol Tests
```
Total Tests: 5
Passed: 5
Failed: 0
Success Rate: 100.0%

🎉 ALL TESTS PASSED!
```

## Documentation

- **MCP Protocol Guide:** `docs/protocol/MCP_PROTOCOL_GUIDE.md`
- **Complete Report:** `docs/reports/COMPREHENSIVE_MCP_FIX_COMPLETE_REPORT.md`

---

**Status:** All Tests Operational ✅
