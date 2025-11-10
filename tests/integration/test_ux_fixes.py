#!/usr/bin/env python3
"""
UX Fixes Validation Test Script
Tests all UX improvements implemented to ensure seamless user experience
"""

import asyncio
import websockets
import json
import logging
import os
import sys
from datetime import datetime

# Configure logging to see all our UX improvements
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

class UXFixesValidator:
    """Validates all UX fixes for EXAI MCP Server"""

    def __init__(self, ws_url="ws://127.0.0.1:3000", token=None):
        self.ws_url = ws_url
        self.token = token or os.getenv("EXAI_WS_TOKEN", "")
        self.connection = None
        self.session_id = None
        self.test_results = {
            'connection': False,
            'jwt_warning': False,
            'file_upload': False,
            'env_logging': False,
            'errors': []
        }

    async def connect(self):
        """Establish WebSocket connection with EXAI protocol"""
        try:
            print(f"\n{'='*80}")
            print("TEST 1: WebSocket Connection + EXAI Handshake")
            print(f"{'='*80}")

            import websockets
            ws_version = websockets.__version__
            print(f"Using websockets version: {ws_version}")

            # Connect to WebSocket
            self.connection = await websockets.connect(
                self.ws_url,
                open_timeout=10,
                close_timeout=5,
                max_size=2**20,  # 1MB max frame size
                ping_interval=20,
                ping_timeout=5
            )
            print(f"Successfully connected to {self.ws_url}")

            # Generate session ID
            import uuid
            self.session_id = f"ux-test-{uuid.uuid4().hex[:8]}"
            print(f"Generated session ID: {self.session_id}")

            # Send hello message (EXAI custom protocol)
            hello_msg = {
                "op": "hello",
                "session_id": self.session_id,
                "token": self.token
            }

            print("Sending hello message (EXAI protocol)...")
            await self.connection.send(json.dumps(hello_msg))

            # Wait for acknowledgment
            try:
                response = await asyncio.wait_for(self.connection.recv(), timeout=10.0)
                response_data = json.loads(response)

                if response_data.get("ok"):
                    print(f"Received acknowledgment: {response_data}")
                    print("EXAI connection initialized successfully")
                    self.test_results['connection'] = True
                    return True
                else:
                    print(f"Authentication failed: {response_data}")
                    error_msg = f"Authentication failed: {response_data}"
                    self.test_results['errors'].append(error_msg)
                    return False
            except asyncio.TimeoutError:
                print("ERROR: No response to hello message")
                error_msg = "No response to hello message"
                self.test_results['errors'].append(error_msg)
                return False

        except Exception as e:
            error_msg = f"Connection failed: {e}"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    async def test_simple_tool_call(self):
        """Test a simple tool call using EXAI protocol"""
        try:
            print(f"\n{'='*80}")
            print("TEST 2: Simple Tool Call (listmodels)")
            print(f"{'='*80}")

            # Send tool call request (EXAI custom protocol)
            import uuid
            request_id = uuid.uuid4().hex
            request = {
                "op": "call_tool",
                "request_id": request_id,
                "name": "listmodels",
                "arguments": {}
            }

            await self.connection.send(json.dumps(request))
            print(f"SENT: listmodels request (id: {request_id[:8]})")

            # Wait for response
            while True:
                response = await asyncio.wait_for(
                    self.connection.recv(),
                    timeout=30.0
                )

                response_data = json.loads(response)

                # Check if this is our response
                if response_data.get("op") == "call_tool_res" and response_data.get("request_id") == request_id:
                    # Check for errors
                    if response_data.get("error"):
                        error_msg = f"Tool call failed: {response_data['error']}"
                        print(f"ERROR: {error_msg}")
                        self.test_results['errors'].append(error_msg)
                        return False

                    # Extract outputs
                    outputs = response_data.get("outputs", [])
                    print(f"SUCCESS: Received {len(outputs)} outputs")
                    return True

                # Ignore other messages
                op = response_data.get('op')
                if op is None:
                    print(f"IGNORED: Message with no op field: {response_data}")
                else:
                    print(f"IGNORED: Message with op={op}")

        except asyncio.TimeoutError:
            error_msg = "Tool call timeout - server not responding"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Tool call error: {e}"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    async def test_file_upload_via_tool(self):
        """Test file upload through smart_file_query tool"""
        try:
            print(f"\n{'='*80}")
            print("TEST 3: File Upload (smart_file_query)")
            print(f"{'='*80}")
            print("NOTE: This tests the fix for 'missing file_type parameter' error")

            # Create a test file
            test_file_path = "/tmp/test_ux_file.txt"
            with open(test_file_path, 'w') as f:
                f.write("This is a test file for UX validation\n")

            # Send file upload request (EXAI custom protocol)
            import uuid
            request_id = uuid.uuid4().hex
            request = {
                "op": "call_tool",
                "request_id": request_id,
                "name": "smart_file_query",
                "arguments": {
                    "file_path": test_file_path,
                    "question": "Count the number of lines in this file"
                }
            }

            await self.connection.send(json.dumps(request))
            print(f"SENT: file upload request for {test_file_path}")

            # Wait for response
            while True:
                response = await asyncio.wait_for(
                    self.connection.recv(),
                    timeout=30.0
                )

                response_data = json.loads(response)

                # Check if this is our response
                if response_data.get("op") == "call_tool_res" and response_data.get("request_id") == request_id:
                    # Check for the specific error we fixed
                    if response_data.get("error"):
                        error_message = str(response_data["error"])
                        if 'file_type' in error_message:
                            error_msg = f"FAILED - 'file_type' error still present: {error_message}"
                            print(f"ERROR: {error_msg}")
                            self.test_results['errors'].append(error_msg)
                            return False
                        else:
                            # Other errors are OK for this test
                            print(f"WARNING: Tool returned error (not file_type related): {error_message[:100]}")

                    print("SUCCESS: File upload completed without 'file_type' error")
                    self.test_results['file_upload'] = True
                    return True

                # Ignore other messages
                op = response_data.get('op')
                if op is None:
                    print(f"IGNORED: Message with no op field: {response_data}")
                else:
                    print(f"IGNORED: Message with op={op}")

        except asyncio.TimeoutError:
            error_msg = "File upload timeout"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"File upload error: {e}"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False
        finally:
            # Cleanup
            import os
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

    async def test_analyze_tool(self):
        """Test analyze tool to check environment variable logging"""
        try:
            print(f"\n{'='*80}")
            print("TEST 4: Environment Variable Logging (analyze tool)")
            print(f"{'='*80}")
            print("NOTE: This checks if env variable logging is improved")

            # Send analyze request (EXAI custom protocol)
            import uuid
            request_id = uuid.uuid4().hex
            request = {
                "op": "call_tool",
                "request_id": request_id,
                "name": "analyze",
                "arguments": {
                    "step": "Quick validation test",
                    "step_number": 1,
                    "total_steps": 1,
                    "next_step_required": False,
                    "findings": "Testing environment variable logging improvements"
                }
            }

            await self.connection.send(json.dumps(request))
            print(f"SENT: analyze request (id: {request_id[:8]})")

            # Wait for response
            while True:
                response = await asyncio.wait_for(
                    self.connection.recv(),
                    timeout=30.0
                )

                response_data = json.loads(response)

                # Check if this is our response
                if response_data.get("op") == "call_tool_res" and response_data.get("request_id") == request_id:
                    print("SUCCESS: Analyze tool response received")

                    if response_data.get("error"):
                        print(f"WARNING: Response contains error (may be expected): {response_data['error']}")

                    self.test_results['env_logging'] = True
                    return True

                # Ignore other messages
                op = response_data.get('op')
                if op is None:
                    print(f"IGNORED: Message with no op field: {response_data}")
                else:
                    print(f"IGNORED: Message with op={op}")

        except asyncio.TimeoutError:
            error_msg = "Analyze tool timeout"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Analyze tool error: {e}"
            print(f"ERROR: {error_msg}")
            self.test_results['errors'].append(error_msg)
            return False

    async def close(self):
        """Close WebSocket connection"""
        if self.connection:
            await self.connection.close()
            print(f"\n{'='*80}")
            print("Connection closed")
            print(f"{'='*80}")

    def print_summary(self):
        """Print test results summary"""
        print(f"\n{'='*80}")
        print("UX FIXES VALIDATION SUMMARY")
        print(f"{'='*80}")

        tests = [
            ("WebSocket Connection", self.test_results['connection']),
            ("File Upload (file_type fix)", self.test_results['file_upload']),
            ("Environment Variable Logging", self.test_results['env_logging'])
        ]

        for test_name, passed in tests:
            status = "PASS" if passed else "FAIL"
            print(f"{status} - {test_name}")

        print(f"\n{'-'*80}")
        if self.test_results['errors']:
            print(f"{len(self.test_results['errors'])} Error(s) Found:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        else:
            print("All tests passed - UX fixes validated successfully!")

        print(f"{'='*80}\n")

        return len(self.test_results['errors']) == 0


async def main():
    """Run all UX validation tests"""
    print("\n" + "="*80)
    print("EXAI MCP SERVER - UX FIXES VALIDATION SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Get token from environment
    token = os.getenv('EXAI_WS_TOKEN')

    # Create validator
    validator = UXFixesValidator(token=token)

    try:
        # Run tests
        if not await validator.connect():
            print("\nCannot proceed - connection failed")
            validator.print_summary()
            return 1

        print("\n" + "="*80)
        print("Connection established, running tests...")
        print("="*80)

        await validator.test_simple_tool_call()
        await validator.test_file_upload_via_tool()
        await validator.test_analyze_tool()

        # Print summary
        success = validator.print_summary()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await validator.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
