#!/usr/bin/env python3
"""Test the WebSocket shim connection to Docker daemon."""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for Docker connection
os.environ["EXAI_WS_HOST"] = "127.0.0.1"
os.environ["EXAI_WS_PORT"] = "8079"
os.environ["EXAI_WS_SKIP_HEALTH_CHECK"] = "true"
os.environ["EXAI_WS_AUTOSTART"] = "false"
os.environ["EXAI_WS_CONNECT_TIMEOUT"] = "10"
os.environ["ENV_FILE"] = str(project_root / ".env")

# Import after setting env vars
from scripts.run_ws_shim import _ensure_ws


async def test_shim():
    """Test shim connection to Docker daemon."""
    try:
        print("Testing shim connection to Docker daemon...")
        print(f"Host: {os.environ['EXAI_WS_HOST']}")
        print(f"Port: {os.environ['EXAI_WS_PORT']}")
        print(f"Skip health check: {os.environ['EXAI_WS_SKIP_HEALTH_CHECK']}")
        print(f"Autostart: {os.environ['EXAI_WS_AUTOSTART']}")
        print()

        # Try to get WebSocket connection
        ws = await _ensure_ws()
        print("✅ Successfully connected to Docker daemon!")
        print(f"WebSocket state: {ws.state.name if hasattr(ws, 'state') else 'connected'}")
        
        # Try to send a ping
        await ws.ping()
        print("✅ Ping successful!")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_shim())
    sys.exit(0 if result else 1)

