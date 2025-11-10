"""
Expert Analysis Mixin for Workflow Tools

This module provides external model integration, analysis request formatting,
response consolidation, and findings aggregation for workflow tools.

Key Features:
- Expert model integration with timeout and fallback
- Analysis context preparation
- Response parsing and consolidation
- Findings aggregation across workflow steps
- Graceful degradation on provider failures
- Duplicate call prevention with caching and in-progress tracking
"""

import asyncio
import json
import logging
import time
from typing import Any, Optional, Dict, Set

from tools.shared.base_models import ConsolidatedFindings
from utils.progress import send_progress

# Import TimeoutConfig for coordinated timeout hierarchy
from config import TimeoutConfig

# Import PerformanceProfiler for bottleneck identification (EXAI recommendation 2025-10-21)
from src.utils.performance_profiler import PerformanceProfiler

logger = logging.getLogger(__name__)

# Global cache for expert validation results (shared across all tool instances)
# This prevents duplicate calls even if the tool is instantiated multiple times
# EXAI Fix #6 (2025-10-21): Added TTL and size limits for cache management
_expert_validation_cache: Dict[str, tuple[dict, float]] = {}  # (result, timestamp)
_expert_validation_in_progress: Set[str] = set()
_expert_validation_lock = asyncio.Lock()

# Cache configuration (EXAI Fix #6 - 2025-10-21)
_CACHE_TTL_SECS = 3600  # 1 hour TTL
_CACHE_MAX_SIZE = 100  # Maximum 100 cached results


class ExpertAnalysisMixin:
    """
    Mixin providing expert analysis integration for workflow tools.

    This class handles calling external models for expert analysis,
    with timeout management, fallback strategies, and graceful degradation.

    Note: This mixin expects certain methods to be provided by the parent class
    or other mixins. These are declared as abstract in BaseWorkflowMixin:
    - get_name(), get_system_prompt(), get_language_instruction()
    - get_expert_analysis_instruction()
    - get_request_model_name(), get_request_thinking_mode()
    - get_request_use_websearch(), get_request_use_assistant_model()
    - get_validated_temperature(), _resolve_model_context()
    - _prepare_files_for_expert_analysis(), _add_files_to_expert_context()
    """

    # ================================================================================
    # Expert Analysis Configuration
    # ================================================================================

    def get_expert_analysis_instruction(self) -> str:
        """
        Get the instruction for expert analysis.

        Default implementation for tools that don't use expert analysis.
        Override this for tools that do use expert analysis.
        """
        return "Please provide expert analysis based on the investigation findings."

    def should_call_expert_analysis(self, consolidated_findings: ConsolidatedFindings, request=None) -> bool:
        """
        Decide when to call external model based on tool-specific criteria.
        
        Default implementation for tools that don't use expert analysis.
        Override this for tools that do use expert analysis.
        
        Args:
            consolidated_findings: Findings from workflow steps
            request: Current request object (optional for backwards compatibility)
        """
        if not self.requires_expert_analysis():
            return False
        
        # Check if user requested to skip assistant model
        if request and not self.get_request_use_assistant_model(request):
            return False
        
        # Default logic for tools that support expert analysis
        # FIXED (2025-11-03): Changed findings threshold from >= 2 to >= 1
        # Even a single meaningful finding warrants expert validation
        return (
            len(consolidated_findings.relevant_files) > 0
            or len(consolidated_findings.findings) >= 1  # Changed from >= 2
            or len(consolidated_findings.issues_found) > 0
        )

    def should_use_message_arrays(self) -> bool:
        """
        Check if message arrays should be used instead of text prompts.

        Phase 2 Migration: Feature flag to enable SDK-native message arrays.
        Set USE_MESSAGE_ARRAYS=true in .env to enable.
        """
        import os
        use_message_arrays = os.getenv("USE_MESSAGE_ARRAYS", "false").strip().lower()
        return use_message_arrays in ("true", "1", "yes")

    def prepare_messages_for_expert_analysis(
        self,
        system_prompt: str,
        expert_context: str,
        consolidated_findings: ConsolidatedFindings
    ) -> list[dict[str, str]]:
        """
        Prepare message array for expert analysis (Phase 2 Migration).

        Builds SDK-native message array format:
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

        Args:
            system_prompt: System prompt for expert analysis
            expert_context: Context prepared from consolidated findings
            consolidated_findings: All findings from workflow steps

        Returns:
            List of message dicts in SDK-native format
        """
        messages = []

        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user message with expert context
        messages.append({"role": "user", "content": expert_context})

        return messages

    def prepare_expert_analysis_context(self, consolidated_findings: ConsolidatedFindings) -> str:
        """
        Prepare context for external model call.
        
        Default implementation for tools that don't use expert analysis.
        Override this for tools that do use expert analysis.
        """
        if not self.requires_expert_analysis():
            return ""
        
        # Default context preparation
        context_parts = [
            f"=== {self.get_name().upper()} WORK SUMMARY ===",
            f"Total steps: {len(consolidated_findings.findings)}",
            f"Files examined: {len(consolidated_findings.files_checked)}",
            f"Relevant files: {len(consolidated_findings.relevant_files)}",
            "",
            "=== WORK PROGRESSION ===",
        ]
        
        for finding in consolidated_findings.findings:
            context_parts.append(finding)
        
        return "\n".join(context_parts)
    
    def requires_expert_analysis(self) -> bool:
        """
        Check if expert analysis is enabled globally via environment variable.

        Can be disabled via EXPERT_ANALYSIS_ENABLED=false in .env
        This provides a centralized way to disable expert analysis across all tools
        without modifying individual tool implementations.

        Individual tools can still override this method to force-disable expert analysis
        (e.g., planner tool which is self-contained).

        Returns True if expert analysis is enabled globally AND the tool supports it.
        Returns False if disabled globally OR the tool doesn't support it.
        """
        import os
        # Check global enable/disable flag
        enabled = os.getenv("EXPERT_ANALYSIS_ENABLED", "false").strip().lower()
        return enabled in ("true", "1", "yes")
    
    def should_include_files_in_expert_prompt(self) -> bool:
        """
        Check if files should be included in expert analysis prompt via environment variable.

        Can be enabled via EXPERT_ANALYSIS_INCLUDE_FILES=true in .env
        When enabled, embeds entire file contents into prompt, significantly increasing size and latency.

        Individual tools can still override this method to force-enable file inclusion
        (e.g., precommit tool which needs to see actual code changes).

        Returns True if file inclusion is enabled globally AND the tool supports it.
        Returns False if disabled globally OR the tool doesn't need files.
        """
        import os
        enabled = os.getenv("EXPERT_ANALYSIS_INCLUDE_FILES", "false").strip().lower()
        return enabled in ("true", "1", "yes")
    
    def should_embed_system_prompt(self) -> bool:
        """
        Whether to embed the system prompt in the main prompt.
        Override this to return True if your tool needs the system prompt embedded.
        """
        return False

    def _get_thinking_model_for_provider(self, provider) -> Optional[str]:
        """Get a thinking-capable model for the given provider.

        This method provides automatic fallback to thinking-capable models
        when expert analysis requires thinking mode but the user-specified
        model doesn't support it.

        Args:
            provider: The model provider instance

        Returns:
            Model name that supports thinking mode, or None if no fallback available
        """
        from src.providers.base import ProviderType

        # Map provider types to their thinking-capable models
        THINKING_MODELS = {
            ProviderType.GLM: 'glm-4.5-flash',  # Fast model to prevent Augment Code timeout (was glm-4.6)
            ProviderType.KIMI: 'kimi-thinking-preview',  # Upgrade from kimi-k2-0905-preview
        }

        try:
            provider_type = provider.get_provider_type()
            return THINKING_MODELS.get(provider_type)
        except Exception as e:
            logger.warning(f"Failed to get thinking model for provider: {e}")
            return None

    def get_expert_thinking_mode(self, request=None) -> str:
        """
        Get the thinking mode for expert analysis with hybrid fallback.

        Priority:
        1. User-provided parameter (request.thinking_mode)
        2. Environment variable (EXPERT_ANALYSIS_THINKING_MODE)
        3. Default (minimal for speed)

        Modes:
        - minimal: 0.5% model capacity, ~5-7s response time (DEFAULT for speed)
        - low: 8% model capacity, ~8-10s response time
        - medium: 33% model capacity, ~15-20s response time
        - high: 67% model capacity, ~25-30s response time
        - max: 100% model capacity, ~40-60s response time
        """
        import os

        # 1. Check if user provided thinking_mode parameter
        if request and hasattr(request, 'thinking_mode') and request.thinking_mode:
            mode = request.thinking_mode.strip().lower()
            logger.warning(f"🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE={mode} | REQUEST_HAS_PARAM=True")
        else:
            # 2. Fall back to environment variable
            mode = os.getenv("EXPERT_ANALYSIS_THINKING_MODE", "minimal").strip().lower()
            env_value = os.getenv("EXPERT_ANALYSIS_THINKING_MODE", "NOT_SET")
            logger.warning(f"🎯 [THINKING_MODE] SOURCE=ENV_FALLBACK | MODE={mode} | ENV_VALUE={env_value} | REQUEST_HAS_PARAM=False")

        # Validate mode
        valid_modes = ["minimal", "low", "medium", "high", "max"]
        if mode not in valid_modes:
            logger.warning(f"❌ [THINKING_MODE] INVALID_MODE={mode} | FALLING_BACK_TO=minimal")
            return "minimal"

        logger.warning(f"✅ [THINKING_MODE] FINAL_MODE={mode} | VALID=True")
        return mode
    
    def get_expert_timeout_secs(self, request=None) -> float:
        """Return wall-clock timeout for expert analysis.
        Uses coordinated timeout from TimeoutConfig (default 90s).
        Tools may override for per-tool tuning.
        """
        return float(TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS)
    
    def get_expert_heartbeat_interval_secs(self, request=None) -> float:
        """Interval in seconds for emitting progress while waiting on expert analysis.

        CRITICAL FIX: Reduced default from 10s to 2s for better UX.
        This provides more frequent progress updates for ADHD-C users who need continuous feedback.

        Priority: EXAI_WS_EXPERT_KEEPALIVE_MS (ms) > EXPERT_HEARTBEAT_INTERVAL_SECS (s) > 2s default.
        """
        import os
        try:
            ms = os.getenv("EXAI_WS_EXPERT_KEEPALIVE_MS", "").strip()
            if ms:
                val = float(ms) / 1000.0
                if val > 0:
                    return max(0.5, val)
        except Exception:
            pass
        try:
            return float(os.getenv("EXPERT_HEARTBEAT_INTERVAL_SECS", "2"))  # Reduced from 10s to 2s
        except Exception:
            return 2.0  # Reduced from 10.0 to 2.0
    
    # ================================================================================
    # Expert Analysis Execution
    # ================================================================================
    
    async def _call_expert_analysis(self, arguments: dict, request) -> dict:
        """Call external model for expert analysis with watchdog and graceful degradation.

        We see occasional UI disconnects exactly after '[WORKFLOW_FILES] ... Prepared X unique relevant files' and
        before '[PROGRESS] ... Step N/M complete'. That window corresponds to this method executing the slow
        provider call. If the UI disconnects (websocket drop) or the provider stalls, we still want to finish
        and persist a best-effort result instead of leaving the tool 'stuck'.

        CRITICAL FIX: Implements duplicate call prevention using global cache and in-progress tracking.
        This prevents the duplicate expert analysis calls that were causing 300+ second timeouts.
        """
        # EXAI Recommendation (2025-10-21): Performance profiling to identify bottlenecks
        profiler = PerformanceProfiler(f"expert_analysis_{self.get_name()}")
        profiler.checkpoint("start")

        # CRITICAL DIAGNOSTIC: Log entry IMMEDIATELY
        import sys
        print(f"[EXPERT_ENTRY] ========== ENTERED _call_expert_analysis ==========", file=sys.stderr, flush=True)
        print(f"[EXPERT_ENTRY] Tool: {self.get_name()}", file=sys.stderr, flush=True)
        print(f"[EXPERT_ENTRY] Thread: {__import__('threading').current_thread().name}", file=sys.stderr, flush=True)
        print(f"[EXPERT_ENTRY] ========================================", file=sys.stderr, flush=True)

        print(f"[EXPERT_ENTRY] ENTERED _call_expert_analysis for {self.get_name()}")
        logger.info(f"[EXPERT_ENTRY] Expert analysis called for tool: {self.get_name()}")
        print(f"[EXPERT_ENTRY] About to create cache key")

        # CRITICAL FIX: Duplicate call prevention
        # Create cache key from request_id and consolidated findings content
        # This ensures we don't call expert analysis twice for the same content
        # EXAI Fix #6 (2025-10-21): Use deterministic hash (hashlib.md5) instead of hash()
        print(f"[EXPERT_ENTRY] Getting request_id from arguments")
        request_id = arguments.get("request_id", "unknown")
        print(f"[EXPERT_ENTRY] request_id={request_id}")
        print(f"[EXPERT_ENTRY] About to hash findings")
        import hashlib
        findings_str = str(self.consolidated_findings.findings)  # type: ignore
        findings_hash = hashlib.md5(findings_str.encode('utf-8')).hexdigest()[:16]  # First 16 chars
        print(f"[EXPERT_ENTRY] findings_hash={findings_hash}")
        print(f"[EXPERT_ENTRY] Creating cache_key string")
        cache_key = f"{self.get_name()}:{request_id}:{findings_hash}"
        print(f"[EXPERT_ENTRY] cache_key created: {cache_key}")

        logger.info(f"[EXPERT_DEDUP] Cache key: {cache_key}")
        logger.info(f"[EXPERT_DEDUP] Cache size: {len(_expert_validation_cache)}")
        logger.info(f"[EXPERT_DEDUP] In-progress size: {len(_expert_validation_in_progress)}")

        # SIMPLIFIED DUPLICATE PREVENTION (EXAI Fix #4 - 2025-10-21)
        # Single lock acquisition to check cache and mark in-progress
        # Removed duplicate lock handling that was causing complexity
        async with _expert_validation_lock:
            # EXAI Fix #6 (2025-10-21): Clean up expired cache entries
            now = time.time()
            expired_keys = [k for k, (_, ts) in _expert_validation_cache.items() if now - ts > _CACHE_TTL_SECS]
            for k in expired_keys:
                _expert_validation_cache.pop(k, None)
            if expired_keys:
                logger.info(f"[EXPERT_CACHE] Cleaned up {len(expired_keys)} expired entries")

            # EXAI Fix #6 (2025-10-21): Enforce cache size limit (LRU eviction)
            if len(_expert_validation_cache) >= _CACHE_MAX_SIZE:
                # Remove oldest entry (first in dict)
                oldest_key = next(iter(_expert_validation_cache))
                _expert_validation_cache.pop(oldest_key, None)
                logger.info(f"[EXPERT_CACHE] Evicted oldest entry {oldest_key} (cache full)")

            # Check cache first (with TTL validation)
            if cache_key in _expert_validation_cache:
                result, timestamp = _expert_validation_cache[cache_key]
                if now - timestamp <= _CACHE_TTL_SECS:
                    logger.info(f"[EXPERT_DEDUP] Using cached result for {cache_key} (age: {now - timestamp:.1f}s)")
                    return result
                else:
                    # Expired, remove it
                    _expert_validation_cache.pop(cache_key, None)
                    logger.info(f"[EXPERT_CACHE] Removed expired entry {cache_key}")

            # Check if already in progress - return error instead of waiting
            if cache_key in _expert_validation_in_progress:
                logger.warning(f"[EXPERT_DEDUP] Duplicate call detected for {cache_key}, returning error")
                return {
                    "error": "Expert analysis already in progress for this request",
                    "status": "duplicate_request",
                    "raw_analysis": ""
                }

            # Mark as in progress
            _expert_validation_in_progress.add(cache_key)
            logger.info(f"[EXPERT_DEDUP] Marked {cache_key} as in-progress")

        # CRITICAL FIX: Wrap entire method in try/except to ensure we ALWAYS return a dict
        result = None
        try:
            # Model context should be resolved from early validation, but handle fallback for tests
            if not self._model_context:  # type: ignore
                try:
                    model_name, model_context = self._resolve_model_context(arguments, request)
                    self._model_context = model_context  # type: ignore
                    self._current_model_name = model_name  # type: ignore
                except Exception as e:
                    logger.error(f"Failed to resolve model context for expert analysis: {e}")
                    # Use request model as fallback (preserves existing test behavior)
                    model_name = self.get_request_model_name(request)
                    from utils.model.context import ModelContext
                    model_context = ModelContext(model_name)
                    self._model_context = model_context  # type: ignore
                    self._current_model_name = model_name  # type: ignore
            else:
                model_name = self._current_model_name  # type: ignore
            
            provider = self._model_context.provider  # type: ignore
            logger.info(f"[EXPERT_ANALYSIS_DEBUG] Provider resolved: {provider.get_provider_type().value if provider else 'None'}")

            # CRITICAL: Validate model supports thinking mode, auto-upgrade if needed
            # This prevents hangs when using models like glm-4.5-flash that don't support thinking
            # ISSUE #10 FIX: Make auto-upgrade configurable via EXPERT_ANALYSIS_AUTO_UPGRADE env var
            import os
            from src.providers.base import ProviderType
            auto_upgrade_enabled = os.getenv("EXPERT_ANALYSIS_AUTO_UPGRADE", "true").strip().lower() in ("true", "1", "yes")

            if provider and hasattr(provider, 'supports_thinking_mode'):
                if not provider.supports_thinking_mode(model_name):
                    thinking_model = self._get_thinking_model_for_provider(provider)
                    if thinking_model and auto_upgrade_enabled:
                        logger.warning(
                            f"[EXPERT_ANALYSIS] Auto-upgrading {model_name} → {thinking_model} for thinking mode support. "
                            f"This may affect cost/performance. To disable, set EXPERT_ANALYSIS_AUTO_UPGRADE=false in .env"
                        )
                        model_name = thinking_model
                        # Update model context with thinking-capable model
                        from utils.model.context import ModelContext
                        self._model_context = ModelContext(thinking_model)
                        self._current_model_name = thinking_model
                        # Update provider reference
                        provider = self._model_context.provider  # type: ignore
                    elif thinking_model and not auto_upgrade_enabled:
                        logger.warning(
                            f"[EXPERT_ANALYSIS] Model {model_name} doesn't support thinking mode. "
                            f"Auto-upgrade is disabled (EXPERT_ANALYSIS_AUTO_UPGRADE=false). "
                            f"Expert analysis may not work as expected. Consider using {thinking_model} instead."
                        )
                    elif not thinking_model:
                        logger.warning(
                            f"[EXPERT_ANALYSIS] Model {model_name} doesn't support thinking mode and no fallback available. "
                            f"Expert analysis may not work as expected."
                        )
                        logger.info(f"[EXPERT_ANALYSIS] Model context updated to use {thinking_model}")
                    else:
                        logger.warning(f"[EXPERT_ANALYSIS] Model {model_name} doesn't support thinking mode and no fallback available")
                else:
                    logger.info(f"[EXPERT_ANALYSIS] Model {model_name} supports thinking mode ✓")

            # Prepare expert analysis context
            expert_context = self.prepare_expert_analysis_context(self.consolidated_findings)  # type: ignore
            logger.info(f"[EXPERT_ANALYSIS_DEBUG] Expert context prepared ({len(expert_context)} chars)")
            
            # ISSUE #9 FIX: Clarify file embedding terminology
            # "File inclusion" means embedding FULL file contents in the prompt
            # File paths/names are ALWAYS included in the context regardless of this setting
            if self.should_include_files_in_expert_prompt():
                logger.info(f"[EXPERT_ANALYSIS_DEBUG] Full file content embedding enabled (EXPERT_ANALYSIS_INCLUDE_FILES=true)")
                file_content = self._prepare_files_for_expert_analysis()
                if file_content:
                    logger.info(f"[EXPERT_ANALYSIS_DEBUG] Embedding {len(file_content)} chars of full file content into expert context")
                    expert_context = self._add_files_to_expert_context(expert_context, file_content)
                else:
                    logger.info(f"[EXPERT_ANALYSIS_DEBUG] No file content to embed (files may be empty or filtered)")
            else:
                logger.info(
                    f"[EXPERT_ANALYSIS_DEBUG] Full file content embedding disabled (EXPERT_ANALYSIS_INCLUDE_FILES=false). "
                    f"File paths/names are still included in context, but not full contents."
                )
            
            # Get system prompt for this tool with localization support
            base_system_prompt = self.get_system_prompt()
            language_instruction = self.get_language_instruction()
            system_prompt = language_instruction + base_system_prompt

            # CRITICAL FIX (2025-10-21): Strengthen JSON enforcement with explicit schema
            # EXAI INSIGHT: Previous enforcement was too weak - models still returned conversational text
            # Solution: Provide explicit JSON schema and examples
            # REVISION (2025-11-02): Further strengthened with explicit warnings and examples
            json_enforcement = (
                "\n\n" + "="*80 + "\n"
                "CRITICAL OUTPUT FORMAT REQUIREMENT - READ CAREFULLY\n"
                "="*80 + "\n\n"
                "⚠️ MANDATORY: You MUST respond with ONLY a valid JSON object. No other text is allowed.\n"
                "❌ DO NOT include any explanatory text before or after the JSON\n"
                "❌ DO NOT wrap the JSON in markdown code blocks\n"
                "❌ DO NOT add any conversational text\n"
                "✅ ONLY output the raw JSON object\n\n"
                "REQUIRED JSON SCHEMA:\n"
                "{\n"
                '  "analysis": "Your detailed analysis here",\n'
                '  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],\n'
                '  "recommendations": ["Recommendation 1", "Recommendation 2"],\n'
                '  "confidence": "high|medium|low",\n'
                '  "needs_more_info": false,\n'
                '  "additional_context": "Optional: what additional info would help"\n'
                "}\n\n"
                "STRICT RULES:\n"
                "1. Output ONLY the JSON object - no markdown code blocks (no ```json)\n"
                "2. No explanatory text before or after the JSON\n"
                "3. No conversational responses like 'I need more information...'\n"
                "4. If you need files, set needs_more_info=true and specify in additional_context\n"
                "5. All text must be inside the JSON structure\n\n"
                "EXAMPLE VALID OUTPUT:\n"
                '{"analysis": "The code shows...", "key_findings": ["Issue 1", "Issue 2"], '
                '"recommendations": ["Fix 1", "Fix 2"], "confidence": "high", "needs_more_info": false}\n\n'
                "EXAMPLE INVALID OUTPUT (DO NOT DO THIS):\n"
                "I need more information to continue... ❌ WRONG\n"
                "```json\\n{...}\\n``` ❌ WRONG\n"
                "Let me analyze this... ❌ WRONG\n"
            )

            # Check if tool wants system prompt embedded in main prompt
            if self.should_embed_system_prompt():
                prompt = f"{system_prompt}{json_enforcement}\n\n{expert_context}\n\n{self.get_expert_analysis_instruction()}"
                system_prompt = ""  # Clear it since we embedded it
            else:
                prompt = expert_context

            # CRITICAL: Monitor prompt size for unpredictability diagnosis (EXAI Fix #3 - 2025-10-21)
            prompt_size = len(prompt)
            prompt_tokens_estimate = prompt_size // 4  # Rough estimate: 1 token ≈ 4 chars
            if prompt_tokens_estimate > 100000:  # Warn if approaching 128k limit
                logger.warning(
                    f"⚠️ [PROMPT_SIZE] Tool: {self.get_name()}, "
                    f"Prompt size: {prompt_size:,} chars (~{prompt_tokens_estimate:,} tokens), "
                    f"Approaching token limit! May cause truncation."
                )
            else:
                logger.info(
                    f"📏 [PROMPT_SIZE] Tool: {self.get_name()}, "
                    f"Prompt size: {prompt_size:,} chars (~{prompt_tokens_estimate:,} tokens)"
                )

            # Optional micro-step draft phase: return early to avoid long expert blocking
            try:
                import os as _os
                if (_os.getenv("EXAI_WS_EXPERT_MICROSTEP", "false").strip().lower() == "true"):
                    try:
                        send_progress(f"{self.get_name()}: Expert micro-step draft returned early; schedule validate phase next")
                    except Exception:
                        pass
                    result = {"status": "analysis_partial", "microstep": "draft", "raw_analysis": ""}
                    # Cache and cleanup will happen in finally block
                    return result
            except Exception:
                pass

            # Validate temperature against model constraints
            validated_temperature, temp_warnings = self.get_validated_temperature(request, self._model_context)  # type: ignore

            # Log any temperature corrections
            for warning in temp_warnings:
                logger.warning(warning)

            # Watchdog and soft-deadline setup
            start = time.time()
            try:
                import os as _os
                _soft_dl = float((_os.getenv("EXAI_WS_EXPERT_SOFT_DEADLINE_SECS", "0") or "0").strip() or 0)
            except Exception:
                _soft_dl = 0.0
            deadline = start + self.get_expert_timeout_secs(request)
            timeout_secs = self.get_expert_timeout_secs(request)

            # CRITICAL FIX: Use websearch adapter to check model support
            # Workflow tools were bypassing the adapter and passing use_websearch directly,
            # causing hangs with models that don't support websearch (glm-4.5-flash)
            provider_kwargs = {}
            try:
                logger.info(f"[EXPERT_DEBUG] About to build websearch kwargs for {model_name}")
                from src.providers.orchestration.websearch_adapter import build_websearch_provider_kwargs
                logger.info(f"[EXPERT_DEBUG] Imported websearch_adapter successfully")
                use_web = self.get_request_use_websearch(request)
                logger.info(f"[EXPERT_DEBUG] use_websearch={use_web}")
                provider_kwargs, _ = build_websearch_provider_kwargs(
                    provider_type=provider.get_provider_type(),
                    use_websearch=use_web,
                    model_name=model_name,  # CRITICAL: Pass model name for validation
                    include_event=False,
                )
                logger.info(f"[EXPERT_DEBUG] Built websearch kwargs successfully: {provider_kwargs}")
            except Exception as e:
                logger.error(f"[EXPERT_DEBUG] Failed to build websearch kwargs: {e}")
                # Fallback: no websearch
                provider_kwargs = {}

            # Get thinking mode for expert analysis (with parameter support)
            thinking_mode_start = time.time()
            expert_thinking_mode = self.get_expert_thinking_mode(request)
            thinking_mode_elapsed = time.time() - thinking_mode_start

            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] ========================================")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Tool: {self.get_name()}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Model: {model_name}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Thinking Mode: {expert_thinking_mode}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Temperature: {validated_temperature}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Prompt Length: {len(prompt)} chars")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] Thinking Mode Selection Time: {thinking_mode_elapsed:.3f}s")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_START] ========================================")

            # PHASE 2: Async Provider Support
            # Check if async providers are enabled via feature flag
            import os
            use_async_providers = os.getenv("USE_ASYNC_PROVIDERS", "false").strip().lower() in ("true", "1", "yes")

            start_time = time.time()
            max_wait = timeout_secs  # Use configured timeout (480s for expert analysis)

            # CRITICAL: Log final model selection for unpredictability diagnosis (EXAI Fix #1 - 2025-10-21)
            logger.warning(
                f"🎯 [MODEL_SELECTION] Tool: {self.get_name()}, "
                f"Model: {model_name}, "
                f"Provider: {provider.get_provider_type().value if provider else 'None'}, "
                f"Thinking Mode: {expert_thinking_mode}, "
                f"Temperature: {validated_temperature}, "
                f"Timeout: {max_wait}s"
            )

            # CRITICAL FIX (2025-11-05): Handle GLM thinking_mode incompatibility
            # GLM provider (zai-sdk) doesn't accept thinking_mode parameter even for models marked as supporting it
            # Auto-fallback to Kimi when thinking mode is requested with GLM provider
            thinking_mode_requested = expert_thinking_mode and expert_thinking_mode != "disabled"
            if thinking_mode_requested and provider and provider.get_provider_type() == ProviderType.GLM:
                logger.warning(
                    f"[EXPERT_ANALYSIS] GLM provider does not support thinking_mode parameter with zai-sdk. "
                    f"Auto-fallback to Kimi provider for thinking mode support. "
                    f"This may affect cost/performance."
                )
                # CRITICAL FIX (2025-11-05): Use SYNC Kimi provider for thinking mode fallback
                # Problem: AsyncKimiProvider.chat_completions_create() returns coroutine when called sync
                # Solution: Use sync Kimi provider instead to avoid coroutine error in sync execution path
                from src.providers.kimi import KimiModelProvider
                from src.providers.base import ProviderType
                kimi_api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
                if kimi_api_key:
                    # Create SYNC Kimi provider (not async) to avoid coroutine issues in sync path
                    provider = KimiModelProvider(
                        api_key=kimi_api_key,
                        base_url=os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1")
                    )
                    model_name = "kimi-thinking-preview"
                    # Update model context
                    from utils.model.context import ModelContext
                    self._model_context = ModelContext(model_name)
                    self._current_model_name = model_name
                    logger.info(f"[EXPERT_ANALYSIS] Successfully switched to SYNC Kimi provider with {model_name}")

                    # CRITICAL FIX (2025-11-09): Rebuild provider_kwargs for the NEW provider
                    # The web_search tools were built for GLM at line 587, but we just switched to Kimi
                    # We must rebuild the kwargs for Kimi since it doesn't support web_search tools
                    try:
                        logger.info(f"[EXPERT_DEBUG] Rebuilding websearch kwargs for new provider after provider switch")
                        provider_kwargs, _ = build_websearch_provider_kwargs(
                            provider_type=provider.get_provider_type(),  # Now KIMI
                            use_websearch=self.get_request_use_websearch(request),
                            model_name=model_name,
                            include_event=False,
                        )
                        logger.info(f"[EXPERT_DEBUG] Rebuilt websearch kwargs for {provider.get_provider_type().value}: {provider_kwargs}")
                    except Exception as e:
                        logger.error(f"[EXPERT_DEBUG] Failed to rebuild websearch kwargs after provider switch: {e}")
                        provider_kwargs = {}
                else:
                    logger.error(
                        f"[EXPERT_ANALYSIS] Cannot fallback to Kimi: KIMI_API_KEY or MOONSHOT_API_KEY not configured. "
                        f"Expert analysis will proceed without thinking mode."
                    )
                    # Disable thinking mode if Kimi is not available
                    expert_thinking_mode = "disabled"

            if use_async_providers:
                # PHASE 2: Native async provider path (no run_in_executor)
                logger.info(f"[EXPERT_DEBUG] Using ASYNC providers for {self.get_name()}")
                logger.info(
                    f"[EXPERT_DEBUG] About to call async provider.generate_content() for {self.get_name()}: "
                    f"prompt={len(prompt)} chars, model={model_name}, temp={validated_temperature}, "
                    f"thinking_mode={expert_thinking_mode}"
                )

                # Create async provider based on provider type
                from src.providers.base import ProviderType
                provider_type = provider.get_provider_type()

                async_provider = None
                try:
                    if provider_type == ProviderType.GLM:
                        from src.providers.async_glm import AsyncGLMProvider
                        async_provider = AsyncGLMProvider(
                            api_key=os.getenv("GLM_API_KEY"),
                            base_url=os.getenv("GLM_API_URL")
                        )
                    elif provider_type == ProviderType.KIMI:
                        from src.providers.async_kimi import AsyncKimiProvider
                        async_provider = AsyncKimiProvider(
                            api_key=os.getenv("KIMI_API_KEY"),
                            base_url=os.getenv("KIMI_API_URL")
                        )
                    else:
                        logger.warning(f"[EXPERT_DEBUG] Async provider not available for {provider_type}, falling back to sync")
                        use_async_providers = False  # Fall back to sync path
                except Exception as e:
                    logger.error(f"[EXPERT_DEBUG] Failed to create async provider: {e}, falling back to sync")
                    use_async_providers = False  # Fall back to sync path

                if use_async_providers and async_provider:
                    try:
                        # Use async context manager for proper resource cleanup
                        async with async_provider:
                            # PHASE 2 MIGRATION: Use message arrays when feature flag enabled
                            if self.should_use_message_arrays():
                                logger.info(f"[EXPERT_DEBUG] Using MESSAGE ARRAYS for async provider call")

                                # Prepare message array
                                messages = self.prepare_messages_for_expert_analysis(
                                    system_prompt=system_prompt,
                                    expert_context=expert_context,
                                    consolidated_findings=self.consolidated_findings
                                )

                                logger.info(f"[EXPERT_DEBUG] Calling async provider.chat_completions_create() with {len(messages)} messages")

                                # CRITICAL: Native async call with timeout wrapper
                                raw_response = await asyncio.wait_for(
                                    async_provider.chat_completions_create(
                                        model=model_name,
                                        messages=messages,
                                        temperature=validated_temperature,
                                        thinking_mode=expert_thinking_mode,
                                        **provider_kwargs,
                                    ),
                                    timeout=max_wait
                                )

                                # CRITICAL FIX: Handle ModelResponse objects (which don't have .get() method)
                                # Convert ModelResponse to dict-like object for compatibility
                                from types import SimpleNamespace
                                if hasattr(raw_response, 'content') and not isinstance(raw_response, dict):
                                    # This is a ModelResponse object - convert to SimpleNamespace
                                    model_response = SimpleNamespace(
                                        content=raw_response.content,
                                        model=getattr(raw_response, 'model', model_name),
                                        usage=getattr(raw_response, 'usage', {})
                                    )
                                else:
                                    # This is a dict response
                                    model_response = SimpleNamespace(
                                        content=raw_response.get('content', ''),
                                        model=raw_response.get('model', model_name),
                                        usage=raw_response.get('usage', {})
                                    )

                                logger.info(f"[EXPERT_DEBUG] Async provider.chat_completions_create() returned successfully (MESSAGE ARRAYS)")
                            else:
                                logger.info(f"[EXPERT_DEBUG] Using LEGACY TEXT PROMPTS for async provider call")
                                logger.info(f"[EXPERT_DEBUG] Calling async provider.generate_content()")

                                # LEGACY PATH: Use text-based prompts
                                raw_response = await asyncio.wait_for(
                                    async_provider.generate_content(
                                        prompt=prompt,
                                        model_name=model_name,
                                        system_prompt=system_prompt,
                                        temperature=validated_temperature,
                                        thinking_mode=expert_thinking_mode,
                                        images=list(set(self.consolidated_findings.images)) if self.consolidated_findings.images else None,  # type: ignore
                                        **provider_kwargs,
                                    ),
                                    timeout=max_wait
                                )

                                # CRITICAL FIX: Handle ModelResponse objects (which don't have .get() method)
                                # Convert ModelResponse to dict-like object for compatibility
                                from types import SimpleNamespace
                                if hasattr(raw_response, 'content') and not isinstance(raw_response, dict):
                                    # This is a ModelResponse object - convert to SimpleNamespace
                                    model_response = SimpleNamespace(
                                        content=raw_response.content,
                                        model=getattr(raw_response, 'model', model_name),
                                        usage=getattr(raw_response, 'usage', {})
                                    )
                                else:
                                    # This is a dict response
                                    model_response = SimpleNamespace(
                                        content=raw_response.get('content', '') if isinstance(raw_response, dict) else str(raw_response),
                                        model=raw_response.get('model', model_name) if isinstance(raw_response, dict) else model_name,
                                        usage=raw_response.get('usage', {}) if isinstance(raw_response, dict) else {}
                                    )

                                logger.info(f"[EXPERT_DEBUG] Async provider.generate_content() returned successfully (LEGACY)")

                            duration = time.time() - start_time
                            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Tool: {self.get_name()}, Duration: {duration:.2f}s (ASYNC)")

                    except asyncio.TimeoutError:
                        # Timeout - return error result immediately
                        duration = time.time() - start_time
                        logger.error(f"🔥 [EXPERT_ANALYSIS_TIMEOUT] Tool: {self.get_name()}, Duration: {duration:.2f}s, Timeout: {max_wait}s (ASYNC)")

                        return {
                            "error": f"Expert analysis timed out after {max_wait}s",
                            "status": "analysis_timeout",
                            "raw_analysis": ""
                        }
                    except Exception as e:
                        logger.error(f"[EXPERT_DEBUG] Async provider call failed: {e}, falling back to sync")
                        use_async_providers = False  # Fall back to sync path

            if not use_async_providers:
                # PHASE 1: Sync provider path with run_in_executor (backward compatible)
                logger.info(f"[EXPERT_DEBUG] Using SYNC providers for {self.get_name()}")

                # PHASE 2 MIGRATION: Use message arrays when feature flag enabled
                if self.should_use_message_arrays():
                    logger.info(f"[EXPERT_DEBUG] Using MESSAGE ARRAYS for sync provider call")

                    # Prepare message array
                    messages = self.prepare_messages_for_expert_analysis(
                        system_prompt=system_prompt,
                        expert_context=expert_context,
                        consolidated_findings=self.consolidated_findings
                    )

                    logger.info(
                        f"[EXPERT_DEBUG] About to call provider.chat_completions_create() for {self.get_name()}: "
                        f"messages={len(messages)}, model={model_name}, temp={validated_temperature}, "
                        f"thinking_mode={expert_thinking_mode}"
                    )

                    loop = asyncio.get_running_loop()
                    def _invoke_provider():
                        logger.info(f"[EXPERT_DEBUG] Inside _invoke_provider thread, about to call provider.chat_completions_create()")
                        raw_response = provider.chat_completions_create(
                            model=model_name,
                            messages=messages,
                            temperature=validated_temperature,
                            thinking_mode=expert_thinking_mode,
                            **provider_kwargs,
                        )

                        # CRITICAL FIX: Handle ModelResponse objects (which don't have .get() method)
                        # Convert ModelResponse to dict-like object for compatibility
                        if hasattr(raw_response, 'content') and not isinstance(raw_response, dict):
                            # This is a ModelResponse object - convert to SimpleNamespace with .get() support
                            from types import SimpleNamespace
                            result = SimpleNamespace(
                                content=raw_response.content,
                                model=getattr(raw_response, 'model', model_name),
                                usage=getattr(raw_response, 'usage', {})
                            )
                        else:
                            # This is already a dict response
                            from types import SimpleNamespace
                            result = SimpleNamespace(
                                content=raw_response.get('content', ''),
                                model=raw_response.get('model', model_name),
                                usage=raw_response.get('usage', {})
                            )
                        logger.info(f"[EXPERT_DEBUG] provider.chat_completions_create() returned successfully (MESSAGE ARRAYS)")
                        return result

                    logger.info(f"[EXPERT_DEBUG] About to submit _invoke_provider to executor")
                    task = loop.run_in_executor(None, _invoke_provider)
                    logger.info(f"[EXPERT_DEBUG] Task submitted to executor, using asyncio.wait_for for timeout")
                else:
                    logger.info(f"[EXPERT_DEBUG] Using LEGACY TEXT PROMPTS for sync provider call")
                    logger.info(
                        f"[EXPERT_DEBUG] About to call provider.generate_content() for {self.get_name()}: "
                        f"prompt={len(prompt)} chars, model={model_name}, temp={validated_temperature}, "
                        f"thinking_mode={expert_thinking_mode}"
                    )
                    logger.debug(f"Calling provider.generate_content() for {self.get_name()}: prompt={len(prompt)} chars, model={model_name}, temp={validated_temperature}")

                    loop = asyncio.get_running_loop()
                    def _invoke_provider():
                        logger.info(f"[EXPERT_DEBUG] Inside _invoke_provider thread, about to call provider.generate_content()")
                        logger.debug(f"Inside _invoke_provider, calling provider.generate_content()")
                        result = provider.generate_content(
                            prompt=prompt,
                            model_name=model_name,
                            system_prompt=system_prompt,
                            temperature=validated_temperature,
                            thinking_mode=expert_thinking_mode,  # Use pre-fetched thinking mode
                            images=list(set(self.consolidated_findings.images)) if self.consolidated_findings.images else None,  # type: ignore
                            **provider_kwargs,  # CRITICAL: Use adapter-validated kwargs instead of raw use_websearch
                        )
                        logger.info(f"[EXPERT_DEBUG] provider.generate_content() returned successfully (LEGACY)")
                        # CRITICAL FIX: Handle ModelResponse objects (which don't have .get() method)
                        # Convert ModelResponse to dict-like object for compatibility
                        if hasattr(result, 'content') and not isinstance(result, dict):
                            # This is a ModelResponse object - convert to SimpleNamespace with .get() support
                            from types import SimpleNamespace
                            return SimpleNamespace(
                                content=result.content,
                                model=getattr(result, 'model', model_name),
                                usage=getattr(result, 'usage', {})
                            )
                        return result

                    logger.info(f"[EXPERT_DEBUG] About to submit _invoke_provider to executor")
                    task = loop.run_in_executor(None, _invoke_provider)
                    logger.info(f"[EXPERT_DEBUG] Task submitted to executor, using asyncio.wait_for for timeout")

                try:
                    # Single async call with timeout - no polling needed!
                    logger.info(f"[EXPERT_DEBUG] Waiting for task with {max_wait}s timeout")
                    model_response = await asyncio.wait_for(task, timeout=max_wait)
                    logger.info(f"[EXPERT_DEBUG] Task completed successfully")

                    # Success - continue with existing response handling
                    duration = time.time() - start_time
                    logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Tool: {self.get_name()}, Duration: {duration:.2f}s (SYNC)")

                except asyncio.TimeoutError:
                    # Timeout - return error result immediately
                    duration = time.time() - start_time
                    logger.error(f"🔥 [EXPERT_ANALYSIS_TIMEOUT] Tool: {self.get_name()}, Duration: {duration:.2f}s, Timeout: {max_wait}s (SYNC)")

                    # Try to cancel the task to free resources
                    try:
                        task.cancel()
                    except Exception:
                        pass

                    # Return timeout error immediately - skip response processing
                    return {
                        "error": f"Expert analysis timed out after {max_wait}s",
                        "status": "analysis_timeout",
                        "raw_analysis": ""
                    }

            # (Dead code block removed - see git history for old poll loop implementation)

            # Continue with response handling (works for both timeout and success cases)
            logger.info(f"[EXPERT_DEBUG] Processing expert analysis result")
            expert_analysis_duration = time.time() - thinking_mode_start
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Tool: {self.get_name()}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Model: {model_name}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: {expert_thinking_mode}")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: {expert_analysis_duration:.2f}s")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] Response Length: {len(model_response.content) if model_response.content else 0} chars")
            logger.warning(f"🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================")

            logger.info(f"Provider call completed, processing response")
            if model_response.content:
                try:
                    # Log the raw response for debugging
                    response_preview = model_response.content[:500] if len(model_response.content) > 500 else model_response.content
                    logger.debug(f"[EXPERT_ANALYSIS_DEBUG] Raw response preview (first 500 chars): {response_preview}")

                    # EXAI INSIGHT (2025-10-21): Try to extract JSON even if wrapped in markdown
                    content = model_response.content.strip()

                    # Try direct parse first
                    try:
                        analysis_result = json.loads(content)
                        logger.info(f"Successfully parsed JSON response (direct parse)")
                    except json.JSONDecodeError:
                        # Try to extract JSON from markdown code blocks
                        import re
                        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                        if json_match:
                            logger.info(f"Found JSON wrapped in markdown, extracting...")
                            analysis_result = json.loads(json_match.group(1))
                            logger.info(f"Successfully parsed JSON response (extracted from markdown)")
                        else:
                            # Try to find any JSON object in the response
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                logger.info(f"Found JSON object in response, extracting...")
                                analysis_result = json.loads(json_match.group(0))
                                logger.info(f"Successfully parsed JSON response (extracted from text)")
                            else:
                                raise json.JSONDecodeError("No JSON found in response", content, 0)

                    result = analysis_result
                except json.JSONDecodeError as json_err:
                    # Enhanced logging for JSON parse errors
                    logger.error(
                        f"[EXPERT_ANALYSIS_DEBUG] JSON parse error: {json_err}\n"
                        f"Response length: {len(model_response.content)} chars\n"
                        f"Response preview (first 1000 chars): {model_response.content[:1000]}\n"
                        f"Response preview (last 500 chars): {model_response.content[-500:]}"
                    )
                    result = {
                        "status": "analysis_complete",
                        "raw_analysis": model_response.content,
                        "parse_error": f"Response was not valid JSON: {str(json_err)}",
                    }
            else:
                logger.warning(f"[EXPERT_ANALYSIS_DEBUG] Empty response from model")
                result = {"error": "No response from model", "status": "empty_response"}

        except Exception as e:
            logger.error(f"Exception in _call_expert_analysis: {e}", exc_info=True)
            result = {"error": str(e), "status": "analysis_error"}

        finally:
            # CRITICAL FIX: Always remove from in-progress and cache result
            async with _expert_validation_lock:
                _expert_validation_in_progress.discard(cache_key)
                logger.info(f"[EXPERT_DEDUP] Removed {cache_key} from in-progress")

                # Cache the result if we have one (EXAI Fix #6 - 2025-10-21: with timestamp)
                if result is not None:
                    _expert_validation_cache[cache_key] = (result, time.time())
                    logger.info(f"[EXPERT_DEDUP] Cached result for {cache_key}")
                    logger.info(f"[EXPERT_DEDUP] Cache size now: {len(_expert_validation_cache)}/{_CACHE_MAX_SIZE}")

        # CRITICAL FIX: Ensure we ALWAYS return a dict, never None
        if result is None:
            logger.error(f"CRITICAL: result is None at end of method! This should be impossible!")
            result = {
                "error": "Expert analysis method completed but result is None - this indicates a serious bug in the code flow",
                "status": "analysis_error",
                "tool_name": self.get_name()
            }

        logger.debug(f"_call_expert_analysis() returning: {type(result)}, is_dict: {isinstance(result, dict)}")
        return result

