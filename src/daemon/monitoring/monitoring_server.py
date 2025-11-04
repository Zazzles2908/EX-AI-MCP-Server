"""
Monitoring Server Module

Main server that combines WebSocket and HTTP for monitoring dashboard.
Orchestrates all monitoring components.

Split from monitoring_endpoint.py (2025-11-04) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Start monitoring server
- Coordinate WebSocket and HTTP handlers
- Manage periodic tasks
- Handle graceful shutdown
"""

import asyncio
import logging
from typing import Optional, Callable
from aiohttp import web
from aiohttp.web_runner import TCPSite

from src.daemon.monitoring.websocket_handler import MonitoringWebSocketHandler
from src.daemon.monitoring.http_server import MonitoringHTTPServer
from src.daemon.monitoring.dashboard_broadcaster import get_broadcaster

logger = logging.getLogger(__name__)


class MonitoringServer:
    """
    Main monitoring server that orchestrates WebSocket and HTTP handlers.
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 8080):
        """
        Initialize monitoring server.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.ws_handler = MonitoringWebSocketHandler()
        self.http_server = MonitoringHTTPServer('/path/to/dashboard.html')
        self.site: Optional[TCPSite] = None
        self._shutdown_handler: Optional[Callable] = None
        self._periodic_tasks: list[asyncio.Task] = []

    def set_dashboard_path(self, path: str):
        """
        Set path to dashboard HTML file.

        Args:
            path: Path to dashboard HTML
        """
        self.http_server = MonitoringHTTPServer(path)

    def set_shutdown_handler(self, handler: Callable):
        """
        Set shutdown handler function.

        Args:
            handler: Function to call on shutdown
        """
        self._shutdown_handler = handler

    async def start(self):
        """Start the monitoring server"""
        # Setup HTTP app
        app = self.http_server.get_app()

        # Add WebSocket route
        app.router.add_get('/ws/dashboard', self.ws_handler.handle_connection)

        # Create runner
        runner = web.AppRunner(app)
        await runner.setup()

        # Create site
        self.site = TCPSite(runner, self.host, self.port)
        await self.site.start()

        logger.info(f"Monitoring server started on http://{self.host}:{self.port}")
        logger.info(f"Dashboard: http://{self.host}:{self.port}/")
        logger.info(f"WebSocket: ws://{self.host}:{self.port}/ws/dashboard")

    async def stop(self):
        """Stop the monitoring server"""
        logger.info("Stopping monitoring server...")

        # Cancel periodic tasks
        for task in self._periodic_tasks:
            if not task.done():
                task.cancel()

        # Stop site
        if self.site:
            await self.site.stop()
            self.site = None

        logger.info("Monitoring server stopped")

    async def run_forever(self, shutdown_handler: Optional[Callable] = None):
        """
        Run monitoring server until shutdown.

        Args:
            shutdown_handler: Optional shutdown handler
        """
        await self.start()

        if shutdown_handler:
            self._shutdown_handler = shutdown_handler

        # Keep running
        try:
            await asyncio.Future()
        finally:
            await self.stop()

            # Execute shutdown handler
            if self._shutdown_handler:
                try:
                    logger.info("Executing shutdown handler...")
                    self._shutdown_handler()
                    logger.info("Shutdown handler completed")
                except Exception as e:
                    logger.error(f"Error in shutdown handler: {e}")
