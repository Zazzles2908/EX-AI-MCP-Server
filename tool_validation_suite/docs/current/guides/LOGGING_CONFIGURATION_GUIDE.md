# Logging Configuration Guide

**Last Updated:** 2025-10-07  
**Status:** ✅ ACTIVE  
**Purpose:** Comprehensive guide to logging configuration in EX-AI MCP Server

---

## 🎯 Overview

The EX-AI MCP Server uses Python's built-in `logging` module with structured configuration for different components. This guide explains how logging is configured, how to adjust log levels, and best practices for debugging.

---

## 📊 Logging Architecture

### Log Levels (Standard Python)

| Level | Value | When to Use |
|-------|-------|-------------|
| `DEBUG` | 10 | Detailed diagnostic information for development |
| `INFO` | 20 | General informational messages about normal operation |
| `WARNING` | 30 | Warning messages for potentially problematic situations |
| `ERROR` | 40 | Error messages for serious problems |
| `CRITICAL` | 50 | Critical messages for very serious errors |

### Default Log Levels by Component

```python
# Server components
server.py: INFO
ws_server.py: INFO
daemon.py: INFO

# Core tools
src/tools/: INFO
src/core/: INFO

# Providers
src/providers/: INFO

# Utilities
utils/: INFO

# Test suite
tool_validation_suite/: INFO
```

---

## ⚙️ Configuration Methods

### Method 1: Environment Variables (Recommended)

**Set log level for entire application:**
```bash
# In .env file
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Set log level for specific modules:**
```bash
# Provider-specific logging
PROVIDER_LOG_LEVEL=DEBUG

# Tool-specific logging
TOOL_LOG_LEVEL=INFO

# MCP server logging
MCP_LOG_LEVEL=INFO
```

### Method 2: Code Configuration

**In your Python code:**
```python
import logging

# Set root logger level
logging.basicConfig(level=logging.DEBUG)

# Set specific logger level
logger = logging.getLogger("src.providers.glm")
logger.setLevel(logging.DEBUG)
```

### Method 3: Runtime Configuration

**Using logging.conf file:**
```ini
[loggers]
keys=root,providers,tools

[handlers]
keys=console,file

[formatters]
keys=detailed,simple

[logger_root]
level=INFO
handlers=console

[logger_providers]
level=DEBUG
handlers=console,file
qualname=src.providers
propagate=0

[logger_tools]
level=INFO
handlers=console
qualname=src.tools
propagate=0

[handler_console]
class=StreamHandler
level=DEBUG
formatter=simple
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=detailed
args=('logs/exai.log', 'a')

[formatter_simple]
format=%(levelname)s - %(name)s - %(message)s

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

---

## 📝 Log Format

### Standard Format
```
2025-10-07 10:30:45 - src.providers.glm - INFO - Initializing GLM provider
```

**Components:**
- `2025-10-07 10:30:45` - Timestamp
- `src.providers.glm` - Logger name (module path)
- `INFO` - Log level
- `Initializing GLM provider` - Message

### Structured Logging (JSON)

For production environments, consider structured logging:
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_data)
```

---

## 🔍 Common Logging Patterns

### Provider Logging

**GLM Provider:**
```python
import logging
logger = logging.getLogger(__name__)

# Initialization
logger.info(f"Initializing GLM provider with base_url: {base_url}")

# API calls
logger.debug(f"Calling GLM API with model: {model}")

# Errors
logger.error(f"GLM API call failed: {error}", exc_info=True)

# Warnings
logger.warning(f"GLM web search not supported for model: {model}")
```

**Kimi Provider:**
```python
import logging
logger = logging.getLogger(__name__)

# Context caching
logger.debug(f"Cache hit for prefix: {prefix_hash}")
logger.info(f"Saved {tokens} tokens via caching")

# File uploads
logger.info(f"Uploading file: {file_path}")
logger.debug(f"File upload response: {response}")
```

### Tool Logging

**Workflow Tools:**
```python
import logging
logger = logging.getLogger(__name__)

# Tool execution
logger.info(f"Starting {tool_name} workflow (step {step_number}/{total_steps})")

# Progress tracking
logger.debug(f"Findings: {findings}")

# Completion
logger.info(f"Workflow complete: {tool_name}")
```

### Server Logging

**MCP Server:**
```python
import logging
logger = logging.getLogger(__name__)

# Server startup
logger.info("MCP server starting on port 8080")

# Request handling
logger.debug(f"Received request: {request_type}")

# Errors
logger.error(f"Request failed: {error}", exc_info=True)
```

---

## 🐛 Debugging with Logs

### Enable Debug Logging

**For entire application:**
```bash
LOG_LEVEL=DEBUG python server.py
```

**For specific module:**
```python
import logging
logging.getLogger("src.providers.glm").setLevel(logging.DEBUG)
```

### Useful Debug Patterns

**1. Trace function calls:**
```python
logger.debug(f"Entering {function_name} with args: {args}")
logger.debug(f"Exiting {function_name} with result: {result}")
```

**2. Log variable values:**
```python
logger.debug(f"Variable state: model={model}, temperature={temperature}")
```

**3. Log API requests/responses:**
```python
logger.debug(f"API Request: {json.dumps(request_data, indent=2)}")
logger.debug(f"API Response: {json.dumps(response_data, indent=2)}")
```

**4. Log timing information:**
```python
import time
start = time.time()
# ... operation ...
logger.debug(f"Operation took {time.time() - start:.2f}s")
```

---

## 📂 Log Files

### Default Locations

```
logs/
├── mcp_server.log          # MCP server logs
├── mcp_activity.log        # MCP activity logs (tool calls)
├── daemon.log              # WebSocket daemon logs
├── exai.log                # General application logs
└── test_results.log        # Test execution logs
```

### Log Rotation

**Using RotatingFileHandler:**
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/exai.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5            # Keep 5 backup files
)
```

**Using TimedRotatingFileHandler:**
```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    'logs/exai.log',
    when='midnight',  # Rotate at midnight
    interval=1,       # Every day
    backupCount=7     # Keep 7 days
)
```

---

## 🔧 Troubleshooting

### Issue: No logs appearing

**Possible causes:**
1. Log level too high (e.g., ERROR when you want INFO)
2. Logger not configured
3. Handler not added to logger

**Solutions:**
```python
# Check current log level
import logging
logger = logging.getLogger(__name__)
print(f"Current level: {logger.level}")

# Ensure handler is added
if not logger.handlers:
    handler = logging.StreamHandler()
    logger.addHandler(handler)

# Set level explicitly
logger.setLevel(logging.DEBUG)
```

### Issue: Too many logs

**Solution: Increase log level**
```bash
# Only show warnings and errors
LOG_LEVEL=WARNING
```

**Or filter specific modules:**
```python
# Silence noisy module
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
```

### Issue: Logs not showing timestamps

**Solution: Add formatter**
```python
import logging

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

---

## 📋 Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug("Detailed variable state for debugging")
logger.info("Normal operation milestone")
logger.warning("Potential issue, but continuing")
logger.error("Error occurred, operation failed")
logger.critical("System-level failure")

# ❌ Bad
logger.info("x=5, y=10, z=15")  # Too detailed for INFO
logger.error("User not found")  # Not an error, use WARNING
```

### 2. Include Context

```python
# ✅ Good
logger.error(f"Failed to connect to {host}:{port}: {error}")

# ❌ Bad
logger.error("Connection failed")
```

### 3. Use exc_info for Exceptions

```python
# ✅ Good
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)

# ❌ Bad
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")  # No stack trace
```

### 4. Avoid Logging Sensitive Data

```python
# ✅ Good
logger.info(f"User authenticated: {user_id}")

# ❌ Bad
logger.info(f"User logged in: {username}:{password}")
```

### 5. Use Lazy Formatting

```python
# ✅ Good (only formats if log level allows)
logger.debug("Processing %s items", len(items))

# ❌ Bad (always formats, even if not logged)
logger.debug(f"Processing {len(items)} items")
```

---

## 🎯 Quick Reference

### Enable Debug Logging
```bash
LOG_LEVEL=DEBUG python server.py
```

### View Recent Logs
```bash
tail -f logs/mcp_server.log
```

### Search Logs
```bash
grep "ERROR" logs/exai.log
grep -i "timeout" logs/*.log
```

### Clear Old Logs
```bash
find logs/ -name "*.log" -mtime +7 -delete  # Delete logs older than 7 days
```

---

## ✅ Summary

**Logging in EX-AI MCP Server:**
- ✅ Uses Python's standard logging module
- ✅ Configurable via environment variables
- ✅ Supports multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Logs to both console and files
- ✅ Supports log rotation
- ✅ Structured logging available for production

**For debugging:**
1. Set `LOG_LEVEL=DEBUG` in .env
2. Check logs in `logs/` directory
3. Use `tail -f` to monitor in real-time
4. Search logs with `grep` for specific issues

**For production:**
1. Set `LOG_LEVEL=INFO` or `WARNING`
2. Enable log rotation
3. Consider structured (JSON) logging
4. Monitor log files for errors

