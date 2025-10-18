#!/usr/bin/env python
"""WS Daemon launcher - simplified with bootstrap module."""
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

# PHASE 3 (2025-10-18): Import monitoring and health servers
from src.daemon.monitoring_endpoint import start_monitoring_server, setup_monitoring_broadcast
from src.daemon.health_endpoint import start_health_server
from src.daemon.ws_server import main_async

# PHASE 3 CRITICAL GAPS (2025-10-18): Import metrics and correlation
from src.monitoring.metrics import init_metrics_server, start_periodic_updates
from src.middleware.correlation import setup_correlation_logging


async def main_with_monitoring():
    """
    Start WebSocket daemon, monitoring server, health server, and metrics server concurrently.
    Uses asyncio.gather to run all servers in parallel.

    PHASE 3 CRITICAL GAPS (2025-10-18):
    - Added health check server (port 8081)
    - Added Prometheus metrics server (port 8000)
    - Added correlation ID logging setup
    - Added periodic metrics updates
    """
    # Setup correlation ID logging
    setup_correlation_logging()
    logger.info("[MAIN] Correlation ID logging configured")

    # Check if monitoring is enabled
    monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() in ("true", "1", "yes")
    health_enabled = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() in ("true", "1", "yes")
    metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() in ("true", "1", "yes")

    # Setup monitoring broadcast hook if enabled
    if monitoring_enabled:
        setup_monitoring_broadcast()
        logger.info("[MAIN] Monitoring broadcast hook configured")

    # Get ports from environment
    monitoring_port = int(os.getenv("MONITORING_PORT", "8080"))
    monitoring_host = os.getenv("MONITORING_HOST", "0.0.0.0")
    health_port = int(os.getenv("HEALTH_CHECK_PORT", "8081"))
    health_host = os.getenv("HEALTH_CHECK_HOST", "0.0.0.0")
    metrics_port = int(os.getenv("METRICS_PORT", "8000"))

    # Start metrics server (synchronous)
    if metrics_enabled:
        try:
            init_metrics_server(port=metrics_port)
            logger.info(f"[MAIN] Metrics server started on port {metrics_port}")
        except Exception as e:
            logger.error(f"[MAIN] Failed to start metrics server: {e}")
            metrics_enabled = False

    # Build list of servers to run
    servers = [main_async()]  # WebSocket daemon (always runs)

    if monitoring_enabled:
        servers.append(start_monitoring_server(host=monitoring_host, port=monitoring_port))
        logger.info(f"[MAIN] Monitoring dashboard will be available at http://localhost:{monitoring_port}/monitoring_dashboard.html")

    if health_enabled:
        servers.append(start_health_server(host=health_host, port=health_port))
        logger.info(f"[MAIN] Health check will be available at http://localhost:{health_port}/health")

    if metrics_enabled:
        servers.append(start_periodic_updates(interval=60))
        logger.info(f"[MAIN] Periodic metrics updates enabled (60s interval)")

    logger.info(f"[MAIN] Starting {len(servers)} servers concurrently")

    # Run all servers concurrently using asyncio.gather
    # If any server fails, all will be cancelled
    try:
        await asyncio.gather(*servers)
    except Exception as e:
        logger.error(f"[MAIN] Server error: {e}")
        raise


def main():
    """Entry point for the daemon launcher."""
    asyncio.run(main_with_monitoring())


if __name__ == "__main__":
    main()

