"""
Base models for EXAI MCP tools.

This module contains the shared Pydantic models used across all tools,
extracted to avoid circular imports and promote code reuse.

Key Models:
- ToolRequest: Base request model for all tools
- WorkflowRequest: Extended request model for workflow-based tools
- ConsolidatedFindings: Model for tracking workflow progress
"""

import logging
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# Shared field descriptions to avoid duplication
# Last Updated: 2025-10-25 - Enhanced with decision matrices and capability hints
COMMON_FIELD_DESCRIPTIONS = {
    "model": (
        "Model to use. Native models: 'auto', 'kimi-k2-0905-preview', 'kimi-k2-0711-preview', "
        "'moonshot-v1-8k', 'moonshot-v1-32k', 'kimi-k2-turbo-preview', 'moonshot-v1-128k', "
        "'moonshot-v1-8k-vision-preview', 'moonshot-v1-32k-vision-preview', 'moonshot-v1-128k-vision-preview', "
        "'kimi-latest', 'kimi-latest-8k', 'kimi-latest-32k', 'kimi-latest-128k', 'kimi-thinking-preview', "
        "'glm-4.6', 'glm-4.5-flash', 'glm-4.5', 'glm-4.5-air', 'glm-4.5v'. "
        "Use 'auto' to let the server select the best model. Defaults to 'glm-4.5-flash' if not specified."
    ),
    "temperature": (
        "Temperature for response (0.0 to 1.0). Lower values are more focused and deterministic, "
        "higher values are more creative. Tool-specific defaults apply if not specified."
    ),
    "thinking_mode": (
        "Thinking depth: minimal (0.5% of model max), low (8%), medium (33%), high (67%), "
        "max (100% of model max). Higher modes enable deeper reasoning at the cost of speed."
    ),
    "use_websearch": (
        "Enable web search for documentation, best practices, and current information. "
        "When enabled, the manager/server can perform provider-native web searches and share results back "
        "during conversations. Particularly useful for: brainstorming sessions, architectural design "
        "discussions, exploring industry best practices, working with specific frameworks/technologies, "
        "researching solutions to complex problems, or when current documentation and community insights "
        "would enhance the analysis."
    ),
    "continuation_id": (
        "Thread continuation ID for multi-turn conversations. When provided, the complete conversation "
        "history is automatically embedded as context. Your response should build upon this history "
        "without repeating previous analysis or instructions. Focus on providing only new insights, "
        "additional findings, or answers to follow-up questions. Can be used across different tools.\n\n"
        "🔄 LIFECYCLE MANAGEMENT:\n"
        "- Create new ID when starting a fresh conversation or topic\n"
        "- Reuse existing ID when continuing the same conversation across tools\n"
        "- The system automatically tracks conversation state and context\n"
        "- IDs are persistent across tool calls and can be shared between compatible tools"
    ),
    "images": (
        "Optional image(s) for visual context. Accepts absolute file paths or base64 data URLs. "
        "Only provide when user explicitly mentions images. When including images, please describe "
        "what you believe each image contains to aid with contextual understanding. Useful for UI "
        "discussions, diagrams, visual problems, error screens, architecture mockups, and visual analysis tasks."
    ),
    "files": (
        "Optional files for context - EMBEDS CONTENT AS TEXT in prompt (not uploaded to platform). "
        "Use for small files (<5KB). For large files or persistent reference, use kimi_upload_files tool instead. "
        "(must be FULL absolute paths to real files / folders - DO NOT SHORTEN)\n\n"
        "🔒 DEDUPLICATION: Files are automatically deduplicated using SHA256 hashes to prevent redundant uploads.\n\n"
        "📋 DECISION MATRIX:\n"
        "- <5KB, single-use: Use 'files' parameter (embeds as text)\n"
        "- >5KB or multi-turn: Use kimi_upload_files + kimi_chat_with_files (70-80% token savings)\n"
        "- Multiple large files: Upload once, query many times\n\n"
        "⚠️ Files >5KB will trigger automatic warnings suggesting kimi_upload_files workflow."
    ),
}

# Workflow-specific field descriptions
WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Current work step content and findings from your overall work.\n\n"
        "🔍 'YOU INVESTIGATE FIRST' PATTERN:\n"
        "- ALWAYS investigate and analyze before asking for user input\n"
        "- Provide your findings, analysis, and recommendations first\n"
        "- Then ask specific, targeted questions if needed\n"
        "- Never start with 'I need more information' - investigate what's available first\n\n"
        "📝 WHAT TO INCLUDE:\n"
        "- What you investigated in this step\n"
        "- Key findings and evidence discovered\n"
        "- Analysis of what the findings mean\n"
        "- Your current understanding and any remaining questions\n"
        "- Next steps you plan to take (if continuing)"
    ),
    "step_number": "Current step number in the work sequence (starts at 1)",
    "total_steps": "Estimated total steps needed to complete the work",
    "next_step_required": "Whether another work step is needed after this one",
    "findings": (
        "Important findings, evidence and insights discovered in this step of the work.\n\n"
        "📋 WHAT TO DOCUMENT:\n"
        "- Specific evidence discovered (code patterns, error messages, test results)\n"
        "- Key insights and observations\n"
        "- Connections between different pieces of evidence\n"
        "- Patterns or anomalies identified\n"
        "- Root causes or contributing factors\n"
        "- Impact assessment of findings\n\n"
        "💡 EXAMPLES:\n"
        "- 'Found null pointer exception in auth_service.py line 42 when user token expires'\n"
        "- 'Database query timeout occurs only with datasets >10MB, indicating performance bottleneck'\n"
        "- 'Test suite passes in isolation but fails when run with integration tests, suggesting state leakage'"
    ),
    "files_checked": "List of files examined during this work step",
    "relevant_files": "Files identified as relevant to the issue/goal",
    "relevant_context": "Methods/functions identified as involved in the issue",
    "issues_found": "Issues identified with severity levels during work",
    "confidence": (
        "Your confidence level in the current findings and analysis. This enables agentic early termination when goals are achieved.\n\n"
        "Levels (progress naturally as you investigate):\n"
        "• exploring - Just starting, forming initial hypotheses\n"
        "• low - Early investigation, limited evidence gathered\n"
        "• medium - Some solid evidence, partial understanding (DEFAULT for ongoing work)\n"
        "• high - Strong evidence, clear understanding, most questions answered\n"
        "• very_high - Comprehensive understanding, all major questions answered, ready to conclude\n"
        "• almost_certain - Near complete confidence, minimal uncertainty remains\n"
        "• certain - Complete confidence, analysis is thorough and conclusive\n\n"
        "💡 PROGRESSION GUIDANCE:\n"
        "- Start at 'exploring' or 'low' for new investigations\n"
        "- Progress to 'medium' once you have solid evidence\n"
        "- Use 'high' or 'very_high' when you have clear answers to most questions\n"
        "- Use 'certain' only when analysis is comprehensive and conclusive\n\n"
        "🚀 EFFICIENCY TIP: Use higher confidence when appropriate to enable early termination. "
        "Don't be overly cautious - if you're confident, say so!"
    ),
    "hypothesis": "Current theory about the issue/goal based on work",
    "backtrack_from_step": "Step number to backtrack from if work needs revision",
    "use_assistant_model": (
        "Whether to use assistant model for expert analysis after completing the workflow steps. "
        "Set to False to skip expert analysis and rely solely on the tool's own investigation. "
        "Defaults to True for comprehensive validation."
    ),
}


class ToolRequest(BaseModel):
    """
    Base request model for all EXAI MCP tools.

    This model defines common fields that all tools accept, including
    model selection, temperature control, and conversation threading.
    Tool-specific request models should inherit from this class.
    """

    # Model configuration
    model: Optional[str] = Field(None, description=COMMON_FIELD_DESCRIPTIONS["model"])
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description=COMMON_FIELD_DESCRIPTIONS["temperature"])
    thinking_mode: Optional[Literal["minimal", "low", "medium", "high", "max"]] = Field(
        None, description=COMMON_FIELD_DESCRIPTIONS["thinking_mode"]
    )

    # Features
    use_websearch: Optional[bool] = Field(True, description=COMMON_FIELD_DESCRIPTIONS["use_websearch"])

    # Conversation support
    continuation_id: Optional[str] = Field(None, description=COMMON_FIELD_DESCRIPTIONS["continuation_id"])

    # Visual context
    images: Optional[list[str]] = Field(None, description=COMMON_FIELD_DESCRIPTIONS["images"])


class BaseWorkflowRequest(ToolRequest):
    """
    Minimal base request model for workflow tools.

    This provides only the essential fields that ALL workflow tools need,
    allowing for maximum flexibility in tool-specific implementations.
    """

    # Core workflow fields that ALL workflow tools need
    step: str = Field(..., description=WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., ge=1, description=WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., ge=1, description=WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])


class WorkflowRequest(BaseWorkflowRequest):
    """
    Extended request model for workflow-based tools.

    This model extends ToolRequest with fields specific to the workflow
    pattern, where tools perform multi-step work with forced pauses between steps.

    Used by: debug, precommit, codereview, refactor, thinkdeep, analyze
    """

    # Note: step, step_number, total_steps, next_step_required inherited from BaseWorkflowRequest
    # No need to redefine them here

    # Work tracking fields
    findings: str = Field(..., max_length=50000, description=WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(default_factory=list, max_length=1000, description=WORKFLOW_FIELD_DESCRIPTIONS["files_checked"])
    relevant_files: list[str] = Field(default_factory=list, max_length=1000, description=WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"])
    relevant_context: list[str] = Field(
        default_factory=list, max_length=1000, description=WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )
    issues_found: list[dict] = Field(default_factory=list, max_length=1000, description=WORKFLOW_FIELD_DESCRIPTIONS["issues_found"])
    confidence: Literal["exploring", "low", "medium", "high", "very_high", "almost_certain", "certain"] = Field(
        "low", description=WORKFLOW_FIELD_DESCRIPTIONS["confidence"]
    )

    # Optional workflow fields
    hypothesis: Optional[str] = Field(None, max_length=10000, description=WORKFLOW_FIELD_DESCRIPTIONS["hypothesis"])
    backtrack_from_step: Optional[int] = Field(
        None, ge=1, description=WORKFLOW_FIELD_DESCRIPTIONS["backtrack_from_step"]
    )
    # CRITICAL FIX: Default to None so env var DEFAULT_USE_ASSISTANT_MODEL is respected
    use_assistant_model: Optional[bool] = Field(None, description=WORKFLOW_FIELD_DESCRIPTIONS["use_assistant_model"])

    @field_validator("files_checked", "relevant_files", "relevant_context", mode="before")
    @classmethod
    def convert_string_to_list(cls, v):
        """Convert string inputs to empty lists to handle malformed inputs gracefully."""
        if isinstance(v, str):
            logger.warning(f"Field received string '{v}' instead of list, converting to empty list")
            return []
        return v

    @field_validator("step_number")
    @classmethod
    def validate_step_number(cls, v, info):
        """Validate that step_number doesn't exceed total_steps."""
        if info.data.get("total_steps") and v > info.data["total_steps"]:
            raise ValueError(f"step_number ({v}) cannot exceed total_steps ({info.data['total_steps']})")
        return v

    @field_validator("backtrack_from_step")
    @classmethod
    def validate_backtrack(cls, v, info):
        """Validate that backtrack_from_step is less than current step_number."""
        if v is not None and info.data.get("step_number") and v >= info.data["step_number"]:
            raise ValueError(f"backtrack_from_step ({v}) must be less than current step_number ({info.data['step_number']})")
        return v

    @field_validator("step", "findings", "hypothesis")
    @classmethod
    def validate_non_empty_strings(cls, v):
        """Validate that string fields contain actual content, not just whitespace."""
        if v is not None and isinstance(v, str) and not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")
        return v


class ConsolidatedFindings(BaseModel):
    """
    Model for tracking consolidated findings across workflow steps.

    This model accumulates findings, files, methods, and issues
    discovered during multi-step work. It's used by
    BaseWorkflowMixin to track progress across workflow steps.
    """

    files_checked: set[str] = Field(default_factory=set, description="All files examined across all steps")
    relevant_files: set[str] = Field(
        default_factory=set,
        description="A subset of files_checked that have been identified as relevant for the work at hand",
    )
    relevant_context: set[str] = Field(
        default_factory=set, description="All methods/functions identified during overall work being performed"
    )
    findings: list[str] = Field(default_factory=list, description="Chronological list of findings from each work step")
    hypotheses: list[dict] = Field(default_factory=list, description="Evolution of hypotheses across work steps")
    issues_found: list[dict] = Field(default_factory=list, description="All issues found with severity levels")
    images: list[str] = Field(default_factory=list, description="Images collected during overall work")
    confidence: Literal["exploring", "low", "medium", "high", "very_high", "almost_certain", "certain"] = Field(
        "low", description="Latest confidence level from work steps"
    )


# Tool-specific field descriptions are now declared in each tool file
# This keeps concerns separated and makes each tool self-contained
