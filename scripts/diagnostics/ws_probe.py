import asyncio
import json
import os
import sys
import uuid

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

        # direct GLM web_search tool if available
        if "glm_web_search" in names:
            rid = uuid.uuid4().hex
            args = {
                "search_query": "GLM-4.5 ZhipuAI latest update",
                "count": 5,
                "search_recency_filter": "oneMonth",
            }
            await ws.send(
                json.dumps({"op": "call_tool", "request_id": rid, "name": "glm_web_search", "arguments": args})
            )
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                    _p(f"[probe] glm_web_search preview: {str(msg.get('outputs'))[:200]}")
                    break

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
        if AGENT_ID:
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

