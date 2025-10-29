"""Lean Tool Registry for Zen MCP.

Build the tool set once at server startup, honoring env flags:
- LEAN_MODE=true|false (default false)
- LEAN_TOOLS=comma,list (when LEAN_MODE=true, overrides default lean set)
- DISABLED_TOOLS=comma,list (always excluded)

Always expose light utility tools (listmodels, version) for diagnostics.
Provide helpful error if a disabled tool is invoked.
"""
from __future__ import annotations

import os
from typing import Any, Dict

# Map tool names to import paths (module, class)
TOOL_MAP: Dict[str, tuple[str, str]] = {
    # Core
    "chat": ("tools.chat", "ChatTool"),
    "analyze": ("tools.workflows.analyze", "AnalyzeTool"),
    "debug": ("tools.workflows.debug", "DebugIssueTool"),
    "codereview": ("tools.workflows.codereview", "CodeReviewTool"),
    "refactor": ("tools.workflows.refactor", "RefactorTool"),
    "secaudit": ("tools.workflows.secaudit", "SecauditTool"),
    "planner": ("tools.workflows.planner", "PlannerTool"),
    "tracer": ("tools.workflows.tracer", "TracerTool"),
    "testgen": ("tools.workflows.testgen", "TestGenTool"),
    "consensus": ("tools.workflows.consensus", "ConsensusTool"),
    "thinkdeep": ("tools.workflows.thinkdeep", "ThinkDeepTool"),
    "docgen": ("tools.workflows.docgen", "DocgenTool"),
    # Utilities (always on)
    "version": ("tools.capabilities.version", "VersionTool"),
    "listmodels": ("tools.capabilities.listmodels", "ListModelsTool"),
    "self-check": ("tools.selfcheck", "SelfCheckTool"),
    # Web tools removed: internet access disabled in production build

    # Testing utilities
    "test_echo": ("tools.simple.test_echo", "TestEchoTool"),

    # Precommit and Challenge utilities
    "precommit": ("tools.workflows.precommit", "PrecommitTool"),
    "challenge": ("tools.challenge", "ChallengeTool"),
    # Orchestrators (aliases map to autopilot)
    # Smart File Query (unified interface)
    "smart_file_query": ("tools.smart_file_query", "SmartFileQueryTool"),
    # Smart File Download (unified download interface)
    "smart_file_download": ("tools.smart_file_download", "SmartFileDownloadTool"),
    # Kimi utilities
    "kimi_upload_files": ("tools.providers.kimi.kimi_files", "KimiUploadFilesTool"),
    "kimi_chat_with_files": ("tools.providers.kimi.kimi_files", "KimiChatWithFilesTool"),
    "kimi_manage_files": ("tools.providers.kimi.kimi_files", "KimiManageFilesTool"),
    "kimi_intent_analysis": ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool"),
    "kimi_capture_headers": ("tools.providers.kimi.kimi_capture_headers", "KimiCaptureHeadersTool"),
    # GLM utilities
    "kimi_chat_with_tools": ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool"),
    "glm_upload_file": ("tools.providers.glm.glm_files", "GLMUploadFileTool"),
    "glm_multi_file_chat": ("tools.providers.glm.glm_files", "GLMMultiFileChatTool"),  # Added 2025-10-27
    "glm_web_search": ("tools.providers.glm.glm_web_search", "GLMWebSearchTool"),
    "glm_payload_preview": ("tools.providers.glm.glm_payload_preview", "GLMPayloadPreviewTool"),
    # Diagnostics
    "provider_capabilities": ("tools.capabilities.provider_capabilities", "ProviderCapabilitiesTool"),
    # Observability helpers
    "toolcall_log_tail": ("tools.diagnostics.toolcall_log_tail", "ToolcallLogTail"),
    "activity": ("tools.activity", "ActivityTool"),
    # Health
    "health": ("tools.diagnostics.health", "HealthTool"),
    # Status alias (friendly summary)
    "status": ("tools.diagnostics.status", "StatusTool"),
    # Autopilot orchestrator (opt-in)
    # Browse orchestrator (alias to autopilot)
    # Streaming demo (utility)

}
# Visibility map for tools: 'core' | 'advanced' | 'hidden'
# 4-TIER TOOL VISIBILITY SYSTEM
# Designed to prevent overwhelming agents while maintaining full functionality
#
# ESSENTIAL (3 tools): Absolute must-haves for basic operation
# CORE (7 tools): Frequently used for common workflows (80% of use cases)
# ADVANCED (7 tools): Specialized tools for complex scenarios
# HIDDEN (16 tools): Internal/diagnostic/deprecated tools
#
# Progressive disclosure: Agents see Essential + Core (10 tools) by default
# Advanced tools revealed based on context or explicit request
# Hidden tools completely invisible to agents
TOOL_VISIBILITY = {
    # ========== ESSENTIAL TIER (3 tools) ==========
    # Always visible - basic operations every agent needs
    "status": "essential",      # System status checking
    "chat": "essential",        # Basic communication interface
    "planner": "essential",     # Task planning and coordination

    # ========== CORE TIER (8 tools) ==========
    # Default visibility - 80% of use cases covered here
    "analyze": "core",          # Strategic architectural assessment
    "codereview": "core",       # Systematic code review
    "debug": "core",            # Root cause investigation
    "refactor": "core",         # Code improvement and modernization
    "testgen": "core",          # Test case generation
    "thinkdeep": "core",        # Extended hypothesis-driven reasoning
    "smart_file_query": "core", # ⭐ UNIFIED file upload/query interface (replaces 6+ tools)
    "smart_file_download": "core", # ⭐ UNIFIED file download interface with caching

    # ========== ADVANCED TIER (7 tools) ==========
    # Visible on request - specialized scenarios
    "consensus": "advanced",           # Multi-agent coordination
    "docgen": "advanced",              # Documentation generation
    "secaudit": "advanced",            # Security auditing
    "tracer": "advanced",              # Code execution tracing
    "precommit": "advanced",           # Pre-commit hook management
    "kimi_chat_with_tools": "advanced", # Advanced Kimi capabilities
    "glm_payload_preview": "advanced",  # GLM payload inspection

    # ========== HIDDEN TIER (16 tools) ==========
    # System/diagnostic only - invisible to agents

    # Diagnostic tools
    "provider_capabilities": "hidden",  # System diagnostics
    "listmodels": "hidden",             # Model listing
    "activity": "hidden",               # Activity monitoring
    "version": "hidden",                # Version information
    "health": "hidden",                 # Health checks
    "toolcall_log_tail": "hidden",      # Tool call logging
    "test_echo": "hidden",              # Load testing
    "kimi_capture_headers": "hidden",   # Header inspection
    "kimi_intent_analysis": "hidden",   # Intent classification

    # ⚠️ DEPRECATED - Use smart_file_query instead
    "kimi_upload_files": "hidden",      # DEPRECATED: Use smart_file_query
    "kimi_chat_with_files": "hidden",   # DEPRECATED: Use smart_file_query
    "kimi_manage_files": "hidden",      # DEPRECATED: Use smart_file_query
    "glm_upload_file": "hidden",        # DEPRECATED: Use smart_file_query
    "glm_multi_file_chat": "hidden",    # DEPRECATED: Use smart_file_query
    "glm_web_search": "hidden",         # Internal utility
    "kimi_web_search": "hidden",        # Internal utility
}


# Derive DEFAULT_LEAN_TOOLS dynamically from TOOL_VISIBILITY
# Includes ESSENTIAL + CORE tools (10 total) for optimal agent experience
DEFAULT_LEAN_TOOLS = {
    name for name, vis in TOOL_VISIBILITY.items()
    if vis in ("essential", "core")
}


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

    def _load_tool(self, name: str) -> None:
        module_path, class_name = TOOL_MAP[name]
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            self._tools[name] = cls()
        except Exception as e:
            self._errors[name] = str(e)

    def build_tools(self) -> None:
        disabled = {t.strip().lower() for t in os.getenv("DISABLED_TOOLS", "").split(",") if t.strip()}
        lean_mode = os.getenv("LEAN_MODE", "false").strip().lower() == "true"

        if lean_mode:
            lean_overrides = {t.strip().lower() for t in os.getenv("LEAN_TOOLS", "").split(",") if t.strip()}
            if lean_overrides:
                active = lean_overrides
            else:
                # Use TOOL_VISIBILITY to determine active tools in lean mode
                # Only include ESSENTIAL + CORE tiers (10 tools total)
                active = {name for name, vis in TOOL_VISIBILITY.items()
                         if vis in ("essential", "core")}
        else:
            active = set(TOOL_MAP.keys())

        # Only add utilities if NOT in lean mode AND not in strict lean mode
        # This prevents version/listmodels from being added in LEAN_MODE
        if (os.getenv("STRICT_LEAN", "false").strip().lower() != "true" and
            not lean_mode):
            active.update({"version", "listmodels"})

        # Remove disabled
        active = {t for t in active if t not in disabled}

        # Hide diagnostics-only tools unless explicitly enabled
        if os.getenv("DIAGNOSTICS", "false").strip().lower() != "true":
            active.discard("self-check")

        # Web tools removed; no gating needed
        for name in sorted(active):
            self._load_tool(name)

    def get_tool(self, name: str) -> Any:
        if name in self._tools:
            return self._tools[name]
        if name in self._errors:
            raise RuntimeError(f"Tool '{name}' failed to load: {self._errors[name]}")
        raise KeyError(
            f"Tool '{name}' is not registered. It may be disabled (LEAN_MODE/DISABLED_TOOLS) or unavailable."
        )

    def list_tools(self) -> Dict[str, Any]:
        return dict(self._tools)

    def list_descriptors(self) -> Dict[str, Any]:
        """Return machine-readable descriptors for all loaded tools (MVP)."""
        descs: Dict[str, Any] = {}
        for name, tool in self._tools.items():
            try:
                # Each tool provides a default get_descriptor()
                descs[name] = tool.get_descriptor()
            except Exception as e:
                descs[name] = {"error": f"Failed to get descriptor: {e}"}
        return descs

