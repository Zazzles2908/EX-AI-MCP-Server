#!/usr/bin/env python3
"""
Real-Time Log Monitoring Script
================================

Monitors Docker logs in real-time during intensive load testing.
Alerts on errors, tracks log volume, validates sampling rates.

EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
"""

import asyncio
import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogMonitor:
    """Real-time Docker log monitor"""
    
    def __init__(self, container_name: str = "exai-mcp-daemon"):
        self.container_name = container_name
        self.log_counts = defaultdict(int)
        self.error_patterns = []
        self.warning_patterns = []
        self.sampling_stats = defaultdict(lambda: {'total': 0, 'sampled': 0})
        self.start_time = datetime.now()
        
        # Alert thresholds
        self.error_threshold = 10  # Alert if >10 errors per minute
        self.warning_threshold = 50  # Alert if >50 warnings per minute
        self.log_volume_threshold = 1000  # Alert if >1000 logs per minute
        
        # Sampling rate validation
        self.expected_sampling_rates = {
            'high_freq': 0.01,  # 1%
            'medium_freq': 0.05,  # 5%
            'low_freq': 0.20,  # 20%
        }
    
    async def monitor_logs(self, duration_seconds: int = 5400):  # 90 minutes
        """Monitor Docker logs in real-time"""
        logger.info("=" * 80)
        logger.info(f"Starting real-time log monitoring for {duration_seconds}s")
        logger.info(f"Container: {self.container_name}")
        logger.info("=" * 80)
        
        try:
            # Start docker logs process
            process = await asyncio.create_subprocess_exec(
                "docker", "logs", "-f", self.container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor both stdout and stderr
            tasks = [
                self._monitor_stream(process.stdout, "stdout"),
                self._monitor_stream(process.stderr, "stderr"),
                self._periodic_summary(duration_seconds)
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Monitoring failed: {e}", exc_info=True)
    
    async def _monitor_stream(self, stream, stream_name: str):
        """Monitor a single log stream"""
        line_count = 0
        
        while True:
            try:
                line = await stream.readline()
                if not line:
                    break
                
                line_text = line.decode('utf-8', errors='ignore').strip()
                if not line_text:
                    continue
                
                line_count += 1
                
                # Analyze log line
                self._analyze_log_line(line_text)
                
                # Print errors and warnings immediately
                if 'ERROR' in line_text:
                    logger.error(f"[DOCKER] {line_text}")
                elif 'WARNING' in line_text and 'Circuit breaker' in line_text:
                    logger.warning(f"[DOCKER] {line_text}")
                
            except Exception as e:
                logger.error(f"Stream monitoring error: {e}")
                break
    
    def _analyze_log_line(self, line: str):
        """Analyze a single log line"""
        # Count by log level
        if 'ERROR' in line:
            self.log_counts['ERROR'] += 1
            self.error_patterns.append(line)
        elif 'WARNING' in line:
            self.log_counts['WARNING'] += 1
            self.warning_patterns.append(line)
        elif 'INFO' in line:
            self.log_counts['INFO'] += 1
        elif 'DEBUG' in line:
            self.log_counts['DEBUG'] += 1
        
        self.log_counts['TOTAL'] += 1
        
        # Track sampling statistics
        if 'high_freq_sampler' in line or '[1%]' in line:
            self.sampling_stats['high_freq']['total'] += 1
            if 'SAMPLED' in line or 'logged' in line:
                self.sampling_stats['high_freq']['sampled'] += 1
        
        elif 'medium_freq_sampler' in line or '[5%]' in line:
            self.sampling_stats['medium_freq']['total'] += 1
            if 'SAMPLED' in line or 'logged' in line:
                self.sampling_stats['medium_freq']['sampled'] += 1
        
        elif 'low_freq_sampler' in line or '[20%]' in line:
            self.sampling_stats['low_freq']['total'] += 1
            if 'SAMPLED' in line or 'logged' in line:
                self.sampling_stats['low_freq']['sampled'] += 1
    
    async def _periodic_summary(self, duration_seconds: int):
        """Print periodic summary every 5 minutes"""
        summary_interval = 300  # 5 minutes
        end_time = asyncio.get_event_loop().time() + duration_seconds
        
        while asyncio.get_event_loop().time() < end_time:
            await asyncio.sleep(summary_interval)
            self._print_summary()
    
    def _print_summary(self):
        """Print monitoring summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        elapsed_minutes = elapsed / 60
        
        logger.info("=" * 80)
        logger.info(f"MONITORING SUMMARY ({elapsed_minutes:.1f} minutes elapsed)")
        logger.info("=" * 80)
        
        # Log volume
        total_logs = self.log_counts['TOTAL']
        logs_per_minute = total_logs / elapsed_minutes if elapsed_minutes > 0 else 0
        
        logger.info(f"Total log lines: {total_logs}")
        logger.info(f"Logs per minute: {logs_per_minute:.1f}")
        logger.info(f"Log breakdown:")
        for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
            count = self.log_counts[level]
            percentage = (count / total_logs * 100) if total_logs > 0 else 0
            logger.info(f"  {level}: {count} ({percentage:.1f}%)")
        
        # Sampling statistics
        logger.info(f"\nSampling Statistics:")
        for tier, stats in self.sampling_stats.items():
            if stats['total'] > 0:
                actual_rate = stats['sampled'] / stats['total']
                expected_rate = self.expected_sampling_rates.get(tier, 0)
                deviation = abs(actual_rate - expected_rate) / expected_rate * 100 if expected_rate > 0 else 0
                
                logger.info(f"  {tier}: {stats['sampled']}/{stats['total']} "
                           f"(actual: {actual_rate:.2%}, expected: {expected_rate:.2%}, "
                           f"deviation: {deviation:.1f}%)")
        
        # Alerts
        errors_per_minute = self.log_counts['ERROR'] / elapsed_minutes if elapsed_minutes > 0 else 0
        warnings_per_minute = self.log_counts['WARNING'] / elapsed_minutes if elapsed_minutes > 0 else 0
        
        if errors_per_minute > self.error_threshold:
            logger.warning(f"⚠️  HIGH ERROR RATE: {errors_per_minute:.1f} errors/min "
                          f"(threshold: {self.error_threshold})")
        
        if warnings_per_minute > self.warning_threshold:
            logger.warning(f"⚠️  HIGH WARNING RATE: {warnings_per_minute:.1f} warnings/min "
                          f"(threshold: {self.warning_threshold})")
        
        if logs_per_minute > self.log_volume_threshold:
            logger.warning(f"⚠️  HIGH LOG VOLUME: {logs_per_minute:.1f} logs/min "
                          f"(threshold: {self.log_volume_threshold})")
        
        # Recent errors
        if self.error_patterns:
            logger.info(f"\nRecent errors ({len(self.error_patterns)} total):")
            for error in self.error_patterns[-5:]:  # Show last 5 errors
                logger.info(f"  {error[:100]}...")
        
        logger.info("=" * 80)
    
    def save_final_report(self, output_file: Path):
        """Save final monitoring report"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'monitoring_duration_seconds': elapsed,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'log_counts': dict(self.log_counts),
            'sampling_statistics': {
                tier: {
                    'total_operations': stats['total'],
                    'sampled_operations': stats['sampled'],
                    'actual_rate': stats['sampled'] / stats['total'] if stats['total'] > 0 else 0,
                    'expected_rate': self.expected_sampling_rates.get(tier, 0),
                    'deviation_percent': abs((stats['sampled'] / stats['total']) - self.expected_sampling_rates.get(tier, 0)) / self.expected_sampling_rates.get(tier, 1) * 100 if stats['total'] > 0 and self.expected_sampling_rates.get(tier, 0) > 0 else 0
                }
                for tier, stats in self.sampling_stats.items()
            },
            'error_patterns': self.error_patterns[-100:],  # Last 100 errors
            'warning_patterns': self.warning_patterns[-100:],  # Last 100 warnings
            'alerts': {
                'high_error_rate': self.log_counts['ERROR'] / (elapsed / 60) > self.error_threshold if elapsed > 0 else False,
                'high_warning_rate': self.log_counts['WARNING'] / (elapsed / 60) > self.warning_threshold if elapsed > 0 else False,
                'high_log_volume': self.log_counts['TOTAL'] / (elapsed / 60) > self.log_volume_threshold if elapsed > 0 else False
            }
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Final monitoring report saved to {output_file}")


async def main():
    """Main entry point"""
    monitor = LogMonitor()
    
    try:
        # Run monitoring for 90 minutes
        await monitor.monitor_logs(duration_seconds=5400)
        
    finally:
        # Save final report
        output_file = Path(__file__).parent.parent.parent / "logs" / "monitoring_report.json"
        monitor.save_final_report(output_file)
        
        # Print final summary
        monitor._print_summary()


if __name__ == "__main__":
    asyncio.run(main())

