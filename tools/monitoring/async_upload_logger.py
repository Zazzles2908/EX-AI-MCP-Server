"""
Async Upload Structured Logger

Logs rollout metrics to structured files for analysis and monitoring.
Supports JSON and CSV formats for easy integration with dashboards.
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AsyncUploadLogger:
    """Structured logger for async upload rollout metrics"""
    
    def __init__(self, log_dir: str = "logs/async_upload_rollout"):
        """
        Initialize logger
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.json_log_file = self.log_dir / "metrics.jsonl"
        self.csv_log_file = self.log_dir / "metrics.csv"
        self.summary_file = self.log_dir / "summary.json"
        
        # Initialize CSV header if file doesn't exist
        if not self.csv_log_file.exists():
            self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file with headers"""
        headers = [
            "timestamp",
            "execution_type",
            "success",
            "duration_ms",
            "file_size_mb",
            "provider",
            "error_type",
            "fallback_used"
        ]
        
        try:
            with open(self.csv_log_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
        except Exception as e:
            logger.error(f"Failed to initialize CSV: {e}")
    
    def log_metric(self, metric: Dict[str, Any]):
        """
        Log a single metric entry
        
        Args:
            metric: Metric dictionary
        """
        # Add timestamp if not present
        if "timestamp" not in metric:
            metric["timestamp"] = datetime.utcnow().isoformat()
        
        # Log to JSONL
        self._log_jsonl(metric)
        
        # Log to CSV
        self._log_csv(metric)
    
    def _log_jsonl(self, metric: Dict[str, Any]):
        """Log to JSONL file"""
        try:
            with open(self.json_log_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            logger.error(f"Failed to write JSONL: {e}")
    
    def _log_csv(self, metric: Dict[str, Any]):
        """Log to CSV file"""
        try:
            with open(self.csv_log_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=metric.keys())
                writer.writerow(metric)
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")
    
    def log_rollout_stage(self, stage: int, percentage: int, metrics_summary: Dict[str, Any]):
        """
        Log rollout stage transition
        
        Args:
            stage: Rollout stage number (1, 2, 3, 4)
            percentage: Traffic percentage for this stage
            metrics_summary: Summary metrics for the stage
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rollout_stage",
            "stage": stage,
            "percentage": percentage,
            "metrics": metrics_summary
        }
        
        logger.info(f"Rollout Stage {stage}: {percentage}% - {metrics_summary}")
        self._log_jsonl(entry)
    
    def log_rollback(self, reason: str, metrics_summary: Dict[str, Any]):
        """
        Log rollback event
        
        Args:
            reason: Reason for rollback
            metrics_summary: Metrics at time of rollback
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rollback",
            "reason": reason,
            "metrics": metrics_summary
        }
        
        logger.warning(f"Rollback triggered: {reason}")
        self._log_jsonl(entry)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all logged metrics
        
        Returns:
            Summary statistics
        """
        try:
            metrics = []
            with open(self.json_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
            
            if not metrics:
                return {"total_entries": 0}
            
            # Filter out non-metric entries
            metric_entries = [m for m in metrics if m.get("event_type") != "rollout_stage" and m.get("event_type") != "rollback"]
            
            if not metric_entries:
                return {"total_entries": 0}
            
            # Calculate statistics
            successful = sum(1 for m in metric_entries if m.get("success"))
            failed = len(metric_entries) - successful
            
            by_type = {}
            for metric in metric_entries:
                exec_type = metric.get("execution_type", "unknown")
                if exec_type not in by_type:
                    by_type[exec_type] = {"count": 0, "successful": 0}
                
                by_type[exec_type]["count"] += 1
                if metric.get("success"):
                    by_type[exec_type]["successful"] += 1
            
            return {
                "total_entries": len(metric_entries),
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / len(metric_entries) * 100) if metric_entries else 0,
                "by_execution_type": by_type
            }
        
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}
    
    def save_summary(self):
        """Save current summary to file"""
        try:
            summary = self.get_metrics_summary()
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Summary saved to {self.summary_file}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")


# Global logger instance
_logger: Optional[AsyncUploadLogger] = None


def get_async_upload_logger(log_dir: str = "logs/async_upload_rollout") -> AsyncUploadLogger:
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = AsyncUploadLogger(log_dir=log_dir)
    return _logger


def reset_logger():
    """Reset global logger (useful for testing)"""
    global _logger
    _logger = None

