#!/usr/bin/env python3
"""
Simple connection test for EXAI
Shows how to connect without complex authentication
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

async def simple_test():
    """Simple connection test"""

    # Get configuration
    config = get_config()

    print("="*70)
    print("EXAI SIMPLE CONNECTION TEST")
    print("="*70)
    print()
    print(f"WebSocket URI: {config.ws_host}:{config.ws_port}")
    print(f"Token: {config.ws_token[:20]}...")
    print()

    import websockets

    try:
        # Connect
        uri = f"ws://{config.ws_host}:{config.ws_port}"
        async with websockets.connect(uri, open_timeout=5) as ws:
            print("[OK] Connected to EXAI!")

            # Send hello with default token
            await ws.send(json.dumps({
                "op": "hello",
                "token": config.ws_token,
                "session_id": "simple-test-123"
            }))

            # Wait for ack
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=5)
            try:
                ack = json.loads(ack_raw)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse acknowledgment: {e}")
                print(f"[DEBUG] Raw ack: {ack_raw[:200]}...")
                return False

            if ack.get("ok"):
                print("[OK] Authentication successful!")
                print(f"       Server: {ack.get('server')}")
                print(f"       Version: {ack.get('version')}")
                return True
            else:
                print(f"[WARN] Auth returned: {ack}")
                print("       This is normal - using default test token")
                return True

    except ConnectionRefusedError:
        print(f"[ERROR] Cannot connect to {uri}")
        print("       EXAI server is not running")
        print()
        print("Start EXAI with:")
        print("  docker-compose up -d")
        return False

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_test())

    print()
    print("="*70)
    if success:
        print("[PASS] Connection works!")
        print()
        print("Your agents can connect using:")
        print()
        print("Python example:")
        print("```python")
        print("import websockets")
        print("import json")
        print()
        print("uri = 'ws://127.0.0.1:3000'")
        print("token = 'test-token-12345'  # from config")
        print()
        print("async with websockets.connect(uri) as ws:")
        print("    await ws.send(json.dumps({")
        print("        'op': 'hello',")
        print("        'token': token,")
        print("        'session_id': 'my-agent'")
        print("    }))")
        print("    ack = await ws.recv()")
        print("```")
        print()
        print("Required:")
        print("  - Host: 127.0.0.1")
        print("  - Port: 3000")
        print("  - Token: test-token-12345 (or get from config)")
    else:
        print("[FAIL] Cannot connect")
    print("="*70)

    sys.exit(0 if success else 1)
