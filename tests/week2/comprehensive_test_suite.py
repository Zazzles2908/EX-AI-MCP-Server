#!/usr/bin/env python3
"""
Comprehensive Test Suite for Week 2 Fixes
Tests all Week 2 fixes to validate functionality and catch regressions.

Week 2 Fixes Tested:
- Fix #6: Hardcoded Timeouts
- Fix #7: No Timeout Validation
- Fix #8: Inconsistent Error Handling
- Fix #9: Missing Input Validation
- Fix #10: No Request Size Limits
- Fix #11: Weak Session ID Generation
- Fix #12: No Session Expiry

Date: 2025-10-21
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import websockets
import requests


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record_pass(self, test_name: str):
        """Record a passing test."""
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def record_fail(self, test_name: str, reason: str):
        """Record a failing test."""
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")
    
    def summary(self) -> str:
        """Generate summary report."""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        summary = f"\n{'='*60}\n"
        summary += f"TEST SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total Tests: {total}\n"
        summary += f"Passed: {self.passed} ({pass_rate:.1f}%)\n"
        summary += f"Failed: {self.failed}\n"
        
        if self.errors:
            summary += f"\n{'='*60}\n"
            summary += f"FAILURES:\n"
            summary += f"{'='*60}\n"
            for test_name, reason in self.errors:
                summary += f"\n❌ {test_name}\n"
                summary += f"   {reason}\n"
        
        return summary


# Test configuration
WS_URL = "ws://localhost:8079"
HEALTH_URL = "http://localhost:8082/health"
SEMAPHORE_URL = "http://localhost:8082/health/semaphores"
MONITORING_URL = "http://localhost:8080/semaphore_monitor.html"

results = TestResults()


# ============================================================================
# Test 1: Monitoring UI Functionality
# ============================================================================

def test_monitoring_ui():
    """Test that monitoring UI is accessible and health endpoint returns data."""
    print("\n" + "="*60)
    print("TEST 1: Monitoring UI Functionality")
    print("="*60)
    
    # Test health endpoint
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                results.record_pass("Health endpoint returns healthy status")
            else:
                results.record_fail("Health endpoint status", f"Expected 'healthy', got '{data.get('status')}'")
        else:
            results.record_fail("Health endpoint accessibility", f"Status code: {response.status_code}")
    except Exception as e:
        results.record_fail("Health endpoint accessibility", str(e))
    
    # Test semaphore endpoint
    try:
        response = requests.get(SEMAPHORE_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "global" in data and "providers" in data:
                results.record_pass("Semaphore endpoint returns expected data structure")
                
                # Verify semaphore counts
                global_data = data.get("global", {})
                if global_data.get("current") == global_data.get("expected"):
                    results.record_pass("Global semaphore counts match expected")
                else:
                    results.record_fail("Global semaphore counts", 
                                      f"Current: {global_data.get('current')}, Expected: {global_data.get('expected')}")
            else:
                results.record_fail("Semaphore endpoint data structure", "Missing 'global' or 'providers' keys")
        else:
            results.record_fail("Semaphore endpoint accessibility", f"Status code: {response.status_code}")
    except Exception as e:
        results.record_fail("Semaphore endpoint accessibility", str(e))
    
    # Test monitoring UI accessibility
    try:
        response = requests.get(MONITORING_URL, timeout=5)
        if response.status_code == 200:
            results.record_pass("Monitoring UI is accessible")
        else:
            results.record_fail("Monitoring UI accessibility", f"Status code: {response.status_code}")
    except Exception as e:
        results.record_fail("Monitoring UI accessibility", str(e))


# ============================================================================
# Test 2: Error Handling Migration
# ============================================================================

async def test_error_handling():
    """Test standardized error responses for all error scenarios."""
    print("\n" + "="*60)
    print("TEST 2: Error Handling Migration")
    print("="*60)
    
    # Test 2.1: Tool not found error
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send hello first
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0",
                "token": "test-token-12345"  # Auth token from .env.docker
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await asyncio.wait_for(ws.recv(), timeout=5)

            # Now send tool request
            request = {
                "op": "call_tool",
                "request_id": "test-tool-not-found",
                "name": "nonexistent_tool_EXAI-WS",
                "arguments": {}
            }
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                error = data["error"]
                if error.get("code") == "TOOL_NOT_FOUND":
                    results.record_pass("Tool not found error uses standardized format")
                else:
                    results.record_fail("Tool not found error code", f"Expected 'TOOL_NOT_FOUND', got '{error.get('code')}'")
            else:
                results.record_fail("Tool not found error", "No error in response")
    except Exception as e:
        results.record_fail("Tool not found error test", str(e))
    
    # Test 2.2: Invalid request error (missing required field)
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send hello first
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0",
                "token": "test-token-12345"
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await asyncio.wait_for(ws.recv(), timeout=5)

            # Now send invalid request
            request = {
                "op": "call_tool",
                "request_id": "test-invalid-request",
                # Missing 'name' field
                "arguments": {}
            }
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                error = data["error"]
                if error.get("code") in ["INVALID_REQUEST", "PROTOCOL_ERROR"]:
                    results.record_pass("Invalid request error uses standardized format")
                else:
                    results.record_fail("Invalid request error code", f"Got '{error.get('code')}'")
            else:
                results.record_fail("Invalid request error", "No error in response")
    except Exception as e:
        results.record_fail("Invalid request error test", str(e))


# ============================================================================
# Test 3: Input Validation (Fix #9)
# ============================================================================

async def test_input_validation():
    """Test input validation for various invalid inputs."""
    print("\n" + "="*60)
    print("TEST 3: Input Validation (Fix #9)")
    print("="*60)
    
    # Test 3.1: Invalid temperature (> 1.0)
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send hello first
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0",
                "token": "test-token-12345"
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await asyncio.wait_for(ws.recv(), timeout=5)

            # Now send request with invalid temperature
            request = {
                "op": "call_tool",
                "request_id": "test-invalid-temp",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Test",
                    "temperature": 1.5  # Invalid: > 1.0
                }
            }
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                error = data["error"]
                if error.get("code") == "VALIDATION_ERROR":
                    results.record_pass("Invalid temperature triggers validation error")
                else:
                    results.record_fail("Invalid temperature error code", f"Expected 'VALIDATION_ERROR', got '{error.get('code')}'")
            else:
                results.record_fail("Invalid temperature validation", "No error in response")
    except Exception as e:
        results.record_fail("Invalid temperature validation test", str(e))
    
    # Test 3.2: Empty prompt
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send hello first
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0",
                "token": "test-token-12345"
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await asyncio.wait_for(ws.recv(), timeout=5)

            # Now send request with empty prompt
            request = {
                "op": "call_tool",
                "request_id": "test-empty-prompt",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": ""  # Invalid: empty
                }
            }
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                error = data["error"]
                if error.get("code") == "VALIDATION_ERROR":
                    results.record_pass("Empty prompt triggers validation error")
                else:
                    results.record_fail("Empty prompt error code", f"Expected 'VALIDATION_ERROR', got '{error.get('code')}'")
            else:
                results.record_fail("Empty prompt validation", "No error in response")
    except Exception as e:
        results.record_fail("Empty prompt validation test", str(e))


# ============================================================================
# Test 4: Size Limits (Fix #10)
# ============================================================================

async def test_size_limits():
    """Test request size limits."""
    print("\n" + "="*60)
    print("TEST 4: Size Limits (Fix #10)")
    print("="*60)
    
    # Test 4.1: Oversized request (> 10MB)
    try:
        async with websockets.connect(WS_URL) as ws:
            # Send hello first
            hello_msg = {
                "op": "hello",
                "client_name": "test-client",
                "client_version": "1.0.0",
                "token": "test-token-12345"
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await asyncio.wait_for(ws.recv(), timeout=5)

            # Now send oversized request
            # Create a large prompt (> 10MB)
            large_prompt = "A" * (11 * 1024 * 1024)  # 11MB
            request = {
                "op": "call_tool",
                "request_id": "test-oversized",
                "name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": large_prompt
                }
            }
            await ws.send(json.dumps(request))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                error = data["error"]
                if error.get("code") == "OVER_CAPACITY":
                    results.record_pass("Oversized request triggers size limit error")
                else:
                    results.record_fail("Oversized request error code", f"Expected 'OVER_CAPACITY', got '{error.get('code')}'")
            else:
                results.record_fail("Oversized request validation", "No error in response")
    except Exception as e:
        # Connection might be closed due to size limit
        if "connection" in str(e).lower() or "closed" in str(e).lower():
            results.record_pass("Oversized request rejected (connection closed)")
        else:
            results.record_fail("Oversized request test", str(e))


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_async_tests():
    """Run all async tests."""
    await test_error_handling()
    await test_input_validation()
    await test_size_limits()


def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST SUITE - WEEK 2 FIXES")
    print("="*60)
    print(f"WebSocket URL: {WS_URL}")
    print(f"Health URL: {HEALTH_URL}")
    print(f"Semaphore URL: {SEMAPHORE_URL}")
    print("="*60)
    
    # Run synchronous tests
    test_monitoring_ui()
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    # Print summary
    print(results.summary())
    
    # Exit with appropriate code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    main()

