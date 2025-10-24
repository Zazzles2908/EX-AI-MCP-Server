#!/usr/bin/env python3
"""
Shadow Mode Monitoring Script

Monitors shadow mode metrics in real-time by parsing logs and tracking:
- Comparison count
- Error rate
- Discrepancy rate
- Performance impact

Usage:
    python scripts/monitor_shadow_mode.py [--interval SECONDS] [--duration HOURS]

Options:
    --interval SECONDS  Monitoring interval in seconds (default: 60)
    --duration HOURS    Total monitoring duration in hours (default: 24)
    --log-file PATH     Path to shadow mode log file (default: logs/shadow_mode.log)
    --output PATH       Path to output metrics file (default: logs/shadow_mode_metrics.json)
    --alert-threshold   Error rate threshold for alerts (default: 0.05)

Reference: Phase 2.4.2 Task 3 - Shadow Mode Validation
Date: 2025-10-22
"""

import argparse
import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MigrationConfig


class ShadowModeMonitor:
    """Monitor shadow mode metrics from logs."""

    def __init__(
        self,
        log_file: Path,
        output_file: Path,
        alert_threshold: float = 0.05
    ):
        self.log_file = log_file
        self.output_file = output_file
        self.alert_threshold = alert_threshold
        
        # Metrics
        self.comparison_count = 0
        self.error_count = 0
        self.discrepancy_count = 0
        self.success_count = 0
        
        # Timing metrics
        self.total_duration = 0.0
        self.max_duration = 0.0
        self.min_duration = float('inf')
        
        # Discrepancy details
        self.discrepancies: List[Dict] = []
        
        # Start time
        self.start_time = datetime.now()
        self.last_check_time = self.start_time

    def parse_log_entry(self, line: str) -> Optional[Dict]:
        """Parse a shadow mode log entry."""
        try:
            # Look for shadow mode comparison logs
            if '"operation": "shadow_mode_upload"' not in line:
                return None
            
            # Extract JSON from log line
            # Format: timestamp [level] message {json}
            json_start = line.find('{')
            if json_start == -1:
                return None
            
            json_str = line[json_start:]
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return None

    def update_metrics(self, entry: Dict):
        """Update metrics from a log entry."""
        self.comparison_count += 1
        
        # Update status counts
        if entry.get('has_errors', False):
            self.error_count += 1
        elif not entry.get('results_match', True):
            self.discrepancy_count += 1
            self.discrepancies.append({
                'timestamp': entry.get('timestamp'),
                'file_path': entry.get('file_path'),
                'provider': entry.get('provider'),
                'primary_impl': entry.get('primary_impl'),
                'shadow_impl': entry.get('shadow_impl'),
                'primary_success': entry.get('primary_success'),
                'shadow_success': entry.get('shadow_success')
            })
        else:
            self.success_count += 1
        
        # Update timing metrics
        duration = entry.get('duration_seconds', 0.0)
        self.total_duration += duration
        self.max_duration = max(self.max_duration, duration)
        self.min_duration = min(self.min_duration, duration)

    def calculate_metrics(self) -> Dict:
        """Calculate current metrics."""
        error_rate = self.error_count / self.comparison_count if self.comparison_count > 0 else 0.0
        discrepancy_rate = self.discrepancy_count / self.comparison_count if self.comparison_count > 0 else 0.0
        success_rate = self.success_count / self.comparison_count if self.comparison_count > 0 else 0.0
        avg_duration = self.total_duration / self.comparison_count if self.comparison_count > 0 else 0.0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'monitoring_duration_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'comparison_count': self.comparison_count,
            'error_count': self.error_count,
            'discrepancy_count': self.discrepancy_count,
            'success_count': self.success_count,
            'error_rate': round(error_rate, 4),
            'discrepancy_rate': round(discrepancy_rate, 4),
            'success_rate': round(success_rate, 4),
            'avg_duration_seconds': round(avg_duration, 3),
            'max_duration_seconds': round(self.max_duration, 3),
            'min_duration_seconds': round(self.min_duration, 3) if self.min_duration != float('inf') else 0.0,
            'alert_threshold': self.alert_threshold,
            'threshold_breached': error_rate > self.alert_threshold,
            'config': {
                'shadow_mode_enabled': MigrationConfig.ENABLE_SHADOW_MODE,
                'sample_rate': MigrationConfig.SHADOW_MODE_SAMPLE_RATE,
                'error_threshold': MigrationConfig.SHADOW_MODE_ERROR_THRESHOLD,
                'min_samples': MigrationConfig.SHADOW_MODE_MIN_SAMPLES
            }
        }

    def check_alerts(self, metrics: Dict):
        """Check for alert conditions."""
        if metrics['threshold_breached']:
            print(f"\n⚠️  ALERT: Error rate ({metrics['error_rate']:.2%}) exceeds threshold ({self.alert_threshold:.2%})")
            print(f"   Comparison count: {metrics['comparison_count']}")
            print(f"   Error count: {metrics['error_count']}")
        
        if metrics['comparison_count'] >= MigrationConfig.SHADOW_MODE_MIN_SAMPLES:
            if metrics['discrepancy_rate'] > 0.02:  # 2% threshold
                print(f"\n⚠️  WARNING: Discrepancy rate ({metrics['discrepancy_rate']:.2%}) exceeds 2%")
                print(f"   Discrepancy count: {metrics['discrepancy_count']}")

    def monitor(self, interval: int, duration_hours: float):
        """Monitor shadow mode metrics."""
        end_time = self.start_time + timedelta(hours=duration_hours)
        
        print(f"Shadow Mode Monitoring Started")
        print(f"Start time: {self.start_time.isoformat()}")
        print(f"Duration: {duration_hours} hours")
        print(f"Interval: {interval} seconds")
        print(f"Log file: {self.log_file}")
        print(f"Output file: {self.output_file}")
        print(f"Alert threshold: {self.alert_threshold:.2%}")
        print("-" * 80)
        
        # Track last position in log file
        last_position = 0
        
        try:
            while datetime.now() < end_time:
                # Read new log entries
                if self.log_file.exists():
                    with open(self.log_file, 'r') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                    
                    # Parse new entries
                    for line in new_lines:
                        entry = self.parse_log_entry(line)
                        if entry:
                            self.update_metrics(entry)
                
                # Calculate and display metrics
                metrics = self.calculate_metrics()
                
                # Save metrics to file
                with open(self.output_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                # Display current status
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Shadow Mode Metrics:")
                print(f"  Comparisons: {metrics['comparison_count']}")
                print(f"  Success: {metrics['success_count']} ({metrics['success_rate']:.1%})")
                print(f"  Errors: {metrics['error_count']} ({metrics['error_rate']:.1%})")
                print(f"  Discrepancies: {metrics['discrepancy_count']} ({metrics['discrepancy_rate']:.1%})")
                print(f"  Avg Duration: {metrics['avg_duration_seconds']:.3f}s")
                
                # Check for alerts
                self.check_alerts(metrics)
                
                # Wait for next interval
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user")
        
        # Final report
        print("\n" + "=" * 80)
        print("Shadow Mode Monitoring Complete")
        print("=" * 80)
        
        final_metrics = self.calculate_metrics()
        print(f"\nFinal Metrics:")
        print(f"  Total Comparisons: {final_metrics['comparison_count']}")
        print(f"  Success Rate: {final_metrics['success_rate']:.1%}")
        print(f"  Error Rate: {final_metrics['error_rate']:.1%}")
        print(f"  Discrepancy Rate: {final_metrics['discrepancy_rate']:.1%}")
        print(f"  Avg Duration: {final_metrics['avg_duration_seconds']:.3f}s")
        print(f"\nMetrics saved to: {self.output_file}")
        
        # Save discrepancies if any
        if self.discrepancies:
            discrepancy_file = self.output_file.parent / "shadow_mode_discrepancies.json"
            with open(discrepancy_file, 'w') as f:
                json.dump(self.discrepancies, f, indent=2)
            print(f"Discrepancies saved to: {discrepancy_file}")


def main():
    parser = argparse.ArgumentParser(description='Monitor shadow mode metrics')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--duration', type=float, default=24.0, help='Total monitoring duration in hours')
    parser.add_argument('--log-file', type=Path, default=Path('logs/shadow_mode.log'), help='Shadow mode log file')
    parser.add_argument('--output', type=Path, default=Path('logs/shadow_mode_metrics.json'), help='Output metrics file')
    parser.add_argument('--alert-threshold', type=float, default=0.05, help='Error rate alert threshold')
    
    args = parser.parse_args()
    
    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Create monitor
    monitor = ShadowModeMonitor(
        log_file=args.log_file,
        output_file=args.output,
        alert_threshold=args.alert_threshold
    )
    
    # Start monitoring
    monitor.monitor(interval=args.interval, duration_hours=args.duration)


if __name__ == '__main__':
    main()

