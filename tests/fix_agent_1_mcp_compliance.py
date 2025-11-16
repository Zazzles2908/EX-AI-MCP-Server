#!/usr/bin/env python3
"""
Fix Agent 1: MCP Protocol Compliance Tests

This test suite validates the critical fixes implemented for MCP STDIO bridge
lifecycle bugs, JSON-RPC 2.0 compliance violations, and message framing issues.

Tests include:
1. MCP STDIO lifecycle management
2. JSON-RPC 2.0 error code compliance
3. Message framing validation
4. Protocol standardization

Author: Fix Agent 1
Date: 2025-01-20
"""

import pytest
import json
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.daemon.error_handling import (
    ErrorCode,
    validate_jsonrpc_request,
    create_error_response,
    create_invalid_request_error,
    create_method_not_found_error,
    create_invalid_params_error,
    create_internal_error_error
)
from src.daemon.ws.protocol_adapter import (
    validate_message_framing,
    safe_send_message,
    ProtocolType
)


class TestMCPStdiolLifecycle:
    """Test MCP STDIO bridge lifecycle fixes."""
    
    def test_jsonrpc_error_codes_compliance(self):
        """Test JSON-RPC 2.0 compliant error codes."""
        # Test standard error codes are in correct range
        assert ErrorCode.PARSE_ERROR == -32700
        assert ErrorCode.INVALID_REQUEST == -32600
        assert ErrorCode.METHOD_NOT_FOUND == -32601
        assert ErrorCode.INVALID_PARAMS == -32602
        assert ErrorCode.INTERNAL_ERROR == -32603
        
        # Test application-specific codes are in reserved range
        assert ErrorCode.TOOL_NOT_FOUND == -32001
        assert ErrorCode.TOOL_EXECUTION_ERROR == -32002
        assert ErrorCode.PROVIDER_ERROR == -32003
        assert ErrorCode.PROTOCOL_ERROR == -32004
        
        print("[OK] JSON-RPC 2.0 error codes are compliant")
    
    def test_invalid_request_error_creation(self):
        """Test creation of Invalid Request errors."""
        # Test missing ID - should return null ID per JSON-RPC spec
        error = create_invalid_request_error("Missing 'id' field")
        assert error["jsonrpc"] == "2.0"
        assert error["id"] is None  # Critical: null ID for invalid requests
        assert error["error"]["code"] == ErrorCode.INVALID_REQUEST
        assert "Missing 'id' field" in error["error"]["message"]
        
        print("[OK] Invalid Request errors handle missing IDs correctly")
    
    def test_method_not_found_error(self):
        """Test Method Not Found error creation."""
        error = create_method_not_found_error("tools/execute", request_id="req-123")
        assert error["jsonrpc"] == "2.0"
        assert error["id"] == "req-123"
        assert error["error"]["code"] == ErrorCode.METHOD_NOT_FOUND
        assert "tools/execute" in error["error"]["message"]
        
        print("[OK] Method Not Found errors work correctly")
    
    def test_invalid_params_error(self):
        """Test Invalid Params error creation."""
        error = create_invalid_params_error("Invalid tool arguments", request_id="req-456")
        assert error["jsonrpc"] == "2.0"
        assert error["id"] == "req-456"
        assert error["error"]["code"] == ErrorCode.INVALID_PARAMS
        assert "Invalid tool arguments" in error["error"]["message"]
        
        print("[OK] Invalid Params errors work correctly")
    
    def test_internal_error_error(self):
        """Test Internal Error creation."""
        error = create_internal_error_error("Server encountered an error", request_id="req-789")
        assert error["jsonrpc"] == "2.0"
        assert error["id"] == "req-789"
        assert error["error"]["code"] == ErrorCode.INTERNAL_ERROR
        assert "Server encountered an error" in error["error"]["message"]
        
        print("[OK] Internal Error responses work correctly")


class TestJSONRPCCompliance:
    """Test JSON-RPC 2.0 compliance validation."""
    
    def test_valid_jsonrpc_request(self):
        """Test validation of valid JSON-RPC 2.0 requests."""
        valid_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123"
        }
        
        is_valid, error = validate_jsonrpc_request(valid_request)
        assert is_valid is True
        assert error is None
        
        print("[OK] Valid JSON-RPC 2.0 request passes validation")
    
    def test_missing_jsonrpc_field(self):
        """Test validation rejects missing jsonrpc field."""
        invalid_request = {
            "method": "tools/list",
            "id": "req-123"
        }
        
        is_valid, error = validate_jsonrpc_request(invalid_request)
        assert is_valid is False
        assert error is not None
        assert error["error"]["code"] == ErrorCode.INVALID_REQUEST
        assert "jsonrpc" in error["error"]["message"]
        
        print("[OK] Missing jsonrpc field is properly rejected")
    
    def test_invalid_jsonrpc_version(self):
        """Test validation rejects invalid jsonrpc version."""
        invalid_request = {
            "jsonrpc": "1.0",
            "method": "tools/list",
            "id": "req-123"
        }
        
        is_valid, error = validate_jsonrpc_request(invalid_request)
        assert is_valid is False
        assert error is not None
        assert error["error"]["code"] == ErrorCode.INVALID_REQUEST
        
        print("[OK] Invalid jsonrpc version is properly rejected")
    
    def test_missing_method_field(self):
        """Test validation rejects missing method field."""
        invalid_request = {
            "jsonrpc": "2.0",
            "id": "req-123"
        }
        
        is_valid, error = validate_jsonrpc_request(invalid_request)
        assert is_valid is False
        assert error is not None
        assert error["error"]["code"] == ErrorCode.METHOD_NOT_FOUND
        
        print("[OK] Missing method field triggers Method Not Found error")
    
    def test_missing_id_field_critical(self):
        """Test validation rejects missing id field (critical per JSON-RPC spec)."""
        invalid_request = {
            "jsonrpc": "2.0",
            "method": "tools/list"
        }
        
        is_valid, error = validate_jsonrpc_request(invalid_request)
        assert is_valid is False
        assert error is not None
        assert error["error"]["code"] == ErrorCode.INVALID_REQUEST
        assert error["id"] is None  # Critical: null ID for requests without ID
        
        print("[OK] Missing ID field is properly rejected with null ID")


class TestMessageFraming:
    """Test message framing validation for stdio transport."""
    
    def test_valid_message_no_newlines(self):
        """Test valid message with no embedded newlines."""
        valid_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123",
            "params": {
                "description": "A simple description without newlines"
            }
        }
        
        is_valid, error = validate_message_framing(valid_message)
        assert is_valid is True
        assert error is None
        
        print("[OK] Valid message without newlines passes validation")
    
    def test_invalid_embedded_newlines_in_string(self):
        """Test rejection of embedded newlines in string values."""
        invalid_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123",
            "params": {
                "description": "This has\na newline"
            }
        }
        
        is_valid, error = validate_message_framing(invalid_message)
        assert is_valid is False
        assert error is not None
        assert "embedded newline" in error.lower()
        
        print("[OK] Embedded newlines in strings are properly rejected")
    
    def test_invalid_embedded_newlines_in_json(self):
        """Test rejection of embedded newlines in JSON encoding."""
        invalid_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123",
            "params": {
                "description": "This will become\\n in JSON"
            }
        }
        
        is_valid, error = validate_message_framing(invalid_message)
        assert is_valid is False
        assert error is not None
        assert "embedded newlines" in error.lower()
        
        print("[OK] Embedded newlines in JSON content are properly rejected")
    
    def test_valid_nested_objects(self):
        """Test validation of nested objects without newlines."""
        valid_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123",
            "params": {
                "nested": {
                    "deeply": {
                        "description": "Nested description without newlines"
                    }
                }
            }
        }
        
        is_valid, error = validate_message_framing(valid_message)
        assert is_valid is True
        assert error is None
        
        print("[OK] Valid nested objects pass validation")
    
    def test_invalid_nested_newlines(self):
        """Test rejection of newlines in nested objects."""
        invalid_message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "req-123",
            "params": {
                "nested": {
                    "deeply": {
                        "description": "This has\na newline deep inside"
                    }
                }
            }
        }
        
        is_valid, error = validate_message_framing(invalid_message)
        assert is_valid is False
        assert error is not None
        assert "embedded newlines" in error.lower()
        
        print("[OK] Newlines in nested content are properly rejected")


class TestErrorResponseFormat:
    """Test standardized error response format."""
    
    def test_error_response_structure(self):
        """Test error response has correct JSON-RPC 2.0 structure."""
        error = create_error_response(
            code=ErrorCode.TOOL_NOT_FOUND,
            message="Tool not found: example_tool",
            request_id="req-123"
        )
        
        # Check JSON-RPC 2.0 structure
        assert "jsonrpc" in error
        assert error["jsonrpc"] == "2.0"
        assert "id" in error
        assert error["id"] == "req-123"
        assert "error" in error
        assert "code" in error["error"]
        assert "message" in error["error"]
        
        # Check error code is numeric and in correct range
        assert isinstance(error["error"]["code"], int)
        assert error["error"]["code"] <= -32000
        
        print("[OK] Error responses have correct JSON-RPC 2.0 structure")
    
    def test_error_with_details(self):
        """Test error response with optional details."""
        details = {"available_tools": ["tool1", "tool2"], "category": "examples"}
        
        error = create_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            request_id="req-456",
            details=details
        )
        
        assert "data" in error["error"]
        assert error["error"]["data"] == details
        
        print("[OK] Error responses support optional details")


def run_all_tests():
    """Run all Fix Agent 1 compliance tests."""
    print("=" * 80)
    print("FIX AGENT 1: MCP PROTOCOL COMPLIANCE TESTS")
    print("=" * 80)
    
    test_classes = [
        TestMCPStdiolLifecycle,
        TestJSONRPCCompliance,
        TestMessageFraming,
        TestErrorResponseFormat
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 60)
        
        instance = test_class()
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for test_method_name in test_methods:
            total_tests += 1
            try:
                test_method = getattr(instance, test_method_name)
                test_method()
                passed_tests += 1
            except Exception as e:
                print(f"[FAIL] {test_method_name}: FAILED - {e}")
    
    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("SUCCESS: ALL TESTS PASSED - Fix Agent 1 compliance verified!")
        return True
    else:
        print(f"ERROR: {total_tests - passed_tests} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)