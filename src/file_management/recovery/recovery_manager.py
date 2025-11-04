"""
Error Recovery Manager for File Management System

Provides robust error handling and recovery mechanisms including:
- Circuit breaker pattern for storage service failures
- Automatic retry mechanisms with exponential backoff
- File operation rollback capabilities
- Error categorization and appropriate recovery strategies
- Integration with Supabase for error tracking and alerts
- Recovery workflow automation and monitoring
- Fallback mechanisms when Moonshot storage is unavailable
"""

import asyncio
import time
import logging
import json
import hashlib
import traceback
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import aiofiles
import aiohttp
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error types for categorization and appropriate handling"""
    NETWORK_ERROR = "network_error"
    STORAGE_ERROR = "storage_error"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    FILE_NOT_FOUND = "file_not_found"
    CORRUPTED_DATA = "corrupted_data"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    PERMISSION_ERROR = "permission_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class RecoveryStrategy(Enum):
    """Recovery strategies based on error type"""
    RETRY = "retry"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK_STORAGE = "fallback_storage"
    ROLLBACK = "rollback"
    SKIP_AND_LOG = "skip_and_log"
    ESCALATE = "escalate"
    COMPENSATE = "compensate"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    error_type: ErrorType
    operation: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    original_error: Optional[Exception] = None


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception_types: tuple = (Exception,)
    state_change_callback: Optional[Callable] = None


class CircuitBreaker:
    """Circuit breaker implementation for storage service failures"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def _get_time_since_last_failure(self) -> float:
        """Get time elapsed since last failure"""
        if self.last_failure_time is None:
            return float('inf')
        return time.time() - self.last_failure_time
        
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (self.state == CircuitBreakerState.OPEN and 
                self._get_time_since_last_failure() >= self.config.recovery_timeout)
                
    def _record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.last_failure_time = None
        if self.state != CircuitBreakerState.CLOSED:
            self.state = CircuitBreakerState.CLOSED
            if self.config.state_change_callback:
                self.config.state_change_callback(self.state)
                
    def _record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker reopened after half-open failure")
            
        if self.state == CircuitBreakerState.OPEN and self.config.state_change_callback:
            self.config.state_change_callback(self.state)
            
    @asynccontextmanager
    async def execute(self, operation: Callable, *args, **kwargs):
        """Execute operation with circuit breaker protection"""
        
        # Check if we should attempt reset
        if self._should_attempt_reset():
            self.state = CircuitBreakerState.HALF_OPEN
            logger.info("Circuit breaker entering half-open state")
            
        if self.state == CircuitBreakerState.OPEN:
            raise Exception("Circuit breaker is OPEN - operation blocked")
            
        try:
            result = await operation(*args, **kwargs) if asyncio.iscoroutinefunction(operation) else operation(*args, **kwargs)
            self._record_success()
            yield result
        except self.config.expected_exception_types as e:
            self._record_failure()
            raise


class RetryConfig:
    """Configuration for retry mechanisms"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_factor: float = 2.0,
                 jitter: bool = True,
                 retryable_exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
        
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for attempt number with exponential backoff"""
        delay = min(self.base_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            import random
            delay = delay * (0.5 + random.random() * 0.5)
            
        return delay


class FileOperationRollback:
    """Manages rollback capabilities for file operations"""
    
    def __init__(self, rollback_dir: str = "/tmp/file_rollbacks"):
        self.rollback_dir = Path(rollback_dir)
        self.rollback_dir.mkdir(exist_ok=True)
        self.operation_log: List[Dict] = []
        
    async def create_backup(self, file_path: str) -> str:
        """Create backup of file for potential rollback"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return ""
                
            backup_filename = f"{source_path.name}_{int(time.time())}_backup"
            backup_path = self.rollback_dir / backup_filename
            
            async with aiofiles.open(source_path, 'rb') as src:
                async with aiofiles.open(backup_path, 'wb') as dst:
                    content = await src.read()
                    await dst.write(content)
                    
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return ""
            
    async def restore_from_backup(self, backup_path: str, original_path: str) -> bool:
        """Restore file from backup"""
        try:
            backup = Path(backup_path)
            original = Path(original_path)
            
            if not backup.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
                
            async with aiofiles.open(backup, 'rb') as src:
                async with aiofiles.open(original, 'wb') as dst:
                    content = await src.read()
                    await dst.write(content)
                    
            # Clean up backup after restore
            backup.unlink(missing_ok=True)
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup {backup_path}: {e}")
            return False
            
    def log_operation(self, operation: str, file_path: str, backup_path: str = "", metadata: Dict = None):
        """Log operation for rollback tracking"""
        operation_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": file_path,
            "backup_path": backup_path,
            "metadata": metadata or {},
            "id": hashlib.md5(f"{operation}_{file_path}_{time.time()}".encode()).hexdigest()[:8]
        }
        self.operation_log.append(operation_entry)
        
    async def rollback_operation(self, operation_id: str) -> bool:
        """Rollback specific operation by ID"""
        for entry in reversed(self.operation_log):
            if entry["id"] == operation_id and entry["backup_path"]:
                success = await self.restore_from_backup(entry["backup_path"], entry["file_path"])
                if success:
                    logger.info(f"Successfully rolled back operation {operation_id}")
                    self.operation_log.remove(entry)
                    return True
        return False
        
    async def cleanup_old_backups(self, max_age_hours: int = 24):
        """Clean up old backup files"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for backup_file in self.rollback_dir.glob("*_backup"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink(missing_ok=True)
                logger.info(f"Cleaned up old backup: {backup_file}")


class SupabaseErrorTracker:
    """Integration with Supabase for error tracking and alerts"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def track_error(self, error_context: ErrorContext, recovery_attempted: bool = False, recovery_successful: bool = False):
        """Track error in Supabase database"""
        try:
            error_record = {
                "error_type": error_context.error_type.value,
                "operation": error_context.operation,
                "file_path": error_context.file_path,
                "error_message": str(error_context.original_error) if error_context.original_error else "",
                "retry_count": error_context.retry_count,
                "timestamp": error_context.timestamp.isoformat(),
                "recovery_attempted": recovery_attempted,
                "recovery_successful": recovery_successful,
                "metadata": json.dumps(error_context.metadata)
            }
            
            async with self.session.post(
                f"{self.supabase_url}/rest/v1/error_logs",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                json=error_record
            ) as response:
                if response.status == 201:
                    logger.info("Error tracked in Supabase")
                else:
                    logger.warning(f"Failed to track error in Supabase: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to track error in Supabase: {e}")
            
    async def get_error_statistics(self, hours: int = 24) -> Dict:
        """Get error statistics from Supabase"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            async with self.session.get(
                f"{self.supabase_url}/rest/v1/error_logs?timestamp=gte.{cutoff_time}&select=*",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Calculate statistics
                    stats = {
                        "total_errors": len(data),
                        "errors_by_type": {},
                        "recovery_rate": 0.0,
                        "most_common_errors": []
                    }
                    
                    if data:
                        # Group by error type
                        for record in data:
                            error_type = record["error_type"]
                            stats["errors_by_type"][error_type] = stats["errors_by_type"].get(error_type, 0) + 1
                            
                        # Calculate recovery rate
                        successful_recoveries = sum(1 for r in data if r.get("recovery_successful", False))
                        stats["recovery_rate"] = successful_recoveries / len(data) * 100
                        
                        # Most common errors
                        sorted_errors = sorted(stats["errors_by_type"].items(), key=lambda x: x[1], reverse=True)
                        stats["most_common_errors"] = sorted_errors[:5]
                        
                    return stats
                    
        except Exception as e:
            logger.error(f"Failed to get error statistics: {e}")
            
        return {}


class RecoveryStrategyManager:
    """Manages recovery strategies based on error context"""
    
    def __init__(self):
        self.strategy_mapping = {
            ErrorType.NETWORK_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.FALLBACK_STORAGE],
            ErrorType.STORAGE_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.FALLBACK_STORAGE, RecoveryStrategy.ROLLBACK],
            ErrorType.AUTHENTICATION_ERROR: [RecoveryStrategy.ESCALATE, RecoveryStrategy.SKIP_AND_LOG],
            ErrorType.QUOTA_EXCEEDED: [RecoveryStrategy.ESCALATE, RecoveryStrategy.SKIP_AND_LOG],
            ErrorType.FILE_NOT_FOUND: [RecoveryStrategy.SKIP_AND_LOG],
            ErrorType.CORRUPTED_DATA: [RecoveryStrategy.ROLLBACK, RecoveryStrategy.SKIP_AND_LOG],
            ErrorType.TIMEOUT_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF],
            ErrorType.RATE_LIMIT_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF],
            ErrorType.PERMISSION_ERROR: [RecoveryStrategy.ESCALATE, RecoveryStrategy.SKIP_AND_LOG],
            ErrorType.SYSTEM_ERROR: [RecoveryStrategy.RETRY, RecoveryStrategy.ESCALATE],
            ErrorType.UNKNOWN_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.SKIP_AND_LOG]
        }
        
    def get_recovery_strategies(self, error_type: ErrorType) -> List[RecoveryStrategy]:
        """Get appropriate recovery strategies for error type"""
        return self.strategy_mapping.get(error_type, [RecoveryStrategy.SKIP_AND_LOG])
        
    def determine_error_type(self, error: Exception) -> ErrorType:
        """Determine error type from exception"""
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if any(keyword in error_message for keyword in ["network", "connection", "dns", "timeout"]):
            return ErrorType.NETWORK_ERROR
        elif any(keyword in error_message for keyword in ["storage", "disk", "quota", "space"]):
            return ErrorType.STORAGE_ERROR
        elif any(keyword in error_message for keyword in ["auth", "unauthorized", "forbidden", "token"]):
            return ErrorType.AUTHENTICATION_ERROR
        elif any(keyword in error_message for keyword in ["quota", "limit", "exceeded"]):
            return ErrorType.QUOTA_EXCEEDED
        elif any(keyword in error_message for keyword in ["not found", "404", "missing"]):
            return ErrorType.FILE_NOT_FOUND
        elif any(keyword in error_message for keyword in ["corrupt", "invalid", "checksum"]):
            return ErrorType.CORRUPTED_DATA
        elif any(keyword in error_message for keyword in ["timeout", "timed out"]):
            return ErrorType.TIMEOUT_ERROR
        elif any(keyword in error_message for keyword in ["rate limit", "too many requests", "429"]):
            return ErrorType.RATE_LIMIT_ERROR
        elif any(keyword in error_message for keyword in ["permission", "access denied", "403"]):
            return ErrorType.PERMISSION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR


class FallbackStorageManager:
    """Manages fallback storage mechanisms when Moonshot storage is unavailable"""
    
    def __init__(self):
        self.primary_storage = "moonshot"
        self.fallback_storages = [
            {"name": "local", "path": "/tmp/fallback_storage", "priority": 1},
            {"name": "memory", "type": "memory", "priority": 2}
        ]
        self.current_storage = self.primary_storage
        self.storage_health = {}
        
    async def check_storage_health(self, storage_name: str) -> bool:
        """Check health of storage service"""
        try:
            if storage_name == "local":
                path = Path("/tmp/fallback_storage")
                path.mkdir(exist_ok=True)
                test_file = path / "health_check.tmp"
                async with aiofiles.open(test_file, 'w') as f:
                    await f.write("health_check")
                test_file.unlink(missing_ok=True)
                return True
            elif storage_name == "memory":
                # Memory storage is always available
                return True
            else:
                return False
        except Exception:
            return False
            
    async def select_best_storage(self) -> str:
        """Select the best available storage option"""
        available_storages = []
        
        # Check primary storage
        if await self.check_storage_health(self.primary_storage):
            available_storages.append(self.primary_storage)
            
        # Check fallback storages
        for fallback in sorted(self.fallback_storages, key=lambda x: x["priority"]):
            if await self.check_storage_health(fallback["name"]):
                available_storages.append(fallback["name"])
                
        return available_storages[0] if available_storages else "memory"
        
    async def switch_storage(self, new_storage: str) -> bool:
        """Switch to a different storage backend"""
        if await self.check_storage_health(new_storage):
            self.current_storage = new_storage
            logger.info(f"Switched storage from {self.current_storage} to {new_storage}")
            return True
        return False
        
    async def store_file(self, data: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
        """Store file in current storage with fallback"""
        storage = await self.select_best_storage()
        
        try:
            if storage == "local":
                path = Path("/tmp/fallback_storage")
                path.mkdir(exist_ok=True)
                file_path = path / filename
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(data)
                return True, str(file_path), None
                
            elif storage == "memory":
                # In-memory storage (simple implementation)
                import tempfile
                temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{filename}")
                with os.fdopen(temp_fd, 'wb') as f:
                    f.write(data)
                return True, temp_path, None
                
        except Exception as e:
            return False, "", str(e)
            
        return False, "", "No suitable storage found"


class ErrorRecoveryManager:
    """Main error recovery manager orchestrating all recovery mechanisms"""
    
    def __init__(self, 
                 supabase_url: Optional[str] = None,
                 supabase_key: Optional[str] = None,
                 rollback_dir: str = "/tmp/file_rollbacks"):
        
        # Initialize components
        self.circuit_breaker_config = CircuitBreakerConfig()
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        self.retry_config = RetryConfig()
        self.rollback_manager = FileOperationRollback(rollback_dir)
        self.recovery_strategy_manager = RecoveryStrategyManager()
        self.fallback_storage = FallbackStorageManager()
        
        # Supabase integration
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.error_tracker = None
        
        # Monitoring and metrics
        self.metrics = {
            "total_errors": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "circuit_breaker_trips": 0,
            "retry_attempts": 0
        }
        
        # Recovery workflows
        self.active_workflows: Dict[str, Dict] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self.supabase_url and self.supabase_key:
            self.error_tracker = SupabaseErrorTracker(self.supabase_url, self.supabase_key)
            await self.error_tracker.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.error_tracker:
            await self.error_tracker.__aexit__(exc_type, exc_val, exc_tb)
            
    def categorize_error(self, error: Exception) -> ErrorType:
        """Categorize error and determine recovery strategies"""
        return self.recovery_strategy_manager.determine_error_type(error)
        
    async def retry_operation(self, 
                            operation: Callable,
                            error_context: ErrorContext,
                            *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute operation with retry logic"""
        
        last_error = None
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                # Execute operation with circuit breaker protection
                async with self.circuit_breaker.execute(operation, *args, **kwargs):
                    if asyncio.iscoroutinefunction(operation):
                        result = await operation(*args, **kwargs)
                    else:
                        result = operation(*args, **kwargs)
                        
                self.metrics["retry_attempts"] += attempt
                logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return True, result, None
                
            except Exception as e:
                last_error = e
                error_context.retry_count = attempt + 1
                error_context.original_error = e
                
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                # Track error
                await self._track_error(error_context)
                
                # Calculate delay before next retry
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self.retry_config.calculate_delay(attempt + 1)
                    await asyncio.sleep(delay)
                    
        # All retries exhausted
        self.metrics["failed_recoveries"] += 1
        return False, None, str(last_error)
        
    async def _track_error(self, error_context: ErrorContext):
        """Track error in metrics and optionally Supabase"""
        self.metrics["total_errors"] += 1
        
        if self.error_tracker:
            await self.error_tracker.track_error(error_context)
            
    async def execute_with_recovery(self, 
                                  operation: Callable,
                                  operation_name: str,
                                  file_path: Optional[str] = None,
                                  create_backup: bool = True,
                                  *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute operation with full recovery mechanisms"""
        
        backup_path = ""
        
        try:
            # Create backup if needed
            if create_backup and file_path:
                backup_path = await self.rollback_manager.create_backup(file_path)
                self.rollback_manager.log_operation(operation_name, file_path, backup_path)
                
            # Execute operation with retry logic
            error_context = ErrorContext(
                error_type=ErrorType.UNKNOWN_ERROR,
                operation=operation_name,
                file_path=file_path
            )
            
            success, result, error = await self.retry_operation(operation, error_context, *args, **kwargs)
            
            if success:
                self.metrics["successful_recoveries"] += 1
                
                # Track successful recovery
                if self.error_tracker:
                    await self.error_tracker.track_error(error_context, recovery_attempted=True, recovery_successful=True)
                    
                return True, result, None
            else:
                # Attempt rollback if backup exists
                if backup_path:
                    rollback_success = await self.rollback_manager.restore_from_backup(backup_path, file_path)
                    if rollback_success:
                        logger.info(f"Successfully rolled back operation {operation_name}")
                        
                return False, None, error
                
        except Exception as e:
            self.metrics["failed_recoveries"] += 1
            logger.error(f"Recovery operation failed: {e}")
            
            # Attempt final rollback
            if backup_path and file_path:
                await self.rollback_manager.restore_from_backup(backup_path, file_path)
                
            return False, None, str(e)
            
    async def execute_with_fallback(self, 
                                  operation: Callable,
                                  *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute operation with fallback storage if primary fails"""
        
        try:
            # Try primary storage first
            success, result, error = await self.execute_with_recovery(operation, "primary_storage", *args, **kwargs)
            
            if success:
                return True, result, None
                
            # Primary failed, try fallback storage
            logger.info("Primary storage failed, attempting fallback")
            
            # Switch to fallback storage
            fallback_storage = await self.fallback_storage.select_best_storage()
            await self.fallback_storage.switch_storage(fallback_storage)
            
            # Retry with fallback
            return await self.execute_with_recovery(operation, "fallback_storage", *args, **kwargs)
            
        except Exception as e:
            return False, None, str(e)
            
    async def get_recovery_metrics(self) -> Dict:
        """Get recovery system metrics"""
        metrics = self.metrics.copy()
        metrics["circuit_breaker_state"] = self.circuit_breaker.state.value
        metrics["current_storage"] = self.fallback_storage.current_storage
        
        # Add error statistics if available
        if self.error_tracker:
            try:
                stats = await self.error_tracker.get_error_statistics()
                metrics["error_statistics"] = stats
            except Exception as e:
                logger.error(f"Failed to get error statistics: {e}")
                
        return metrics
        
    async def cleanup_recovery_resources(self):
        """Cleanup recovery resources"""
        await self.rollback_manager.cleanup_old_backups()
        
    async def create_recovery_workflow(self, 
                                     workflow_id: str,
                                     operations: List[Dict[str, Any]],
                                     rollback_on_failure: bool = True) -> str:
        """Create automated recovery workflow"""
        
        workflow = {
            "id": workflow_id,
            "operations": operations,
            "status": "pending",
            "start_time": datetime.now(),
            "completed_operations": [],
            "failed_operations": [],
            "rollback_on_failure": rollback_on_failure
        }
        
        self.active_workflows[workflow_id] = workflow
        return workflow_id
        
    async def execute_recovery_workflow(self, workflow_id: str) -> Tuple[bool, List[str]]:
        """Execute recovery workflow"""
        
        if workflow_id not in self.active_workflows:
            return False, ["Workflow not found"]
            
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "running"
        
        executed_ops = []
        errors = []
        
        try:
            for i, operation in enumerate(workflow["operations"]):
                op_name = operation.get("name", f"operation_{i}")
                op_callable = operation.get("callable")
                op_args = operation.get("args", [])
                op_kwargs = operation.get("kwargs", {})
                
                try:
                    if op_callable:
                        success, result, error = await self.execute_with_recovery(
                            op_callable, op_name, *op_args, **op_kwargs
                        )
                        
                        if success:
                            executed_ops.append(op_name)
                            workflow["completed_operations"].append({
                                "name": op_name,
                                "timestamp": datetime.now(),
                                "result": result
                            })
                        else:
                            errors.append(f"{op_name}: {error}")
                            workflow["failed_operations"].append({
                                "name": op_name,
                                "timestamp": datetime.now(),
                                "error": error
                            })
                            
                            # Rollback if configured
                            if workflow["rollback_on_failure"]:
                                await self.rollback_operations(executed_ops)
                                break
                                
                except Exception as e:
                    error_msg = f"{op_name}: {str(e)}"
                    errors.append(error_msg)
                    workflow["failed_operations"].append({
                        "name": op_name,
                        "timestamp": datetime.now(),
                        "error": str(e)
                    })
                    
            workflow["status"] = "completed" if not errors else "failed"
            workflow["end_time"] = datetime.now()
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            errors.append(str(e))
            
        return len(errors) == 0, errors
        
    async def rollback_operations(self, operation_names: List[str]):
        """Rollback a list of operations"""
        for op_name in reversed(operation_names):
            # Find operation in rollback log and rollback
            for entry in reversed(self.rollback_manager.operation_log):
                if entry["operation"] == op_name and entry["backup_path"]:
                    success = await self.rollback_manager.restore_from_backup(
                        entry["backup_path"], entry["file_path"]
                    )
                    if success:
                        logger.info(f"Rolled back operation: {op_name}")
                        break


# Decorator for easy integration
def recovery_operation(manager: ErrorRecoveryManager):
    """Decorator for automatic error recovery"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            success, result, error = await manager.execute_with_recovery(
                func, func.__name__, *args, **kwargs
            )
            if success:
                return result
            else:
                raise Exception(f"Operation failed with recovery attempts: {error}")
        return wrapper
    return decorator


# Usage example
async def example_usage():
    """Example usage of the Error Recovery Manager"""
    
    # Initialize recovery manager
    async with ErrorRecoveryManager(
        supabase_url="https://your-project.supabase.co",
        supabase_key="your-supabase-key"
    ) as recovery_manager:
        
        # Example operation that might fail
        async def risky_file_operation(file_path: str, data: str):
            # Simulate a risky operation
            await asyncio.sleep(0.1)  # Simulate I/O
            if True:  # Random failure simulation
                raise Exception("Simulated storage failure")
            return "success"
            
        # Execute with full recovery
        success, result, error = await recovery_manager.execute_with_recovery(
            risky_file_operation,
            "example_operation",
            "/tmp/example.txt",
            "sample data"
        )
        
        if success:
            print(f"Operation succeeded: {result}")
        else:
            print(f"Operation failed: {error}")
            
        # Get metrics
        metrics = await recovery_manager.get_recovery_metrics()
        print(f"Recovery metrics: {metrics}")
        
        # Cleanup
        await recovery_manager.cleanup_recovery_resources()


if __name__ == "__main__":
    asyncio.run(example_usage())