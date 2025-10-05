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
        Override this to completely disable expert analysis for the tool.
        
        Returns True if the tool supports expert analysis (default).
        Returns False if the tool is self-contained (like planner).
        """
        return True
    
    def should_include_files_in_expert_prompt(self) -> bool:
        """
        Whether to include file content in the expert analysis prompt.
        Override this to return True if your tool needs files in the prompt.
        """
        return False
    
    def should_embed_system_prompt(self) -> bool:
        """
        Whether to embed the system prompt in the main prompt.
        Override this to return True if your tool needs the system prompt embedded.
        """
        return False
    
    def get_expert_thinking_mode(self) -> str:
        """
        Get the thinking mode for expert analysis.
        Override this to customize the thinking mode.
        """
        return "high"
    
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
        print(f"[PRINT_DEBUG] _call_expert_analysis() ENTERED for tool: {self.get_name()}")
        logger.info(f"[EXPERT_ANALYSIS_DEBUG] _call_expert_analysis() called for tool: {self.get_name()}")

        # CRITICAL FIX: Duplicate call prevention
        # Create cache key from request_id and consolidated findings content
        # This ensures we don't call expert analysis twice for the same content
        request_id = arguments.get("request_id", "unknown")
        findings_hash = hash(str(self.consolidated_findings.findings))  # type: ignore
        cache_key = f"{self.get_name()}:{request_id}:{findings_hash}"

        logger.info(f"[EXPERT_DEDUP] Cache key: {cache_key}")
        logger.info(f"[EXPERT_DEDUP] Cache size: {len(_expert_validation_cache)}")
        logger.info(f"[EXPERT_DEDUP] In-progress size: {len(_expert_validation_in_progress)}")

        # Check cache first (outside lock for performance)
        if cache_key in _expert_validation_cache:
            logger.info(f"[EXPERT_DEDUP] Using cached expert validation for {cache_key}")
            print(f"[PRINT_DEBUG] Using cached expert validation result")
            return _expert_validation_cache[cache_key]

        # Acquire lock to check/set in-progress status
        async with _expert_validation_lock:
            # Double-check cache after acquiring lock
            if cache_key in _expert_validation_cache:
                logger.info(f"[EXPERT_DEDUP] Using cached expert validation (after lock) for {cache_key}")
                return _expert_validation_cache[cache_key]

            # Check if already in progress
            if cache_key in _expert_validation_in_progress:
                logger.warning(f"[EXPERT_DEDUP] Expert validation already in progress for {cache_key}")
                print(f"[PRINT_DEBUG] Expert validation already in progress, waiting...")

        # Wait for in-progress validation to complete (outside lock to allow progress)
        if cache_key in _expert_validation_in_progress:
            max_wait = 120  # Maximum 2 minutes wait
            wait_interval = 0.5
            waited = 0.0
            while cache_key in _expert_validation_in_progress and waited < max_wait:
                await asyncio.sleep(wait_interval)
                waited += wait_interval
                if waited % 5 == 0:  # Log every 5 seconds
                    logger.info(f"[EXPERT_DEDUP] Still waiting for in-progress validation ({waited:.1f}s)")

            # Check cache again after waiting
            if cache_key in _expert_validation_cache:
                logger.info(f"[EXPERT_DEDUP] Using cached result after waiting {waited:.1f}s")
                return _expert_validation_cache[cache_key]

            # If still in progress after max wait, log warning and proceed anyway
            if cache_key in _expert_validation_in_progress:
                logger.error(f"[EXPERT_DEDUP] In-progress validation timed out after {waited:.1f}s, proceeding anyway")

        # Mark as in progress
        async with _expert_validation_lock:
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
                    from utils.model_context import ModelContext
                    model_context = ModelContext(model_name)
                    self._model_context = model_context  # type: ignore
                    self._current_model_name = model_name  # type: ignore
            else:
                model_name = self._current_model_name  # type: ignore
            
            provider = self._model_context.provider  # type: ignore
            logger.info(f"[EXPERT_ANALYSIS_DEBUG] Provider resolved: {provider.get_provider_type().value if provider else 'None'}")

            # Prepare expert analysis context
            expert_context = self.prepare_expert_analysis_context(self.consolidated_findings)  # type: ignore
            logger.info(f"[EXPERT_ANALYSIS_DEBUG] Expert context prepared, about to call provider.generate_content()")
            
            # Check if tool wants to include files in prompt
            if self.should_include_files_in_expert_prompt():
                file_content = self._prepare_files_for_expert_analysis()
                if file_content:
                    expert_context = self._add_files_to_expert_context(expert_context, file_content)
            
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

            # Run provider call in a thread to allow cancellation/timeouts even if provider blocks
            print(f"[PRINT_DEBUG] About to call provider.generate_content() for {self.get_name()}")
            loop = asyncio.get_running_loop()
            def _invoke_provider():
                print(f"[PRINT_DEBUG] Inside _invoke_provider, calling provider.generate_content()")
                return provider.generate_content(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=validated_temperature,
                    thinking_mode=self.get_request_thinking_mode(request),
                    use_websearch=self.get_request_use_websearch(request),
                    images=list(set(self.consolidated_findings.images)) if self.consolidated_findings.images else None,  # type: ignore
                )
            task = loop.run_in_executor(None, _invoke_provider)

            # Poll until done or deadline; emit progress breadcrumbs so UI stays alive
            # CRITICAL FIX: Removed max(5.0, ...) to allow 2s heartbeat for better UX
            hb = self.get_expert_heartbeat_interval_secs(request)
            while True:
                # Check completion first
                if task.done():
                    try:
                        model_response = task.result()
                    except Exception as e:
                        # Provider error - attempt graceful fallback on rate limit if enabled and time remains
                        try:
                            import os as _os
                            allow_fb = _os.getenv("EXPERT_FALLBACK_ON_RATELIMIT", "true").strip().lower() == "true"
                        except Exception:
                            allow_fb = True
                        err_text = str(e)
                        is_rate_limited = ("429" in err_text) or ("ReachLimit" in err_text) or ("concurrent" in err_text.lower())
                        time_left = deadline - time.time()
                        if allow_fb and is_rate_limited and time_left > 3.0:
                            # Try fallback to Kimi provider quickly
                            try:
                                send_progress(f"{self.get_name()}: Rate-limited on {provider.get_provider_type().value}, falling back to Kimi...")
                            except Exception:
                                pass
                            try:
                                from src.providers.registry import ModelProviderRegistry
                                from src.providers.base import ProviderType as _PT
                                fb_provider = ModelProviderRegistry.get_provider(_PT.KIMI)
                                fb_model = _os.getenv("KIMI_THINKING_MODEL", "kimi-thinking-preview")
                            except Exception:
                                fb_provider = None
                                fb_model = None
                            if fb_provider and fb_model:
                                def _invoke_fb():
                                    return fb_provider.generate_content(
                                        prompt=prompt,
                                        model_name=fb_model,
                                        system_prompt=system_prompt,
                                        temperature=validated_temperature,
                                        thinking_mode=self.get_request_thinking_mode(request),
                                        use_websearch=self.get_request_use_websearch(request),
                                        images=list(set(self.consolidated_findings.images)) if self.consolidated_findings.images else None,  # type: ignore
                                    )
                                fb_task = loop.run_in_executor(None, _invoke_fb)
                                # Wait within remaining time, emitting heartbeats
                                while True:
                                    if fb_task.done():
                                        model_response = fb_task.result()
                                        break
                                    now_fb = time.time()
                                    # Soft-deadline early return with partial to avoid client cancel
                                    if _soft_dl and (now_fb - start) >= _soft_dl:
                                        logger.warning("Expert analysis fallback soft-deadline reached; returning partial result early")
                                        result = {"status":"analysis_partial","soft_deadline_exceeded": True, "raw_analysis": ""}
                                        break
                                    if now_fb >= deadline:
                                        try:
                                            fb_task.cancel()
                                        except Exception:
                                            pass
                                        logger.error("Expert analysis fallback timed out; returning partial context-only result")
                                        result = {"status":"analysis_timeout","error":"Expert analysis exceeded timeout","raw_analysis":""}
                                        break
                                    # CRITICAL FIX: Enhanced progress message with elapsed time and ETA
                                    elapsed_fb = now_fb - start
                                    remaining_fb = max(0, deadline - now_fb)
                                    progress_pct_fb = min(100, int((elapsed_fb / timeout_secs) * 100))
                                    try:
                                        send_progress(
                                            f"{self.get_name()}: Waiting on expert analysis (provider=kimi, fallback) | "
                                            f"Progress: {progress_pct_fb}% | Elapsed: {elapsed_fb:.1f}s | ETA: {remaining_fb:.1f}s"
                                        )
                                    except Exception:
                                        pass
                                    # Sleep only up to remaining time
                                    await asyncio.sleep(min(hb, max(0.1, deadline - now_fb)))
                                # Check if we set result during fallback timeout/soft-deadline
                                if result is not None:
                                    break  # Exit outer loop too
                                break
                        # No fallback or still failing - re-raise to outer handler
                        raise
                    break

                # Check if we set result during fallback
                if result is not None:
                    break  # Exit main loop

                now = time.time()
                # Soft-deadline early return with partial to avoid client cancel
                if _soft_dl and (now - start) >= _soft_dl:
                    logger.warning("Expert analysis soft-deadline reached; returning partial result early")
                    result = {
                        "status": "analysis_partial",
                        "soft_deadline_exceeded": True,
                        "raw_analysis": "",
                    }
                    break
                if now >= deadline:
                    try:
                        task.cancel()
                    except Exception:
                        pass
                    logger.error("Expert analysis timed out; returning partial context-only result")
                    result = {
                        "status": "analysis_timeout",
                        "error": "Expert analysis exceeded timeout",
                        "raw_analysis": "",
                    }
                    break
                # CRITICAL FIX: Enhanced progress message with elapsed time, ETA, and progress percentage
                elapsed = now - start
                remaining = max(0, deadline - now)
                progress_pct = min(100, int((elapsed / timeout_secs) * 100))
                try:
                    send_progress(
                        f"{self.get_name()}: Waiting on expert analysis (provider={provider.get_provider_type().value}) | "
                        f"Progress: {progress_pct}% | Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s"
                    )
                except Exception:
                    pass
                # Sleep only up to remaining time to avoid overshooting deadline
                await asyncio.sleep(min(hb, max(0.1, deadline - time.time())))


            print(f"[PRINT_DEBUG] Provider call completed, processing response")
            logger.info(f"[EXPERT_ANALYSIS_DEBUG] Provider call completed, processing response")
            if model_response.content:
                try:
                    # Log the raw response for debugging
                    response_preview = model_response.content[:500] if len(model_response.content) > 500 else model_response.content
                    logger.debug(f"[EXPERT_ANALYSIS_DEBUG] Raw response preview (first 500 chars): {response_preview}")

                    analysis_result = json.loads(model_response.content.strip())
                    print(f"[PRINT_DEBUG] Successfully parsed JSON, caching and returning analysis_result")
                    logger.info(f"[EXPERT_ANALYSIS_DEBUG] Successfully parsed JSON response, caching and returning analysis_result")
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
            print(f"[PRINT_DEBUG] Exception in _call_expert_analysis: {e}")
            logger.error(f"[EXPERT_ANALYSIS_DEBUG] Exception in _call_expert_analysis: {e}", exc_info=True)
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
            print(f"[PRINT_DEBUG] CRITICAL: result is None at end of method! This should be impossible!")
            result = {
                "error": "Expert analysis method completed but result is None - this indicates a serious bug in the code flow",
                "status": "analysis_error",
                "tool_name": self.get_name()
            }

        print(f"[PRINT_DEBUG] _call_expert_analysis() RETURNING: {type(result)}, is_dict: {isinstance(result, dict)}")
        return result

