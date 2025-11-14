#!/usr/bin/env python3
"""
Safe WebSocket Shim Startup - Windows Compatible

This script ensures clean startup by:
1. Killing any orphaned shim processes
2. Ensuring port 3005 is free
3. Starting the shim with proper error handling

Designed to prevent port conflicts caused by orphaned processes.
"""

import os
import sys
import time
import socket
import subprocess
import logging
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

SHIM_PORT = 3005
SHIM_SCRIPT = Path(__file__).parent / "run_ws_shim.py"


def check_port_available(port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def kill_orphaned_shims():
    """Kill any orphaned WebSocket shim processes."""
    logger.info("Checking for orphaned shims...")

    try:
        result = subprocess.run(
            [sys.executable, "cleanup_orphaned_shims.py", "--check-only"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("Found orphaned shims, cleaning up...")
            subprocess.run(
                [sys.executable, "cleanup_orphaned_shims.py"],
                cwd=Path(__file__).parent,
                check=True
            )
            # Give the system time to release the port
            time.sleep(1)
        else:
            logger.info("No orphaned shims found")
    except Exception as e:
        logger.warning(f"Cleanup check failed: {e}")


def ensure_port_free():
    """Ensure the shim port is free."""
    max_attempts = 5
    for attempt in range(max_attempts):
        if check_port_available(SHIM_PORT):
            logger.info(f"✓ Port {SHIM_PORT} is available")
            return True

        logger.warning(f"Port {SHIM_PORT} is in use (attempt {attempt + 1}/{max_attempts})")
        kill_orphaned_shims()
        time.sleep(0.5)

    logger.error(f"Failed to free port {SHIM_PORT} after {max_attempts} attempts")
    return False


def start_shim():
    """Start the WebSocket shim."""
    logger.info("=" * 60)
    logger.info("Starting WebSocket Shim (Safe Mode)")
    logger.info("=" * 60)

    # Ensure port is free
    if not ensure_port_free():
        logger.error("Cannot start shim - port is busy")
        return 1

    # Load environment from .env file
    logger.info("Loading environment from .env file...")
    try:
        from dotenv import load_dotenv
        repo_root = Path(__file__).parent.parent.parent
        env_file = repo_root / ".env"
        load_dotenv(dotenv_path=str(env_file), override=True)
        logger.info(f"✓ Loaded environment from {env_file}")

        # DEBUG: Log the token to verify it loaded
        token = os.getenv("EXAI_WS_TOKEN", "NOT SET")
        logger.info(f"[DEBUG] EXAI_WS_TOKEN in wrapper: {token[:20]}...")
        port = os.getenv("EXAI_WS_PORT", "NOT SET")
        logger.info(f"[DEBUG] EXAI_WS_PORT in wrapper: {port}")

    except ImportError:
        logger.warning("python-dotenv not available, using inherited environment")
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")

    # TURNKEY FIX (2025-11-14): Validate daemon connection BEFORE starting shim
    logger.info("=" * 60)
    logger.info("TURNKEY STARTUP - Validating Daemon Connection")
    logger.info("=" * 60)
    try:
        import asyncio
        import websockets

        async def test_daemon():
            uri = f"ws://127.0.0.1:{os.getenv('EXAI_WS_PORT', '3010')}"
            token = os.getenv("EXAI_WS_TOKEN", "")
            async with websockets.connect(uri, ping_interval=None) as websocket:
                hello = {'op': 'hello', 'token': token, 'data': {'protocolVersion': '2024-11-05', 'clientInfo': {'name': 'shim-validator'}}}
                await websocket.send(json.dumps(hello))
                ack = await asyncio.wait_for(websocket.recv(), timeout=5)
                return json.loads(ack).get('ok', False)

        result = asyncio.run(test_daemon())
        if result:
            logger.info("✓ DAEMON READY - Starting shim")
        else:
            logger.error("✗ DAEMON NOT READY - Please ensure container is running")
            logger.error("  Run: docker-compose up -d")
            return 1
    except Exception as e:
        logger.error(f"✗ Daemon validation failed: {e}")
        logger.error("  Is EXAI MCP container running on port 3010?")
        return 1

    # Start the shim
    logger.info("=" * 60)
    logger.info(f"Starting shim: {SHIM_SCRIPT}")
    logger.info("=" * 60)
    try:
        # CRITICAL: Get environment AFTER loading .env
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        # DEBUG: Verify token is in the env being passed
        shim_token = env.get("EXAI_WS_TOKEN", "NOT IN ENV")
        logger.info(f"[DEBUG] EXAI_WS_TOKEN in subprocess env: {shim_token[:20]}...")

        process = subprocess.Popen(
            [sys.executable, "-u", str(SHIM_SCRIPT)],
            cwd=Path(__file__).parent.parent.parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # FIX: Keep stderr separate from stdout
            text=True,
            encoding='utf-8',  # CRITICAL: Fix Unicode errors on Windows
            bufsize=1
        )

        # Stream stderr (logs) and stdout (MCP responses) separately
        import threading

        def read_stderr():
            """Read stderr from shim (logs)."""
            for line in iter(process.stderr.readline, ''):
                if not line:
                    break
                logger.info(f"[SHIM STDERR] {line.rstrip()}")

        # Start stderr reader in thread
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Read stdout (MCP protocol) - DON'T LOG IT, just pass it through
        for line in iter(process.stdout.readline, ''):
            # MCP protocol messages go to stdout, don't log them
            if line:
                try:
                    print(line.rstrip(), flush=True)
                except Exception as e:
                    # Handle any encoding errors gracefully
                    logger.error(f"Error printing line: {e}")
                    try:
                        # Try to print with replacement characters
                        print(line.rstrip().encode('utf-8', errors='replace').decode('utf-8', errors='replace'), flush=True)
                    except:
                        pass

        return process.wait()

    except KeyboardInterrupt:
        logger.info("Shim stopped by user")
        process.terminate()
        return 0
    except Exception as e:
        logger.error(f"Failed to start shim: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = start_shim()
    sys.exit(exit_code)
