"""
Log Volume Analyzer for Phase 2 Logging Optimization

Analyzes Docker logs to measure:
- Total log volume before/after Phase 2
- Log volume by level (DEBUG/INFO/WARNING/ERROR)
- Log volume by module
- Sampling effectiveness

Created: 2025-10-28
EXAI Consultation: 7e59bfd7-a9cc-4a19-9807-5ebd84082cab
"""

import subprocess
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class LogAnalysis:
    """Analysis results for log volume."""
    total_lines: int = 0
    by_level: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    by_module: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    sampled_logs: int = 0
    
    def add_log_line(self, level: str, module: str, is_sampled: bool = False):
        """Add a log line to the analysis."""
        self.total_lines += 1
        self.by_level[level] += 1
        self.by_module[module] += 1
        if is_sampled:
            self.sampled_logs += 1
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            "total_lines": self.total_lines,
            "by_level": dict(self.by_level),
            "by_module": dict(self.by_module),
            "sampled_logs": self.sampled_logs,
            "sampling_rate": self.sampled_logs / self.total_lines if self.total_lines > 0 else 0
        }


def get_docker_logs(container_name: str = "exai-mcp-daemon", tail: int = 1000) -> List[str]:
    """
    Get Docker logs for analysis.

    Args:
        container_name: Docker container name
        tail: Number of lines to retrieve

    Returns:
        List of log lines
    """
    try:
        result = subprocess.run(
            ["docker", "logs", container_name, "--tail", str(tail)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid characters
            check=True
        )
        if result.stdout:
            return result.stdout.split('\n')
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error getting Docker logs: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def parse_log_line(line: str) -> Tuple[str, str, bool]:
    """
    Parse a log line to extract level, module, and sampling status.
    
    Args:
        line: Log line to parse
    
    Returns:
        Tuple of (level, module, is_sampled)
    """
    # Pattern: 2025-10-28 21:25:29 INFO src.daemon.warmup: [WARMUP] Starting...
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (\w+) ([\w\.]+): (.+)$'
    match = re.match(pattern, line)
    
    if not match:
        return ("UNKNOWN", "UNKNOWN", False)
    
    level = match.group(1)
    module = match.group(2)
    message = match.group(3)
    
    # Check if sampled
    is_sampled = "[SAMPLED]" in message
    
    return (level, module, is_sampled)


def analyze_logs(lines: List[str]) -> LogAnalysis:
    """
    Analyze log lines.
    
    Args:
        lines: List of log lines
    
    Returns:
        LogAnalysis with results
    """
    analysis = LogAnalysis()
    
    for line in lines:
        if not line.strip():
            continue
        
        level, module, is_sampled = parse_log_line(line)
        
        if level != "UNKNOWN":
            analysis.add_log_line(level, module, is_sampled)
    
    return analysis


def print_analysis(analysis: LogAnalysis, title: str = "Log Analysis"):
    """Print analysis results."""
    summary = analysis.get_summary()
    
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Total log lines: {summary['total_lines']}")
    print(f"Sampled logs: {summary['sampled_logs']} ({summary['sampling_rate']*100:.1f}%)")
    
    print(f"\nBy Level:")
    for level, count in sorted(summary['by_level'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / summary['total_lines'] * 100) if summary['total_lines'] > 0 else 0
        print(f"  {level:<10} {count:>6} ({percentage:>5.1f}%)")
    
    print(f"\nTop 10 Modules by Volume:")
    sorted_modules = sorted(summary['by_module'].items(), key=lambda x: x[1], reverse=True)[:10]
    for module, count in sorted_modules:
        percentage = (count / summary['total_lines'] * 100) if summary['total_lines'] > 0 else 0
        print(f"  {module:<40} {count:>6} ({percentage:>5.1f}%)")
    
    print(f"{'='*60}\n")


def compare_analyses(before: LogAnalysis, after: LogAnalysis):
    """Compare two log analyses."""
    before_summary = before.get_summary()
    after_summary = after.get_summary()
    
    print(f"\n{'='*60}")
    print(f"Before/After Comparison")
    print(f"{'='*60}")
    
    # Total volume
    total_reduction = (before_summary['total_lines'] - after_summary['total_lines']) / before_summary['total_lines'] * 100 if before_summary['total_lines'] > 0 else 0
    print(f"Total Lines:")
    print(f"  Before: {before_summary['total_lines']}")
    print(f"  After:  {after_summary['total_lines']}")
    print(f"  Reduction: {total_reduction:.1f}%")
    
    # By level
    print(f"\nBy Level:")
    all_levels = set(before_summary['by_level'].keys()) | set(after_summary['by_level'].keys())
    for level in sorted(all_levels):
        before_count = before_summary['by_level'].get(level, 0)
        after_count = after_summary['by_level'].get(level, 0)
        reduction = (before_count - after_count) / before_count * 100 if before_count > 0 else 0
        print(f"  {level:<10} Before: {before_count:>6}  After: {after_count:>6}  Reduction: {reduction:>5.1f}%")
    
    # Sampling effectiveness
    print(f"\nSampling:")
    print(f"  Sampled logs: {after_summary['sampled_logs']}")
    print(f"  Sampling rate: {after_summary['sampling_rate']*100:.1f}%")
    
    print(f"{'='*60}\n")
    
    # Assessment
    if total_reduction >= 80:
        print("✅ EXCELLENT: Log volume reduced by >80%")
    elif total_reduction >= 60:
        print("✅ GOOD: Log volume reduced by >60%")
    elif total_reduction >= 40:
        print("⚠️  ACCEPTABLE: Log volume reduced by >40%")
    else:
        print("❌ POOR: Log volume reduction <40%")


def main():
    """Main entry point."""
    print(f"\n{'#'*60}")
    print(f"# Log Volume Analysis - Phase 2 Logging Optimization")
    print(f"{'#'*60}\n")
    
    # Get current logs
    print("Fetching Docker logs (last 1000 lines)...")
    lines = get_docker_logs(tail=1000)
    
    if not lines:
        print("❌ Failed to retrieve Docker logs")
        return
    
    # Analyze
    analysis = analyze_logs(lines)
    print_analysis(analysis, "Current Log Volume")
    
    # Check for sampling
    summary = analysis.get_summary()
    if summary['sampled_logs'] > 0:
        print(f"✅ Sampling is active ({summary['sampled_logs']} sampled logs found)")
        print(f"   Effective sampling rate: {summary['sampling_rate']*100:.1f}%")
    else:
        print(f"⚠️  No sampled logs found - sampling may not be active")
    
    # Module-specific analysis
    print(f"\n{'='*60}")
    print(f"Module-Specific Analysis")
    print(f"{'='*60}")
    
    resilient_ws_logs = summary['by_module'].get('src.monitoring.resilient_websocket', 0)
    connection_mgr_logs = summary['by_module'].get('src.daemon.ws.connection_manager', 0)
    
    print(f"resilient_websocket: {resilient_ws_logs} logs")
    print(f"connection_manager: {connection_mgr_logs} logs")
    
    if resilient_ws_logs > 0:
        print(f"\n✅ resilient_websocket is generating logs")
    else:
        print(f"\n⚠️  No logs from resilient_websocket (may not be active)")
    
    print(f"{'='*60}\n")
    
    # Save results
    output_file = "log_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()

