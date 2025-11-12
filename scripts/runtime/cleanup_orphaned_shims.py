#!/usr/bin/env python3
"""
Cleanup orphaned WebSocket shim processes.

This script detects and kills orphaned run_ws_shim.py instances
that didn't shut down properly (e.g., when VSCode closes forcibly).
"""

import os
import sys
import psutil
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

SHIM_PORT = 3005
SHIM_SCRIPT = "run_ws_shim.py"


def find_shim_processes():
    """Find all run_ws_shim.py processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if SHIM_SCRIPT in cmdline and 'python' in proc.info['name'].lower():
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes


def is_port_in_use(port):
    """Check if a port is in use."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTENING':
            return conn.pid
    return None


def cleanup_orphaned_shims():
    """Find and kill orphaned WebSocket shims."""
    shim_processes = find_shim_processes()

    if not shim_processes:
        logger.info("No run_ws_shim processes found")
        return

    logger.info(f"Found {len(shim_processes)} run_ws_shim process(es)")

    # Check which ports are in use
    port_pids = {SHIM_PORT: is_port_in_use(SHIM_PORT)}

    killed_any = False
    for proc in shim_processes:
        try:
            cmdline = ' '.join(proc.cmdline() or [])
            pid = proc.pid

            port_holder = port_pids.get(SHIM_PORT)

            # If port is in use by a different PID, or multiple shims detected
            if (port_holder and port_holder != pid) or len(shim_processes) > 1:
                logger.warning(f"Killing orphaned shim (PID {pid}): {cmdline[:100]}...")
                proc.terminate()
                killed_any = True
            else:
                logger.info(f"Active shim (PID {pid}): {cmdline[:100]}...")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Wait for terminated processes to die
    if killed_any:
        import time
        time.sleep(1)

        # Force kill if still alive
        for proc in shim_processes:
            try:
                if proc.is_running():
                    logger.warning(f"Force killing PID {pid}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    return killed_any


def main():
    parser = argparse.ArgumentParser(description="Cleanup orphaned WebSocket shims")
    parser.add_argument('--check-only', action='store_true',
                       help='Only check, do not kill processes')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("WebSocket Shim Cleanup")
    logger.info(f"  Target Port: {SHIM_PORT}")
    logger.info(f"  Target Script: {SHIM_SCRIPT}")
    logger.info("=" * 60)

    killed = cleanup_orphaned_shims()

    if not args.check_only:
        port_pid = is_port_in_use(SHIM_PORT)
        if port_pid:
            logger.info(f"Port {SHIM_PORT} is now held by PID {port_pid}")
        else:
            logger.info(f"Port {SHIM_PORT} is available")

    if killed:
        logger.info("Cleanup completed")
        return 0
    else:
        logger.info("No cleanup needed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
