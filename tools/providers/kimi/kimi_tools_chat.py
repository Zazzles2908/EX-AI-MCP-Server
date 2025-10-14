from __future__ import annotations
import json
import os
from typing import Any, Dict, List
from mcp.types import TextContent
from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from src.providers.kimi import KimiModelProvider
from src.providers.registry import ModelProviderRegistry
from src.providers.base import ProviderType

class KimiChatWithToolsTool(BaseTool):
    def get_name(self) -> str:
        return "kimi_chat_with_tools"

    def get_description(self) -> str:
        return (
            "Call Kimi chat completion with optional tools/tool_choice. Can auto-inject an internet tool based on env.\n"
            "Examples:\n"
            "- {\"messages\":[\"Summarize README.md\"], \"model\":\"auto\"}\n"
            "- {\"messages\":[\"research X\"], \"use_websearch\":true, \"tool_choice\":\"auto\"}"
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "messages": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"oneOf": [{"type": "string"}, {"type": "object"}]}}
                    ]
                },
                "model": {"type": "string", "default": os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")},
                "tools": {"type": "array", "items": {"type": "object"}},
                "tool_choice": {"oneOf": [{"type": "string"}, {"type": "object"}]},
                "temperature": {"type": "number", "default": 0.6},
                "stream": {"type": "boolean", "default": False},
                # Fixed: use_websearch (without $ prefix)
                "use_websearch": {"type": "boolean", "default": False},
            },
            "required": ["messages"],
            "additionalProperties": False,
        }

    def get_system_prompt(self) -> str:
        return (
            "You are the EX-AI MCP Kimi chat orchestrator with tool-use support.\n"
            "Purpose: Call Kimi chat completions with optional tools/tool_choice under EX-AI routing.\n\n"
            "Parameters:\n"
            "- messages: OpenAI-compatible message array.\n"
            "- model: Kimi model id (default via KIMI_DEFAULT_MODEL). Non-Kimi (e.g., 'auto') will be remapped.\n"
            "- tools: Optional OpenAI tools spec array; may be auto-injected from env.\n"
            "- tool_choice: 'auto'|'none'|'required' or provider-specific structure.\n"
            "- temperature, stream (SSE).\n\n"
            "Provider Features:\n"
            "- use_websearch: When True, inject Kimi's built-in $web_search tool via capabilities layer (env-gated).\n"
            "- File context: Prefer kimi_upload_and_extract / kimi_multi_file_chat for ingestion before chat.\n\n"
            "Streaming & Observability:\n"
            "- If stream=true, responses may include metadata.streamed=true and partial content; a non-stream follow-up may finalize.\n"
            "- Context-cache and idempotency headers may be attached automatically (do not expose secrets).\n\n"
            "Output: Return raw provider JSON (choices, usage, tool_calls if any). Keep responses concise and on-task."
        )

    def get_request_model(self):
        return ToolRequest

    def requires_model(self) -> bool:
        return False

    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""

    def format_response(self, response: str, request: ToolRequest, model_info: dict | None = None) -> str:
        return response

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        # Resolve provider instance from registry; force Kimi provider and model id
        requested_model = arguments.get("model") or os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
        # Map any non-Kimi requests (e.g., 'auto', 'glm-4.5-flash') to a valid Kimi default
        if requested_model not in {"kimi-k2-0711-preview","kimi-k2-0905-preview","kimi-k2-turbo-preview","kimi-latest","kimi-thinking-preview","moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k","moonshot-v1-8k-vision-preview","moonshot-v1-32k-vision-preview","moonshot-v1-128k-vision-preview"}:
            requested_model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")

        prov = ModelProviderRegistry.get_provider(ProviderType.KIMI)
        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Observability: log final provider/model and flags (debug-level, no secrets)
        try:
            import logging
            logging.getLogger("kimi_tools_chat").info(
                "KimiChatWithTools: provider=KIMI model=%s stream=%s use_web=%s tools=%s tool_choice=%s",
                requested_model,
                stream_flag if 'stream_flag' in locals() else None,
                bool(arguments.get("use_websearch", False)),
                bool(tools),
                tool_choice,
            )
        except Exception:
            pass

        # Normalize tools and tool_choice
        tools = arguments.get("tools")
        tool_choice = arguments.get("tool_choice")
        # Accept JSON strings for tools and normalize to list/dict per OpenAI schema
        if isinstance(tools, str):
            try:
                tools = json.loads(tools)
            except Exception:
                tools = None  # let provider run without tools rather than 400
        # Normalize tools into list[dict] per provider schema
        if isinstance(tools, list):
            coerced: list[dict] = []
            for it in tools:
                if isinstance(it, dict):
                    coerced.append(it)
                elif isinstance(it, str):
                    nm = it.strip()
                    if nm.startswith("$"):
                        # Builtin function shorthand like "$web_search"
                        coerced.append({"type": "builtin_function", "function": {"name": nm}})
                    else:
                        # Drop unrecognized string tool spec to avoid provider 400s
                        continue
                else:
                    # Unsupported type - drop
                    continue
            tools = coerced or None
        elif tools is not None and not isinstance(tools, list):
            tools = [tools] if isinstance(tools, dict) else None

        # Standardize tool_choice to allowed strings when a complex object isn't provided
        if isinstance(tool_choice, str):
            lc = tool_choice.strip().lower()
            if lc in {"auto", "none", "required"}:
                tool_choice = lc
            else:
                tool_choice = None

        # Websearch tool injection via provider capabilities layer for consistency
        # CRITICAL FIX (Bug #2): Respect explicit user choice first, then fall back to env defaults
        use_websearch_arg = arguments.get("use_websearch")
        if use_websearch_arg is not None:
            # User explicitly set use_websearch - respect their choice (even if False)
            use_websearch = bool(use_websearch_arg)
        else:
            # No explicit choice - use environment variable defaults
            use_websearch = (
                os.getenv("KIMI_ENABLE_INTERNET_TOOL", "false").strip().lower() == "true" or
                os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "false").strip().lower() == "true"
            )
        if use_websearch:
            try:
                from src.providers.capabilities import get_capabilities_for_provider
                caps = get_capabilities_for_provider(ProviderType.KIMI)
                ws = caps.get_websearch_tool_schema({"use_websearch": True})
                if ws.tools:
                    tools = (tools or []) + ws.tools
                if tool_choice is None and ws.tool_choice is not None:
                    tool_choice = ws.tool_choice
            except Exception:
                # If capabilities lookup fails, proceed without injecting tools
                pass

        # Normalize messages into OpenAI-style list of {role, content}
        raw_msgs = arguments.get("messages")

        def _coerce_message(item: Any) -> dict | None:
            try:
                # Return a normalized {role, content} or None to drop
                if item is None:
                    return None
                if isinstance(item, str):
                    txt = item.strip()
                    return {"role": "user", "content": txt} if txt else None
                if isinstance(item, dict):
                    role = str(item.get("role") or "user").strip() or "user"
                    content = item.get("content")
                    if content is None and "text" in item:
                        content = item.get("text")
                    # Some SDKs wrap content in arrays/objects; coerce conservatively
                    if isinstance(content, (list, dict)):
                        try:
                            import json as _json
                            content = _json.dumps(content, ensure_ascii=False)
                        except Exception:
                            content = str(content)
                    txt = ("" if content is None else str(content)).strip()
                    return {"role": role, "content": txt} if txt else None
                # Fallback coercion for unknown types
                txt = str(item).strip()
                return {"role": "user", "content": txt} if txt else None
            except Exception:
                return None

        norm_msgs: list[dict[str, Any]] = []
        if isinstance(raw_msgs, str):
            m = _coerce_message(raw_msgs)
            if m:
                norm_msgs.append(m)
        elif isinstance(raw_msgs, list):
            for it in raw_msgs:
                m = _coerce_message(it)
                if m:
                    norm_msgs.append(m)
        elif raw_msgs is not None:
            m = _coerce_message(raw_msgs)
            if m:
                norm_msgs.append(m)

        # Validation: must contain at least one non-empty 'user' message
        if not norm_msgs:
            err = {
                "status": "invalid_request",
                "error": "No non-empty messages provided. Provide at least one user message with non-empty content.",
            }
            return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]

        import asyncio as _aio
        # Enable streaming when explicitly requested or when KIMI_STREAM_ENABLED=true (default false)
        env_stream = os.getenv("KIMI_STREAM_ENABLED", "false").strip().lower() in ("1", "true", "yes")
        stream_flag = bool(arguments.get("stream", os.getenv("KIMI_CHAT_STREAM_DEFAULT", "false").strip().lower() == "true") or env_stream)
        model_used = requested_model

        if stream_flag:
            # For web-enabled flows, prefer the non-stream tool-call loop for reliability (handles tool_calls)
            if bool(arguments.get("use_websearch", False)):
                stream_flag = False
            else:
                # Optional: prime context-cache token via quick non-stream call (env-gated)
                try:
                    prime_ok = os.getenv("KIMI_STREAM_PRIME_CACHE", "false").strip().lower() in ("1","true","yes")
                    if prime_ok:
                        # Only when no token is present yet
                        sid = arguments.get("_session_id")
                        if sid:
                            import hashlib as _hash
                            parts = []
                            for m in norm_msgs[:6]:
                                parts.append(str(m.get("role","")) + "\n" + str(m.get("content",""))[:2048])
                            pf = _hash.sha256("\n".join(parts).encode("utf-8", errors="ignore")).hexdigest()
                            existing = getattr(prov, "get_cache_token", lambda *a, **k: None)(sid, "kimi_chat_with_tools", pf)
                            if not existing:
                                # Prime using provider wrapper (captures token via headers)
                                _ = await _aio.to_thread(
                                    lambda: prov.chat_completions_create(
                                        model=model_used,
                                        messages=norm_msgs[:max(1, min(3, len(norm_msgs)))],
                                        tools=None,
                                        tool_choice=None,
                                        temperature=float(arguments.get("temperature", 0.6)),
                                        _session_id=sid,
                                        _call_key=arguments.get("_call_key") or arguments.get("call_key"),
                                        _tool_name=self.get_name(),
                                    )
                                )
                except Exception:
                    pass

                # Handle streaming in a background thread via shared adapter; accumulate content (no tool_calls loop in stream mode)
                def _stream_call():
                    extra_headers = {"Msh-Trace-Mode": "on"}
                    try:
                        # Defensive header length cap to avoid NGINX 400 on large headers
                        try:
                            max_hdr_len = int(os.getenv("KIMI_MAX_HEADER_LEN", "4096"))
                        except Exception:
                            max_hdr_len = 4096
                        def _safe_set(hname: str, hval: str):
                            try:
                                if not hval:
                                    return
                                if max_hdr_len > 0 and len(hval) > max_hdr_len:
                                    # Drop overly large headers rather than sending
                                    return
                                extra_headers[hname] = hval
                            except Exception:
                                pass
                        ck = arguments.get("_call_key") or arguments.get("call_key")
                        if ck:
                            _safe_set("Idempotency-Key", str(ck))
                        sid = arguments.get("_session_id")
                        ctok = getattr(prov, "get_cache_token", None)
                        if ctok and sid:
                            import hashlib
                            parts = []
                            for m in norm_msgs[:6]:
                                parts.append(str(m.get("role","")) + "\n" + str(m.get("content",""))[:2048])
                            pf = hashlib.sha256("\n".join(parts).encode("utf-8", errors="ignore")).hexdigest()
                            t = prov.get_cache_token(sid, "kimi_chat_with_tools", pf)
                            if t:
                                _safe_set("Msh-Context-Cache-Token", t)
                    except Exception:
                        pass
                    # Use centralized adapter
                    from streaming.streaming_adapter import stream_openai_chat_events
                    # Build kwargs without None entries for provider compliance
                    _ckw = {
                        "model": model_used,
                        "messages": norm_msgs,
                        "temperature": float(arguments.get("temperature", 0.6)),
                        "extra_headers": (extra_headers or None),
                    }
                    if tools:
                        _ckw["tools"] = tools
                    if tools and tool_choice is not None:
                        _ckw["tool_choice"] = tool_choice
                    return stream_openai_chat_events(
                        client=prov.client,
                        create_kwargs=_ckw,
                    )

                # Apply overall streaming timeout (env: KIMI_STREAM_TIMEOUT_SECS)
                try:
                    timeout_secs = float(os.getenv("KIMI_STREAM_TIMEOUT_SECS", "240"))
                except Exception:
                    timeout_secs = 240.0
                try:
                    content_text, raw_stream = await _aio.wait_for(_aio.to_thread(_stream_call), timeout=timeout_secs)
                except _aio.TimeoutError:
                    err = {"status": "execution_error", "error": f"Kimi streaming timed out after {int(timeout_secs)}s"}
                    return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]

                normalized = {
                    "provider": "KIMI",
                    "model": model_used,
                    "content": content_text,
                    "tool_calls": None,
                    "usage": None,
                    "raw": {"stream": True, "items": [str(it) for it in raw_stream[:10]]},
                }
                return [TextContent(type="text", text=json.dumps(normalized, ensure_ascii=False))]
        else:
            # Non-streaming with minimal tool-call loop for function web_search
            import copy
            import urllib.parse, urllib.request

            # Debug trace helper: write last payload to .logs when enabled
            def _emit_trace(payload: dict):
                try:
                    import os, json
                    os.makedirs('.logs', exist_ok=True)
                    with open('.logs/kimi_tool_last.json', 'w', encoding='utf-8') as f:
                        json.dump(payload, f, ensure_ascii=False)
                except Exception:
                    pass

            def _is_trace_enabled() -> bool:
                try:
                    # Default ON to capture evidence unless explicitly disabled
                    return bool(arguments.get("debug_trace", False)) or os.getenv("KIMI_TOOLTRACE", "1").strip().lower() in ("1","true","yes")
                except Exception:
                    return True

            def _extract_tool_calls(raw_any: any) -> list[dict] | None:
                """Robustly extract tool_calls from provider payloads.
                Handles dicts or model objects, and falls back to function_call.
                """
                try:
                    import json
                    def _to_dict(x):
                        if x is None:
                            return None
                        if isinstance(x, dict):
                            return x
                        if hasattr(x, "model_dump"):
                            try:
                                return x.model_dump()
                            except Exception:
                                pass
                        try:
                            return {k: getattr(x, k) for k in dir(x) if not k.startswith("_")}
                        except Exception:
                            return None

                    payload = raw_any
                    if hasattr(payload, "model_dump"):
                        try:
                            payload = payload.model_dump()
                        except Exception:
                            payload = _to_dict(payload)
                    choices = (payload or {}).get("choices") or []
                    if not choices:
                        return None
                    ch0 = choices[0]
                    ch0 = _to_dict(ch0) or ch0
                    msg = (ch0.get("message") if isinstance(ch0, dict) else None) or {}

                    # 1) Direct tool_calls on message
                    tcs = None
                    if isinstance(msg, dict):
                        tcs = msg.get("tool_calls")
                    if tcs is None and not isinstance(msg, dict):
                        tcs = getattr(msg, "tool_calls", None)

                    # 2) Fallback: legacy single function_call
                    if not tcs:
                        fc = (msg.get("function_call") if isinstance(msg, dict) else getattr(msg, "function_call", None))
                        if fc:
                            fc = _to_dict(fc) or fc
                            name = (fc.get("name") if isinstance(fc, dict) else getattr(fc, "name", None)) or ""
                            args = (fc.get("arguments") if isinstance(fc, dict) else getattr(fc, "arguments", None))
                            if args is None:
                                args = ""
                            if not isinstance(args, str):
                                try:
                                    args = json.dumps(args, ensure_ascii=False)
                                except Exception:
                                    args = str(args)
                            return [{"type": "function", "id": None, "function": {"name": name, "arguments": args}}]

                    if not tcs:
                        return None

                    # 3) Normalize tool_calls to plain dicts
                    norm: list[dict] = []
                    for tc in tcs:
                        tcd = _to_dict(tc) or tc
                        if not isinstance(tcd, dict):
                            continue
                        fn = tcd.get("function")
                        if fn is not None and not isinstance(fn, dict):
                            fn = _to_dict(fn) or {}
                            tcd["function"] = fn
                        norm.append(tcd)
                    return norm if norm else None
                except Exception:
                    return None

            def _run_web_search_backend(query: str) -> dict:
                # Pluggable backend controlled by env SEARCH_BACKEND: duckduckgo | tavily | bing
                backend = os.getenv("SEARCH_BACKEND", "duckduckgo").strip().lower()
                try:
                    if backend == "tavily":
                        api_key = os.getenv("TAVILY_API_KEY", "").strip()
                        if not api_key:
                            raise RuntimeError("TAVILY_API_KEY not set")
                        payload = json.dumps({"api_key": api_key, "query": query, "max_results": 5}).encode("utf-8")
                        req = urllib.request.Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req, timeout=25) as resp:
                            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                            results = []
                            for it in (data.get("results") or [])[:5]:
                                url = it.get("url") or it.get("link")
                                if url:
                                    results.append({"title": it.get("title") or it.get("snippet"), "url": url})
                            return {"engine": "tavily", "query": query, "results": results}
                    if backend == "bing":
                        key = os.getenv("BING_SEARCH_API_KEY", "").strip()
                        if not key:
                            raise RuntimeError("BING_SEARCH_API_KEY not set")
                        q = urllib.parse.urlencode({"q": query})
                        req = urllib.request.Request(f"https://api.bing.microsoft.com/v7.0/search?{q}")
                        req.add_header("Ocp-Apim-Subscription-Key", key)
                        with urllib.request.urlopen(req, timeout=25) as resp:
                            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                            results = []
                            for it in (data.get("webPages", {}).get("value", [])[:5]):
                                if it.get("url"):
                                    results.append({"title": it.get("name"), "url": it.get("url")})
                            return {"engine": "bing", "query": query, "results": results}
                    # Default: DuckDuckGo Instant Answer API
                    q = urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "skip_disambig": 1})
                    url = f"https://api.duckduckgo.com/?{q}"
                    with urllib.request.urlopen(url, timeout=20) as resp:
                        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        results = []
                        if data.get("AbstractURL"):
                            results.append({"title": data.get("Heading"), "url": data.get("AbstractURL")})
                        for item in (data.get("RelatedTopics") or [])[:5]:
                            if isinstance(item, dict) and item.get("FirstURL"):
                                results.append({"title": item.get("Text"), "url": item.get("FirstURL")})
                        return {"engine": "duckduckgo", "query": query, "results": results[:5]}
                except Exception as e:
                    return {"engine": backend or "duckduckgo", "query": query, "error": str(e), "results": []}

            messages_local = copy.deepcopy(norm_msgs)

            for _ in range(3):  # limit tool loop depth
                def _call():
                    return prov.chat_completions_create(
                        model=model_used,
                        messages=messages_local,
                        tools=tools,
                        tool_choice=tool_choice,
                        temperature=float(arguments.get("temperature", 0.6)),
                        _session_id=arguments.get("_session_id"),
                        _call_key=arguments.get("_call_key"),
                        _tool_name=self.get_name(),
                    )
                # Apply per-call timeout to avoid long hangs on web-enabled prompts
                # Choose timeout based on whether web search is enabled
                try:
                    if bool(arguments.get("use_websearch", False)):
                        timeout_secs = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS", "300"))
                    else:
                        timeout_secs = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_SECS", "180"))
                except Exception:
                    timeout_secs = 180.0
                try:
                    result = await _aio.wait_for(_aio.to_thread(_call), timeout=timeout_secs)
                except _aio.TimeoutError:
                    err = {"status": "execution_error", "error": f"Kimi chat timed out after {int(timeout_secs)}s"}
                    return [TextContent(type="text", text=json.dumps(err, ensure_ascii=False))]

                # If no tool calls, return normalized assistant content immediately
                tcs = _extract_tool_calls(result.get("raw")) if isinstance(result, dict) else None
                if not tcs:
                    _dbg = _is_trace_enabled()
                    try:
                        raw_payload = result.get("raw") if isinstance(result, dict) else None
                        if hasattr(raw_payload, "model_dump"):
                            raw_payload = raw_payload.model_dump()
                        choices = (raw_payload or {}).get("choices") or []
                        msg = (choices[0].get("message") if choices else {}) or {}
                        content_text = (msg.get("content") or "") if isinstance(msg, dict) else ""
                        normalized = {
                            "provider": "KIMI",
                            "model": model_used,
                            "content": content_text,
                            "tool_calls": None,
                            "usage": result.get("usage") if isinstance(result, dict) else None,
                            "raw": raw_payload or (result.get("raw") if isinstance(result, dict) else {}),
                        }
                        if _dbg:
                            summary = {
                                "status": "no_tool_calls",
                                "content_preview": (content_text or "")[:256],
                                "has_tool_calls_field": bool((msg or {}).get("tool_calls")) if isinstance(msg, dict) else False,
                            }
                            _emit_trace({"normalized": normalized, "trace": summary})
                        return [TextContent(type="text", text=json.dumps(normalized, ensure_ascii=False))]
                    except Exception:
                        # Fallback to returning the original provider result for visibility
                        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

                # Append the assistant message that requested tool calls so provider can correlate tool_call_id
                try:
                    raw_payload = result.get("raw") if isinstance(result, dict) else None
                    if hasattr(raw_payload, "model_dump"):
                        raw_payload = raw_payload.model_dump()
                    choices = (raw_payload or {}).get("choices") or []
                    msg = (choices[0].get("message") if choices else {}) or {}
                    assistant_content = msg.get("content") or ""
                    # Preserve tool_calls exactly as returned by provider
                    assistant_msg = {"role": "assistant", "content": assistant_content, "tool_calls": tcs}
                    messages_local.append(assistant_msg)
                except Exception:
                    # If anything goes wrong, still try to proceed with tool messages
                    pass

                # Execute supported tools locally (function web_search)
                tool_msgs = []
                for tc in tcs:
                    try:
                        fn = tc.get("function") or {}
                        fname = (fn.get("name") or "").strip()
                        fargs_raw = fn.get("arguments")
                        fargs = {}
                        if isinstance(fargs_raw, str):
                            try:
                                fargs = json.loads(fargs_raw)
                            except Exception:
                                fargs = {"query": fargs_raw}
                        elif isinstance(fargs_raw, dict):
                            fargs = fargs_raw

                        if fname in ("web_search",):
                            query = fargs.get("query") or ""
                            res = _run_web_search_backend(query)
                            tool_msgs.append({
                                "role": "tool",
                                "tool_call_id": str(tc.get("id") or tc.get("tool_call_id") or (tc.get("function",{}).get("id") if isinstance(tc.get("function"), dict) else "")) or "tc-0",
                                "content": json.dumps(res, ensure_ascii=False),
                            })
                        else:
                            # Unsupported tool - return partial with hint
                            return [TextContent(type="text", text=json.dumps({
                                "status": "tool_call_pending",
                                "note": f"Unsupported tool {fname}. Supported: web_search.",
                                "raw": result.get("raw"),
                            }, ensure_ascii=False))]
                    except Exception as e:
                        return [TextContent(type="text", text=json.dumps({
                            "status": "tool_call_error",
                            "error": str(e),
                            "raw": result.get("raw"),
                        }, ensure_ascii=False))]

                # Append tool messages and continue the loop
                messages_local.extend(tool_msgs)

            # If we exit loop due to depth, return last result
            return [TextContent(type="text", text=json.dumps({
                "status": "max_tool_depth_reached",
                "raw": result if isinstance(result, dict) else {},
            }, ensure_ascii=False))]
