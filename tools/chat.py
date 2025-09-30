"""
Chat tool - General development chat and collaborative thinking

This tool provides a conversational interface for general development assistance,
brainstorming, problem-solving, and collaborative thinking. It supports file context,
images, and conversation continuation for seamless multi-turn interactions.
"""

from typing import TYPE_CHECKING, Any, Optional

from pydantic import Field

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from config import TEMPERATURE_BALANCED
from systemprompts import CHAT_PROMPT
from tools.shared.base_models import ToolRequest

from .simple.base import SimpleTool

# Field descriptions matching the original Chat tool exactly
CHAT_FIELD_DESCRIPTIONS = {
    "prompt": (
        "You MUST provide a thorough, expressive question or share an idea with as much context as possible. "
        "IMPORTANT: When referring to code, use the files parameter to pass relevant files and only use the prompt to refer to "
        "function / method names or very small code snippets if absolutely necessary to explain the issue. Do NOT "
        "pass large code snippets in the prompt as this is exclusively reserved for descriptive text only. "
        "Remember: you're talking to an assistant who has deep expertise and can provide nuanced insights. Include your "
        "current thinking, specific challenges, background context, what you've already tried, and what "
        "kind of response would be most helpful. The more context and detail you provide, the more "
        "valuable and targeted the response will be."
    ),
    "files": "Optional files for context (must be FULL absolute paths to real files / folders - DO NOT SHORTEN)",
    "images": (
        "Optional images for visual context. Useful for UI discussions, diagrams, visual problems, "
        "error screens, or architectural mockups. (must be FULL absolute paths to real files / folders - DO NOT SHORTEN - OR these can be base64 data)"
    ),
}


class ChatRequest(ToolRequest):
    """Request model for Chat tool"""

    prompt: str = Field(..., description=CHAT_FIELD_DESCRIPTIONS["prompt"])
    files: Optional[list[str]] = Field(default_factory=list, description=CHAT_FIELD_DESCRIPTIONS["files"])
    images: Optional[list[str]] = Field(default_factory=list, description=CHAT_FIELD_DESCRIPTIONS["images"])
    continuation_id: Optional[str] = Field(default=None, description=(
        "Thread continuation ID for multi-turn conversations."
    ))
    # Optional flags propagated to providers via capability layer and env-gated streaming
    use_websearch: Optional[bool] = Field(default=True, description="Enable provider-native web browsing when available")
    stream: Optional[bool] = Field(default=None, description="Request streaming when supported; env-gated per provider")


class ChatTool(SimpleTool):
    """
    General development chat and collaborative thinking tool using SimpleTool architecture.

    This tool provides identical functionality to the original Chat tool but uses the new
    SimpleTool architecture for cleaner code organization and better maintainability.

    Migration note: This tool is designed to be a drop-in replacement for the original
    Chat tool with 100% behavioral compatibility.
    """

    def get_name(self) -> str:
        return "chat"

    def get_description(self) -> str:
        return (
            "GENERAL CHAT & COLLABORATIVE THINKING - Use the AI model as your thinking partner! "
            "Perfect for: bouncing ideas during your own analysis, getting second opinions on your plans, "
            "collaborative brainstorming, validating your checklists and approaches, exploring alternatives. "
            "Also great for: explanations, comparisons, general development questions. "
            "Use this when you want to ask questions, brainstorm ideas, get opinions, discuss topics, "
            "share your thinking, or need explanations about concepts and approaches. "
            "Note: If you're not currently using a top-tier model such as Opus 4 or above, these tools can "
            "provide enhanced capabilities."
        )

    def get_system_prompt(self) -> str:
        return CHAT_PROMPT

    def get_default_temperature(self) -> float:
        return TEMPERATURE_BALANCED

    def get_model_category(self) -> "ToolModelCategory":
        """Chat prioritizes fast responses and cost efficiency"""
        from tools.models import ToolModelCategory

        return ToolModelCategory.FAST_RESPONSE

    def get_request_model(self):
        """Return the Chat-specific request model"""
        return ChatRequest

    # === Schema Generation ===
    # For maximum compatibility, we override get_input_schema() to match the original Chat tool exactly

    def get_input_schema(self) -> dict[str, Any]:
        """
        Generate input schema matching the original Chat tool exactly, with Phase 5 flags.
        Enforces draft-07 compliance and additionalProperties:false.
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": CHAT_FIELD_DESCRIPTIONS["prompt"]},
                "files": {"type": "array", "items": {"type": "string"}, "description": CHAT_FIELD_DESCRIPTIONS["files"]},
                "images": {"type": "array", "items": {"type": "string"}, "description": CHAT_FIELD_DESCRIPTIONS["images"]},
                "model": self.get_model_field_schema(),
                "temperature": {"type": "number", "description": "Response creativity (0-1, default 0.5)", "minimum": 0, "maximum": 1},
                "thinking_mode": {"type": "string", "enum": ["minimal", "low", "medium", "high", "max"], "description": "Thinking depth selector"},
                "use_websearch": {"type": "boolean", "description": "Enable provider-native web browsing", "default": True},
                "stream": {"type": "boolean", "description": "Request streaming when supported; env-gated per provider", "default": False},
                "continuation_id": {"type": "string", "description": "Thread continuation ID for multi-turn conversations."},
            },
            "additionalProperties": False,
            "required": ["prompt"] + (["model"] if self.is_effective_auto_mode() else []),
        }
        return schema

    # === Tool-specific field definitions (alternative approach for reference) ===
    # These aren't used since we override get_input_schema(), but they show how
    # the tool could be implemented using the automatic SimpleTool schema building

    def get_tool_fields(self) -> dict[str, dict[str, Any]]:
        """
        Tool-specific field definitions for ChatSimple.

        Note: This method isn't used since we override get_input_schema() for
        exact compatibility, but it demonstrates how ChatSimple could be
        implemented using automatic schema building.
        """
        return {
            "prompt": {
                "type": "string",
                "description": CHAT_FIELD_DESCRIPTIONS["prompt"],
            },
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": CHAT_FIELD_DESCRIPTIONS["files"],
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "description": CHAT_FIELD_DESCRIPTIONS["images"],
            },
        }

    def get_required_fields(self) -> list[str]:
        """Required fields for ChatSimple tool"""
        return ["prompt"]

    # === Hook Method Implementations ===

    async def prepare_prompt(self, request: ChatRequest) -> str:
        """
        Prepare the chat prompt with optional context files + conversation context
        when continuation_id is provided.
        """
        # Optional security enforcement per Cleanup/Upgrade prompts
        try:
            from config import SECURE_INPUTS_ENFORCED
            if SECURE_INPUTS_ENFORCED:
                from pathlib import Path
                from src.core.validation.secure_input_validator import SecureInputValidator

                repo_root = Path(__file__).resolve().parents[1]
                v = SecureInputValidator(repo_root=str(repo_root))

                # Normalize/validate files inside repo
                if request.files:
                    normalized_files: list[str] = []
                    for f in request.files:
                        p = v.normalize_and_check(f)
                        normalized_files.append(str(p))
                    request.files = normalized_files

                # Validate images count and normalize path-based images
                imgs = request.images or []
                # Use size placeholders (0) since Chat may receive data URLs; count enforcement still applies
                v.validate_images([0] * len(imgs), max_images=10)
                normalized_images: list[str] = []
                for img in imgs:
                    if isinstance(img, str) and (img.startswith("data:") or "base64," in img):
                        normalized_images.append(img)
                    else:
                        p = v.normalize_and_check(img)
                        normalized_images.append(str(p))
                request.images = normalized_images
        except Exception as e:
            # Surface a clear validation error; callers will see this as tool error
            raise ValueError(f"[chat:security] {e}")

        # Build conversation preface
        preface = ""
        try:
            if request.continuation_id:
                from src.conversation.memory_policy import assemble_context_block
                from src.conversation.cache_store import get_cache_store
                preface = assemble_context_block(request.continuation_id, max_turns=6)
                # Attach cache context header if available
                cache = get_cache_store().load(request.continuation_id)
                if cache:
                    cache_bits = []
                    for k in ("session_id", "call_key", "token"):
                        v = cache.get(k)
                        if v:
                            cache_bits.append(f"{k}={v}")
                    if cache_bits:
                        preface = "[Context cache: " + ", ".join(cache_bits) + "]\n" + preface
                # Record the user turn immediately
                from src.conversation.history_store import get_history_store
                get_history_store().record_turn(request.continuation_id, "user", request.prompt)
        except Exception:
            pass

        # Phase 5: propagate stream flag by temporarily setting GLM_STREAM_ENABLED for duration of call
        try:
            import os as _os
            self._prev_stream_env = _os.getenv("GLM_STREAM_ENABLED", None)
            if getattr(request, "stream", None) is not None:
                _os.environ["GLM_STREAM_ENABLED"] = "true" if bool(request.stream) else "false"
        except Exception:
            self._prev_stream_env = None

        base_prompt = self.prepare_chat_style_prompt(request)
        if preface:
            return f"{preface}\nCurrent request:\n{base_prompt}"
        return base_prompt

    def format_response(self, response: str, request: ChatRequest, model_info: Optional[dict] = None) -> str:
        """
        Format the chat response and persist assistant turn when continuation_id is provided.
        Also captures provider cache tokens from model_info for context reuse.
        """
        try:
            if getattr(request, "continuation_id", None):
                # Persist assistant turn
                from src.conversation.history_store import get_history_store
                get_history_store().record_turn(request.continuation_id, "assistant", str(response))
                # Capture cache tokens if present in model_info
                try:
                    if model_info and isinstance(model_info, dict):
                        cache = model_info.get("cache") or {}
                        if isinstance(cache, dict) and any(k in cache for k in ("session_id", "call_key", "token")):
                            from src.conversation.cache_store import get_cache_store
                            get_cache_store().record(request.continuation_id, {
                                k: cache.get(k) for k in ("session_id", "call_key", "token") if cache.get(k)
                            })
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            # Restore GLM_STREAM_ENABLED after call
            try:
                import os as _os
                if hasattr(self, "_prev_stream_env"):
                    prev = getattr(self, "_prev_stream_env")
                    if prev is None:
                        _os.environ.pop("GLM_STREAM_ENABLED", None)
                    else:
                        _os.environ["GLM_STREAM_ENABLED"] = str(prev)
            except Exception:
                pass
        return (
            f"{response}\n\n---\n\nAGENT'S TURN: Evaluate this perspective alongside your analysis to "
            "form a comprehensive solution and continue with the user's request and task at hand."
        )

    def get_websearch_guidance(self) -> str:
        """
        Return Chat tool-style web search guidance.
        """
        return self.get_chat_style_websearch_guidance()
