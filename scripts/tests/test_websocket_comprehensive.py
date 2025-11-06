#!/usr/bin/env python3
"""
Comprehensive WebSocket Test Suite

Consolidates 5 duplicate WebSocket test scripts:
- /scripts/test_ws_connection.py
- /scripts/testing/test_ws_connection.py
- /scripts/maintenance/test_ws_connection.py
- /scripts/testing/test_ws_internal.py
- /scripts/test_ws_inside_docker.py

Features:
- Support for multiple ports (8079, 8080)
- Environment-based configuration
- MCP protocol compliance
- Connection health checks
- List tools verification
"""

import asyncio
import json
import websockets
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

# Add repo root to path
_repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env
load_env()

# Configuration from environment
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORTS = [int(p) for p in os.getenv("EXAI_WS_PORTS", "8079,8080").split(",")]
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "test-token-12345")


class WebSocketTester:
    """Comprehensive WebSocket testing suite."""

    def __init__(self, host: str = WS_HOST, ports: list = WS_PORTS):
        self.host = host
        self.ports = ports
        self.results = []

    async def test_connection(self, port: int, session_id: str = "test-session") -> Dict[str, Any]:
        """Test WebSocket connection to specified port."""
        uri = f"ws://{self.host}:{port}"

        try:
            # Connect with timeout
            websocket = await asyncio.wait_for(
                websockets.connect(uri, ping_interval=None, open_timeout=10),
                timeout=15
            )

            result = {
                "port": port,
                "status": "connected",
                "uri": uri,
                "error": None,
                "mcp_version": None,
                "tools_available": False
            }

            try:
                # Test MCP protocol: send list_tools request
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }

                await websocket.send(json.dumps(list_tools_request))

                # Wait for response with timeout
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)

                # Verify response structure
                if "result" in response_data and "tools" in response_data["result"]:
                    result["tools_available"] = True
                    result["tools_count"] = len(response_data["result"]["tools"])
                    result["status"] = "fully_functional"
                else:
                    result["status"] = "connected_but_mcp_issue"

            except asyncio.TimeoutError:
                result["status"] = "connected_timeout"
                result["error"] = "No response to list_tools request"

            except json.JSONDecodeError as e:
                result["status"] = "connected_invalid_json"
                result["error"] = f"Invalid JSON response: {e}"

            except Exception as e:
                result["status"] = "connected_error"
                result["error"] = str(e)

            finally:
                await websocket.close()

        except asyncio.TimeoutError:
            result = {
                "port": port,
                "status": "timeout",
                "uri": uri,
                "error": "Connection timeout (15s)",
                "tools_available": False
            }

        except ConnectionRefusedError:
            result = {
                "port": port,
                "status": "refused",
                "uri": uri,
                "error": "Connection refused - server not running",
                "tools_available": False
            }

        except Exception as e:
            result = {
                "port": port,
                "status": "error",
                "uri": uri,
                "error": str(e),
                "tools_available": False
            }

        return result

    async def test_all_ports(self) -> list:
        """Test all configured ports."""
        print(f"\n=== WebSocket Connection Test ===")
        print(f"Host: {self.host}")
        print(f"Ports: {self.ports}")
        print("-" * 50)

        tasks = []
        for port in self.ports:
            task = self.test_connection(port)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        self.results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.append({
                    "port": self.ports[i],
                    "status": "exception",
                    "error": str(result)
                })
            else:
                self.results.append(result)

        return self.results

    def print_results(self):
        """Print formatted test results."""
        if not self.results:
            print("No test results available")
            return

        print("\n=== Test Results ===\n")

        for result in self.results:
            port = result["port"]
            status = result["status"]
            uri = result["uri"]

            # Status icon (ASCII only for Windows compatibility)
            if status == "fully_functional":
                icon = "[OK]"
            elif status == "connected":
                icon = "[WARN]"
            elif status == "timeout":
                icon = "[TIMO]"
            elif status == "refused":
                icon = "[FAIL]"
            else:
                icon = "[FAIL]"

            print(f"{icon} Port {port}: {status}")

            if status == "fully_functional":
                tools_count = result.get("tools_count", 0)
                print(f"   └─ MCP tools available: {tools_count}")

            if result.get("error"):
                print(f"   └─ Error: {result['error']}")

        # Summary
        functional = sum(1 for r in self.results if r["status"] == "fully_functional")
        connected = sum(1 for r in self.results if r["status"] == "connected")
        failed = len(self.results) - functional - connected

        print("\n=== Summary ===")
        print(f"Functional: {functional}")
        print(f"Connected: {connected}")
        print(f"Failed: {failed}")
        print(f"Total tested: {len(self.results)}")


async def main():
    """Main test execution."""
    tester = WebSocketTester()

    # Test all ports
    await tester.test_all_ports()

    # Print results
    tester.print_results()

    # Exit with appropriate code
    functional = sum(1 for r in tester.results if r["status"] == "fully_functional")
    sys.exit(0 if functional > 0 else 1)


if __name__ == "__main__":
    print("Starting WebSocket Connection Test Suite")
    print("(Consolidated from 5 duplicate test scripts)")
    asyncio.run(main())
