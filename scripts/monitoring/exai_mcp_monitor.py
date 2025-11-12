#!/usr/bin/env python3
"""
EXAI MCP Monitoring Client

Provides easy access to EXAI MCP metrics and health information
for external applications like Orchestator.

Usage:
    python exai_mcp_monitor.py --health          # Check health
    python exai_mcp_monitor.py --metrics         # Get all metrics
    python exai_mcp_monitor.py --watch           # Monitor in real-time
    python exai_mcp_monitor.py --connections     # Show connection count
"""

import argparse
import json
import time
import sys
import requests
from typing import Dict, Any

# Configuration
EXAI_HOST = "127.0.0.1"
HEALTH_PORT = 3002
METRICS_PORT = 3003
WS_PORT = 3010

# Global variables (for argparse to update)
GLOBAL_HOST = EXAI_HOST
GLOBAL_HEALTH_PORT = HEALTH_PORT
GLOBAL_METRICS_PORT = METRICS_PORT


def get_health() -> Dict[str, Any]:
    """Get EXAI MCP health status."""
    url = f"http://{GLOBAL_HOST}:{GLOBAL_HEALTH_PORT}/health"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status": "unreachable"}


def get_metrics() -> str:
    """Get EXAI MCP metrics in Prometheus format."""
    url = f"http://{GLOBAL_HOST}:{GLOBAL_METRICS_PORT}/metrics"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"# ERROR: {e}"


def parse_metrics(metrics_text: str) -> Dict[str, float]:
    """Parse Prometheus metrics text into a dictionary."""
    metrics = {}
    for line in metrics_text.split('\n'):
        line = line.strip()
        # Skip comments and empty lines
        if line.startswith('#') or not line:
            continue

        # Parse metric line
        parts = line.split()
        if len(parts) >= 2:
            metric_name = parts[0]
            try:
                metric_value = float(parts[1])
                metrics[metric_name] = metric_value
            except ValueError:
                pass

    return metrics


def format_health(health_data: Dict[str, Any]) -> str:
    """Format health data for display."""
    if "error" in health_data:
        return f"[FAIL] EXAI MCP: UNREACHABLE - {health_data['error']}"

    status_indicator = "[OK]" if health_data.get("status") == "healthy" else "[WARN]"
    uptime = health_data.get("uptime_seconds", 0)
    connections = health_data.get("active_connections", 0)

    return f"""
{status_indicator} EXAI MCP Status: {health_data.get('status', 'unknown')}
   Uptime: {uptime:.0f} seconds ({uptime/3600:.1f} hours)
   Active Connections: {connections}
   Version: {health_data.get('version', 'unknown')}
   Timestamp: {health_data.get('timestamp', 'unknown')}
"""


def format_metrics(metrics: Dict[str, float]) -> str:
    """Format key metrics for display."""
    lines = ["[METRICS] EXAI MCP Metrics:", ""]

    # Key metrics to display
    key_metrics = {
        "exai_mcp_active_connections": "Active Connections",
        "exai_mcp_sessions_active": "Active Sessions",
        "exai_mcp_messages_total": "Total Messages",
        "exai_mcp_tool_calls_total": "Total Tool Calls",
        "exai_mcp_errors_total": "Total Errors",
        "exai_mcp_provider_requests_total": "Provider Requests",
    }

    for metric_name, display_name in key_metrics.items():
        value = metrics.get(metric_name, 0)
        lines.append(f"   {display_name:25} : {value:10.0f}")

    return "\n".join(lines)


def monitor_realtime(interval: int = 5):
    """Monitor EXAI MCP in real-time."""
    print("Monitoring EXAI MCP (Press Ctrl+C to stop)...\n")

    try:
        while True:
            health = get_health()
            print(format_health(health))

            if "error" not in health:
                metrics_text = get_metrics()
                metrics = parse_metrics(metrics_text)
                print(format_metrics(metrics))

            print(f"\n[WAIT] Next update in {interval} seconds...")
            print("=" * 60)
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[EXIT] Monitoring stopped")
        sys.exit(0)


def check_connections():
    """Check current connection count."""
    health = get_health()

    if "error" in health:
        print(f"[FAIL] Cannot check connections: {health['error']}")
        return 1

    connections = health.get("active_connections", 0)
    max_connections = 15

    status = "[OK]" if connections < max_connections else "[WARN]"

    print(f"{status} Active Connections: {connections}/{max_connections}")

    if connections >= max_connections:
        print("[WARN] WARNING: At maximum capacity!")
        return 2

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="EXAI MCP Monitoring Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --health           Check health status
  %(prog)s --metrics           Get all metrics
  %(prog)s --connections       Show connection count
  %(prog)s --watch             Monitor in real-time
        """
    )

    parser.add_argument(
        "--host",
        default=EXAI_HOST,
        help=f"EXAI MCP host (default: {EXAI_HOST})"
    )

    parser.add_argument(
        "--health-port",
        type=int,
        default=HEALTH_PORT,
        help=f"Health endpoint port (default: {HEALTH_PORT})"
    )

    parser.add_argument(
        "--metrics-port",
        type=int,
        default=METRICS_PORT,
        help=f"Metrics endpoint port (default: {METRICS_PORT})"
    )

    parser.add_argument(
        "--health",
        action="store_true",
        help="Check EXAI MCP health status"
    )

    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Get EXAI MCP metrics"
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Monitor EXAI MCP in real-time"
    )

    parser.add_argument(
        "--connections",
        action="store_true",
        help="Show current connection count"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval for --watch (seconds, default: 5)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    # Update global config if ports changed
    global GLOBAL_HEALTH_PORT, GLOBAL_METRICS_PORT, GLOBAL_HOST
    GLOBAL_HEALTH_PORT = args.health_port
    GLOBAL_METRICS_PORT = args.metrics_port
    GLOBAL_HOST = args.host

    # Default to health check if no specific action requested
    if not any([args.health, args.metrics, args.watch, args.connections]):
        args.health = True

    # Execute requested action
    if args.health:
        health = get_health()
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            print(format_health(health))

    if args.metrics:
        metrics_text = get_metrics()
        if args.json:
            metrics = parse_metrics(metrics_text)
            print(json.dumps(metrics, indent=2))
        else:
            metrics = parse_metrics(metrics_text)
            print(format_metrics(metrics))

    if args.connections:
        exit_code = check_connections()
        sys.exit(exit_code)

    if args.watch:
        monitor_realtime(args.interval)

    return 0


if __name__ == "__main__":
    sys.exit(main())
