# Daemon & WebSocket Management

## Purpose & Responsibility

The Daemon & WebSocket Management component maintains persistent connections, handles message queuing, and ensures reliable communication between clients and AI providers through background daemon processes.

## Architecture

### Background Daemon Processes

The server runs several specialized daemon processes:

```json
{
  "daemons": {
    "websocket_manager": {
      "process": "ws_daemon.py",
      "priority": "high",
      "auto_restart": true,
      "health_check_interval": 30
    },
    "message_queue": {
      "process": "queue_daemon.py",
      "priority": "high",
      "memory_limit": "512MB",
      "batch_size": 100
    },
    "connection_monitor": {
      "process": "monitor_daemon.py",
      "priority": "medium",
      "check_interval": 15
    }
  }
}
```

Each daemon operates independently with:
- Automatic restart on failure
- Resource usage monitoring
- Graceful shutdown handling
- Inter-process communication via IPC

## WebSocket Connection Pooling

The server maintains dynamic connection pools optimized for different AI providers:

```python
# Configuration example
connection_pools = {
    "moonshot": {
        "min_connections": 2,
        "max_connections": 10,
        "idle_timeout": 30000,
        "acquire_timeout": 5000,
        "create_retry_interval": 200
    },
    "zhipuai": {
        "min_connections": 1,
        "max_connections": 5,
        "idle_timeout": 45000,
        "acquire_timeout": 3000,
        "create_retry_interval": 500
    }
}
```

Connection pooling features:
- **Dynamic scaling**: Automatically adjusts pool size based on demand
- **Health monitoring**: Regularly checks connection validity
- **Load balancing**: Distributes requests across available connections
- **Resource optimization**: Closes idle connections to free resources

## Message Queuing

The server implements a priority-based message queuing system:

```json
{
  "queue_config": {
    "max_size": 10000,
    "batch_size": 50,
    "processing_interval": 100,
    "retry_policy": {
      "max_retries": 3,
      "backoff_factor": 2,
      "initial_delay": 1000
    },
    "priority_levels": {
      "critical": 0,
      "high": 1,
      "normal": 2,
      "low": 3
    }
  }
}
```

Queue features:
- **Priority processing**: Higher priority messages processed first
- **Batch processing**: Groups messages for efficiency
- **Dead letter queue**: Handles failed messages after retry exhaustion
- **Persistence**: Critical messages saved to disk during shutdown

## Heartbeat and Reconnection Logic

The system implements a sophisticated heartbeat mechanism:

```python
heartbeat_config = {
    "interval": 30000,  # 30 seconds
    "timeout": 5000,    # 5 seconds
    "missed_threshold": 3,
    "reconnection": {
        "strategy": "exponential_backoff",
        "initial_delay": 1000,
        "max_delay": 30000,
        "jitter": True,
        "max_attempts": 10
    }
}
```

Reconnection features:
- **Adaptive backoff**: Exponential delay with jitter to prevent thundering herd
- **Circuit breaker**: Temporarily stops reconnection attempts after repeated failures
- **State preservation**: Maintains message context during reconnection
- **Fallback mechanisms**: Switches to HTTP mode when WebSocket fails repeatedly

## Configuration Examples

### Basic WebSocket Configuration
```yaml
websocket:
  port: 8079
  host: "0.0.0.0"
  path: "/mcp"
  compression: true
  max_frame_size: 1048576  # 1MB
  ping_interval: 30000
  ping_timeout: 5000
```

### Advanced Daemon Configuration
```yaml
daemons:
  enabled: true
  log_level: "info"
  process_management:
    graceful_shutdown_timeout: 10000
    max_restarts: 5
    restart_delay: 5000
  resource_limits:
    max_memory: "1GB"
    max_cpu: "80%"
```

### Production-ready Configuration
```yaml
production:
  websocket:
    ssl:
      enabled: true
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
    security:
      origin_check: true
      rate_limiting:
        enabled: true
        requests_per_minute: 100
  monitoring:
    metrics:
      enabled: true
      endpoint: "/metrics"
    health_check:
      enabled: true
      endpoint: "/health"
```

## Key Files & Their Roles

```
src/
├── daemon/
│   ├── ws_server.py              # Main WebSocket daemon
│   ├── conversation_queue.py     # Message queue management
│   ├── session_semaphore_manager.py  # Connection pooling
│   └── warmup.py                 # Connection pre-warming
├── websocket/
│   ├── connection_manager.py     # Connection lifecycle
│   ├── heartbeat.py              # Heartbeat monitoring
│   └── reconnection.py           # Reconnection logic
└── config/
    └── daemon.yaml               # Daemon configuration
```

## Usage Examples

### Starting the Daemon

```python
from src.daemon.ws_server import start_daemon

# Start WebSocket daemon
await start_daemon(
    host="0.0.0.0",
    port=8079,
    auth_token="your-auth-token"
)
```

### Connecting to WebSocket

```python
import websockets
import json

async def connect_to_daemon():
    uri = "ws://localhost:8079"
    
    async with websockets.connect(uri) as websocket:
        # Send hello message
        await websocket.send(json.dumps({
            "op": "hello",
            "token": "your-auth-token"
        }))
        
        # Receive hello_ack
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Call tool
        await websocket.send(json.dumps({
            "op": "call_tool",
            "request_id": "req-123",
            "name": "chat",
            "arguments": {"prompt": "Hello!"}
        }))
        
        # Receive response
        result = await websocket.recv()
        print(f"Result: {result}")
```

## Best Practices

1. **Connection Management**
   - Always release connections back to the pool after use
   - Implement connection validation before use
   - Monitor pool metrics to optimize sizing

2. **Error Handling**
   - Implement comprehensive error logging
   - Use circuit breakers for external service dependencies
   - Provide meaningful error messages to clients

3. **Performance Optimization**
   - Adjust queue batch sizes based on message volume
   - Tune heartbeat intervals for your network conditions
   - Monitor and optimize memory usage in daemons

4. **Security Considerations**
   - Implement proper authentication and authorization
   - Use rate limiting to prevent abuse
   - Secure WebSocket connections with WSS in production

## Integration Points

- **MCP Server**: Receives tool calls via WebSocket protocol
- **SDK Integration**: Routes requests to appropriate AI providers
- **Supabase Storage**: Records all interactions in parallel
- **Monitoring**: Exposes metrics for health checks and observability

