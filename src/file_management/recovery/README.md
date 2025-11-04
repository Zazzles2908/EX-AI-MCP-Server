# Error Recovery Manager

A comprehensive error recovery system for file management operations with robust error handling, automatic recovery mechanisms, and integration capabilities.

## Features

### 🛡️ Circuit Breaker Pattern
- Prevents cascading failures by blocking requests to failing services
- Configurable failure thresholds and recovery timeouts
- Automatic state transitions between CLOSED, OPEN, and HALF_OPEN states

### 🔄 Automatic Retry Mechanisms
- Exponential backoff with configurable delay factors
- Jitter to prevent thundering herd problems
- Customizable retry limits and exception filtering

### 📁 File Operation Rollback
- Automatic backup creation before risky operations
- Restore capabilities from backup files
- Operation logging for audit trails
- Cleanup of old backup files

### 🎯 Error Categorization
- Intelligent error type detection and classification
- Appropriate recovery strategies for different error types
- Contextual error information tracking

### 📊 Supabase Integration
- Error tracking and logging to Supabase database
- Error statistics and metrics collection
- Recovery success rate monitoring
- Alert capabilities for critical failures

### 🔧 Recovery Workflow Automation
- Multi-step workflow execution with rollback capabilities
- Parallel and sequential operation support
- Workflow state management and monitoring
- Automated error recovery sequences

### 🔀 Fallback Mechanisms
- Multiple storage backend support
- Automatic fallback when primary storage fails
- Health checking for storage services
- Load balancing between storage options

## Architecture

### Core Components

1. **ErrorRecoveryManager**: Main orchestrator class
2. **CircuitBreaker**: Service failure protection
3. **RetryConfig**: Retry mechanism configuration
4. **FileOperationRollback**: File backup and restore
5. **SupabaseErrorTracker**: Error logging and monitoring
6. **RecoveryStrategyManager**: Strategy selection logic
7. **FallbackStorageManager**: Multi-storage management

### Error Types Supported

- `NETWORK_ERROR`: Connection and timeout issues
- `STORAGE_ERROR`: Disk and storage problems
- `AUTHENTICATION_ERROR`: Auth and permission failures
- `QUOTA_EXCEEDED`: Storage quota limitations
- `FILE_NOT_FOUND`: Missing file errors
- `CORRUPTED_DATA`: Data integrity issues
- `TIMEOUT_ERROR`: Operation timeouts
- `RATE_LIMIT_ERROR`: API rate limiting
- `PERMISSION_ERROR`: Access control issues
- `SYSTEM_ERROR`: System-level failures

## Usage Examples

### Basic Usage

```python
from src.file_management.recovery import ErrorRecoveryManager

async with ErrorRecoveryManager() as recovery_manager:
    # Execute operation with full recovery
    success, result, error = await recovery_manager.execute_with_recovery(
        risky_operation,
        "operation_name",
        file_path,
        create_backup=True
    )
    
    if success:
        print(f"Operation succeeded: {result}")
    else:
        print(f"Operation failed: {error}")
```

### Circuit Breaker Protection

```python
from src.file_management.recovery import CircuitBreakerConfig, CircuitBreaker

config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0
)

circuit_breaker = CircuitBreaker(config)

async with circuit_breaker.execute(unreliable_service):
    response = await unreliable_service()
```

### Fallback Storage

```python
# Automatic fallback when primary storage fails
success, result, error = await recovery_manager.execute_with_fallback(
    storage_operation
)

current_storage = recovery_manager.fallback_storage.current_storage
print(f"Storage used: {current_storage}")
```

### Workflow Automation

```python
operations = [
    {"name": "prepare", "callable": prepare_data},
    {"name": "process", "callable": process_data},
    {"name": "save", "callable": save_results}
]

workflow_id = await recovery_manager.create_recovery_workflow(
    "data_workflow", operations, rollback_on_failure=True
)

success, errors = await recovery_manager.execute_recovery_workflow(workflow_id)
```

### Decorator Usage

```python
@recovery_operation(recovery_manager)
async def decorated_function(data: str):
    # This function will automatically get error recovery
    return process_data(data)

result = await decorated_function("test data")
```

## Configuration

### Retry Configuration

```python
retry_config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError)
)
```

### Circuit Breaker Configuration

```python
circuit_config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    expected_exception_types=(ServiceError, ConnectionError),
    state_change_callback=handle_state_change
)
```

## Metrics and Monitoring

Get comprehensive recovery metrics:

```python
metrics = await recovery_manager.get_recovery_metrics()
print(f"Total errors: {metrics['total_errors']}")
print(f"Recovery rate: {metrics['successful_recoveries']}")
print(f"Circuit breaker state: {metrics['circuit_breaker_state']}")
```

## Supabase Integration

Configure error tracking:

```python
async with ErrorRecoveryManager(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-supabase-key"
) as recovery_manager:
    # Errors will be automatically tracked
    pass
```

## Error Recovery Strategies

| Error Type | Primary Strategy | Fallback Strategy |
|------------|------------------|-------------------|
| Network Error | Retry with Backoff | Fallback Storage |
| Storage Error | Retry with Backoff | Rollback + Fallback |
| Auth Error | Escalate | Skip and Log |
| Quota Exceeded | Escalate | Skip and Log |
| File Not Found | Skip and Log | - |
| Corrupted Data | Rollback | Skip and Log |
| Timeout Error | Retry with Backoff | - |
| Rate Limit Error | Retry with Backoff | - |
| Permission Error | Escalate | Skip and Log |
| System Error | Retry | Escalate |

## Files Structure

```
src/file_management/recovery/
├── __init__.py           # Package exports
├── recovery_manager.py   # Main implementation
├── examples.py          # Usage examples
└── README.md           # This documentation
```

## Dependencies

- `aiofiles`: Async file operations
- `aiohttp`: Async HTTP client for Supabase integration
- `asyncio`: Async programming support
- `json`: JSON data handling
- `pathlib`: Path manipulation
- `logging`: Error logging
- `hashlib`: File integrity checking
- `datetime`: Timestamp handling

## Best Practices

1. **Always use async context manager** for proper resource cleanup
2. **Create backups** before risky file operations
3. **Monitor metrics** to track system health
4. **Configure appropriate timeouts** for your use case
5. **Use decorator** for simple function protection
6. **Implement workflow** for complex multi-step operations
7. **Set up Supabase** for production error tracking

## License

This implementation is part of the file management system and follows the same licensing terms.