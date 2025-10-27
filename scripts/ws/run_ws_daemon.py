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
    Start WebSocket daemon, monitoring server, health server, metrics server, and AI auditor concurrently.
    Uses asyncio.gather to run all servers in parallel.

    PHASE 3 CRITICAL GAPS (2025-10-18):
    - Added health check server (port 8081)
    - Added Prometheus metrics server (port 8000)
    - Added correlation ID logging setup
    - Added periodic metrics updates

    PHASE 0.1 (2025-10-24):
    - Added AI Auditor service for real-time system observation
    """
    # Setup correlation ID logging
    setup_correlation_logging()
    logger.info("[MAIN] Correlation ID logging configured")

    # Check if monitoring is enabled
    monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() in ("true", "1", "yes")
    health_enabled = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() in ("true", "1", "yes")
    metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() in ("true", "1", "yes")
    auditor_enabled = os.getenv("AUDITOR_ENABLED", "true").lower() in ("true", "1", "yes")

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
        try:
            logger.info(f"[MAIN] Adding monitoring server to servers list (host={monitoring_host}, port={monitoring_port})")
            monitoring_server = start_monitoring_server(host=monitoring_host, port=monitoring_port)
            servers.append(monitoring_server)
            logger.info(f"[MAIN] Monitoring server task added successfully")
            logger.info(f"[MAIN] Monitoring dashboard will be available at http://localhost:{monitoring_port}/monitoring_dashboard.html")
        except Exception as e:
            logger.error(f"[MAIN] Failed to add monitoring server: {e}")
            import traceback
            logger.error(f"[MAIN] Traceback: {traceback.format_exc()}")
            monitoring_enabled = False

    if health_enabled:
        try:
            logger.info(f"[MAIN] Adding health server to servers list (host={health_host}, port={health_port})")
            health_server = start_health_server(host=health_host, port=health_port)
            servers.append(health_server)
            logger.info(f"[MAIN] Health server task added successfully")
            logger.info(f"[MAIN] Health check will be available at http://localhost:{health_port}/health")
        except Exception as e:
            logger.error(f"[MAIN] Failed to add health server: {e}")
            import traceback
            logger.error(f"[MAIN] Traceback: {traceback.format_exc()}")
            health_enabled = False

    if metrics_enabled:
        try:
            logger.info(f"[MAIN] Adding periodic metrics updates to servers list")
            metrics_server = start_periodic_updates(interval=60)
            servers.append(metrics_server)
            logger.info(f"[MAIN] Periodic metrics updates task added successfully")
            logger.info(f"[MAIN] Periodic metrics updates enabled (60s interval)")
        except Exception as e:
            logger.error(f"[MAIN] Failed to add metrics updates: {e}")
            import traceback
            logger.error(f"[MAIN] Traceback: {traceback.format_exc()}")
            metrics_enabled = False

    # PHASE 0.1 (2025-10-24): Start AI Auditor service
    if auditor_enabled:
        try:
            from utils.monitoring.ai_auditor import AIAuditor

            # CRITICAL FIX (2025-10-24): Pass environment variables to AIAuditor constructor
            auditor_model = os.getenv('AUDITOR_MODEL', 'glm-4.5-flash')
            auditor_batch_size = int(os.getenv('AUDITOR_BATCH_SIZE', '10'))
            auditor_interval = int(os.getenv('AUDITOR_ANALYSIS_INTERVAL', '5'))
            auditor_ws_url = os.getenv('AUDITOR_WS_URL', 'ws://localhost:8080/ws')

            auditor = AIAuditor(
                model=auditor_model,
                batch_size=auditor_batch_size,
                analysis_interval=auditor_interval,
                ws_url=auditor_ws_url
            )
            servers.append(auditor.start())
            logger.info(f"[MAIN] AI Auditor service enabled (model: {auditor_model}, batch_size: {auditor_batch_size})")
        except Exception as e:
            logger.error(f"[MAIN] Failed to start AI Auditor: {e}")
            auditor_enabled = False

    logger.info(f"[MAIN] Starting {len(servers)} servers concurrently")
    logger.info(f"[MAIN] Server list: {[type(s).__name__ for s in servers]}")

    # Run all servers concurrently using asyncio.gather
    # Use return_exceptions=True to capture individual server failures
    try:
        results = await asyncio.gather(*servers, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[MAIN] Server {i} failed: {result}")
                import traceback
                logger.error(f"[MAIN] Traceback: {''.join(traceback.format_exception(type(result), result, result.__traceback__))}")
            else:
                logger.info(f"[MAIN] Server {i} completed successfully")
    except Exception as e:
        logger.error(f"[MAIN] Server error: {e}")
        import traceback
        logger.error(f"[MAIN] Traceback: {traceback.format_exc()}")
        raise


def main():
    """Entry point for the daemon launcher."""
    asyncio.run(main_with_monitoring())


if __name__ == "__main__":
    main()

