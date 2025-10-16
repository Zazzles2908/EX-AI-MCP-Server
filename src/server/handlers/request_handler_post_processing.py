"""
Request Handler Post-Processing Module

This module handles post-execution processing including:
- Files required to continue handling
- Auto-continue workflows (multi-step execution)
- Progress attachment
- Activity summary generation
- Session cache write-back
- Evidence tap (Kimi bridge tracing)
"""

import logging
import os
import json
import glob
import time
from typing import Any, Dict, Callable, Optional
from mcp.types import TextContent

logger = logging.getLogger(__name__)


async def handle_files_required(
    result: list,
    arguments: Dict[str, Any],
    tool,
    tool_name: str,
    model_name: str,
    execute_with_monitor_func: Callable
) -> list:
    """
    Handle tools requesting files to continue (files_required_to_continue).
    
    Args:
        result: Current result list
        arguments: Tool arguments
        tool: Tool object
        tool_name: Tool name
        model_name: Resolved model name
        execute_with_monitor_func: Function to execute with monitoring
        
    Returns:
        Updated result list
    """
    try:
        _primary = result[-1] if isinstance(result, list) and result else None
        _text = None
        if _primary is not None:
            if isinstance(_primary, TextContent) and _primary.type == "text":
                _text = _primary.text or ""
            elif isinstance(_primary, dict):
                _text = _primary.get("text")
        if _text:
            try:
                _data = json.loads(_text)
            except Exception as e:
                logger.debug(f"Failed to parse result JSON: {e}")
                _data = None
            if isinstance(_data, dict) and str(_data.get("status", "")).lower() == "files_required_to_continue":
                _next = dict((_data.get("next_call") or {}).get("arguments") or {})
                _files = list(_next.get("files") or arguments.get("files") or [])
                if not _files:
                    _globs = _data.get("file_globs") or []
                    try:
                        from src.server.utils.file_context_resolver import resolve_files
                        resolved = resolve_files(_globs)
                        _files.extend(resolved)
                    except Exception as e:
                        logger.debug(f"File context resolver failed, using legacy globbing: {e}")
                        # Fallback to legacy best-effort globbing if resolver fails
                        for _g in list(_globs)[:8]:
                            try:
                                for p in glob.glob(_g, recursive=True)[:20]:
                                    if isinstance(p, str):
                                        _files.append(p)
                            except Exception as glob_err:
                                logger.debug(f"Failed to glob pattern '{_g}': {glob_err}")
                if not _files:
                    try:
                        from utils.cache import get_session_cache, make_session_key
                        _cache = get_session_cache()
                        _cid = arguments.get("continuation_id")
                        if _cid:
                            _cached = _cache.get(make_session_key(_cid)) or {}
                            _files = list(_cached.get("files") or [])
                    except Exception as e:
                        logger.debug(f"Failed to retrieve files from session cache: {e}")
                # CRITICAL FIX: Prevent infinite recursion loops
                # Check if we have new files to provide
                _prev_files = set(arguments.get("files") or [])
                _new_files = set(_files)

                if not _files:
                    # No files available - return error instead of recursing
                    logger.warning(f"[FILES-AUTO] Expert requested files but none available - returning error instead of recursing")
                    error_response = {
                        "status": "error",
                        "content": (
                            "Expert analysis requested additional files but none were available. "
                            "Please provide the requested files manually and try again."
                        ),
                        "files_requested": _data.get("files_needed") or [],
                        "instructions": _data.get("mandatory_instructions"),
                        "metadata": {"error_type": "files_not_available"}
                    }
                    return [TextContent(type="text", text=json.dumps(error_response, ensure_ascii=False))]

                if _prev_files == _new_files and _prev_files:
                    # Same files as before - would cause infinite loop
                    logger.warning(f"[FILES-AUTO] File list unchanged ({len(_files)} files) - breaking potential infinite loop")
                    error_response = {
                        "status": "error",
                        "content": (
                            "Expert analysis requested files that were already provided. "
                            "This indicates the analysis cannot proceed with the current information. "
                            "Please provide additional context or different files."
                        ),
                        "files_already_provided": sorted(list(_prev_files)),
                        "files_requested": _data.get("files_needed") or [],
                        "instructions": _data.get("mandatory_instructions"),
                        "metadata": {"error_type": "infinite_loop_prevented"}
                    }
                    return [TextContent(type="text", text=json.dumps(error_response, ensure_ascii=False))]

                # We have new files - safe to continue
                _next["files"] = sorted(list(dict.fromkeys(_files)))[:50]
                # ensure continuation_id and model
                if not _next.get("continuation_id"):
                    _cid = _data.get("continuation_id") or arguments.get("continuation_id")
                    if _cid:
                        _next["continuation_id"] = _cid
                _resolved_model = _next.get("model") or arguments.get("model") or model_name
                if str(_resolved_model or "").lower() == "auto":
                    _resolved_model = os.getenv("DEFAULT_MODEL", "glm-4.5-flash")
                _next["model"] = _resolved_model
                logger.info(f"[FILES-AUTO] Providing {len(_next.get('files') or [])} NEW files to {tool_name} and continuing (prev: {len(_prev_files)}, new: {len(_new_files)})")
                result = await execute_with_monitor_func(lambda: tool.execute(_next))
                if isinstance(result, TextContent):
                    result = [result]
                elif not isinstance(result, list):
                    try:
                        result = [TextContent(type="text", text=str(result))]
                    except Exception as e:
                        logger.debug(f"Failed to normalize result to TextContent: {e}")
                        result = []
    except Exception as _e:
        logger.debug(f"[FILES-AUTO] skipped/failed: {_e}")
    
    return result


async def auto_continue_workflows(
    result: list,
    arguments: Dict[str, Any],
    tool,
    tool_name: str,
    model_name: str,
    execute_with_monitor_func: Callable,
    env_true_func
) -> tuple[list, int]:
    """
    Auto-continue workflow tools if enabled (env-gated).
    
    Args:
        result: Current result list
        arguments: Tool arguments
        tool: Tool object
        tool_name: Tool name
        model_name: Resolved model name
        execute_with_monitor_func: Function to execute with monitoring
        env_true_func: Function to check environment variables
        
    Returns:
        Tuple of (updated_result, steps_completed)
    """
    steps = 0
    try:
        auto_en = env_true_func("EX_AUTOCONTINUE_WORKFLOWS", "false")
        only_think = env_true_func("EX_AUTOCONTINUE_ONLY_THINKDEEP", "true")
        max_steps = int(os.getenv("EX_AUTOCONTINUE_MAX_STEPS", "3"))
        # Apply optional per-client workflow step cap (generic with legacy fallback)
        try:
            cap = int((os.getenv("CLIENT_MAX_WORKFLOW_STEPS") or os.getenv("CLAUDE_MAX_WORKFLOW_STEPS", "0") or "0"))
            if cap > 0:
                max_steps = min(max_steps, cap)
        except Exception as e:
            logger.debug(f"Failed to parse workflow step cap: {e}")
        
        if auto_en and isinstance(result, list) and result:
            while steps < max_steps:
                primary = result[-1]
                text = None
                if isinstance(primary, TextContent) and primary.type == "text":
                    text = primary.text or ""
                elif isinstance(primary, dict):
                    text = primary.get("text")
                if not text:
                    break
                try:
                    data = json.loads(text)
                except Exception as e:
                    logger.debug(f"Failed to parse workflow result JSON: {e}")
                    break
                status = str(data.get("status", ""))
                if not status.startswith("pause_for_"):
                    break
                if only_think and tool_name != "thinkdeep":
                    break
                next_call = data.get("next_call") or {}
                next_args = dict(next_call.get("arguments") or {})
                if not next_args:
                    break
                # Ensure continuation and model are present
                if not next_args.get("continuation_id"):
                    cid = data.get("continuation_id") or arguments.get("continuation_id")
                    if cid:
                        next_args["continuation_id"] = cid
                if not next_args.get("model"):
                    next_args["model"] = arguments.get("model") or model_name
                # Execute next step directly
                logger.info(f"[AUTO-CONTINUE] Executing next step for {tool_name}: step_number={next_args.get('step_number')}")
                result = await execute_with_monitor_func(lambda: tool.execute(next_args))
                # Normalize result shape for auto-continued step
                if isinstance(result, TextContent):
                    result = [result]
                elif not isinstance(result, list):
                    try:
                        result = [TextContent(type="text", text=str(result))]
                    except Exception as e:
                        logger.debug(f"Failed to normalize workflow result to TextContent: {e}")
                        result = []
                steps += 1
    except Exception as _e:
        logger.debug(f"[AUTO-CONTINUE] skipped/failed: {_e}")
    
    return result, steps


def attach_progress_and_summary(
    result: list,
    arguments: Dict[str, Any],
    tool_name: str,
    model_name: str,
    req_id: str,
    overall_start: float,
    workflow_steps_completed: int
) -> list:
    """
    Attach progress log and activity summary to result.
    
    Args:
        result: Current result list
        arguments: Tool arguments
        tool_name: Tool name
        model_name: Resolved model name
        req_id: Request ID
        overall_start: Start time
        workflow_steps_completed: Number of workflow steps completed
        
    Returns:
        Updated result with progress and summary
    """
    try:
        from utils.progress import get_progress_log
        from utils.model.token_utils import estimate_tokens as __est_tokens
        
        progress_log = get_progress_log()
        if isinstance(result, list) and result:
            primary = result[-1]
            progress_block = None
            if progress_log:
                progress_block = "\n".join(["[PROGRESS] " + p for p in progress_log])
                if isinstance(primary, TextContent) and primary.type == "text":
                    text = primary.text or ""
                    try:
                        data = json.loads(text)
                    except Exception as e:
                        logger.debug(f"Failed to parse progress JSON: {e}")
                        data = None
                    if isinstance(data, dict):
                        data.setdefault("metadata", {})["progress"] = progress_log
                        try:
                            if isinstance(data.get("content"), str):
                                data["content"] = f"=== PROGRESS ===\n{progress_block}\n=== END PROGRESS ===\n\n" + data["content"]
                            else:
                                data["progress_text"] = progress_block
                        except Exception as e:
                            logger.debug(f"Failed to inject progress into content: {e}")
                            data["progress_text"] = progress_block
                        primary.text = json.dumps(data, ensure_ascii=False)
            
            # Always include a visible activity summary block for UI dropdowns
            try:
                tail = f"=== PROGRESS ===\n{progress_block}\n=== END PROGRESS ===" if progress_block else "(no progress captured)"
                
                # Build MCP CALL SUMMARY
                __total_dur = max(0.0, time.time() - overall_start)
                __last_text = None
                try:
                    __primary = result[-1] if isinstance(result, list) and result else None
                    if isinstance(__primary, TextContent):
                        __last_text = __primary.text or ""
                    elif isinstance(__primary, dict):
                        __last_text = __primary.get("text")
                except Exception as e:
                    logger.debug(f"Failed to extract last text from result: {e}")
                    __last_text = None
                __meta = {}
                try:
                    if __last_text:
                        __meta = json.loads(__last_text)
                    else:
                        __meta = {}
                except Exception as e:
                    logger.debug(f"Failed to parse metadata JSON: {e}")
                    __meta = {}
                __next_req = bool(__meta.get("next_step_required") is True)
                __status = str(__meta.get("status") or ("pause_for_analysis" if __next_req else "ok")).upper()
                __step_no = __meta.get("step_number") or workflow_steps_completed
                __total_steps = __meta.get("total_steps")
                __cid = __meta.get("continuation_id") or arguments.get("continuation_id")
                __model_used = arguments.get("model") or model_name
                try:
                    __tokens = 0
                    for __blk in (result or []):
                        if isinstance(__blk, TextContent):
                            __tokens += __est_tokens(__blk.text or "")
                        elif isinstance(__blk, dict):
                            __tokens += __est_tokens(str(__blk.get("text") or ""))
                except Exception as e:
                    logger.debug(f"Failed to estimate token count: {e}")
                    __tokens = 0
                __expert_flag = bool(arguments.get("use_assistant_model") or __meta.get("use_assistant_model"))
                if __expert_flag:
                    __expert_status = "Pending" if __next_req else "Completed"
                else:
                    __expert_status = "Disabled"
                __status_label = "WORKFLOW_PAUSED" if __next_req or (__status.startswith("PAUSE_FOR_")) else "COMPLETE"
                __next_action = f"Continue with step {((__step_no or 0) + 1)}" if __next_req else "None"
                __summary_text = (
                    "=== MCP CALL SUMMARY ===\n"
                    f"Tool: {tool_name} | Status: {__status_label} (Step {__step_no}/{__total_steps or '?'} complete)\n"
                    f"Duration: {__total_dur:.1f}s | Model: {__model_used} | Tokens: ~{__tokens}\n"
                    f"Continuation ID: {__cid or '-'}\n"
                    f"Next Action Required: {__next_action}\n"
                    f"Expert Validation: {__expert_status}\n"
                    "=== END SUMMARY ==="
                )
                
                # Append summary as new TextContent block
                result.append(TextContent(type="text", text=f"\n{__summary_text}\n\n{tail}\nreq_id={req_id}"))
            except Exception as _e:
                logger.debug(f"[SUMMARY] generation failed: {_e}")
    except Exception as _e:
        logger.debug(f"[PROGRESS] attachment failed: {_e}")
    
    return result


def write_session_cache(arguments: Dict[str, Any]):
    """
    Write-back compact summary to session cache.
    
    Args:
        arguments: Tool arguments (may contain continuation_id)
    """
    try:
        cont_id = arguments.get("continuation_id")
        if cont_id:
            from utils.cache import get_session_cache, make_session_key
            cache = get_session_cache()
            skey = make_session_key(cont_id)
            cached = cache.get(skey) or {}
            # Compose compact summary (non-invasive; placeholders)
            # This is a simplified version - full implementation would include more details
            cached["last_updated"] = time.time()
            cache.set(skey, cached)
            logger.debug(f"[CACHE] write-back for {skey}")
    except Exception as _e:
        logger.debug(f"[CACHE] write-back skipped/failed: {_e}")


# Export public API
__all__ = [
    'handle_files_required',
    'auto_continue_workflows',
    'attach_progress_and_summary',
    'write_session_cache',
]

