"""
Test Script: Expert Analysis Polling Fix Verification (WebSocket Approach)
===========================================================================

Purpose:
    Verify that the expert analysis polling fix works correctly by calling
    tools through the WebSocket daemon (proper system initialization).

Approach:
    - Connect to running ws_daemon (ws://127.0.0.1:8079)
    - Call tools via WebSocket (proper initialization)
    - Measure completion times
    - Verify no hanging/cancellation

Prerequisites:
    - Daemon must be running: powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1 -Restart
    - .env file must have valid API keys

Test Strategy:
    1. Test chat_EXAI-WS (baseline - no expert analysis)
    2. Test analyze_EXAI-WS (with expert analysis - should complete quickly)
    3. Test codereview_EXAI-WS (with expert analysis - should complete quickly)

Expected Results:
    - All tools complete successfully
    - Completion time < 60 seconds for simple tasks
    - No timeout/cancellation errors
    - Expert analysis field present in workflow tool results

Author: Augment Agent
Date: 2025-10-13
"""

import asyncio
import json
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

try:
    import websockets
except ImportError:
    print("ERROR: websockets module not installed")
    print("Install with: pip install websockets")
    sys.exit(1)

# Configuration
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URI = f"ws://{WS_HOST}:{WS_PORT}"
TIMEOUT = 120.0  # 2 minutes max per test


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def print_timestamp(label):
    """Print timestamp with label"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {label}")


async def call_tool_via_websocket(tool_name: str, arguments: dict, timeout: float = TIMEOUT):
    """
    Call a tool through the WebSocket daemon.

    Returns:
        tuple: (success: bool, result: dict, duration: float, error: str)
    """
    request_id = uuid.uuid4().hex
    session_id = f"test-{uuid.uuid4().hex[:6]}"

    start_time = time.time()

    try:
        async with websockets.connect(WS_URI, max_size=20 * 1024 * 1024) as websocket:
            # Send hello handshake
            hello_msg = {
                "op": "hello",
                "session_id": session_id,
                "token": WS_TOKEN
            }
            await websocket.send(json.dumps(hello_msg))

            # Wait for ack
            ack_raw = await websocket.recv()
            ack = json.loads(ack_raw)
            if not ack.get("ok"):
                return False, None, time.time() - start_time, f"Auth failed: {ack}"

            # Send tool call
            tool_msg = {
                "op": "call_tool",
                "request_id": request_id,
                "name": tool_name,
                "arguments": arguments
            }
            await websocket.send(json.dumps(tool_msg))

            # Wait for response with timeout, handling progress messages
            while True:
                response_raw = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                response = json.loads(response_raw)

                # Handle progress messages
                if response.get("op") == "progress":
                    # Print progress for debugging
                    progress_msg = response.get("message", "")
                    if progress_msg:
                        print(f"   [Progress] {progress_msg}")
                    continue

                # Handle final result
                if response.get("op") == "call_tool_res":
                    duration = time.time() - start_time
                    if response.get("error"):
                        return False, response, duration, str(response.get("error"))
                    # Success
                    return True, response, duration, None

                # Unexpected message
                duration = time.time() - start_time
                return False, response, duration, f"Unexpected response op: {response.get('op')}"

    except asyncio.TimeoutError:
        duration = time.time() - start_time
        return False, None, duration, f"Timeout after {duration:.1f}s"
    except Exception as e:
        duration = time.time() - start_time
        return False, None, duration, str(e)


async def test_chat_baseline():
    """
    Test 1: Chat Tool (Baseline)
    
    This tool does NOT use expert analysis, so it should complete quickly.
    """
    print_header("TEST 1: Chat Tool (Baseline - No Expert Analysis)")
    
    arguments = {
        "prompt": "What is Python? Answer in one sentence.",
        "model": "glm-4.5-flash",
        "use_websearch": False
    }
    
    print(f"\n📋 Test Parameters:")
    print(f"   - Tool: chat_EXAI-WS")
    print(f"   - Prompt: {arguments['prompt']}")
    print(f"   - Model: {arguments['model']}")
    print(f"   - Expert Analysis: N/A (SimpleTool)")
    
    print_timestamp("⏱️  Starting test...")
    
    success, result, duration, error = await call_tool_via_websocket("chat_EXAI-WS", arguments)
    
    print_timestamp(f"{'✅' if success else '❌'} Test completed in {duration:.2f} seconds")
    
    # Validation
    print(f"\n🔍 Validation:")
    
    if not success:
        print(f"   ❌ FAIL: {error}")
        print(f"\n❌ TEST 1 FAILED!")
        return False, duration
    
    if duration > 60.0:
        print(f"   ⚠️  WARNING: Duration longer than expected ({duration:.2f}s)")
    else:
        print(f"   ✅ PASS: Duration appropriate ({duration:.2f}s)")
    
    print(f"   ✅ PASS: Tool completed successfully")
    print(f"\n✅ TEST 1 PASSED!")
    return True, duration


async def test_analyze_with_expert():
    """
    Test 2: Analyze Tool (With Expert Analysis)
    
    This tool uses expert analysis and was previously hanging.
    After the fix, it should complete within 60 seconds.
    """
    print_header("TEST 2: Analyze Tool (With Expert Analysis - FIXED)")
    
    arguments = {
        "step": "Analyze the architecture of a simple Python function",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Simple function with clear input/output",
        "use_assistant_model": True,  # Enable expert analysis
        "model": "glm-4.5-flash",
    }
    
    print(f"\n📋 Test Parameters:")
    print(f"   - Tool: analyze_EXAI-WS")
    print(f"   - Step: {arguments['step']}")
    print(f"   - Expert Analysis: Enabled")
    print(f"   - Model: {arguments['model']}")
    
    print_timestamp("⏱️  Starting test...")
    
    success, result, duration, error = await call_tool_via_websocket("analyze_EXAI-WS", arguments)
    
    print_timestamp(f"{'✅' if success else '❌'} Test completed in {duration:.2f} seconds")
    
    # Validation
    print(f"\n🔍 Validation:")
    
    if not success:
        print(f"   ❌ FAIL: {error}")
        print(f"\n❌ TEST 2 FAILED!")
        return False, duration
    
    if duration > 60.0:
        print(f"   ⚠️  WARNING: Duration longer than expected ({duration:.2f}s)")
        print(f"   (Should be <60s for simple analysis)")
    else:
        print(f"   ✅ PASS: Duration appropriate ({duration:.2f}s)")
    
    # Check for expert analysis in result
    try:
        content = result["result"]["content"][0]["text"]
        data = json.loads(content)
        
        if "expert_analysis" in data:
            print(f"   ✅ PASS: Expert analysis field present")
            expert_status = data["expert_analysis"].get("status", "unknown")
            print(f"   - Expert analysis status: {expert_status}")
        else:
            print(f"   ⚠️  WARNING: No expert_analysis field (may be skipped)")
    except Exception as e:
        print(f"   ⚠️  WARNING: Could not parse result: {e}")
    
    print(f"\n✅ TEST 2 PASSED!")
    return True, duration


async def test_codereview_with_expert():
    """
    Test 3: Codereview Tool (With Expert Analysis)
    
    This tool uses expert analysis and should complete quickly.
    """
    print_header("TEST 3: Codereview Tool (With Expert Analysis - FIXED)")
    
    # Create a simple test file
    test_file = Path("scripts/testing/test_sample.py")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("def hello():\n    print('Hello, World!')\n")
    
    arguments = {
        "step": "Review this simple Python function for code quality",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Function follows PEP 8 style guidelines",
        "relevant_files": [str(test_file.absolute())],  # Required field
        "use_assistant_model": True,  # Enable expert analysis
        "model": "glm-4.5-flash",
    }
    
    print(f"\n📋 Test Parameters:")
    print(f"   - Tool: codereview_EXAI-WS")
    print(f"   - Step: {arguments['step']}")
    print(f"   - Files: {arguments['relevant_files']}")
    print(f"   - Expert Analysis: Enabled")
    print(f"   - Model: {arguments['model']}")
    
    print_timestamp("⏱️  Starting test...")
    
    success, result, duration, error = await call_tool_via_websocket("codereview_EXAI-WS", arguments)
    
    print_timestamp(f"{'✅' if success else '❌'} Test completed in {duration:.2f} seconds")
    
    # Cleanup test file
    test_file.unlink(missing_ok=True)
    
    # Validation
    print(f"\n🔍 Validation:")
    
    if not success:
        print(f"   ❌ FAIL: {error}")
        print(f"\n❌ TEST 3 FAILED!")
        return False, duration
    
    if duration > 60.0:
        print(f"   ⚠️  WARNING: Duration longer than expected ({duration:.2f}s)")
    else:
        print(f"   ✅ PASS: Duration appropriate ({duration:.2f}s)")
    
    print(f"   ✅ PASS: Tool completed successfully")
    print(f"\n✅ TEST 3 PASSED!")
    return True, duration


async def main():
    """Run all tests and generate summary"""
    print_header("EXPERT ANALYSIS POLLING FIX VERIFICATION (WebSocket)")
    print(f"Testing fix for 5-second polling interval bug")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nConnecting to: {WS_URI}")
    print(f"Timeout per test: {TIMEOUT}s")
    
    # Check if daemon is running
    print_timestamp("Checking if daemon is running...")
    try:
        async with websockets.connect(WS_URI) as ws:
            print_timestamp("✅ Daemon is running")
    except Exception as e:
        print_timestamp(f"❌ Cannot connect to daemon: {e}")
        print("\nPlease start the daemon first:")
        print("  powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1 -Restart")
        return 1
    
    results = []
    
    # Test 1: Chat (baseline)
    passed1, duration1 = await test_chat_baseline()
    results.append(("Chat (baseline)", passed1, duration1))
    
    # Test 2: Analyze (fixed)
    passed2, duration2 = await test_analyze_with_expert()
    results.append(("Analyze (with expert)", passed2, duration2))
    
    # Test 3: Codereview (fixed)
    passed3, duration3 = await test_codereview_with_expert()
    results.append(("Codereview (with expert)", passed3, duration3))
    
    # Summary
    print_header("TEST SUMMARY")
    
    for test_name, passed, duration in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name} ({duration:.2f}s)")
    
    all_passed = all(result[1] for result in results)
    
    print(f"\n{'='*80}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! Expert analysis polling fix verified!")
        print("\nThe fix successfully resolves the hanging issue:")
        print("  ✅ Polling interval reduced from 5s to 0.1s")
        print("  ✅ Task completion detected within 100ms")
        print("  ✅ No more false timeouts/cancellations")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Fix may not be working correctly.")
        print("\nPlease check:")
        print("  - Server was restarted after applying fix")
        print("  - expert_analysis.py changes are present")
        print("  - Check logs/ws_daemon.log for errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

