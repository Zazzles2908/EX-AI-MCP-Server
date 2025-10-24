"""
MCP Protocol Handlers Module

This module contains the main MCP protocol handlers for tools and prompts.
These handlers implement the MCP specification for tool discovery and execution.

ARCHITECTURE NOTE (v2.0.2+):
- This module delegates to singleton registry via src/server/registry_bridge
- NEVER instantiate ToolRegistry directly - always use get_registry()
- registry_bridge.build() is idempotent and delegates to src/bootstrap/singletons
- Ensures TOOLS is SERVER_TOOLS identity check always passes
"""

import logging
import os
from typing import Any, List
from mcp.types import Tool, Prompt, TextContent, GetPromptResult, PromptMessage


logger = logging.getLogger(__name__)
# Lazy server import to avoid circular import; import inside handlers when needed
server = None  # placeholder, will be lazily imported


async def handle_list_tools() -> list[Tool]:
    """
    List all available tools with their descriptions and input schemas.

    This handler is called by MCP clients during initialization to discover
    what tools are available. Each tool provides:
    - name: Unique identifier for the tool
    - description: Detailed explanation of what the tool does
    - inputSchema: JSON Schema defining the expected parameters

    Returns:
        List of Tool objects representing all available tools
    """
    logger.debug("MCP client requested tool list")

    tools = []

    # Client-aware allow/deny filtering (generic CLIENT_* with legacy CLAUDE_* fallback for backward compatibility)
    try:
        from utils.client_info import get_client_info_from_context
        # Lazy import to avoid circular import when server.py imports this module
        try:
            import importlib
            _server = importlib.import_module("server")
        except Exception:
            _server = None
        ci = get_client_info_from_context(_server) or {}
        client_name = (ci.get("friendly_name") or ci.get("name") or "").lower()
        # Check CLIENT_* env vars first, then legacy CLAUDE_* vars for backward compatibility
        raw_allow = os.getenv("CLIENT_TOOL_ALLOWLIST", os.getenv("CLAUDE_TOOL_ALLOWLIST", ""))
        raw_deny  = os.getenv("CLIENT_TOOL_DENYLIST",  os.getenv("CLAUDE_TOOL_DENYLIST",  ""))
        allowlist = {t.strip().lower() for t in raw_allow.split(",") if t.strip()}
        denylist  = {t.strip().lower() for t in raw_deny.split(",") if t.strip()}
    except Exception:
        client_name = ""
        allowlist = set()
        denylist = set()

    # Add all registered AI-powered tools from the dynamic registry (lazy build to avoid cycles)
    from src.server.registry_bridge import get_registry as _get_reg  # type: ignore
    _reg = _get_reg()
    # Idempotent guard: build() delegates to singleton, safe to call multiple times
    _reg.build()
    for tool in _reg.list_tools().values():
        nm = tool.name.lower()
        if allowlist and nm not in allowlist:
            continue
        if denylist and nm in denylist:
            continue

        # Use enhanced schema if available, fallback to base schema for compatibility
        if hasattr(tool, 'get_enhanced_input_schema'):
            schema = tool.get_enhanced_input_schema()
        else:
            schema = tool.get_input_schema()

        tools.append(Tool(name=tool.name, description=tool.description, inputSchema=schema))

    # Log cache efficiency info
    if os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_API_KEY") != "your_openrouter_api_key_here":
        logger.debug("OpenRouter registry cache used efficiently across all tool schemas")

    logger.debug(f"Returning {len(tools)} tools to MCP client")
    return tools


# Optional module-level override for tests; monkeypatchable in pytest
_resolve_auto_model = None
# Lazy provider configuration guard for internal tool calls (e.g., audit script)
_providers_configured = False


async def handle_list_prompts() -> list[Prompt]:
    """
    List all available prompts for MCP client shortcuts.

    This handler returns prompts that enable shortcuts like /ex:thinkdeeper.
    We automatically generate prompts from all tools (1:1 mapping) plus add
    a few marketing aliases with richer templates for commonly used tools.

    Returns:
        List of Prompt objects representing all available prompts
    """
    logger.debug("MCP client requested prompt list")
    prompts = []

    # Add a prompt for each tool (lazy build to avoid cycles)
    from src.server.registry_bridge import get_registry as _get_reg  # type: ignore
    _reg = _get_reg()
    # Idempotent guard: build() delegates to singleton, safe to call multiple times
    _reg.build()
    for tool_name, tool in _reg.list_tools().items():
        prompts.append(
            Prompt(
                name=tool_name,
                description=tool.description,
                arguments=[],
            )
        )

    # Add special "continue" prompt
    prompts.append(
        Prompt(
            name="continue",
            description="Continue the previous conversation using the chat tool",
            arguments=[],
        )
    )

    logger.debug(f"Returning {len(prompts)} prompts to MCP client")
    return prompts




async def handle_get_prompt(name: str, arguments: dict[str, Any] = None) -> GetPromptResult:
    """
    Get prompt details and generate the actual prompt text.

    This handler is called when a user invokes a prompt (e.g., /ex:thinkdeeper or /ex:chat:gpt5).
    It generates the appropriate text that the MCP client will then use to call the
    underlying tool.

    Supports structured prompt names like "chat:gpt5" where:
    - "chat" is the tool name
    - "gpt5" is the model to use

    Args:
        name: The name of the prompt to execute (can include model like "chat:gpt5")
        arguments: Optional arguments for the prompt (e.g., model, thinking_mode)

    Returns:
        GetPromptResult with the prompt details and generated message

    Raises:
        ValueError: If the prompt name is unknown
    """
    logger.debug(f"MCP client requested prompt: {name} with args: {arguments}")

    # Handle special "continue" case or direct tool prompts (no rich templates)
    from src.server.registry_bridge import get_registry as _get_reg  # type: ignore
    _reg = _get_reg()
    # Idempotent guard: build() delegates to singleton, safe to call multiple times
    _reg.build()
    _tool_names = set(_reg.list_tools().keys())
    if name.lower() == "continue":
        tool_name = "chat"
        description = "Continue the previous conversation"
        tool_instruction = "Continue the conversation"
    else:
        if name not in _tool_names:
            logger.error(f"Unknown prompt requested: {name}")
            raise ValueError(f"Unknown prompt: {name}")
        tool_name = name
        description = f"Use {name} tool"
        tool_instruction = f"Use {name}"

    return GetPromptResult(
        prompt=Prompt(
            name=name,
            description=description,
            arguments=[],
        ),
        messages=[
            PromptMessage(
                role="user",
                content={"type": "text", "text": tool_instruction},
            )
        ],
    )



