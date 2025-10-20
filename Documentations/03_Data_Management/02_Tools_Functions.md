# Tools & Functions Registry

## Purpose & Responsibility

This component manages the registration, validation, and execution of tools and functions available to AI models, providing a centralized registry for all callable functions.

## Tool Registry

### Tool Definition

```python
# types/tool.py
from typing import Dict, List, Any, Callable
from pydantic import BaseModel

class ToolParameter(BaseModel):
    name: str
    type: str  # 'string', 'number', 'boolean', 'object', 'array'
    description: str
    required: bool = False
    default: Any = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    category: str
    tags: List[str] = []
    version: str = "1.0.0"
    handler: Callable = None  # Function to execute
```

### Registry Implementation

```python
# services/tool_registry.py
from typing import Dict, List, Optional, Callable
from types.tool import ToolDefinition, ToolParameter

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.handlers: Dict[str, Callable] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter],
        handler: Callable,
        category: str = "general",
        tags: List[str] = None
    ) -> ToolDefinition:
        """Register a new tool"""
        tool = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            category=category,
            tags=tags or [],
            handler=handler
        )
        
        self.tools[name] = tool
        self.handlers[name] = handler
        
        return tool
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.tools.get(name)
    
    def list_tools(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ToolDefinition]:
        """List all registered tools with optional filtering"""
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if tags:
            tools = [
                t for t in tools 
                if any(tag in t.tags for tag in tags)
            ]
        
        return tools
    
    def validate_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """Validate parameters against tool definition"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Check required parameters
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(
                    f"Required parameter '{param.name}' missing for tool '{tool_name}'"
                )
            
            # Type validation
            if param.name in parameters:
                self._validate_type(
                    param.name,
                    parameters[param.name],
                    param.type
                )
        
        return True
    
    def _validate_type(self, name: str, value: Any, expected_type: str):
        """Validate parameter type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected = type_map.get(expected_type)
        if expected and not isinstance(value, expected):
            raise TypeError(
                f"Parameter '{name}' should be {expected_type}, "
                f"got {type(value).__name__}"
            )
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute a tool with given parameters"""
        # Validate parameters
        self.validate_parameters(tool_name, parameters)
        
        # Get handler
        handler = self.handlers.get(tool_name)
        if not handler:
            raise ValueError(f"No handler found for tool '{tool_name}'")
        
        # Execute
        try:
            result = await handler(**parameters)
            return result
        except Exception as e:
            raise RuntimeError(
                f"Error executing tool '{tool_name}': {str(e)}"
            )
```

## Tool Registration

### Decorator-based Registration

```python
# decorators/tool.py
from services.tool_registry import ToolRegistry
from types.tool import ToolParameter

registry = ToolRegistry()

def tool(
    name: str,
    description: str,
    parameters: List[ToolParameter],
    category: str = "general",
    tags: List[str] = None
):
    """Decorator to register a function as a tool"""
    def decorator(func):
        registry.register_tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=func,
            category=category,
            tags=tags
        )
        return func
    return decorator
```

### Example Tool Definitions

```python
# tools/chat_tools.py
from decorators.tool import tool
from types.tool import ToolParameter

@tool(
    name="chat",
    description="Send a message to an AI model and get a response",
    parameters=[
        ToolParameter(
            name="prompt",
            type="string",
            description="The message to send",
            required=True
        ),
        ToolParameter(
            name="model",
            type="string",
            description="AI model to use",
            required=False,
            default="kimi-k2-0905-preview"
        ),
        ToolParameter(
            name="temperature",
            type="number",
            description="Response creativity (0-1)",
            required=False,
            default=0.7
        )
    ],
    category="ai",
    tags=["chat", "ai", "conversation"]
)
async def chat_tool(prompt: str, model: str = "kimi-k2-0905-preview", temperature: float = 0.7):
    """Execute chat request"""
    from providers.kimi_provider import KimiProvider
    
    provider = KimiProvider()
    response = await provider.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=temperature
    )
    
    return response["choices"][0]["message"]["content"]

@tool(
    name="search",
    description="Search the web for information",
    parameters=[
        ToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True
        ),
        ToolParameter(
            name="max_results",
            type="number",
            description="Maximum number of results",
            required=False,
            default=5
        )
    ],
    category="search",
    tags=["search", "web", "information"]
)
async def search_tool(query: str, max_results: int = 5):
    """Execute web search"""
    # Implementation here
    results = await perform_web_search(query, max_results)
    return results
```

## Tool Execution

### Execution Service

```python
# services/tool_executor.py
from services.tool_registry import ToolRegistry
from typing import Dict, Any

class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: str = None
    ) -> Dict[str, Any]:
        """Execute tool and return result with metadata"""
        import time
        
        start_time = time.time()
        
        try:
            # Execute tool
            result = await self.registry.execute_tool(tool_name, parameters)
            
            execution_time = time.time() - start_time
            
            # Log execution to Supabase (fire-and-forget)
            asyncio.create_task(
                self.log_execution(
                    tool_name=tool_name,
                    parameters=parameters,
                    result=result,
                    execution_time=execution_time,
                    user_id=user_id,
                    status="success"
                )
            )
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log error
            asyncio.create_task(
                self.log_execution(
                    tool_name=tool_name,
                    parameters=parameters,
                    result=None,
                    execution_time=execution_time,
                    user_id=user_id,
                    status="error",
                    error=str(e)
                )
            )
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def log_execution(self, **kwargs):
        """Log tool execution to Supabase"""
        from services.supabase_service import SupabaseService
        
        supabase = SupabaseService()
        await supabase.insert("tool_executions", kwargs)
```

## API Integration

### Tool Endpoints

```python
# routes/tools.py
from fastapi import APIRouter, HTTPException
from services.tool_registry import ToolRegistry
from services.tool_executor import ToolExecutor

router = APIRouter()
registry = ToolRegistry()
executor = ToolExecutor(registry)

@router.get("/tools")
async def list_tools(category: str = None):
    """List all available tools"""
    tools = registry.list_tools(category=category)
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required
                    }
                    for p in t.parameters
                ]
            }
            for t in tools
        ]
    }

@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get tool definition"""
    tool = registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {"tool": tool}

@router.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, parameters: dict):
    """Execute a tool"""
    result = await executor.execute(tool_name, parameters)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
```

## Configuration

### Tool Configuration

```yaml
# config/tools.yaml
tools:
  enabled: true
  auto_register: true
  categories:
    - ai
    - search
    - file
    - data
  
  execution:
    timeout: 30  # seconds
    retry_attempts: 3
    log_executions: true
```

## Best Practices

1. **Parameter Validation**: Always validate parameters before execution
2. **Error Handling**: Implement comprehensive error handling
3. **Logging**: Log all tool executions for audit trail
4. **Timeouts**: Set reasonable timeouts for tool execution
5. **Documentation**: Document each tool's purpose and parameters

## Integration Points

- **AI Providers**: Tools available to AI models for function calling
- **API Layer**: Exposes tools via REST endpoints
- **Supabase**: Logs tool executions and analytics
- **WebSocket**: Supports real-time tool execution

