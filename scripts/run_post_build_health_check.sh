#!/bin/bash
# EXAI MCP Server - Post-Build Health Check Script
# This script runs after container startup to validate everything is working

set -e

echo "=================================="
echo "EXAI MCP Server - Post-Build Health Check"
echo "=================================="
echo ""

# Wait for containers to be ready
echo "[1/5] Waiting for containers to start..."
sleep 5

# Run the automated health check
echo "[2/5] Running automated health check..."
python scripts/health_check_automated.py

# Check if health check passed
HEALTH_CHECK_RESULT=$?

if [ $HEALTH_CHECK_RESULT -eq 0 ]; then
    echo ""
    echo "[3/5] Health check passed - Starting WebSocket daemon..."
    echo ""
    # Start the actual daemon
    python -u scripts/ws/run_ws_daemon.py
elif [ $HEALTH_CHECK_RESULT -eq 1 ]; then
    echo ""
    echo "WARNING: Critical issues detected!"
    echo "Report saved to: docs/reports/CONTAINER_HEALTH_REPORT.md"
    echo ""
    echo "You can still continue, but issues should be addressed."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -u scripts/ws/run_ws_daemon.py
    else
        echo "Exiting. Please fix issues and rebuild."
        exit 1
    fi
else
    echo ""
    echo "Health check completed with warnings."
    echo "Report saved to: docs/reports/CONTAINER_HEALTH_REPORT.md"
    echo ""
    python -u scripts/ws/run_ws_daemon.py
fi
