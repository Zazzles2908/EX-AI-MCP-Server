#!/usr/bin/env python3
"""Quick test to verify localhost:8079 is accessible."""
import asyncio
import json
import websockets


async def test_connection():
    for host in ['localhost', '127.0.0.1', '0.0.0.0']:
        try:
            print(f"\nTrying ws://{host}:8079...")
            ws = await asyncio.wait_for(
                websockets.connect(f'ws://{host}:8079'),
                timeout=5.0
            )
            print(f"✅ Connected to {host}!")

            # Send hello
            hello_msg = {"op": "hello", "token": "test-token-12345"}
            await ws.send(json.dumps(hello_msg))
            print("📤 Sent hello")

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"📥 Received: {response}")

            await ws.close()
            print(f"✅ Test successful with {host}!")
            return True
        except Exception as e:
            print(f"❌ Failed with {host}: {e}")
            continue

    print("❌ All connection attempts failed")
    return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)

