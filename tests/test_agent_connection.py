#!/usr/bin/env python3
"""
Test script to verify agent can connect to EXAI MCP Server
This demonstrates how any agent can connect to EXAI directly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(repo_root))

# Import centralized configuration
from src.config import get_config
from src.config.secrets_manager import get_secrets_manager

async def test_exai_connection():
    """Test connection to EXAI WebSocket server"""

    # Get configuration
    config = get_config()
    secrets = get_secrets_manager()

    print("="*70)
    print("EXAI AGENT CONNECTION TEST")
    print("="*70)
    print()

    # Connection details
    host = config.ws_host
    port = config.ws_port
    uri = f"ws://{host}:{port}"

    # Get JWT token
    print("[KEY] Getting JWT token...")
    try:
        token = secrets.get_jwt_token("claude")
        if not token:
            print("[WARN] JWT token not found in Supabase")
            print("       Using default token from config")
            token = config.ws_token
    except Exception as e:
        print(f"[WARN] Could not retrieve token: {e}")
        print("       Using default token from config")
        token = config.ws_token

    print(f"[OK] Token retrieved: {token[:20]}...{token[-10:]}")
    print()

    # Test connection
    print(f"[CONNECT] Connecting to {uri}...")
    try:
        import websockets

        async with websockets.connect(uri, open_timeout=5) as ws:
            print("[OK] WebSocket connected!")

            # Send hello
            print("[SEND] Sending hello message...")
            hello_msg = {
                "op": "hello",
                "token": token,
                "session_id": f"test-agent-{hash(str(asyncio.get_event_loop())) % 10000}"
            }
            await ws.send(json.dumps(hello_msg))

            # Wait for ack
            print("[WAIT] Waiting for acknowledgment...")
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            ack = json.loads(ack_raw)

            if ack.get("ok"):
                print("[OK] Authentication successful!")
                print(f"       Server: {ack.get('server', 'unknown')}")
                print(f"       Version: {ack.get('version', 'unknown')}")
            else:
                print(f"[ERROR] Authentication failed: {ack}")
                return False

            # Test a simple tool call
            print()
            print("[TEST] Testing tool call...")

            # Request tool list
            req_id = f"test-{hash('list_tools') % 10000}"
            await ws.send(json.dumps({
                "op": "list_tools",
                "request_id": req_id
            }))

            # Wait for response
            response_raw = await asyncio.wait_for(ws.recv(), timeout=10)
            response = json.loads(response_raw)

            if response.get("tools"):
                print(f"[OK] Successfully retrieved {len(response['tools'])} tools!")
                print("       Available tools:")
                for tool in response["tools"][:5]:  # Show first 5
                    print(f"       - {tool.get('name')}: {tool.get('description', '')[:50]}...")
                if len(response["tools"]) > 5:
                    print(f"       ... and {len(response['tools']) - 5} more")
            else:
                print(f"[WARN] No tools in response: {response}")

            return True

    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused! Is EXAI server running on {uri}?")
        print()
        print("To start EXAI server:")
        print("  docker-compose up -d")
        return False

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_exai_connection()

    print()
    print("="*70)
    if success:
        print("[PASS] CONNECTION TEST PASSED")
        print()
        print("Your agent can now connect to EXAI using:")
        print("  - Host: 127.0.0.1")
        print("  - Port: 3000")
        print("  - JWT Token: from secrets manager or config")
        print("  - Protocol: WebSocket with JSON messages")
    else:
        print("[FAIL] CONNECTION TEST FAILED")
        print()
        print("Troubleshooting:")
        print("1. Start EXAI server: docker-compose up -d")
        print("2. Check port 3000 is not blocked")
        print("3. Verify JWT token is valid")
    print("="*70)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
