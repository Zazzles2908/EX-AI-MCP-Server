"""
HTTP Server Module

Serves static files for the monitoring dashboard.
Provides HTTP endpoints for dashboard resources.

Split from monitoring_endpoint.py (2025-11-04) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Serve dashboard HTML
- Serve static assets
- Handle HTTP requests
- Serve monitoring data
"""

import logging
from pathlib import Path
from aiohttp import web
from aiohttp.web_static import StaticResource

logger = logging.getLogger(__name__)


class MonitoringHTTPServer:
    """Serves HTTP endpoints for monitoring dashboard"""

    def __init__(self, dashboard_html_path: str):
        """
        Initialize HTTP server.

        Args:
            dashboard_html_path: Path to dashboard HTML file
        """
        self.dashboard_html_path = Path(dashboard_html_path)
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app = web.Application()

        # Route: Dashboard home
        self.app.router.add_get('/', self._serve_dashboard)

        # Route: API health check
        self.app.router.add_get('/health', self._health_check)

        # Route: API metrics (for non-WebSocket clients)
        self.app.router.add_get('/api/metrics', self._get_metrics)

    async def _serve_dashboard(self, request: web.Request) -> web.Response:
        """
        Serve the monitoring dashboard HTML.

        Args:
            request: aiohttp request

        Returns:
            HTTP response with HTML
        """
        try:
            if self.dashboard_html_path.exists():
                html_content = self.dashboard_html_path.read_text()
                return web.Response(text=html_content, content_type='text/html')
            else:
                # Fallback: simple HTML if file doesn't exist
                html = self._generate_fallback_html()
                return web.Response(text=html, content_type='text/html')
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            return web.Response(
                text="Error loading dashboard",
                status=500,
                content_type='text/plain'
            )

    def _generate_fallback_html(self) -> str:
        """
        Generate fallback HTML if dashboard file not found.

        Returns:
            HTML string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <title>EX-AI MCP Server - Monitoring</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .status { font-size: 24px; color: #4caf50; }
    </style>
</head>
<body>
    <h1>EX-AI MCP Server</h1>
    <div class="status">✓ Monitoring Active</div>
    <p>WebSocket endpoint: /ws/dashboard</p>
</body>
</html>
        """

    async def _health_check(self, request: web.Request) -> web.Response:
        """
        Health check endpoint.

        Args:
            request: aiohttp request

        Returns:
            JSON response with status
        """
        return web.json_response({
            "status": "healthy",
            "service": "monitoring",
            "version": "1.0.0"
        })

    async def _get_metrics(self, request: web.Request) -> web.Response:
        """
        Get current metrics via HTTP (non-WebSocket).

        Args:
            request: aiohttp request

        Returns:
            JSON response with metrics
        """
        # This would normally fetch from actual monitoring system
        # For now, return mock data
        metrics = {
            "timestamp": "2025-11-04T00:00:00Z",
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 34.5,
            "active_connections": 0,
            "response_time_ms": 120
        }

        return web.json_response(metrics)

    def get_app(self) -> web.Application:
        """Get the aiohttp application"""
        return self.app
