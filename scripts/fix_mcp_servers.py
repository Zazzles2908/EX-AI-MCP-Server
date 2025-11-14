#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EX-AI MCP Server Fix Script
Diagnoses and fixes common MCP server issues.
"""

import os
import sys
import json
import time
import socket
import signal
import subprocess
from pathlib import Path


def print_header(title: str):
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


def print_step(step: str):
    print(f"\n>>> {step}")


def check_port(port: int, description: str) -> bool:
    """Check if a port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()

    if result == 0:
        print(f"  [OK] {description} (port {port}): IN USE")
        return True
    else:
        print(f"  [FAIL] {description} (port {port}): AVAILABLE")
        return False


def kill_process_on_port(port: int):
    """Kill process using a specific port."""
    print(f"  Killing process on port {port}...")

    try:
        # Find process using netstat
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"    Found PID: {pid}")
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(1)
                    print(f"    Killed process {pid}")
                    return True
    except Exception as e:
        print(f"    Error: {e}")

    return False


def cleanup_old_logs():
    """Clean up old WS Shim log files."""
    print_step("Cleaning up old logs...")

    logs_dir = Path(__file__).parent.parent / "logs"
    shim_logs = list(logs_dir.glob("ws_shim_*.log"))

    if len(shim_logs) > 50:
        print(f"  Found {len(shim_logs)} old shim log files")
        count = 0
        for log_file in shim_logs:
            try:
                # Keep only the 10 most recent
                if count < len(shim_logs) - 10:
                    log_file.unlink()
                    count += 1
            except Exception as e:
                print(f"    Error deleting {log_file}: {e}")

        print(f"  Deleted {count} old log files")
    else:
        print(f"  Only {len(shim_logs)} log files - no cleanup needed")


def cleanup_orphaned_shims():
    """Run the cleanup orphaned shims script."""
    print_step("Cleaning up orphaned shims...")

    cleanup_script = Path(__file__).parent / "runtime" / "cleanup_orphaned_shims.py"

    if cleanup_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(cleanup_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"  Cleanup script output:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"    {line}")
        except Exception as e:
            print(f"  Error running cleanup: {e}")
    else:
        print(f"  Cleanup script not found: {cleanup_script}")


def start_ws_shim():
    """Start the WebSocket Shim in background."""
    print_step("Starting WS Shim...")

    shim_script = Path(__file__).parent / "runtime" / "start_ws_shim_safe.py"

    if not shim_script.exists():
        print(f"  [FAIL] Shim script not found: {shim_script}")
        return False

    # Check if already running
    if check_port(3005, "WS Shim"):
        print(f"  WS Shim already running on port 3005")
        return True

    print(f"  Starting shim: {shim_script}")
    print(f"  Command: {sys.executable} {shim_script}")

    try:
        # Start shim in background
        process = subprocess.Popen(
            [sys.executable, str(shim_script)],
            cwd=Path(__file__).parent.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"  Shim started with PID: {process.pid}")
        print(f"  Waiting for startup...")

        # Wait a bit for startup
        time.sleep(3)

        # Check if still running
        if process.poll() is None:
            print(f"  [OK] Shim is running (PID: {process.pid})")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"  [FAIL] Shim exited with code {process.returncode}")
            if stdout:
                print(f"    stdout: {stdout[:200]}")
            if stderr:
                print(f"    stderr: {stderr[:200]}")
            return False

    except Exception as e:
        print(f"  [FAIL] Error starting shim: {e}")
        return False


def test_mcp_connection():
    """Test MCP connection to WS Shim."""
    print_step("Testing MCP connection...")

    # Check if shim is listening
    if not check_port(3005, "WS Shim"):
        print(f"  [FAIL] WS Shim not listening on port 3005")
        return False

    print(f"  [OK] WS Shim is listening on port 3005")

    # The actual MCP connection test requires a full MCP client
    # For now, just verify the port is open
    print(f"  Note: Full MCP connection test requires Claude Code client")
    return True


def check_docker_services():
    """Check Docker services status."""
    print_step("Checking Docker services...")

    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(f"  Docker services status:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"    {line}")
            return True
        else:
            print(f"  [FAIL] Error checking Docker: {result.stderr}")
            return False

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def check_exai_health():
    """Check EXAI daemon health."""
    print_step("Checking EXAI daemon health...")

    try:
        import requests
        response = requests.get("http://127.0.0.1:3002/health", timeout=2)
        if response.status_code == 200:
            health = response.json()
            print(f"  [OK] EXAI Daemon healthy: {health.get('status', 'unknown')}")
            return True
        else:
            print(f"  [FAIL] Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    """Main fix script."""
    print_header("EX-AI MCP Server Fix Script")

    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Track results
    results = {}

    # 1. Check Docker services
    results['docker'] = check_docker_services()

    # 2. Check EXAI health
    results['health'] = check_exai_health()

    # 3. Clean up old logs
    cleanup_old_logs()

    # 4. Clean up orphaned shims
    cleanup_orphaned_shims()

    # 5. Kill any processes on port 3005
    if check_port(3005, "WS Shim"):
        print(f"  Port 3005 in use - will need to restart")
        kill_process_on_port(3005)
        time.sleep(1)

    # 6. Start WS Shim
    results['shim'] = start_ws_shim()

    # 7. Test MCP connection
    results['connection'] = test_mcp_connection()

    # Summary
    print_header("FIX SCRIPT SUMMARY")

    print(f"\nResults:")
    print(f"  Docker Services: {'[OK]' if results.get('docker') else '[FAIL]'}")
    print(f"  EXAI Health:     {'[OK]' if results.get('health') else '[FAIL]'}")
    print(f"  WS Shim:         {'[OK]' if results.get('shim') else '[FAIL]'}")
    print(f"  MCP Connection:  {'[OK]' if results.get('connection') else '[FAIL]'}")

    all_ok = all(results.values())

    print(f"\n{'=' * 70}")
    if all_ok:
        print(f"ALL CHECKS PASSED!")
        print(f"\nYour EX-AI MCP Server should now be operational.")
        print(f"\nNext steps:")
        print(f"  1. Start/restart Claude Code")
        print(f"  2. MCP servers should now connect automatically")
        print(f"  3. Check logs/ws-shim.log for any issues")
    else:
        print(f"SOME CHECKS FAILED - Manual intervention required")
        print(f"\nPlease review the output above and:")
        print(f"  1. Check Docker containers: docker-compose ps")
        print(f"  2. Check daemon logs: tail -f logs/ws_daemon.log")
        print(f"  3. Check shim logs: tail -f logs/ws-shim.log")
        print(f"  4. Restart services: docker-compose restart")
    print(f"{'=' * 70}\n")

    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
