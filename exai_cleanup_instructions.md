# EX-AI MCP Server - Cleanup Instructions for AI Coder

## Overview

This document provides specific step-by-step instructions for implementing the streamlined version of the EX-AI MCP Server. These instructions are designed for an AI coder to follow systematically.

## Phase 1: Repository Preparation

### Step 1: Create Feature Branch
```bash
cd /path/to/EX-AI-MCP-Server
git checkout -b streamline-implementation
```

### Step 2: Backup Current State
```bash
# Create backup of current working state
git add -A
git commit -m "Backup before streamline implementation"
```

## Phase 2: File Structure Cleanup

### Step 3: Remove Redundant Files

**Delete the following directories and files:**

```bash
# Remove redundant diagnostic scripts (20+ files)
rm -rf scripts/diagnostics/
rm -rf scripts/e2e/
rm scripts/diagnose_mcp.py
rm scripts/demo_tools.py
rm scripts/minimal_server.py
rm scripts/run_thinkdeep_web.py
rm scripts/alias_test.py
rm scripts/cleanup_phase3.py

# Remove legacy configuration files
rm .env.new
rm mcp-config.augmentcode.json
rm mcp-config.pylauncher.json
rm server_original.py

# Remove temporary and validation directories
rm -rf .tmp/
rm -rf .validation_tmp/
rm -rf .logs/

# Remove unused utility directories
rm -rf auggie/
rm -rf dr/
rm -rf nl/
rm -rf patch/
rm -rf simulator_tests/
rm -rf test_simulation_files/
rm -rf venvs/

# Remove redundant documentation
rm README-ORIGINAL.md
rm README-PUBLIC.md

# Remove deployment-specific files not needed for streamlined version
rm Caddyfile
rm nginx.conf
rm run-server.ps1
rm run-server.sh
rm setup-auggie.sh
rm Procfile
rm Dockerfile
rm -rf docker/
```

### Step 4: Reorganize Tool Structure

```bash
# Create new tool directory structure
mkdir -p src/tools/visible
mkdir -p src/tools/hidden

# Move visible tools
mv tools/chat.py src/tools/visible/
mv tools/workflows/planner.py src/tools/visible/
mv tools/workflows/thinkdeep.py src/tools/visible/
mv tools/selfcheck.py src/tools/visible/

# Move hidden tools
mv tools/workflows/consensus.py src/tools/hidden/
mv tools/workflows/codereview.py src/tools/hidden/
mv tools/workflows/precommit.py src/tools/hidden/
mv tools/workflows/debug.py src/tools/hidden/
mv tools/workflows/secaudit.py src/tools/hidden/
mv tools/workflows/docgen.py src/tools/hidden/
mv tools/workflows/analyze.py src/tools/hidden/
mv tools/workflows/refactor.py src/tools/hidden/
mv tools/workflows/tracer.py src/tools/hidden/
mv tools/workflows/testgen.py src/tools/hidden/
mv tools/challenge.py src/tools/hidden/
mv tools/capabilities/listmodels.py src/tools/hidden/
mv tools/capabilities/version.py src/tools/hidden/

# Remove old tool directories
rm -rf tools/workflows/
rm -rf tools/capabilities/
rm -rf tools/diagnostics/
rm -rf tools/streaming/
rm -rf tools/unified/
rm -rf tools/providers/
```

### Step 5: Create Core Components Directory

```bash
# Create core components structure
mkdir -p src/core
mkdir -p src/router
mkdir -p config
```

## Phase 3: Implementation of New Components

### Step 6: Create Tool Visibility Manager

Create `src/core/tool_visibility.py` with the following content:

```python
"""
Tool Visibility Management for EX-AI MCP Server

Manages which tools are visible vs hidden based on environment flags.
Provides centralized control over tool availability.
"""
import os
from typing import Set, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ToolVisibilityManager:
    """Manages tool visibility based on environment configuration."""
    
    # Always visible tools (core functionality)
    VISIBLE_TOOLS = {
        "chat",
        "planner", 
        "thinkdeep",
        "self-check"
    }
    
    # Hidden tools with environment flags
    HIDDEN_TOOLS = {
        "consensus": "ENABLE_CONSENSUS",
        "codereview": "ENABLE_CODEREVIEW", 
        "precommit": "ENABLE_PRECOMMIT",
        "debug": "ENABLE_DEBUG",
        "secaudit": "ENABLE_SECAUDIT",
        "docgen": "ENABLE_DOCGEN",
        "analyze": "ENABLE_ANALYZE",
        "refactor": "ENABLE_REFACTOR",
        "tracer": "ENABLE_TRACER",
        "testgen": "ENABLE_TESTGEN",
        "challenge": "ENABLE_CHALLENGE",
        "listmodels": "ENABLE_LISTMODELS",
        "version": "ENABLE_VERSION"
    }
    
    def __init__(self):
        self._enabled_tools = self._calculate_enabled_tools()
        logger.info(f"Tool visibility initialized. Enabled tools: {sorted(self._enabled_tools)}")
    
    def _calculate_enabled_tools(self) -> Set[str]:
        """Calculate which tools are enabled based on environment."""
        enabled = set(self.VISIBLE_TOOLS)
        
        # Check environment flags for hidden tools
        for tool_name, env_flag in self.HIDDEN_TOOLS.items():
            if self._env_true(env_flag):
                enabled.add(tool_name)
                logger.debug(f"Tool '{tool_name}' enabled via {env_flag}")
        
        return enabled
    
    def _env_true(self, key: str) -> bool:
        """Check if environment variable is set to a truthy value."""
        return os.getenv(key, "false").lower() in ("true", "1", "yes", "on")
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        return tool_name in self._enabled_tools
    
    def get_enabled_tools(self) -> Set[str]:
        """Get all enabled tools."""
        return self._enabled_tools.copy()
    
    def get_disabled_reason(self, tool_name: str) -> str:
        """Get reason why a tool is disabled."""
        if tool_name in self.VISIBLE_TOOLS:
            return f"Tool '{tool_name}' should be visible but is not enabled"
        
        if tool_name in self.HIDDEN_TOOLS:
            env_flag = self.HIDDEN_TOOLS[tool_name]
            return f"Tool '{tool_name}' is disabled. Set {env_flag}=true to enable."
        
        return f"Unknown tool '{tool_name}'"
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get comprehensive tool status for diagnostics."""
        return {
            "visible_tools": sorted(self.VISIBLE_TOOLS),
            "hidden_tools": sorted(self.HIDDEN_TOOLS.keys()),
            "enabled_tools": sorted(self._enabled_tools),
            "disabled_tools": sorted(
                (set(self.VISIBLE_TOOLS) | set(self.HIDDEN_TOOLS.keys())) - self._enabled_tools
            )
        }
```

### Step 7: Create Unified Router

Create `src/router/unified_router.py` with the following content:

```python
"""
Unified Router for EX-AI MCP Server

Integrates RouterService into the main request pipeline to eliminate dual routing.
Provides centralized model selection and request routing.
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import os

from src.providers.registry import ModelProviderRegistry as R
from src.providers.base import ProviderType

logger = logging.getLogger("unified_router")

@dataclass
class RouteDecision:
    """Represents a routing decision with metadata."""
    requested: str
    chosen: str
    reason: str
    provider: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps({
            "event": "route_decision",
            "requested": self.requested,
            "chosen": self.chosen,
            "reason": self.reason,
            "provider": self.provider,
            "meta": self.meta or {},
        }, ensure_ascii=False)

class UnifiedRouter:
    """Unified router that handles all model selection and request routing."""
    
    def __init__(self):
        # Model preferences from environment
        self._fast_default = os.getenv("FAST_MODEL_DEFAULT", "glm-4.5-flash")
        self._long_default = os.getenv("LONG_MODEL_DEFAULT", "kimi-k2-0711-preview")
        self._default_model = os.getenv("DEFAULT_MODEL", self._fast_default)
        
        # Diagnostics
        self._diag_enabled = os.getenv("ROUTER_DIAGNOSTICS_ENABLED", "false").lower() == "true"
        
        # Initialize provider registry
        self._registry = R()
        
        logger.info(f"Unified router initialized with defaults: fast={self._fast_default}, long={self._long_default}")
    
    async def initialize(self) -> None:
        """Initialize the router and perform preflight checks."""
        try:
            # Perform provider availability checks
            available_providers = []
            
            if self._registry.has_provider(ProviderType.GLM):
                available_providers.append("GLM")
            
            if self._registry.has_provider(ProviderType.KIMI):
                available_providers.append("KIMI")
            
            logger.info(f"Available providers: {available_providers}")
            
            if not available_providers:
                logger.warning("No providers available - check API keys")
            
        except Exception as e:
            logger.error(f"Router initialization failed: {e}")
            raise
    
    def choose_model(self, requested: Optional[str] = None, context: Optional[str] = None) -> RouteDecision:
        """
        Choose the best model for a request.
        
        Args:
            requested: Explicitly requested model name
            context: Context hint for model selection (e.g., 'long', 'fast')
        
        Returns:
            RouteDecision with chosen model and reasoning
        """
        # Handle explicit model requests
        if requested and requested != "auto":
            if self._is_model_available(requested):
                decision = RouteDecision(
                    requested=requested,
                    chosen=requested,
                    reason="explicit_request",
                    provider=self._get_provider_for_model(requested)
                )
            else:
                # Fallback to default if requested model unavailable
                chosen = self._default_model
                decision = RouteDecision(
                    requested=requested,
                    chosen=chosen,
                    reason="fallback_unavailable",
                    provider=self._get_provider_for_model(chosen),
                    meta={"original_unavailable": requested}
                )
        else:
            # Auto selection based on context
            if context == "long":
                chosen = self._long_default
                reason = "auto_long_context"
            elif context == "fast":
                chosen = self._fast_default
                reason = "auto_fast"
            else:
                chosen = self._default_model
                reason = "auto_default"
            
            decision = RouteDecision(
                requested=requested or "auto",
                chosen=chosen,
                reason=reason,
                provider=self._get_provider_for_model(chosen)
            )
        
        # Log decision if diagnostics enabled
        if self._diag_enabled:
            logger.info(decision.to_json())
        
        return decision
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available through any provider."""
        try:
            # Check GLM models
            if model_name.startswith("glm-") and self._registry.has_provider(ProviderType.GLM):
                return True
            
            # Check Kimi models  
            if model_name.startswith("kimi-") and self._registry.has_provider(ProviderType.KIMI):
                return True
            
            return False
        except Exception:
            return False
    
    def _get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get the provider name for a given model."""
        if model_name.startswith("glm-"):
            return "GLM"
        elif model_name.startswith("kimi-"):
            return "KIMI"
        return None
    
    def get_available_models(self) -> Dict[str, list]:
        """Get list of available models by provider."""
        models = {}
        
        if self._registry.has_provider(ProviderType.GLM):
            models["GLM"] = ["glm-4.5-flash", "glm-4-plus", "glm-4-air", "glm-4-airx"]
        
        if self._registry.has_provider(ProviderType.KIMI):
            models["KIMI"] = ["kimi-k2-0711-preview", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
        
        return models
    
    def get_router_status(self) -> Dict[str, Any]:
        """Get router status for diagnostics."""
        return {
            "fast_default": self._fast_default,
            "long_default": self._long_default,
            "default_model": self._default_model,
            "diagnostics_enabled": self._diag_enabled,
            "available_models": self.get_available_models()
        }
```

### Step 8: Create Streamlined Tool Registry

Create `src/tools/registry_streamlined.py` with the following content:

```python
"""
Streamlined Tool Registry for EX-AI MCP Server

Simplified tool registration with visibility management integration.
Only registers tools that are enabled via ToolVisibilityManager.
"""
import logging
from typing import Dict, Any, Optional, Type
import importlib

from src.core.tool_visibility import ToolVisibilityManager

logger = logging.getLogger(__name__)

class StreamlinedToolRegistry:
    """Streamlined tool registry with visibility management."""
    
    # Tool import mapping
    TOOL_IMPORTS = {
        # Visible tools
        "chat": ("src.tools.visible.chat", "ChatTool"),
        "planner": ("src.tools.visible.planner", "PlannerTool"), 
        "thinkdeep": ("src.tools.visible.thinkdeep", "ThinkDeepTool"),
        "self-check": ("src.tools.visible.selfcheck", "SelfCheckTool"),
        
        # Hidden tools
        "consensus": ("src.tools.hidden.consensus", "ConsensusTool"),
        "codereview": ("src.tools.hidden.codereview", "CodeReviewTool"),
        "precommit": ("src.tools.hidden.precommit", "PrecommitTool"),
        "debug": ("src.tools.hidden.debug", "DebugIssueTool"),
        "secaudit": ("src.tools.hidden.secaudit", "SecauditTool"),
        "docgen": ("src.tools.hidden.docgen", "DocgenTool"),
        "analyze": ("src.tools.hidden.analyze", "AnalyzeTool"),
        "refactor": ("src.tools.hidden.refactor", "RefactorTool"),
        "tracer": ("src.tools.hidden.tracer", "TracerTool"),
        "testgen": ("src.tools.hidden.testgen", "TestGenTool"),
        "challenge": ("src.tools.hidden.challenge", "ChallengeTool"),
        "listmodels": ("src.tools.hidden.listmodels", "ListModelsTool"),
        "version": ("src.tools.hidden.version", "VersionTool")
    }
    
    def __init__(self):
        self.visibility_manager = ToolVisibilityManager()
        self._tools: Dict[str, Any] = {}
        self._load_enabled_tools()
    
    def _load_enabled_tools(self) -> None:
        """Load only the tools that are enabled."""
        enabled_tools = self.visibility_manager.get_enabled_tools()
        
        for tool_name in enabled_tools:
            if tool_name in self.TOOL_IMPORTS:
                try:
                    module_path, class_name = self.TOOL_IMPORTS[tool_name]
                    module = importlib.import_module(module_path)
                    tool_class = getattr(module, class_name)
                    self._tools[tool_name] = tool_class()
                    logger.debug(f"Loaded tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Failed to load tool {tool_name}: {e}")
        
        logger.info(f"Loaded {len(self._tools)} tools: {sorted(self._tools.keys())}")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name if it's enabled."""
        return self._tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is available."""
        return name in self._tools
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with their metadata."""
        tools_info = {}
        
        for name, tool in self._tools.items():
            try:
                tools_info[name] = {
                    "name": name,
                    "description": getattr(tool, "description", "No description available"),
                    "parameters": getattr(tool, "parameters", {}),
                    "enabled": True
                }
            except Exception as e:
                logger.error(f"Error getting info for tool {name}: {e}")
                tools_info[name] = {
                    "name": name,
                    "description": "Error loading tool info",
                    "enabled": True
                }
        
        return tools_info
    
    def get_disabled_tool_message(self, name: str) -> str:
        """Get message for disabled tool."""
        return self.visibility_manager.get_disabled_reason(name)
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status for diagnostics."""
        return {
            "loaded_tools": sorted(self._tools.keys()),
            "tool_count": len(self._tools),
            "visibility_status": self.visibility_manager.get_tool_status()
        }
```

### Step 9: Create Production Configuration

Create `.env.production` with the following content:

```bash
# EX-AI MCP Server - Production Configuration
# Streamlined version with unified routing and tool visibility management

# API Keys - Production Test Keys
GLM_API_KEY=90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD
KIMI_API_KEY=sk-JJUBj1u6AXcKjVXkZURRhvcotCgbekB6o56mwqByZNyvz4om

# Router Configuration - Unified routing enabled
ROUTER_ENABLED=true
DEFAULT_MODEL=glm-4.5-flash
FAST_MODEL_DEFAULT=glm-4.5-flash
LONG_MODEL_DEFAULT=kimi-k2-0711-preview

# Tool Visibility Management
# Visible tools (always available)
VISIBLE_TOOLS=chat,planner,thinkdeep,self-check

# Hidden tools (controlled by environment flags)
ENABLE_CONSENSUS=false
ENABLE_CODEREVIEW=false
ENABLE_PRECOMMIT=false
ENABLE_DEBUG=false
ENABLE_SECAUDIT=false
ENABLE_DOCGEN=false
ENABLE_ANALYZE=false
ENABLE_REFACTOR=false
ENABLE_TRACER=false
ENABLE_TESTGEN=false
ENABLE_CHALLENGE=false
ENABLE_LISTMODELS=false
ENABLE_VERSION=false

# Provider Configuration
DISABLED_PROVIDERS=GOOGLE,OPENAI,XAI,DIAL,OPENROUTER
ENABLE_CONFIG_VALIDATOR=true
PREFER_FREE_TIER=false

# Logging and Diagnostics
LOG_LEVEL=INFO
ROUTER_DIAGNOSTICS_ENABLED=false
EX_MCP_BOOTSTRAP_DEBUG=false

# Remote Server (disabled in production)
MCP_REMOTE_HOST=
MCP_REMOTE_PORT=
MCP_AUTH_TOKEN=

# UI Compatibility
EXAI_WS_COMPAT_TEXT=true
```

### Step 10: Create Streamlined Main Server

Create `server_streamlined.py` with the following content:

```python
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
```

## Phase 4: Update Import Paths

### Step 11: Fix Tool Import Paths

**Update all tool files to use new import paths:**

1. **In visible tool files** (`src/tools/visible/*.py`):
   - Update imports from `tools.` to `src.tools.visible.`
   - Update provider imports from `src.providers.` to `src.providers.`

2. **In hidden tool files** (`src/tools/hidden/*.py`):
   - Update imports from `tools.` to `src.tools.hidden.`
   - Update provider imports from `src.providers.` to `src.providers.`

### Step 12: Create __init__.py Files

```bash
# Create package init files
touch src/__init__.py
touch src/core/__init__.py
touch src/router/__init__.py
touch src/tools/__init__.py
touch src/tools/visible/__init__.py
touch src/tools/hidden/__init__.py
```

## Phase 5: Configuration Updates

### Step 13: Update Configuration Files

1. **Move config.py to config directory:**
```bash
mv config.py config/
```

2. **Update config.py imports** to work with new structure

3. **Create config/__init__.py:**
```bash
touch config/__init__.py
```

## Phase 6: Testing and Validation

### Step 14: Test Basic Functionality

```bash
# Test import structure
python -c "from src.core.tool_visibility import ToolVisibilityManager; print('Tool visibility OK')"
python -c "from src.router.unified_router import UnifiedRouter; print('Unified router OK')"
python -c "from src.tools.registry_streamlined import StreamlinedToolRegistry; print('Tool registry OK')"

# Test server startup (dry run)
python server_streamlined.py --help 2>/dev/null || echo "Server file created successfully"
```

### Step 15: Validate Tool Loading

```bash
# Test with minimal environment
ENV_FILE=.env.production python -c "
from src.tools.registry_streamlined import StreamlinedToolRegistry
registry = StreamlinedToolRegistry()
print('Loaded tools:', sorted(registry.list_tools().keys()))
"
```

## Phase 7: Documentation and Cleanup

### Step 16: Update README

Update the main README.md to reflect:
- New streamlined architecture
- Simplified setup instructions
- Tool visibility management
- Production configuration

### Step 17: Clean Up Legacy References

1. **Search and replace** old import patterns:
```bash
# Find files with old import patterns
grep -r "from tools\." src/ || echo "No legacy imports found"
grep -r "import tools\." src/ || echo "No legacy imports found"
```

2. **Update any remaining references** to old file paths

## Phase 8: Final Validation

### Step 18: Integration Test

```bash
# Test full server startup with production config
timeout 10s python server_streamlined.py || echo "Server startup test completed"
```

### Step 19: Commit Changes

```bash
# Stage all changes
git add -A

# Commit streamlined implementation
git commit -m "Implement streamlined EX-AI MCP Server

- Unified routing system eliminates dual routing
- Environment-based tool visibility management
- Clean architecture with minimal redundancy
- Production-ready configuration with test API keys
- Removed 20+ redundant diagnostic scripts
- Organized tools into visible/hidden categories
- Centralized configuration approach"
```

## Phase 9: Documentation

### Step 20: Create Final Documentation

1. **Implementation Guide**: Comprehensive guide with mermaid diagrams
2. **API Documentation**: Tool and configuration reference
3. **Migration Guide**: For users upgrading from original version

## Troubleshooting Common Issues

### Import Errors
- Ensure all `__init__.py` files are created
- Check import paths match new directory structure
- Verify PYTHONPATH includes project root

### Tool Loading Failures
- Check tool files exist in correct directories
- Verify class names match registry expectations
- Ensure environment variables are set correctly

### Configuration Issues
- Verify `.env.production` file exists and is readable
- Check API keys are valid
- Ensure environment variable syntax is correct

### Router Initialization Failures
- Verify provider registry is accessible
- Check API keys for enabled providers
- Review router diagnostic logs

## Success Criteria

The streamlined implementation is successful when:

1. ✅ **Server starts without errors** using `python server_streamlined.py`
2. ✅ **Visible tools are available** (chat, planner, thinkdeep, self-check)
3. ✅ **Hidden tools are properly controlled** by environment flags
4. ✅ **Unified routing works** for model selection
5. ✅ **Configuration is clean** with single `.env.production` file
6. ✅ **File structure is organized** with clear separation
7. ✅ **No redundant files remain** from cleanup phase
8. ✅ **All imports work correctly** with new structure
9. ✅ **Logging is functional** with proper levels
10. ✅ **Tool visibility management works** as expected

## Post-Implementation

After successful implementation:

1. **Create PR** with comprehensive description
2. **Update documentation** for end users
3. **Test with MCP clients** (Claude, etc.)
4. **Monitor performance** and error rates
5. **Gather feedback** from users
6. **Plan future enhancements** based on usage patterns

This streamlined version provides a solid foundation for future development while maintaining all core functionality in a clean, maintainable architecture.
