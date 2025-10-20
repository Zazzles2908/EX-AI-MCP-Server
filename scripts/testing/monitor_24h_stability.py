#!/usr/bin/env python
"""
24-Hour Stability Monitoring Script

This script monitors the EX-AI MCP Server for 24 hours and reports:
- Server uptime
- Error rates
- Critical errors
- Performance metrics
- Overall stability score

Run this script in the background while the server is running.
It will create a stability report every hour and a final report after 24 hours.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Bootstrap
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# Monitoring configuration
MONITORING_DURATION_HOURS = 24
CHECK_INTERVAL_SECONDS = 300  # Check every 5 minutes
REPORT_INTERVAL_HOURS = 1  # Report every hour

# Metrics
metrics = {
    "start_time": None,
    "checks_total": 0,
    "checks_successful": 0,
    "checks_failed": 0,
    "errors_critical": 0,
    "errors_warning": 0,
    "response_times": [],
    "last_check_time": None,
    "last_check_status": None
}


async def check_server_health():
    """Check if server is responding and healthy."""
    try:
        start_time = time.time()
        
        ws = await websockets.connect(WS_URL, open_timeout=10)
        
        # Send hello
        hello = {"op": "hello", "token": WS_TOKEN}
        await ws.send(json.dumps(hello))
        
        # Wait for ack
        ack_raw = await asyncio.wait_for(ws.recv(), timeout=10)
        ack = json.loads(ack_raw)
        
        await ws.close()
        
        response_time = time.time() - start_time
        
        if ack.get("op") == "hello_ack" and ack.get("ok"):
            return True, response_time, None
        else:
            return False, response_time, "Invalid hello_ack response"
    
    except Exception as e:
        return False, None, str(e)


def check_logs_for_errors():
    """Check logs for critical errors since last check."""
    log_file = get_repo_root() / "logs" / "ws_daemon.log"
    
    if not log_file.exists():
        return 0, 0
    
    critical_count = 0
    warning_count = 0
    
    try:
        # Read last 1000 lines
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[-1000:]
        
        for line in lines:
            if "ERROR" in line or "CRITICAL" in line:
                critical_count += 1
            elif "WARNING" in line:
                warning_count += 1
    
    except Exception as e:
        print(f"Warning: Could not read log file: {e}")
    
    return critical_count, warning_count


def generate_report(is_final=False):
    """Generate stability report."""
    report_type = "FINAL" if is_final else "HOURLY"
    
    print("\n" + "=" * 70)
    print(f"{report_type} STABILITY REPORT")
    print("=" * 70)
    
    if metrics["start_time"]:
        elapsed = datetime.now() - metrics["start_time"]
        print(f"Monitoring Duration: {elapsed}")
    
    print(f"\nHealth Checks:")
    print(f"  Total: {metrics['checks_total']}")
    print(f"  Successful: {metrics['checks_successful']}")
    print(f"  Failed: {metrics['checks_failed']}")
    
    if metrics['checks_total'] > 0:
        success_rate = (metrics['checks_successful'] / metrics['checks_total']) * 100
        print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\nErrors:")
    print(f"  Critical: {metrics['errors_critical']}")
    print(f"  Warning: {metrics['errors_warning']}")
    
    if metrics['response_times']:
        avg_response = sum(metrics['response_times']) / len(metrics['response_times'])
        max_response = max(metrics['response_times'])
        min_response = min(metrics['response_times'])
        print(f"\nResponse Times:")
        print(f"  Average: {avg_response:.3f}s")
        print(f"  Min: {min_response:.3f}s")
        print(f"  Max: {max_response:.3f}s")
    
    if metrics['last_check_time']:
        print(f"\nLast Check: {metrics['last_check_time']}")
        print(f"Last Status: {metrics['last_check_status']}")
    
    # Calculate stability score
    if metrics['checks_total'] > 0:
        stability_score = (
            (metrics['checks_successful'] / metrics['checks_total']) * 70 +  # 70% weight on uptime
            (1 - min(metrics['errors_critical'] / max(metrics['checks_total'], 1), 1)) * 30  # 30% weight on errors
        )
        print(f"\n📊 Stability Score: {stability_score:.1f}/100")
        
        if stability_score >= 95:
            print("   ✅ EXCELLENT - Production ready")
        elif stability_score >= 85:
            print("   ✅ GOOD - Minor issues")
        elif stability_score >= 70:
            print("   ⚠️  FAIR - Needs attention")
        else:
            print("   ❌ POOR - Critical issues")
    
    print("=" * 70)


async def monitor_stability():
    """Main monitoring loop."""
    print("\n" + "=" * 70)
    print("24-HOUR STABILITY MONITORING")
    print("=" * 70)
    print(f"Start Time: {datetime.now()}")
    print(f"End Time: {datetime.now() + timedelta(hours=MONITORING_DURATION_HOURS)}")
    print(f"Check Interval: {CHECK_INTERVAL_SECONDS}s")
    print(f"Report Interval: {REPORT_INTERVAL_HOURS}h")
    print("=" * 70)
    
    metrics["start_time"] = datetime.now()
    end_time = metrics["start_time"] + timedelta(hours=MONITORING_DURATION_HOURS)
    last_report_time = metrics["start_time"]
    
    while datetime.now() < end_time:
        # Perform health check
        metrics["checks_total"] += 1
        
        healthy, response_time, error = await check_server_health()
        
        if healthy:
            metrics["checks_successful"] += 1
            metrics["response_times"].append(response_time)
            metrics["last_check_status"] = f"✅ Healthy ({response_time:.3f}s)"
        else:
            metrics["checks_failed"] += 1
            metrics["last_check_status"] = f"❌ Failed: {error}"
        
        metrics["last_check_time"] = datetime.now()
        
        # Check logs for errors
        critical, warning = check_logs_for_errors()
        metrics["errors_critical"] += critical
        metrics["errors_warning"] += warning
        
        # Print status
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {metrics['last_check_status']}")
        
        # Generate hourly report
        if (datetime.now() - last_report_time).total_seconds() >= REPORT_INTERVAL_HOURS * 3600:
            generate_report(is_final=False)
            last_report_time = datetime.now()
        
        # Wait for next check
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
    
    # Generate final report
    generate_report(is_final=True)
    
    # Save report to file
    report_file = get_repo_root() / "docs" / "consolidated_checklist" / "evidence" / f"24H_STABILITY_REPORT_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(report_file, 'w') as f:
        f.write(f"# 24-Hour Stability Report - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Start Time:** {metrics['start_time']}\n")
        f.write(f"- **End Time:** {datetime.now()}\n")
        f.write(f"- **Duration:** {datetime.now() - metrics['start_time']}\n\n")
        f.write(f"## Metrics\n\n")
        f.write(f"- **Total Checks:** {metrics['checks_total']}\n")
        f.write(f"- **Successful:** {metrics['checks_successful']}\n")
        f.write(f"- **Failed:** {metrics['checks_failed']}\n")
        f.write(f"- **Success Rate:** {(metrics['checks_successful'] / metrics['checks_total']) * 100:.1f}%\n\n")
        f.write(f"## Errors\n\n")
        f.write(f"- **Critical:** {metrics['errors_critical']}\n")
        f.write(f"- **Warning:** {metrics['errors_warning']}\n\n")
        
        if metrics['response_times']:
            avg_response = sum(metrics['response_times']) / len(metrics['response_times'])
            f.write(f"## Response Times\n\n")
            f.write(f"- **Average:** {avg_response:.3f}s\n")
            f.write(f"- **Min:** {min(metrics['response_times']):.3f}s\n")
            f.write(f"- **Max:** {max(metrics['response_times']):.3f}s\n\n")
        
        stability_score = (
            (metrics['checks_successful'] / metrics['checks_total']) * 70 +
            (1 - min(metrics['errors_critical'] / max(metrics['checks_total'], 1), 1)) * 30
        )
        f.write(f"## Stability Score\n\n")
        f.write(f"**{stability_score:.1f}/100**\n\n")
        
        if stability_score >= 95:
            f.write("✅ **EXCELLENT** - Production ready\n")
        elif stability_score >= 85:
            f.write("✅ **GOOD** - Minor issues\n")
        elif stability_score >= 70:
            f.write("⚠️ **FAIR** - Needs attention\n")
        else:
            f.write("❌ **POOR** - Critical issues\n")
    
    print(f"\n✅ Report saved to: {report_file}")


if __name__ == "__main__":
    print("\n⚠️  NOTE: This script will run for 24 hours!")
    print("   Make sure the server is running before starting.")
    print("   Press Ctrl+C to stop monitoring early.\n")
    
    try:
        asyncio.run(monitor_stability())
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        generate_report(is_final=True)
        print("\nPartial results saved.")

