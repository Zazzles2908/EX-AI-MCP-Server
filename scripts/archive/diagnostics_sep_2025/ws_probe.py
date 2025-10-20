import asyncio
import json
import os
import sys
import uuid

# Load .env for direct vendor fallbacks
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import websockets
import requests

HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
PORT = int(os.getenv("EXAI_WS_PORT", "8765"))
TOKEN = os.getenv("EXAI_WS_TOKEN", "")

TEST_FILE = os.getenv(
    "EXAI_KIMI_TEST_FILE",
    "docs/external_review/20250927_impl_validation_mcp_raw.md",
)


REPORT_PATH = os.getenv("WS_PROBE_REPORT", "docs/external_review/20250928_ws_probe_run.md")

from datetime import datetime, timezone
from pathlib import Path
import re

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s)[:120]

def _raw_dir() -> Path:
    d = Path("docs/System_layout/_raw")
    d.mkdir(parents=True, exist_ok=True)
    return d

def _write_artifact(tool: str, label: str, payload: dict, outputs: list) -> Path:
    path = _raw_dir() / f"ws_probe_{tool}_{_safe_name(label)}_{_ts()}.json"
    data = {
        "tool": tool,
        "label": label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": payload,
        "outputs": outputs,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _p(f"[probe] saved → {path}")
    return path

def _extract_text_outputs(outputs: list) -> list[str]:
    texts: list[str] = []
    for o in outputs or []:
        if isinstance(o, dict) and o.get("type") == "text" and isinstance(o.get("text"), str):
            texts.append(o["text"])
    return texts

def _parse_first_json(texts: list[str]) -> dict | list | None:
    for t in texts:
        try:
            return json.loads(t)
        except Exception:
            # Try find first JSON object
            m = re.search(r"\{[\s\S]*\}", t)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
    return None

def _validate_glm_web_search(result: dict | list | None, query: str) -> tuple[bool, str, dict]:
    if not isinstance(result, (dict, list)):
        return False, "Result is not JSON", {}
    data = result if isinstance(result, dict) else {"data": result}
    # Try multiple common fields
    candidates = (data.get("search_results") or data.get("search_result") or data.get("results") or data.get("data") or data.get("items"))
    if not isinstance(candidates, list):
        # Some providers may nest deeper
        for k in ("result", "response", "output", "payload"):
            v = data.get(k)
            if isinstance(v, dict):
                inner = v.get("results") or v.get("items")
                if isinstance(inner, list):
                    candidates = inner
                    break
    if not isinstance(candidates, list):
        return False, "No results list found in response", {"keys": list(data.keys())[:10]}
    # Check a few entries for url/title/snippet
    found = 0
    with_url = 0
    with_title = 0
    with_snippet = 0
    recent_hits = 0
    now = datetime.now(timezone.utc)
    for it in candidates[:10]:
        if isinstance(it, dict):
            found += 1
            if any(k in it for k in ("url", "link", "href")):
                with_url += 1
            if any(k in it for k in ("title", "name", "headline")):
                with_title += 1
            if any(k in it for k in ("snippet", "summary", "content", "description")):
                with_snippet += 1
            # recency
            for dk in ("date", "published_at", "publish_time", "time", "timestamp"):
                val = it.get(dk)
                if isinstance(val, str):
                    try:
                        # Try parse ISO-like
                        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                        if (now - dt).days <= 365:
                            recent_hits += 1
                            break
                    except Exception:
                        pass
    ok = found > 0 and with_url > 0 and with_title > 0 and with_snippet > 0
    reason = f"entries={found}, url={with_url}, title={with_title}, snippet={with_snippet}, recent_hits={recent_hits}"
    return ok, reason, {"entries": found, "with_url": with_url, "with_title": with_title, "with_snippet": with_snippet, "recent_hits": recent_hits}

def _validate_kimi_intent(result: dict | list | None) -> tuple[bool, str]:
    if not isinstance(result, (dict, list)):
        return False, "Result is not JSON"
    data = result if isinstance(result, dict) else (result[0] if result else {})
    required = ["needs_websearch", "complexity", "domain", "recommended_provider", "recommended_model", "streaming_preferred"]
    missing = [k for k in required if k not in data]
    if missing:
        return False, f"Missing fields: {missing}"
    # Basic type checks
    if not isinstance(data.get("needs_websearch"), bool):
        return False, "needs_websearch not boolean"
    if not isinstance(data.get("recommended_provider"), str):
        return False, "recommended_provider not string"
    return True, "ok"
def _scan_common_errors(texts: list[str]) -> list[str]:
    errs: list[str] = []
    patterns = [
        r"HTTP\s*401|unauthorized",
        r"HTTP\s*403|forbidden",
        r"HTTP\s*429|rate limit",
        r"timeout|timed out|deadline",
        r"invalid\s*json|malformed\s*json|jsondecodeerror",
    ]
    for t in texts:
        low = t.lower()
        for p in patterns:
            if re.search(p, low):
                errs.append(f"match '{p}' in: {t[:200]}")
                break
    return errs


def _p(msg: str):
    print(msg, flush=True)
    try:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


GLM_BASE = os.getenv("GLM_AGENT_API_URL", "https://api.z.ai/api/v1").rstrip("/")
GLM_KEY = os.getenv("GLM_API_KEY", "").strip()


def _try_agent_create() -> str | None:
    if not GLM_KEY:
        return None
    headers = {"Authorization": f"Bearer {GLM_KEY}", "Content-Type": "application/json"}
    # Try a few plausible endpoints; tolerate 404/400
    payloads = [
        {"name": "exai-temp-agent", "description": "temp agent for ws_probe", "variables": {}, "tools": []},
        {"agent_name": "exai-temp-agent", "description": "temp agent for ws_probe"},
    ]
    candidates = ["/agents/create", "/agent/create", "/agents/templates/create", "/agents/template/create"]
    for path in candidates:
        for body in payloads:
            try:
                r = requests.post(f"{GLM_BASE}{path}", headers=headers, data=json.dumps(body), timeout=30)
                if r.status_code // 100 == 2:
                    try:
                        data = r.json()
                        # Heuristics to find an id
                        for k in ("agent_id", "id", "data"):
                            if k in data and isinstance(data[k], (str, int)):
                                return str(data[k])
                            if k in data and isinstance(data[k], dict):
                                inner = data[k]
                                if "agent_id" in inner:
                                    return str(inner["agent_id"])
                    except Exception:
                        pass
            except Exception:
                pass
    return None


def _try_agent_delete(agent_id: str) -> None:
    if not GLM_KEY or not agent_id:
        return
    headers = {"Authorization": f"Bearer {GLM_KEY}", "Content-Type": "application/json"}
    bodies = [
        {"agent_id": agent_id},
    ]
    paths = [f"/agents/{agent_id}", "/agents/delete", "/agent/delete"]
    for path in paths:
        try:
            # Prefer DELETE when path contains id
            if "{" not in path and path.endswith(agent_id):
                r = requests.delete(f"{GLM_BASE}{path}", headers=headers, timeout=15)
            else:
                r = requests.post(f"{GLM_BASE}{path}", headers=headers, data=json.dumps(bodies[0]), timeout=15)
            if r.status_code // 100 == 2:
                return
        except Exception:
            continue


async def probe():
    uri = f"ws://{HOST}:{PORT}"
    _p(f"[probe] connecting to {uri}")
    async with websockets.connect(uri) as ws:
        rid = None
        # hello/auth
        await ws.send(
            json.dumps(
                {
                    "op": "hello",
                    "session_id": f"probe-{uuid.uuid4().hex[:8]}",
                    "token": TOKEN,
                }
            )
        )
        ack = json.loads(await ws.recv())
        if not ack.get("ok"):
            raise SystemExit(f"[probe] auth failed: {ack}")
        _p("[probe] hello ok")

        # list_tools
        await ws.send(json.dumps({"op": "list_tools"}))
        tools_msg = json.loads(await ws.recv())
        tools = tools_msg.get("tools", [])
        names = sorted([t.get("name") for t in tools])
        _p(f"[probe] tools ({len(names)}): {names[:20]}{'...' if len(names)>20 else ''}")
        _p(f"[probe] has glm_web_search: {'glm_web_search' in names}")

        # version
        if "version" in names:
            rid = uuid.uuid4().hex
            await ws.send(
                json.dumps({"op": "call_tool", "request_id": rid, "name": "version", "arguments": {}})
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    _p(f"[probe] version preview: {str(msg.get('outputs'))[:160]}")
                    break

        # listmodels
        if "listmodels" in names:
            rid = uuid.uuid4().hex
            await ws.send(
                json.dumps({"op": "call_tool", "request_id": rid, "name": "listmodels", "arguments": {}})
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    _p(f"[probe] listmodels preview: {str(msg.get('outputs'))[:200]}")
                    break

        # small GLM web_search via Chat tool
        if "chat" in names:
            rid = uuid.uuid4().hex
            args = {
                "prompt": "Quick check: what is the capital of Japan?",
                "use_websearch": True,
                "model": "auto",
                "temperature": 0.2,
            }
            await ws.send(
                json.dumps({"op": "call_tool", "request_id": rid, "name": "chat", "arguments": args})
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    _p(f"[probe] chat(web) preview: {str(msg.get('outputs'))[:200]}")
                    break

        # direct GLM web_search tool if available (multiple test cases, full capture)
        if "glm_web_search" in names:
            web_tests = [
                {"label": "glm_news_recent", "args": {"search_query": "ZhipuAI GLM-4.5 latest announcement", "count": 5, "search_recency_filter": "oneMonth"}},
                {"label": "tech_python_asyncio", "args": {"search_query": "Python asyncio tutorial", "count": 5, "search_recency_filter": "oneYear"}},
            ]
            prev_first_json = None
            for case in web_tests:
                rid = uuid.uuid4().hex
                args = case["args"]
                await ws.send(json.dumps({"op": "call_tool", "request_id": rid, "name": "glm_web_search", "arguments": args}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                        if msg.get("error"):
                            _p(f"[probe] glm_web_search({case['label']}) ERROR: {msg.get('error')}")
                            _write_artifact("glm_web_search", case["label"], args, [msg.get("error")])
                        else:
                            outputs = msg.get("outputs") or []
                            texts = _extract_text_outputs(outputs)
                            # Full output emit (no truncation)
                            _p(f"[probe] glm_web_search({case['label']}) full outputs: {texts}")
                            # Error pattern scan
                            err_hits = _scan_common_errors(texts)
                            if err_hits:
                                _p(f"[probe] glm_web_search({case['label']}) ERROR_PATTERNS: {err_hits}")
                            _write_artifact("glm_web_search", case["label"], args, outputs)
                            parsed = _parse_first_json(texts)
                            ok, reason, metrics = _validate_glm_web_search(parsed, args.get("search_query", ""))
                            _p(f"[probe] glm_web_search({case['label']}) VALIDATION: ok={ok} reason={reason} metrics={metrics}")
                            # Detect dynamic variation across test cases
                            if prev_first_json is not None:
                                different = json.dumps(parsed, sort_keys=True) != json.dumps(prev_first_json, sort_keys=True)
                                _p(f"[probe] glm_web_search dynamic_variation_vs_prev: {different}")
                            prev_first_json = parsed
                        break

        # Kimi intent analysis if available (multiple prompts, full capture and validation)
        if "kimi_intent_analysis" in names:
            intent_tests = [
                {"label": "simple_math", "args": {"prompt": "What is 2+2?", "use_websearch": False}},
                {"label": "current_events", "args": {"prompt": "Summarize this week's major AI news with sources.", "use_websearch": True}},
                {"label": "domain_programming", "args": {"prompt": "Compare Python asyncio vs Trio for concurrency.", "use_websearch": True}},
            ]
            prev_json = None
            for case in intent_tests:
                rid = uuid.uuid4().hex
                args = case["args"]
                await ws.send(json.dumps({"op": "call_tool", "request_id": rid, "name": "kimi_intent_analysis", "arguments": args}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                        if msg.get("error"):
                            _p(f"[probe] kimi_intent_analysis({case['label']}) ERROR: {msg.get('error')}")
                            _write_artifact("kimi_intent_analysis", case["label"], args, [msg.get("error")])
                        else:
                            outputs = msg.get("outputs") or []
                            texts = _extract_text_outputs(outputs)
                            _p(f"[probe] kimi_intent_analysis({case['label']}) full outputs: {texts}")
                            # Error pattern scan
                            err_hits = _scan_common_errors(texts)
                            if err_hits:
                                _p(f"[probe] kimi_intent_analysis({case['label']}) ERROR_PATTERNS: {err_hits}")
                            _write_artifact("kimi_intent_analysis", case["label"], args, outputs)
                            parsed = _parse_first_json(texts)
                            ok, reason = _validate_kimi_intent(parsed)
                            _p(f"[probe] kimi_intent_analysis({case['label']}) VALIDATION: ok={ok} reason={reason}")
                            if prev_json is not None:
                                different = json.dumps(parsed, sort_keys=True) != json.dumps(prev_json, sort_keys=True)
                                _p(f"[probe] kimi_intent_analysis dynamic_variation_vs_prev: {different}")
                            prev_json = parsed
                        break
        # --- Streaming tests (Phase 6) ---
        try:
            import time
            from datetime import datetime, timezone
        except Exception:
            pass

        # Kimi streaming via kimi_chat_with_tools (if available)
        if "kimi_chat_with_tools" in names:
            rid = uuid.uuid4().hex
            kimi_stream_args = {
                "messages": [
                    {"role": "user", "content": "Write 3 concise bullets on why streaming responses are useful for UX."}
                ],
                "model": "auto",
                "temperature": 0.2,
                "stream": True,
                "use_websearch": False,
            }
            t0 = time.perf_counter(); t0_iso = datetime.now(timezone.utc).isoformat()
            await ws.send(json.dumps({"op":"call_tool","request_id":rid,"name":"kimi_chat_with_tools","arguments":kimi_stream_args}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    t1 = time.perf_counter(); t1_iso = datetime.now(timezone.utc).isoformat()
                    if msg.get("error"):
                        _p(f"[probe] kimi_stream ERROR: {msg.get('error')}")
                        art = _write_artifact("kimi_stream", "error", kimi_stream_args, [msg.get("error")])
                        # Fallback: direct vendor streaming if tool call fails
                        try:
                            import requests, time
                            KIMI_URL = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1").rstrip("/") + "/chat/completions"
                            KIMI_KEY = os.getenv("KIMI_API_KEY", "")
                            headers = {"Authorization": f"Bearer {KIMI_KEY}", "Content-Type": "application/json"}
                            body = {
                                "model": os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"),
                                "messages": [{"role": "user", "content": kimi_stream_args["messages"][0]["content"]}],
                                "temperature": kimi_stream_args.get("temperature", 0.2),
                                "stream": True,
                            }
                            t0h = time.perf_counter(); t0h_iso = datetime.now(timezone.utc).isoformat()
                            resp = requests.post(KIMI_URL, headers=headers, json=body, stream=True, timeout=120)
                            resp.raise_for_status()
                            assembled = []
                            chunks = []
                            for raw in resp.iter_lines(decode_unicode=True):
                                if not raw:
                                    continue
                                line = raw.strip()
                                if line.startswith("data: "):
                                    data = line[len("data: "):]
                                else:
                                    data = line
                                if data == "[DONE]":
                                    break
                                try:
                                    obj = json.loads(data)
                                    choice0 = (obj.get("choices") or [{}])[0]
                                    delta = (choice0.get("delta") or {})
                                    piece = delta.get("content") or ""
                                    if piece:
                                        assembled.append(piece)
                                        chunks.append({"ts": datetime.now(timezone.utc).isoformat(), "len": len(piece)})
                                except Exception:
                                    # Non-JSON chunk; append as-is
                                    assembled.append(data)
                                    chunks.append({"ts": datetime.now(timezone.utc).isoformat(), "len": len(data)})
                            t1h = time.perf_counter(); t1h_iso = datetime.now(timezone.utc).isoformat()
                            # Save a JSON + JSONL pair similar to tool artifacts
                            outputs = [{"type": "text", "text": "".join(assembled)}]
                            art2 = _write_artifact("kimi_stream_direct", "bullets", body, outputs)
                            jsonl2 = art2.with_suffix(art2.suffix + "l")
                            with open(jsonl2, "a", encoding="utf-8") as f:
                                f.write(json.dumps({
                                    "provider": "KIMI",
                                    "start": t0h_iso,
                                    "end": t1h_iso,
                                    "duration_ms": int((t1h - t0h)*1000),
                                    "assembled_len": sum(c["len"] for c in chunks),
                                    "chunks": chunks[:50],
                                }, ensure_ascii=False) + "\n")
                            _p(f"[probe] kimi_stream DIRECT TRACE → {jsonl2}")
                        except Exception as e:
                            _p(f"[probe] kimi_stream direct fallback failed: {e}")
                    else:
                        outputs = msg.get("outputs") or []
                        texts = _extract_text_outputs(outputs)
                        _p(f"[probe] kimi_stream full outputs: {texts}")
                        # If unknown/denied, fall back to direct vendor streaming
                        if any("unknown tool" in (t or "").lower() for t in texts):
                            try:
                                import requests, time
                                KIMI_URL = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1").rstrip("/") + "/chat/completions"
                                KIMI_KEY = os.getenv("KIMI_API_KEY", "")
                                headers = {"Authorization": f"Bearer {KIMI_KEY}", "Content-Type": "application/json"}
                                body = {
                                    "model": os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"),
                                    "messages": [{"role": "user", "content": kimi_stream_args["messages"][0]["content"]}],
                                    "temperature": kimi_stream_args.get("temperature", 0.2),
                                    "stream": True,
                                }
                                t0h = time.perf_counter(); t0h_iso = datetime.now(timezone.utc).isoformat()
                                resp = requests.post(KIMI_URL, headers=headers, json=body, stream=True, timeout=120)
                                resp.raise_for_status()
                                assembled2 = []
                                chunks2 = []
                                for raw in resp.iter_lines(decode_unicode=True):
                                    if not raw:
                                        continue
                                    line = raw.strip()
                                    if line.startswith("data: "):
                                        data = line[len("data: "):]
                                    else:
                                        data = line
                                    if data == "[DONE]":
                                        break
                                    try:
                                        obj = json.loads(data)
                                        choice0 = (obj.get("choices") or [{}])[0]
                                        delta = (choice0.get("delta") or {})
                                        piece = delta.get("content") or ""
                                        if piece:
                                            assembled2.append(piece)
                                            chunks2.append({"ts": datetime.now(timezone.utc).isoformat(), "len": len(piece)})
                                    except Exception:
                                        assembled2.append(data)
                                        chunks2.append({"ts": datetime.now(timezone.utc).isoformat(), "len": len(data)})
                                t1h = time.perf_counter(); t1h_iso = datetime.now(timezone.utc).isoformat()
                                outputs2 = [{"type": "text", "text": "".join(assembled2)}]
                                art2 = _write_artifact("kimi_stream_direct", "bullets", body, outputs2)
                                jsonl2 = art2.with_suffix(art2.suffix + "l")
                                with open(jsonl2, "a", encoding="utf-8") as f:
                                    f.write(json.dumps({
                                        "provider": "KIMI",
                                        "start": t0h_iso,
                                        "end": t1h_iso,
                                        "duration_ms": int((t1h - t0h)*1000),
                                        "assembled_len": sum(c["len"] for c in chunks2),
                                        "chunks": chunks2[:50],
                                    }, ensure_ascii=False) + "\n")
                                _p(f"[probe] kimi_stream DIRECT TRACE → {jsonl2}")
                            except Exception as e:
                                _p(f"[probe] kimi_stream direct fallback failed: {e}")

                        art = _write_artifact("kimi_stream", "bullets", kimi_stream_args, outputs)
                        # Build coarse JSONL trace (assembled only; raw item sample if available)
                        jsonl = art.with_suffix(art.suffix + "l")
                        assembled = "\n".join(texts)
                        parsed = _parse_first_json(texts) or {}
                        raw_items = []
                        try:
                            raw_items = (parsed.get("raw") or {}).get("items") or []
                        except Exception:
                            raw_items = []
                        trace = {
                            "provider": "KIMI",
                            "start": t0_iso,
                            "end": t1_iso,
                            "duration_ms": int((t1 - t0)*1000),
                            "assembled_len": len(assembled),
                            "raw_items_count": len(raw_items),
                            "raw_items_sample": raw_items[:5],
                        }
                        with open(jsonl, "a", encoding="utf-8") as f:
                            f.write(json.dumps(trace, ensure_ascii=False) + "\n")
                        _p(f"[probe] kimi_stream TRACE → {jsonl}")
                    break
        else:
            _p("[probe] kimi_stream skipped: kimi_chat_with_tools tool not available")

        # GLM streaming via chat (env-gated by GLM_STREAM_ENABLED)
        if "chat" in names:
            rid = uuid.uuid4().hex
            glm_stream_args = {
                "prompt": "Write a short paragraph about advantages of streaming responses in UIs, then list 3 bullet points.",
                "use_websearch": False,
                # Chat tool schema ignores 'stream', streaming is enabled via GLM_STREAM_ENABLED on server
            }
            t0 = time.perf_counter(); t0_iso = datetime.now(timezone.utc).isoformat()
            await ws.send(json.dumps({"op":"call_tool","request_id":rid,"name":"chat","arguments":glm_stream_args}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    t1 = time.perf_counter(); t1_iso = datetime.now(timezone.utc).isoformat()
                    if msg.get("error"):
                        _p(f"[probe] glm_stream ERROR: {msg.get('error')}")
                        _write_artifact("glm_stream", "error", glm_stream_args, [msg.get("error")])
                    else:
                        outputs = msg.get("outputs") or []
                        texts = _extract_text_outputs(outputs)
                        _p(f"[probe] glm_stream full outputs: {texts[:1]}")
                        art = _write_artifact("glm_stream", "paragraph_bullets", glm_stream_args, outputs)
                        jsonl = art.with_suffix(art.suffix + "l")
                        assembled = "\n".join(texts)
                        trace = {
                            "provider": "GLM",
                            "start": t0_iso,
                            "end": t1_iso,
                            "duration_ms": int((t1 - t0)*1000),
                            "assembled_len": len(assembled),
                            "note": "Streaming enabled via env; coarse timing only (no per-chunk events available at MCP layer)",
                        }
                        with open(jsonl, "a", encoding="utf-8") as f:
                            f.write(json.dumps(trace, ensure_ascii=False) + "\n")
                        _p(f"[probe] glm_stream TRACE → {jsonl}")
                    break
        else:
            _p("[probe] glm_stream skipped: chat tool not available")


        # Kimi upload+extract (attempt even if hidden). Requires file exists.
        if os.path.exists(TEST_FILE):
            rid = uuid.uuid4().hex
            args = {"files": [TEST_FILE], "purpose": "file-extract"}
            await ws.send(
                json.dumps(
                    {
                        "op": "call_tool",
                        "request_id": rid,
                        "name": "kimi_upload_and_extract",
                        "arguments": args,
                    }
                )
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    if msg.get("error"):
                        _p(f"[probe] kimi_upload_and_extract error: {msg.get('error')}")
                    else:
                        _p(f"[probe] kimi_upload_and_extract preview: {str(msg.get('outputs'))[:200]}")
                    break

        # GLM Agent APIs (requires GLM_TEST_AGENT_ID env)
        AGENT_ID = os.getenv("GLM_TEST_AGENT_ID", "").strip()
        created_agent_id = None
        if not AGENT_ID:
            # Prefer built-in agent if available
            AGENT_ID = "general_translation"
        # Agent tools were de-scoped; disable agent tests
        if False and AGENT_ID:
            # glm_agent_chat (use documented message/content shape)
            rid = uuid.uuid4().hex
            args = {
                "agent_id": AGENT_ID,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "hello from ws_probe"}
                        ],
                    }
                ],
                "stream": False,
            }
            await ws.send(
                json.dumps(
                    {
                        "op": "call_tool",
                        "request_id": rid,
                        "name": "glm_agent_chat",
                        "arguments": args,
                    }
                )
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    if msg.get("error"):
                        _p(f"[probe] glm_agent_chat error: {msg.get('error')}")
                        outputs = []
                    else:
                        outputs = msg.get("outputs") or []
                        _p(f"[probe] glm_agent_chat preview: {str(outputs)[:200]}")
                    break

            # Try to extract conversation_id and agent_id from outputs and immediately fetch conversation
            conv_id = None
            agent_for_conv = AGENT_ID
            captured = {}
            try:
                for o in outputs:
                    if isinstance(o, dict) and o.get("type") == "text" and isinstance(o.get("text"), str):
                        t = o["text"].strip()
                        # Try parse JSON directly
                        try:
                            data = json.loads(t)
                            if isinstance(data, dict):
                                if not captured:
                                    captured = data
                                conv_id = data.get("conversation_id") or data.get("id") or conv_id
                                agent_for_conv = data.get("agent_id") or agent_for_conv
                        except Exception:
                            # Not JSON; skip
                            pass
                # Persist captured ids for follow-on integration
                try:
                    out = {
                        "agent_id": agent_for_conv,
                        "conversation_id": conv_id,
                        "raw": captured,
                    }
                    with open("docs/external_review/20250928_glm_agent_session.json", "w", encoding="utf-8") as f:
                        json.dump(out, f, ensure_ascii=False, indent=2)
                    _p(f"[probe] saved agent session ids -> docs/external_review/20250928_glm_agent_session.json")
                except Exception:
                    pass
                if conv_id:
                    rid = uuid.uuid4().hex
                    args = {"agent_id": agent_for_conv, "conversation_id": conv_id, "page": 1, "page_size": 10}
                    await ws.send(
                        json.dumps(
                            {
                                "op": "call_tool",
                                "request_id": rid,
                                "name": "glm_agent_conversation",
                                "arguments": args,
                            }
                        )
                    )
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                            if msg.get("error"):
                                _p(f"[probe] glm_agent_conversation(error) conv_id={conv_id}: {msg.get('error')}")
                            else:
                                _p(f"[probe] glm_agent_conversation(ok) conv_id={conv_id} preview: {str(msg.get('outputs'))[:200]}")
                            break
            except Exception as e:
                _p(f"[probe] convo follow-up parsing error: {e}")

            # Attempt get_result only if async id provided via env (or parse in future)
            ASYNC_ID = os.getenv("GLM_TEST_ASYNC_ID", "").strip()
            if ASYNC_ID:
                rid = uuid.uuid4().hex
                args = {"async_id": ASYNC_ID, "agent_id": AGENT_ID}
                await ws.send(
                    json.dumps(
                        {
                            "op": "call_tool",
                            "request_id": rid,
                            "name": "glm_agent_get_result",
                            "arguments": args,
                        }
                    )
                )
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                        if msg.get("error"):
                            _p(f"[probe] glm_agent_get_result error: {msg.get('error')}")
                        else:
                            _p(f"[probe] glm_agent_get_result preview: {str(msg.get('outputs'))[:200]}")
                        break

            # Conversation listing (best-effort; requires conversation_id)
            # We skip unless GLM_TEST_CONV_ID is set
            CONV_ID = os.getenv("GLM_TEST_CONV_ID", "").strip()
            if CONV_ID:
                rid = uuid.uuid4().hex
                args = {"agent_id": AGENT_ID, "conversation_id": CONV_ID, "page": 1, "page_size": 20}
                await ws.send(
                    json.dumps(
                        {
                            "op": "call_tool",
                            "request_id": rid,
                            "name": "glm_agent_conversation",
                            "arguments": args,
                        }
                    )
                )
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                        if msg.get("error"):
                            _p(f"[probe] glm_agent_conversation error: {msg.get('error')}")
                        else:
                            _p(f"[probe] glm_agent_conversation preview: {str(msg.get('outputs'))[:200]}")
                        break

            if created_agent_id:
                _try_agent_delete(created_agent_id)


if __name__ == "__main__":
    try:
        asyncio.run(probe())
    except Exception as e:
        _p(f"[probe] error: {e}")
        sys.exit(2)

