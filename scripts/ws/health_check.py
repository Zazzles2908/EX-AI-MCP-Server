#!/usr/bin/env python3
"""
WebSocket Health Check Script
Performs a proper WebSocket connection with hello handshake to verify daemon is running.
"""
import asyncio
import json
import os
import sys
import websockets


def load_token_from_env():
    """Load EXAI_WS_TOKEN from environment or .env file."""
    # First try environment variable
    token = os.getenv("EXAI_WS_TOKEN", "")
    if token:
        return token.strip()

    # Try to load from .env file (Docker container has .env copied)
    env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("EXAI_WS_TOKEN="):
                    # Extract value and remove any comments
                    value = line.split("=", 1)[1]
                    # Remove inline comments (anything after #)
                    if "#" in value:
                        value = value.split("#")[0]
                    return value.strip()

    return ""


async def check_health():
    """Check if WebSocket daemon is responding with proper hello handshake."""
    try:
        # Connect with timeout using asyncio.wait_for
        ws = await asyncio.wait_for(
            websockets.connect(
                'ws://127.0.0.1:8079',
                ping_interval=None,
                ping_timeout=None
            ),
            timeout=5.0
        )

        # Send hello message (required by daemon protocol)
        hello_msg = {
            "op": "hello",
            "session_id": "health_check",
            "token": load_token_from_env()
        }
        await ws.send(json.dumps(hello_msg))

        # Wait for hello_ack with timeout
        hello_ack_str = await asyncio.wait_for(ws.recv(), timeout=3.0)
        hello_ack = json.loads(hello_ack_str)

        # Check if hello was acknowledged
        if not hello_ack.get("ok"):
            print(f'Health check failed: hello not acknowledged - {hello_ack.get("error")}', file=sys.stderr)
            await ws.close()
            return False

        # Clean close
        await ws.close()
        return True
    except Exception as e:
        print(f'Health check failed: {e}', file=sys.stderr)
        return False


if __name__ == '__main__':
    result = asyncio.run(check_health())
    sys.exit(0 if result else 1)

