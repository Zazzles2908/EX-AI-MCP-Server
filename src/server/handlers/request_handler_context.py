"""
Request Handler Context Module

This module manages conversation context and caching including:
- Thread context reconstruction from continuation_id
- Session cache integration
- Continuation ID management
- Consensus auto-model selection
"""

import logging
import os
from typing import Dict, Any
from mcp.types import TextContent

from src.server.context import reconstruct_thread_context

logger = logging.getLogger(__name__)


async def reconstruct_context(name: str, arguments: Dict[str, Any], req_id: str) -> Dict[str, Any]:
    """
    Reconstruct thread context if continuation_id is present.
    
    This function handles conversation thread resumption by:
    - Loading conversation history from in-memory storage
    - Reconstructing file references
    - Preserving context across tool handoffs
    
    Args:
        name: Tool name
        arguments: Tool arguments (may contain continuation_id)
        req_id: Request ID for logging
        
    Returns:
        Updated arguments with reconstructed context
    """
    if "continuation_id" in arguments and arguments["continuation_id"]:
        continuation_id = arguments["continuation_id"]
        logger.debug(f"Resuming conversation thread: {continuation_id}")
        logger.debug(
            f"[CONVERSATION_DEBUG] Tool '{name}' resuming thread {continuation_id} with {len(arguments)} arguments"
        )
        logger.debug(f"[CONVERSATION_DEBUG] Original arguments keys: {list(arguments.keys())}")
        
        # Log to activity file for monitoring
        try:
            mcp_activity_logger = logging.getLogger("mcp_activity")
            mcp_activity_logger.info(f"CONVERSATION_RESUME: {name} resuming thread {continuation_id} req_id={req_id}")
        except Exception:
            pass
        
        arguments = await reconstruct_thread_context(arguments)
        logger.debug(f"[CONVERSATION_DEBUG] After thread reconstruction, arguments keys: {list(arguments.keys())}")
        if "_remaining_tokens" in arguments:
            logger.debug(f"[CONVERSATION_DEBUG] Remaining token budget: {arguments['_remaining_tokens']:,}")
    
    return arguments


def integrate_session_cache(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject cached context hints if available.
    
    Session cache provides compact summaries and file lists from previous
    tool executions in the same conversation thread.
    
    Args:
        arguments: Tool arguments (may contain continuation_id)
        
    Returns:
        Updated arguments with cached context hints
    """
    try:
        from utils.cache import get_session_cache, make_session_key
        cache = get_session_cache()
        cont_id = arguments.get("continuation_id")
        if cont_id:
            skey = make_session_key(cont_id)
            cached = cache.get(skey)
            if cached:
                logger.debug(f"[CACHE] hit for {skey}; injecting compact context")
                # Inject compact context hints for tools
                arguments.setdefault("_cached_summary", cached.get("summary"))
                arguments.setdefault("_cached_files", cached.get("files", []))
            else:
                logger.debug(f"[CACHE] miss for {skey}")
    except Exception as _e:
        logger.debug(f"[CACHE] integration skipped/failed: {_e}")
    
    return arguments


def auto_select_consensus_models(name: str, arguments: Dict[str, Any]) -> tuple[Dict[str, Any], list[TextContent] | None]:
    """
    Auto-select models for consensus tool if not provided.
    
    This function implements intelligent model selection for the consensus tool:
    - Selects quality-tier models first
    - Falls back to speed-tier models
    - Fills remaining from provider priority order
    - Ensures minimum 2 models for cross-model comparison
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tuple of (updated_arguments, error_response)
        error_response is None if successful
    """
    if name != "consensus":
        return arguments, None
    
    models_arg = arguments.get("models")
    if models_arg or os.getenv("ENABLE_CONSENSUS_AUTOMODE", "true").strip().lower() != "true":
        return arguments, None
    
    try:
        from src.providers.registry import ModelProviderRegistry
        from src.providers.base import ProviderType
        
        def _int_env(k: str, d: int) -> int:
            try:
                return int(os.getenv(k, str(d)))
            except Exception:
                return d
        
        min_needed = _int_env("MIN_CONSENSUS_MODELS", 2)
        max_needed = max(_int_env("MAX_CONSENSUS_MODELS", 3), min_needed)
        
        available_map = ModelProviderRegistry.get_available_models(respect_restrictions=True)
        available = set(available_map.keys())
        
        # Preferred quality-tier from env
        prefs = [
            os.getenv("GLM_QUALITY_MODEL"),
            os.getenv("KIMI_QUALITY_MODEL"),
        ]
        # Speed-tier complements
        speed_prefs = [
            os.getenv("GLM_SPEED_MODEL"),
            os.getenv("KIMI_SPEED_MODEL"),
        ]
        
        chosen: list[str] = []
        for m in prefs:
            if m and m in available and m not in chosen:
                chosen.append(m)
                if len(chosen) >= max_needed:
                    break
        
        if len(chosen) < min_needed:
            for m in speed_prefs:
                if m and m in available and m not in chosen:
                    chosen.append(m)
                    if len(chosen) >= max_needed:
                        break
        
        # Fill remaining from provider priority order
        if len(chosen) < min_needed:
            for ptype in ModelProviderRegistry.PROVIDER_PRIORITY_ORDER:
                try:
                    pool = ModelProviderRegistry.list_available_models(provider_type=ptype)
                except Exception:
                    pool = []
                for m in pool:
                    if m in available and m not in chosen:
                        chosen.append(m)
                        if len(chosen) >= max_needed:
                            break
                if len(chosen) >= max_needed:
                    break
        
        if not chosen:
            warn_text = (
                "Consensus requires at least one available model; none were found under current providers. "
                "Configure provider keys or set DEFAULT_MODEL=auto."
            )
            logger.warning("[CONSENSUS] %s", warn_text)
            return arguments, [TextContent(type="text", text=warn_text)]
        
        if len(chosen) == 1:
            logger.warning("[CONSENSUS] Only 1 model available; proceeding without cross-model comparison")
        
        logger.info("Consensus invoked with %d model(s)", len(chosen))
        logger.debug("[CONSENSUS] Auto-selected models: %s", ", ".join(chosen))
        
        arguments["models"] = [{"model": m} for m in chosen[:max_needed]]
    except Exception as _e:
        logger.debug(f"[CONSENSUS] auto-select models skipped/failed: {_e}")
    
    return arguments, None


# Export public API
__all__ = [
    'reconstruct_context',
    'integrate_session_cache',
    'auto_select_consensus_models',
]

