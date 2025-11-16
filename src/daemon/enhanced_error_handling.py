"""
Enhanced Error Handling System for EXAI MCP Server

Provides:
- Error categorization (retryable vs non-retryable)
- Structured logging with correlation IDs
- Performance metrics tracking
- Error alerting for critical failures
- Error dashboard data

This builds on the existing error_handling.py module.
"""

import logging
import time
import uuid
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for better handling and monitoring."""
    CLIENT_ERROR = "client_error"  # Invalid requests, bad parameters
    SERVER_ERROR = "server_error"  # Internal server issues
    TOOL_ERROR = "tool_error"  # Tool execution failures
    PROVIDER_ERROR = "provider_error"  # External API failures
    NETWORK_ERROR = "network_error"  # Connection issues
    VALIDATION_ERROR = "validation_error"  # Input validation failures
    AUTHENTICATION_ERROR = "auth_error"  # Authentication/authorization
    TIMEOUT_ERROR = "timeout_error"  # Request timeouts
    RATE_LIMIT_ERROR = "rate_limit_error"  # Rate limiting
    UNKNOWN_ERROR = "unknown_error"  # Unclassified errors


class ErrorSeverity(Enum):
    """Error severity levels for alerting."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorMetrics:
    """Error tracking metrics."""
    error_code: str
    category: ErrorCategory
    severity: ErrorSeverity
    request_id: Optional[str]
    tool_name: Optional[str]
    provider_name: Optional[str]
    timestamp: datetime
    response_time_ms: Optional[float]
    retryable: bool
    context: Dict[str, Any]


class EnhancedErrorHandler:
    """Enhanced error handling with categorization and metrics."""
    
    def __init__(self, max_metrics_history: int = 1000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.critical_errors: List[ErrorMetrics] = []
        self.metrics_lock = threading.Lock()
        
        # Alerting thresholds
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,  # Alert on first critical error
            ErrorSeverity.HIGH: 5,  # Alert after 5 high severity errors
            ErrorSeverity.MEDIUM: 10,  # Alert after 10 medium severity errors
        }
    
    def categorize_error(self, error_code: str, exception: Optional[Exception] = None) -> ErrorCategory:
        """Categorize error based on code and exception."""
        
        # Tool execution errors
        if error_code in ["TOOL_EXECUTION_ERROR", "TOOL_NOT_FOUND"]:
            return ErrorCategory.TOOL_ERROR
        
        # Provider/API errors
        if error_code in ["PROVIDER_ERROR", "SERVICE_UNAVAILABLE"]:
            return ErrorCategory.PROVIDER_ERROR
        
        # Client errors
        if error_code in ["INVALID_REQUEST", "UNAUTHORIZED", "VALIDATION_ERROR", "NOT_FOUND"]:
            return ErrorCategory.CLIENT_ERROR
        
        # Timeout errors
        if error_code == "TIMEOUT":
            return ErrorCategory.TIMEOUT_ERROR
        
        # Server internal errors
        if error_code == "INTERNAL_ERROR":
            return ErrorCategory.SERVER_ERROR
        
        # Default to unknown
        return ErrorCategory.UNKNOWN_ERROR
    
    def determine_severity(self, category: ErrorCategory, error_code: str, context: Dict[str, Any]) -> ErrorSeverity:
        """Determine error severity based on category and context."""
        
        # Critical severity
        if category == ErrorCategory.SERVER_ERROR and "database" in str(context).lower():
            return ErrorSeverity.CRITICAL
        
        if category == ErrorCategory.PROVIDER_ERROR and "authentication" in str(context).lower():
            return ErrorSeverity.HIGH
        
        if category == ErrorCategory.TIMEOUT_ERROR:
            return ErrorSeverity.MEDIUM
        
        if category == ErrorCategory.CLIENT_ERROR:
            return ErrorSeverity.LOW
        
        # Tool errors are typically medium severity
        if category == ErrorCategory.TOOL_ERROR:
            return ErrorSeverity.MEDIUM
        
        # Default severity
        return ErrorSeverity.MEDIUM
    
    def is_retryable_error(self, category: ErrorCategory, error_code: str, exception: Optional[Exception] = None) -> bool:
        """Determine if an error is retryable."""
        
        # Non-retryable errors
        non_retryable = {
            ErrorCategory.CLIENT_ERROR,
            ErrorCategory.AUTHENTICATION_ERROR,
            ErrorCategory.VALIDATION_ERROR,
        }
        
        if category in non_retryable:
            return False
        
        # Retryable errors
        retryable = {
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.RATE_LIMIT_ERROR,
            ErrorCategory.PROVIDER_ERROR,  # Some provider errors are retryable
            ErrorCategory.SERVER_ERROR,  # Some server errors are retryable
        }
        
        if category in retryable:
            return True
        
        # Tool errors - depends on the specific error
        if category == ErrorCategory.TOOL_ERROR:
            # Tool not found is not retryable, but tool execution timeout might be
            if "not found" in str(exception).lower() if exception else False:
                return False
            return True
        
        # Default: not retryable
        return False
    
    def log_enhanced_error(
        self,
        error_code: str,
        message: str,
        request_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        provider_name: Optional[str] = None,
        exception: Optional[Exception] = None,
        response_time_ms: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> ErrorMetrics:
        """Log enhanced error with full categorization and metrics."""
        
        # Categorize and analyze error
        category = self.categorize_error(error_code, exception)
        context = context or {}
        severity = self.determine_severity(category, error_code, context)
        retryable = self.is_retryable_error(category, error_code, exception)
        
        # Create metrics
        metrics = ErrorMetrics(
            error_code=error_code,
            category=category,
            severity=severity,
            request_id=request_id,
            tool_name=tool_name,
            provider_name=provider_name,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=response_time_ms,
            retryable=retryable,
            context=context
        )
        
        # Store metrics
        with self.metrics_lock:
            self.metrics_history.append(metrics)
            self.error_counts[error_code] += 1
            
            # Store critical errors for alerting
            if severity == ErrorSeverity.CRITICAL:
                self.critical_errors.append(metrics)
        
        # Create enhanced log message
        log_parts = [
            f"[{error_code}]",
            f"[{category.value}]",
            f"[{severity.value}]",
        ]
        
        if request_id:
            log_parts.append(f"[req:{request_id}]")
        if tool_name:
            log_parts.append(f"[tool:{tool_name}]")
        if provider_name:
            log_parts.append(f"[prov:{provider_name}]")
        if response_time_ms:
            log_parts.append(f"[{response_time_ms:.1f}ms]")
        
        log_parts.append(message)
        
        if retryable:
            log_parts.append("[RETRYABLE]")
        
        log_message = " ".join(log_parts)
        
        # Log with appropriate level
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=exc_info)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=exc_info)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, exc_info=exc_info)
        else:
            logger.info(log_message, exc_info=exc_info)
        
        # Check for alerting
        self._check_alerting(metrics)
        
        return metrics
    
    def _check_alerting(self, metrics: ErrorMetrics) -> None:
        """Check if error triggers alerting."""
        threshold = self.alert_thresholds.get(metrics.severity, float('inf'))
        category_count = sum(1 for m in self.metrics_history if m.category == metrics.category)
        
        if category_count >= threshold:
            self._trigger_alert(metrics, category_count)
    
    def _trigger_alert(self, metrics: ErrorMetrics, count: int) -> None:
        """Trigger alert for high error rates."""
        alert_message = (
            f"ERROR ALERT: {metrics.severity.value.upper()} "
            f"{metrics.category.value} errors detected "
            f"(count: {count}, latest: {metrics.error_code})"
        )
        
        if metrics.request_id:
            alert_message += f" [req:{metrics.request_id}]"
        
        logger.critical(alert_message)
        
        # Here you could integrate with external alerting systems
        # (Slack, PagerDuty, email, etc.)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring dashboard."""
        with self.metrics_lock:
            recent_errors = list(self.metrics_history)[-100:]  # Last 100 errors
            
            summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_errors": len(self.metrics_history),
                "error_counts_by_code": dict(self.error_counts),
                "errors_by_category": {},
                "errors_by_severity": {},
                "recent_critical_errors": len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
                "retryable_errors": len([e for e in recent_errors if e.retryable]),
                "avg_response_time_ms": 0,
            }
            
            # Calculate category distribution
            for category in ErrorCategory:
                count = len([e for e in recent_errors if e.category == category])
                if count > 0:
                    summary["errors_by_category"][category.value] = count
            
            # Calculate severity distribution
            for severity in ErrorSeverity:
                count = len([e for e in recent_errors if e.severity == severity])
                if count > 0:
                    summary["errors_by_severity"][severity.value] = count
            
            # Calculate average response time
            response_times = [e.response_time_ms for e in recent_errors if e.response_time_ms is not None]
            if response_times:
                summary["avg_response_time_ms"] = sum(response_times) / len(response_times)
            
            return summary


# Global enhanced error handler instance
_enhanced_handler: Optional[EnhancedErrorHandler] = None


def get_enhanced_handler() -> EnhancedErrorHandler:
    """Get the global enhanced error handler instance."""
    global _enhanced_handler
    if _enhanced_handler is None:
        _enhanced_handler = EnhancedErrorHandler()
    return _enhanced_handler


# Enhanced error logging function
def log_enhanced_error(
    error_code: str,
    message: str,
    request_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    provider_name: Optional[str] = None,
    exception: Optional[Exception] = None,
    response_time_ms: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None,
    exc_info: bool = False
) -> ErrorMetrics:
    """Enhanced error logging with categorization and metrics."""
    handler = get_enhanced_handler()
    return handler.log_enhanced_error(
        error_code=error_code,
        message=message,
        request_id=request_id,
        tool_name=tool_name,
        provider_name=provider_name,
        exception=exception,
        response_time_ms=response_time_ms,
        context=context,
        exc_info=exc_info
    )


# Backward compatibility function
def log_error_enhanced(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    exc_info: bool = False
) -> ErrorMetrics:
    """Enhanced version of existing log_error function."""
    return log_enhanced_error(
        error_code=code,
        message=message,
        request_id=request_id,
        exc_info=exc_info
    )