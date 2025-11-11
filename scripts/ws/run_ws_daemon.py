#!/usr/bin/env python
"""WS Daemon launcher - minimal version for 98% reduction."""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env

# Load environment variables
load_env()

logger = logging.getLogger(__name__)


async def main():
    """Run WebSocket daemon."""
    logger.info("[MAIN] Starting WebSocket daemon")

    # Import and run the WebSocket daemon's async main directly
    from src.daemon.ws_server import main_async
    await main_async()

    logger.info("[MAIN] WebSocket daemon exited")


def main_wrapper():
    """Entry point for the daemon launcher."""
    logger.info("[MAIN] Daemon starting...")
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"[MAIN] Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main_wrapper()
