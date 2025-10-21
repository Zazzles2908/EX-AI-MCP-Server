"""
Simple HTTP server for performance metrics JSON endpoint.

Serves real-time performance metrics at http://localhost:9109/metrics

Usage:
    python scripts/metrics_server.py

Environment Variables:
    METRICS_JSON_PORT: Port for JSON metrics endpoint (default: 9109)
    METRICS_JSON_ENABLED: Enable JSON metrics endpoint (default: true)

Created: 2025-10-11 (Phase 2 Cleanup, Task 2.C Day 4)
"""

import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.infrastructure.performance_metrics import get_all_metrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("METRICS_JSON_PORT", "9109"))
ENABLED = os.getenv("METRICS_JSON_ENABLED", "true").lower() == "true"


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for metrics endpoint."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/metrics" or self.path == "/metrics/":
            self.send_metrics()
        elif self.path == "/health" or self.path == "/health/":
            self.send_health()
        else:
            self.send_error(404, "Not Found")
    
    def send_metrics(self):
        """Send metrics as JSON."""
        try:
            metrics = get_all_metrics()
            response = json.dumps(metrics, indent=2)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            logger.error(f"Error serving metrics: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def send_health(self):
        """Send health check."""
        response = json.dumps({"status": "ok", "service": "metrics-server"})
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server():
    """Run the metrics server."""
    if not ENABLED:
        logger.warning("Metrics JSON endpoint is disabled (METRICS_JSON_ENABLED=false)")
        return
    
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, MetricsHandler)
    
    logger.info(f"Starting metrics server on http://localhost:{PORT}/metrics")
    logger.info("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down metrics server")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()

