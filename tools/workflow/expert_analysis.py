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
_expert_validation_cache: Dict[str, dict] = {}
_expert_validation_in_progress: Set[str] = set()
_expert_validation_lock = asyncio.Lock()


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
        return (
            len(consolidated_findings.relevant_files) > 0
            or len(consolidated_findings.findings) >= 2
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
        print(f"[EXPERT_ENTRY] Getting request_id from arguments")
        request_id = arguments.get("request_id", "unknown")
        print(f"[EXPERT_ENTRY] request_id={request_id}")
        print(f"[EXPERT_ENTRY] About to hash findings")
        findings_hash = hash(str(self.consolidated_findings.findings))  # type: ignore
        print(f"[EXPERT_ENTRY] findings_hash={findings_hash}")
        print(f"[EXPERT_ENTRY] Creating cache_key string")
        cache_key = f"{self.get_name()}:{request_id}:{findings_hash}"
        print(f"[EXPERT_ENTRY] cache_key created: {cache_key}")

        logger.info(f"[EXPERT_DEDUP] Cache key: {cache_key}")
        logger.info(f"[EXPERT_DEDUP] Cache size: {len(_expert_validation_cache)}")
        logger.info(f"[EXPERT_DEDUP] In-progress size: {len(_expert_validation_in_progress)}")

        # Check cache first (outside lock for performance)
        if cache_key in _expert_validation_cache:
            logger.info(f"Using cached expert validation for {cache_key}")
            return _expert_validation_cache[cache_key]

        # Acquire lock to check/set in-progress status
        logger.info(f"[EXPERT_DEDUP] About to acquire lock for {cache_key}")
        async with _expert_validation_lock:
            logger.info(f"[EXPERT_DEDUP] Lock acquired for {cache_key}")
            # Double-check cache after acquiring lock
            if cache_key in _expert_validation_cache:
                logger.info(f"[EXPERT_DEDUP] Using cached expert validation (after lock) for {cache_key}")
                return _expert_validation_cache[cache_key]

            # Check if already in progress
            if cache_key in _expert_validation_in_progress:
                logger.warning(f"Expert validation already in progress for {cache_key}, waiting...")
            logger.info(f"[EXPERT_DEDUP] About to release lock for {cache_key}")

        # SIMPLIFIED DUPLICATE PREVENTION (Expert Recommendation - Phase 2 Fix)
        # Single lock acquisition to check cache and mark in-progress
        async with _expert_validation_lock:
            # Check cache first
            if cache_key in _expert_validation_cache:
                logger.info(f"[EXPERT_DEDUP] Using cached result")
                return _expert_validation_cache[cache_key]

            # Check if already in progress - return error instead of waiting
            if cache_key in _expert_validation_in_progress:
                logger.warning(f"[EXPERT_DEDUP] Duplicate call detected, returning error")
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
            
            # Check if tool wants system prompt embedded in main prompt
            if self.should_embed_system_prompt():
                prompt = f"{system_prompt}\n\n{expert_context}\n\n{self.get_expert_analysis_instruction()}"
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

                                # Convert dict response to ModelResponse-like object for compatibility
                                from types import SimpleNamespace
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
                                model_response = await asyncio.wait_for(
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

                        # Convert dict response to ModelResponse-like object for compatibility
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

                    analysis_result = json.loads(model_response.content.strip())
                    logger.info(f"Successfully parsed JSON response, caching and returning analysis_result")
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

                # Cache the result if we have one
                if result is not None:
                    _expert_validation_cache[cache_key] = result
                    logger.info(f"[EXPERT_DEDUP] Cached result for {cache_key}")
                    logger.info(f"[EXPERT_DEDUP] Cache size now: {len(_expert_validation_cache)}")

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

