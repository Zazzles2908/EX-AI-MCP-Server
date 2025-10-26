# MCP Server Integration

## Purpose & Responsibility

This component implements the Model Context Protocol (MCP) for seamless integration between EXAI and various AI providers, handling connection pooling, request routing, and protocol compliance.

## MCP Protocol Implementation

### Core Protocol Handler

```python
class MCPProtocolHandler:
    def __init__(self, config: MCPConfig):
        self.config = config
        self.connections = {}
        self.request_router = RequestRouter()
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        try:
            # Validate request
            self._validate_request(request)
            
            # Route to appropriate provider
            provider = self.request_router.route(request.provider)
            
            # Execute request
            response = await provider.execute(request)
            
            # Format response
            return self._format_response(response)
        except Exception as e:
            return MCPResponse(error=str(e))
```

### Message Types

```python
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class MCPMessage:
    def __init__(self, type: MessageType, payload: dict, metadata: dict):
        self.type = type
        self.payload = payload
        self.metadata = metadata
        self.timestamp = datetime.utcnow()
```

## Connection Pooling

### Pool Configuration

```python
class ConnectionPool:
    def __init__(self, provider: str, pool_size: int = 10, max_overflow: int = 20):
        self.provider = provider
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._pool = asyncio.Queue(maxsize=pool_size)
        self._active_connections = 0
        self._lock = asyncio.Lock()
    
    async def get_connection(self) -> Connection:
        # Try to get from pool
        try:
            connection = self._pool.get_nowait()
            if await self._validate_connection(connection):
                return connection
            else:
                await self._close_connection(connection)
        except asyncio.QueueEmpty:
            pass
        
        # Create new connection if under limit
        async with self._lock:
            if self._active_connections < self.pool_size + self.max_overflow:
                connection = await self._create_connection()
                self._active_connections += 1
                return connection
        
        # Wait for available connection
        return await self._pool.get()
```

### Connection Lifecycle

```python
async def _create_connection(self) -> Connection:
    """Create a new connection to the provider"""
    if self.provider == "kimi":
        return KimiConnection(api_key=self.config.kimi_api_key)
    elif self.provider == "glm":
        return GLMConnection(api_key=self.config.glm_api_key)
    else:
        raise ValueError(f"Unknown provider: {self.provider}")

async def _validate_connection(self, connection: Connection) -> bool:
    """Validate connection is still active"""
    try:
        await connection.ping()
        return True
    except:
        return False
```

## Request Routing

### Router Implementation

```python
class RequestRouter:
    def __init__(self):
        self.routes = {}
        self.middleware = []
    
    def add_route(self, pattern: str, handler: Callable):
        self.routes[pattern] = handler
    
    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)
    
    async def route(self, request: MCPRequest) -> Provider:
        # Apply middleware
        for middleware in self.middleware:
            request = await middleware(request)
        
        # Find matching route
        for pattern, handler in self.routes.items():
            if re.match(pattern, request.path):
                return await handler(request)
        
        raise RouteNotFoundError(f"No route found for {request.path}")
```

### Load Balancing

```python
class LoadBalancer:
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0
        self.providers = []
    
    def add_provider(self, provider: Provider):
        self.providers.append(provider)
    
    def get_provider(self) -> Provider:
        if not self.providers:
            raise NoProvidersAvailableError()
        
        if self.strategy == "round_robin":
            provider = self.providers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.providers)
            return provider
        elif self.strategy == "least_connections":
            return min(self.providers, key=lambda p: p.active_connections)
        else:
            raise ValueError(f"Unknown load balancing strategy: {self.strategy}")
```

## Error Handling

### Retry Mechanism

```python
class RetryHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs):
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_factor * (2 ** attempt))
                else:
                    raise last_exception
```

## Configuration

### MCP Server Configuration

```yaml
mcp:
  server:
    host: "0.0.0.0"
    port: 8079
    protocol: "websocket"
  
  connection_pool:
    kimi:
      min_connections: 2
      max_connections: 10
      idle_timeout: 30000
    glm:
      min_connections: 1
      max_connections: 5
      idle_timeout: 45000
  
  routing:
    strategy: "round_robin"
    middleware:
      - "auth"
      - "rate_limit"
      - "logging"
  
  retry:
    max_retries: 3
    backoff_factor: 0.5
```

## Key Files & Their Roles

```
src/
├── mcp/
│   ├── protocol_handler.py      # MCP protocol implementation
│   ├── connection_pool.py       # Connection pooling
│   ├── router.py                # Request routing
│   └── load_balancer.py         # Load balancing
├── providers/
│   ├── kimi_provider.py         # Kimi/Moonshot provider
│   ├── glm_provider.py          # GLM/ZhipuAI provider
│   └── base_provider.py         # Base provider interface
└── config/
    └── mcp.yaml                 # MCP configuration
```

## Usage Examples

### Starting MCP Server

```python
from src.mcp.protocol_handler import MCPProtocolHandler
from src.mcp.connection_pool import ConnectionPool

# Initialize connection pools
kimi_pool = ConnectionPool(provider="kimi", pool_size=10)
glm_pool = ConnectionPool(provider="glm", pool_size=5)

# Initialize MCP handler
mcp_handler = MCPProtocolHandler(config=mcp_config)

# Start server
await mcp_handler.start()
```

### Making MCP Request

```python
# Create request
request = MCPRequest(
    provider="kimi",
    model="kimi-k2-0905-preview",
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100
)

# Execute request
response = await mcp_handler.handle_request(request)
print(response.content)
```

## Best Practices

1. **Connection Management**
   - Always release connections back to pool after use
   - Implement connection validation before use
   - Monitor pool metrics to optimize sizing

2. **Error Handling**
   - Implement comprehensive error logging
   - Use circuit breakers for external dependencies
   - Provide meaningful error messages to clients

3. **Performance Optimization**
   - Adjust pool sizes based on load patterns
   - Use load balancing for multiple providers
   - Monitor and optimize retry strategies

4. **Security**
   - Validate all incoming requests
   - Implement rate limiting
   - Use authentication middleware

## Integration Points

- **WebSocket Daemon**: Receives MCP requests via WebSocket
- **SDK Providers**: Routes to Kimi/GLM SDKs
- **Supabase Storage**: Records all interactions in parallel
- **Monitoring**: Exposes metrics for observability

