
"""
EX-AI MCP Server - Streamlined Version

Production-ready MCP server with:
- Unified routing through RouterService integration
- Environment-based tool visibility management  
- Clean architecture with minimal redundancy
- Out-of-the-box operational configuration

This streamlined version eliminates dual routing systems, reduces configuration
complexity, and provides centralized tool visibility control.
"""

import asyncio
import atexit
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

# Environment setup
def _env_true(key: str, default: str = "false") -> bool:
    """Check if environment variable is set to a truthy value."""
    return os.getenv(key, default).lower() in ("true", "1", "yes", "on")

def _write_wrapper_error(text: str) -> None:
    """Write error message to stderr with proper formatting."""
    try:
        print(f"[ex-ai-streamlined] {text}", file=sys.stderr, flush=True)
    except Exception:
        pass

# Bootstrap logging
if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
    print(f"[ex-ai-streamlined] bootstrap starting (pid={os.getpid()}, py={sys.executable})", file=sys.stderr)

# Load environment variables
try:
    from dotenv import load_dotenv
    
    # Load production config by default
    env_file = os.getenv("ENV_FILE", ".env.production")
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"[ex-ai-streamlined] loaded config from {env_file}", file=sys.stderr)
    else:
        load_dotenv()  # fallback to .env
        
except ImportError:
    _write_wrapper_error("python-dotenv not available, using system environment only")

# Configure logging
def setup_logging():
    """Setup centralized logging configuration."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            RotatingFileHandler(
                log_dir / "exai_streamlined.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)

# Import MCP and core components
try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    
    # Import streamlined components
    from src.router.unified_router import UnifiedRouter
    from src.tools.registry_streamlined import StreamlinedToolRegistry
    from src.core.tool_visibility import ToolVisibilityManager
    
except ImportError as e:
    _write_wrapper_error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Global components
app = Server("ex-ai-streamlined")
router = UnifiedRouter()
tool_registry = StreamlinedToolRegistry()
visibility_manager = ToolVisibilityManager()

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available tools based on visibility settings."""
    try:
        tools_info = tool_registry.list_tools()
        tools = []
        
        for name, info in tools_info.items():
            tools.append(types.Tool(
                name=name,
                description=info.get("description", "No description available"),
                inputSchema=info.get("parameters", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            ))
        
        logger.info(f"Listed {len(tools)} available tools")
        return tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return []

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls with unified routing and visibility management."""
    try:
        # Check if tool is enabled
        if not tool_registry.has_tool(name):
            if name in visibility_manager.HIDDEN_TOOLS or name in visibility_manager.VISIBLE_TOOLS:
                error_msg = tool_registry.get_disabled_tool_message(name)
                return [types.TextContent(type="text", text=f"Tool disabled: {error_msg}")]
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
        
        # Get the tool
        tool = tool_registry.get_tool(name)
        if not tool:
            return [types.TextContent(type="text", text=f"Tool {name} not available")]
        
        # Route model selection through unified router
        requested_model = arguments.get("model", "auto")
        context = arguments.get("context", None)
        
        route_decision = router.choose_model(requested_model, context)
        
        # Update arguments with routed model
        arguments["model"] = route_decision.chosen
        
        logger.info(f"Tool call: {name} with model {route_decision.chosen} (reason: {route_decision.reason})")
        
        # Execute the tool
        if hasattr(tool, 'execute'):
            result = await tool.execute(**arguments)
        elif hasattr(tool, '__call__'):
            result = await tool(**arguments)
        else:
            result = "Tool execution method not found"
        
        # Ensure result is properly formatted
        if isinstance(result, str):
            return [types.TextContent(type="text", text=result)]
        elif isinstance(result, list) and all(isinstance(item, types.TextContent) for item in result):
            return result
        else:
            return [types.TextContent(type="text", text=str(result))]
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Tool execution failed: {str(e)}")]

async def main():
    """Main server entry point."""
    try:
        # Initialize router
        await router.initialize()
        
        # Log startup information
        logger.info("EX-AI MCP Server (Streamlined) starting...")
        logger.info(f"Enabled tools: {sorted(tool_registry.list_tools().keys())}")
        logger.info(f"Available models: {router.get_available_models()}")
        
        # Start the server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[ex-ai-streamlined] Shutdown requested", file=sys.stderr)
    except Exception as e:
        print(f"[ex-ai-streamlined] Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
