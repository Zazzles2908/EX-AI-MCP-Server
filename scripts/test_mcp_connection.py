#!/usr/bin/env python3
"""
Test script to verify EX-AI MCP server connection fix.
This script tests the shim's ability to connect to the daemon.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Setup paths
_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("mcp_test")

# Load environment
try:
    from dotenv import load_dotenv
    env_file = _repo_root / ".env"
    load_dotenv(dotenv_path=str(env_file), override=True)
    logger.info(f"✓ Loaded environment from {env_file}")
except Exception as e:
    logger.warning(f"Could not load .env: {e}")

# Configuration
DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3010"))
DAEMON_TOKEN = os.getenv("EXAI_WS_TOKEN", "")

logger.info(f"Configuration:")
logger.info(f"  Daemon: {DAEMON_HOST}:{DAEMON_PORT}")
logger.info(f"  Token: {DAEMON_TOKEN[:20] if DAEMON_TOKEN else 'NOT SET'}...")

async def test_daemon_connection():
    """Test connection to daemon with detailed logging."""
    import websockets

    daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing connection to {daemon_uri}")
    logger.info(f"{'='*60}")

    try:
        # Connect to daemon
        logger.info("Step 1: Connecting to WebSocket...")
        async with websockets.connect(daemon_uri, ping_interval=20, ping_timeout=10) as ws:
            logger.info("✓ Connected successfully")

            # Send hello
            logger.info("Step 2: Sending hello message...")
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "token": DAEMON_TOKEN
            }
            await ws.send(json.dumps(hello_msg))
            logger.info("✓ Hello sent")

            # Wait for hello_ack
            logger.info("Step 3: Waiting for hello_ack (timeout=30s)...")
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                hello_ack = json.loads(response)
                logger.info(f"✓ Received hello_ack: {hello_ack}")

                if not hello_ack.get("ok"):
                    error_msg = hello_ack.get('error', 'Unknown error')
                    logger.error(f"✗ Daemon rejected connection: {error_msg}")
                    return False

            except asyncio.TimeoutError:
                logger.error("✗ Timeout waiting for hello_ack")
                return False

            # Test list_tools
            logger.info("Step 4: Requesting tool list...")
            await ws.send(json.dumps({
                "op": "list_tools",
                "id": "test_123"
            }))
            logger.info("✓ list_tools request sent")

            # Wait for response
            logger.info("Step 5: Waiting for tool list (timeout=35s)...")
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=35)
                data = json.loads(response)
                tools_count = len(data.get("tools", []))
                logger.info(f"✓ Received tool list with {tools_count} tools")

                if tools_count > 0:
                    logger.info("First tool: " + data["tools"][0]["name"])
                else:
                    logger.warning("⚠ No tools returned")

                return tools_count > 0

            except asyncio.TimeoutError:
                logger.error("✗ Timeout waiting for tool list")
                return False

    except ConnectionRefusedError:
        logger.error(f"✗ Connection refused - is daemon running on {daemon_uri}?")
        return False
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}", exc_info=True)
        return False

async def main():
    """Main test function."""
    print("\n" + "="*60)
    print("EX-AI MCP Server Connection Test")
    print("="*60 + "\n")

    # Check daemon health
    import aiohttp
    logger.info("Checking daemon health...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{DAEMON_HOST}:3002/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    health = await resp.json()
                    logger.info(f"✓ Daemon is healthy: {health.get('status')}")
                    logger.info(f"  Uptime: {health.get('uptime_human', 'unknown')}")
                    logger.info(f"  Active connections: {health.get('active_connections', 0)}")
                else:
                    logger.error(f"✗ Health check failed: HTTP {resp.status}")
                    return False
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        logger.error("  Is the daemon running? Try: docker-compose up -d exai-daemon")
        return False

    # Test connection
    success = await test_daemon_connection()

    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED - MCP server connection works!")
        print("="*60)
        return 0
    else:
        print("❌ TESTS FAILED - MCP server connection has issues")
        print("="*60)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
