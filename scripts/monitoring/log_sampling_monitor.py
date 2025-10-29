#!/usr/bin/env python3
"""
Log Sampling Monitoring Script

Monitors sampling effectiveness and provides real-time statistics on log volume reduction.

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
Phase 3: Enhanced Monitoring Implementation
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logging_utils import get_logger, AsyncLogHandler, SamplingLogger


class LogSamplingMonitor:
    """Monitor log sampling effectiveness and performance."""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize monitoring.
        
        Args:
            check_interval: Seconds between monitoring checks
        """
        self.check_interval = check_interval
        self.logger = get_logger(__name__)
        self.start_time = time.time()
        self.previous_stats = {}
        
    def collect_handler_stats(self) -> Dict[str, Any]:
        """Collect statistics from all AsyncLogHandlers."""
        stats = {}
        
        # Find all AsyncLogHandlers in the logging system
        import logging
        root_logger = logging.getLogger()
        
        for handler in root_logger.handlers:
            if isinstance(handler, AsyncLogHandler):
                handler_stats = handler.get_stats()
                stats[f"async_handler_{id(handler)}"] = handler_stats
        
        return stats
    
    def collect_sampler_stats(self) -> Dict[str, Any]:
        """Collect statistics from all SamplingLoggers."""
        # This would need to be implemented by tracking SamplingLogger instances
        # For now, return placeholder
        return {
            "note": "SamplingLogger stats collection requires instance tracking"
        }
    
    def calculate_metrics(self, current_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics from current statistics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "handlers": {}
        }
        
        for handler_id, stats in current_stats.items():
            if handler_id.startswith("async_handler_"):
                processed = stats.get("processed", 0)
                dropped = stats.get("dropped", 0)
                blocked = stats.get("blocked", 0)
                
                # Calculate rates if we have previous stats
                prev_stats = self.previous_stats.get(handler_id, {})
                prev_processed = prev_stats.get("processed", 0)
                prev_dropped = prev_stats.get("dropped", 0)
                
                delta_processed = processed - prev_processed
                delta_dropped = dropped - prev_dropped
                
                metrics["handlers"][handler_id] = {
                    "current": stats,
                    "delta": {
                        "processed": delta_processed,
                        "dropped": delta_dropped,
                        "processing_rate": delta_processed / self.check_interval if self.check_interval > 0 else 0
                    }
                }
        
        return metrics
    
    def print_report(self, metrics: Dict[str, Any]):
        """Print monitoring report to console."""
        print("\n" + "="*80)
        print(f"LOG SAMPLING MONITOR - {metrics['timestamp']}")
        print(f"Uptime: {metrics['uptime_seconds']:.0f}s")
        print("="*80)
        
        for handler_id, handler_metrics in metrics["handlers"].items():
            current = handler_metrics["current"]
            delta = handler_metrics["delta"]
            
            print(f"\n{handler_id}:")
            print(f"  Queue: {current['queue_size']}/{current['queue_max']} ({current['utilization_percent']:.1f}%)")
            print(f"  Processed: {current['processed']} (+{delta['processed']} in last {self.check_interval}s)")
            print(f"  Dropped: {current['dropped']} (+{delta['dropped']})")
            print(f"  Blocked: {current['blocked']}")
            print(f"  Drop Rate: {current['drop_rate']:.2f}%")
            print(f"  Processing Rate: {delta['processing_rate']:.1f} logs/sec")
            print(f"  Strategy: {current['overflow_strategy']}")
        
        print("\n" + "="*80 + "\n")
    
    def save_metrics(self, metrics: Dict[str, Any], output_file: str = "log_sampling_metrics.jsonl"):
        """Save metrics to JSONL file for analysis."""
        output_path = project_root / "logs" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "a") as f:
            f.write(json.dumps(metrics) + "\n")
    
    def run(self, duration: int = None, save_to_file: bool = True):
        """
        Run monitoring loop.
        
        Args:
            duration: Total duration in seconds (None = run forever)
            save_to_file: Whether to save metrics to file
        """
        print(f"Starting log sampling monitor (check interval: {self.check_interval}s)")
        if duration:
            print(f"Will run for {duration}s")
        else:
            print("Press Ctrl+C to stop")
        
        start = time.time()
        
        try:
            while True:
                # Collect current stats
                handler_stats = self.collect_handler_stats()
                sampler_stats = self.collect_sampler_stats()
                
                current_stats = {**handler_stats, **sampler_stats}
                
                # Calculate metrics
                metrics = self.calculate_metrics(current_stats)
                
                # Print report
                self.print_report(metrics)
                
                # Save to file
                if save_to_file:
                    self.save_metrics(metrics)
                
                # Update previous stats
                self.previous_stats = current_stats
                
                # Check duration
                if duration and (time.time() - start) >= duration:
                    print(f"Monitoring duration ({duration}s) complete")
                    break
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        
        # Final report
        print("\n" + "="*80)
        print("FINAL MONITORING SUMMARY")
        print("="*80)
        final_stats = self.collect_handler_stats()
        final_metrics = self.calculate_metrics(final_stats)
        self.print_report(final_metrics)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor log sampling effectiveness")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--duration", type=int, default=None, help="Total duration in seconds (default: run forever)")
    parser.add_argument("--no-save", action="store_true", help="Don't save metrics to file")
    
    args = parser.parse_args()
    
    monitor = LogSamplingMonitor(check_interval=args.interval)
    monitor.run(duration=args.duration, save_to_file=not args.no_save)


if __name__ == "__main__":
    main()

