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

    # Precommit and Challenge utilities
    "precommit": ("tools.workflows.precommit", "PrecommitTool"),
    "challenge": ("tools.challenge", "ChallengeTool"),
    # Orchestrators (aliases map to autopilot)
    # Kimi utilities
    "kimi_upload_and_extract": ("tools.providers.kimi.kimi_upload", "KimiUploadAndExtractTool"),
    "kimi_multi_file_chat": ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool"),
    "kimi_intent_analysis": ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool"),
    "kimi_capture_headers": ("tools.providers.kimi.kimi_capture_headers", "KimiCaptureHeadersTool"),
    # GLM utilities
    "kimi_chat_with_tools": ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool"),
    "glm_upload_file": ("tools.providers.glm.glm_files", "GLMUploadFileTool"),
    "glm_web_search": ("tools.providers.glm.glm_web_search", "GLMWebSearchTool"),
    "glm_payload_preview": ("tools.providers.glm.glm_payload_preview", "GLMPayloadPreviewTool"),
    # De-scoped: glm_multi_file_chat
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
# NOTE: During development, all tools are set to 'core' or 'advanced' for full accessibility.
# In production, consider setting diagnostic tools to 'hidden' to reduce MCP client clutter.
TOOL_VISIBILITY = {
    # Core verbs
    "status": "core",
    "chat": "core",
    "planner": "core",
    "thinkdeep": "core",
    "analyze": "core",
    "codereview": "core",
    "refactor": "core",
    "testgen": "core",
    "debug": "core",
    # Auxiliary (advanced)
    "provider_capabilities": "advanced",  # Diagnostics - useful during development
    "listmodels": "advanced",              # Diagnostics - useful during development
    "activity": "advanced",
    "version": "advanced",                 # Diagnostics - useful during development
    "kimi_upload_and_extract": "advanced", # Backend pathway - useful during development
    "kimi_chat_with_tools": "advanced",
    "kimi_capture_headers": "advanced",    # Diagnostics - useful during development
    "glm_upload_file": "advanced",         # Backend pathway - useful during development
    "glm_payload_preview": "advanced",     # Diagnostics - useful during development
    "consensus": "advanced",
    "docgen": "advanced",
    "secaudit": "advanced",
    "tracer": "advanced",
    "precommit": "advanced",
    # Internal utilities
    "toolcall_log_tail": "advanced",       # Diagnostics - useful during development
    "health": "advanced",                  # Diagnostics - useful during development
}


DEFAULT_LEAN_TOOLS = {
    "chat",
    "analyze",
    "planner",
    "thinkdeep",
    "version",
    "listmodels",
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
            active = lean_overrides or set(DEFAULT_LEAN_TOOLS)
        else:
            active = set(TOOL_MAP.keys())

        # Ensure utilities are always on unless STRICT_LEAN is enabled
        if os.getenv("STRICT_LEAN", "false").strip().lower() != "true":
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

