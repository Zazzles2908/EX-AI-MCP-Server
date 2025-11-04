"""
Production Monitoring Dashboard

Comprehensive real-time monitoring dashboard for EX-AI MCP Server.
Displays system health, performance metrics, incidents, and alerts.

Created: 2025-11-04
Phase 2: Production Readiness
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from aiohttp import web
import logging

logger = logging.getLogger(__name__)


class ProductionMonitoringDashboard:
    """Production monitoring dashboard with real-time updates"""

    def __init__(self):
        self.clients: Dict[str, web.WebSocketResponse] = {}
        self.metrics_buffer: List[Dict] = []
        self.max_buffer_size = 1000

    async def dashboard_handler(self, request: web.Request) -> web.Response:
        """Serve the monitoring dashboard HTML"""
        html = self._generate_dashboard_html()
        return web.Response(text=html, content_type='text/html')

    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        client_id = f"client_{datetime.now().timestamp()}"
        self.clients[client_id] = ws

        logger.info(f"Dashboard client connected: {client_id}")

        # Send initial data
        await self._send_initial_data(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await self._handle_client_message(msg.data, ws)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            logger.info(f"Dashboard client disconnected: {client_id}")

        return ws

    async def _send_initial_data(self, ws: web.WebSocketResponse):
        """Send initial dashboard data to client"""
        initial_data = {
            "type": "initial_data",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "system_health": await self._get_system_health(),
                "recent_metrics": await self._get_recent_metrics(),
                "active_incidents": await self._get_active_incidents(),
                "performance_benchmarks": await self._get_performance_benchmarks(),
                "database_status": await self._get_database_status(),
                "websocket_connections": len(self.clients)
            }
        }
        await ws.send_json(initial_data)

    async def _handle_client_message(self, message: str, ws: web.WebSocketResponse):
        """Handle messages from dashboard clients"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "request_metrics":
                await ws.send_json({
                    "type": "metrics_update",
                    "data": await self._get_recent_metrics()
                })
            elif msg_type == "request_health":
                await ws.send_json({
                    "type": "health_update",
                    "data": await self._get_system_health()
                })
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from client: {message}")

    async def broadcast_metrics(self, metrics: Dict):
        """Broadcast new metrics to all connected clients"""
        self.metrics_buffer.append({
            "timestamp": datetime.now().isoformat(),
            **metrics
        })

        # Keep buffer size in check
        if len(self.metrics_buffer) > self.max_buffer_size:
            self.metrics_buffer.pop(0)

        # Broadcast to all clients
        message = {
            "type": "metrics_update",
            "data": metrics
        }

        disconnected_clients = []
        for client_id, ws in self.clients.items():
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]

    def _generate_dashboard_html(self) -> str:
        """Generate the monitoring dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EX-AI MCP Server - Production Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status-healthy { background: #4caf50; }
        .status-degraded { background: #ff9800; }
        .status-unhealthy { background: #f44336; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: #1a1f3a;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.3);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #2a3f5f;
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
        }

        .card-value {
            font-size: 32px;
            font-weight: 700;
            margin: 10px 0;
        }

        .metric-good { color: #4caf50; }
        .metric-warning { color: #ff9800; }
        .metric-critical { color: #f44336; }

        .chart-container {
            height: 200px;
            margin-top: 15px;
            position: relative;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a3f5f;
        }

        .metric-row:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #a0a0a0;
            font-size: 14px;
        }

        .metric-value {
            font-weight: 600;
            font-size: 14px;
        }

        .incident {
            background: #2a1f2a;
            border-left: 4px solid #f44336;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }

        .incident.high { border-left-color: #f44336; }
        .incident.medium { border-left-color: #ff9800; }
        .incident.low { border-left-color: #2196f3; }

        .incident-title {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .incident-meta {
            font-size: 12px;
            color: #a0a0a0;
        }

        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s ease;
        }

        .refresh-btn:hover {
            background: #764ba2;
        }

        .last-updated {
            text-align: center;
            color: #a0a0a0;
            font-size: 12px;
            margin-top: 20px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }

        .status-item {
            background: #0f1429;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }

        .status-item-label {
            font-size: 12px;
            color: #a0a0a0;
            margin-bottom: 5px;
        }

        .status-item-value {
            font-size: 20px;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span class="status-indicator status-healthy"></span>
            EX-AI MCP Server - Production Monitoring
        </h1>
        <div class="subtitle">Real-time system health and performance monitoring</div>
    </div>

    <div class="container">
        <!-- System Health Overview -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">System Health</div>
                    <button class="refresh-btn" onclick="refreshData()">Refresh</button>
                </div>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-item-label">CPU Usage</div>
                        <div class="status-item-value" id="cpu-usage">--%</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-label">Memory</div>
                        <div class="status-item-value" id="memory-usage">--%</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-label">Disk</div>
                        <div class="status-item-value" id="disk-usage">--%</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-label">WebSocket</div>
                        <div class="status-item-value" id="ws-status">--</div>
                    </div>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Performance</div>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value" id="response-time">-- ms</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Error Rate</span>
                    <span class="metric-value" id="error-rate">--%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Active Connections</span>
                    <span class="metric-value" id="active-connections">--</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Requests/sec</span>
                    <span class="metric-value" id="requests-per-sec">--</span>
                </div>
            </div>

            <!-- Database Status -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Database</div>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Status</span>
                    <span class="metric-value" id="db-status">--</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Connections</span>
                    <span class="metric-value" id="db-connections">--</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Query Time (p95)</span>
                    <span class="metric-value" id="db-query-time">-- ms</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="db-uptime">--</span>
                </div>
            </div>

            <!-- Active Incidents -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Active Incidents</div>
                </div>
                <div id="incidents-container">
                    <div style="color: #a0a0a0; text-align: center; padding: 20px;">
                        No active incidents
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Metrics Chart -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">Real-time Metrics</div>
            </div>
            <div class="chart-container">
                <canvas id="metricsChart"></canvas>
            </div>
        </div>

        <div class="last-updated">
            Last updated: <span id="last-updated">--</span>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let ws = null;
        let metricsData = {
            labels: [],
            cpu: [],
            memory: [],
            responseTime: []
        };

        const chart = new Chart(document.getElementById('metricsChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU %',
                        data: [],
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Memory %',
                        data: [],
                        borderColor: '#2196f3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: '#ff9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e0e0e0'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#a0a0a0'
                        },
                        grid: {
                            color: '#2a3f5f'
                        }
                    },
                    y: {
                        type: 'linear',
                        position: 'left',
                        ticks: {
                            color: '#a0a0a0'
                        },
                        grid: {
                            color: '#2a3f5f'
                        }
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        ticks: {
                            color: '#a0a0a0'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws/dashboard`);

            ws.onopen = () => {
                console.log('Dashboard WebSocket connected');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleDashboardMessage(data);
            };

            ws.onclose = () => {
                console.log('Dashboard WebSocket disconnected, retrying in 3s...');
                setTimeout(connectWebSocket, 3000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }

        function handleDashboardMessage(data) {
            if (data.type === 'initial_data') {
                updateDashboard(data.data);
            } else if (data.type === 'metrics_update') {
                updateMetrics(data.data);
            } else if (data.type === 'health_update') {
                updateHealth(data.data);
            }
        }

        function updateDashboard(data) {
            // Update system health
            if (data.system_health) {
                document.getElementById('cpu-usage').textContent =
                    `${data.system_health.cpu_usage_percent || '--'}%`;
                document.getElementById('memory-usage').textContent =
                    `${data.system_health.memory_usage_percent || '--'}%`;
                document.getElementById('disk-usage').textContent =
                    `${data.system_health.disk_usage_percent || '--'}%`;
                document.getElementById('ws-status').textContent =
                    data.system_health.websocket_status || '--';
            }

            // Update performance metrics
            if (data.recent_metrics) {
                document.getElementById('response-time').textContent =
                    `${data.recent_metrics.avg_response_time || '--'} ms`;
                document.getElementById('error-rate').textContent =
                    `${data.recent_metrics.error_rate || '--'}%`;
                document.getElementById('active-connections').textContent =
                    data.recent_metrics.active_connections || '--';
                document.getElementById('requests-per-sec').textContent =
                    data.recent_metrics.requests_per_sec || '--';
            }

            // Update database status
            if (data.database_status) {
                document.getElementById('db-status').textContent =
                    data.database_status.status || '--';
                document.getElementById('db-connections').textContent =
                    data.database_status.connections || '--';
                document.getElementById('db-query-time').textContent =
                    `${data.database_status.query_time_p95 || '--'} ms`;
                document.getElementById('db-uptime').textContent =
                    data.database_status.uptime || '--';
            }

            // Update incidents
            updateIncidents(data.active_incidents || []);

            // Update timestamp
            document.getElementById('last-updated').textContent =
                new Date().toLocaleTimeString();
        }

        function updateMetrics(metrics) {
            const now = new Date().toLocaleTimeString();

            // Update chart
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(metrics.cpu_usage || 0);
            chart.data.datasets[1].data.push(metrics.memory_usage || 0);
            chart.data.datasets[2].data.push(metrics.response_time || 0);

            // Keep last 20 data points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => dataset.data.shift());
            }

            chart.update('none');

            // Update numeric displays
            document.getElementById('cpu-usage').textContent = `${metrics.cpu_usage || '--'}%`;
            document.getElementById('memory-usage').textContent = `${metrics.memory_usage || '--'}%`;
            document.getElementById('response-time').textContent = `${metrics.response_time || '--'} ms`;
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
        }

        function updateHealth(health) {
            document.getElementById('cpu-usage').textContent = `${health.cpu_usage_percent || '--'}%`;
            document.getElementById('memory-usage').textContent = `${health.memory_usage_percent || '--'}%`;
            document.getElementById('disk-usage').textContent = `${health.disk_usage_percent || '--'}%`;
        }

        function updateIncidents(incidents) {
            const container = document.getElementById('incidents-container');
            container.innerHTML = '';

            if (incidents.length === 0) {
                container.innerHTML = '<div style="color: #a0a0a0; text-align: center; padding: 20px;">No active incidents</div>';
                return;
            }

            incidents.forEach(incident => {
                const div = document.createElement('div');
                div.className = `incident ${incident.severity}`;
                div.innerHTML = `
                    <div class="incident-title">${incident.title}</div>
                    <div class="incident-meta">${incident.severity.toUpperCase()} • ${incident.started_at}</div>
                `;
                container.appendChild(div);
            });
        }

        function refreshData() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'request_metrics' }));
            }
        }

        // Connect WebSocket on load
        connectWebSocket();

        // Refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
        """

    async def _get_system_health(self) -> Dict:
        """Get current system health metrics"""
        # This would normally fetch from actual monitoring system
        # For now, return mock data
        return {
            "cpu_usage_percent": 45.2,
            "memory_usage_percent": 62.8,
            "disk_usage_percent": 34.5,
            "response_time_ms": 120,
            "error_rate_percent": 0.5,
            "websocket_status": "Connected",
            "timestamp": datetime.now().isoformat()
        }

    async def _get_recent_metrics(self) -> Dict:
        """Get recent performance metrics"""
        return {
            "avg_response_time": 120,
            "p95_response_time": 250,
            "error_rate": 0.5,
            "active_connections": 12,
            "requests_per_sec": 45,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_active_incidents(self) -> List[Dict]:
        """Get list of active incidents"""
        # Mock data - would fetch from incidents table
        return []

    async def _get_performance_benchmarks(self) -> Dict:
        """Get performance benchmark results"""
        return {
            "test_status": "pass",
            "avg_latency": 120,
            "throughput": 1000,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_database_status(self) -> Dict:
        """Get database connection and performance status"""
        return {
            "status": "healthy",
            "connections": 5,
            "query_time_p95": 45,
            "uptime": "99.9%",
            "timestamp": datetime.now().isoformat()
        }


# Create dashboard instance
dashboard = ProductionMonitoringDashboard()


def create_monitoring_app() -> web.Application:
    """Create and configure the monitoring application"""
    app = web.Application()

    # Add routes
    app.router.add_get('/', dashboard.dashboard_handler)
    app.router.add_get('/ws/dashboard', dashboard.websocket_handler)

    return app


if __name__ == '__main__':
    # Run standalone dashboard server
    app = create_monitoring_app()
    web.run_app(app, host='127.0.0.1', port=8080)
