import os, json, sys, pathlib
# Ensure repo root on sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from src.providers.kimi import KimiModelProvider

def main():
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1")
    if not api_key:
        print(json.dumps({"error": "KIMI_API_KEY missing"}))
        return
    prov = KimiModelProvider(api_key=api_key, base_url=base_url)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Use web search to find the official Moonshot tool-use documentation URL and list three relevant URLs.",
        },
    ]

    tools = [{
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Internet search",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    }]

    res = prov.chat_completions_create(
        model=os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"),
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
        _session_id="probe",
        _call_key="probe_kimi_tooluse",
        _tool_name="probe_kimi_tooluse",
    )

    # Emit full normalized initial result (should include tool_calls)
    print(json.dumps(res, ensure_ascii=False))

    # Persist raw provider payload for evidence
    raw = res.get("raw") if isinstance(res, dict) else None
    if raw is not None:
        try:
            with open("docs/augmentcode_phase2/raw/kimi_provider_probe_raw.json", "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False)
        except Exception:
            pass

    # Minimal tool loop: execute function web_search up to 3 times and return final assistant message
    try:
        depth = 0
        current_raw = raw
        while depth < 3:
            depth += 1
            choices = (current_raw or {}).get("choices") or []
            msg = (choices[0].get("message") if choices else {}) or {}
            tcs = msg.get("tool_calls") or []
            if not tcs:
                break
            # Append assistant message with tool_calls for correlation
            messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": tcs})
            tool_msgs = []
            for tc in tcs:
                fn = tc.get("function") or {}
                if (fn.get("name") or "") == "web_search":
                    # Parse arguments
                    args_raw = fn.get("arguments")
                    if isinstance(args_raw, str):
                        try:
                            args = json.loads(args_raw)
                        except Exception:
                            args = {"query": args_raw}
                    else:
                        args = args_raw or {}
                    query = (args.get("query") or "").strip()
                    # DuckDuckGo Instant Answer API (no key)
                    import urllib.parse, urllib.request
                    q = urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "skip_disambig": 1})
                    url = f"https://api.duckduckgo.com/?{q}"
                    try:
                        with urllib.request.urlopen(url, timeout=20) as resp:
                            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    except Exception as e:
                        data = {"error": str(e), "results": []}
                    # Build tool message
                    tool_msgs.append({
                        "role": "tool",
                        "tool_call_id": str(tc.get("id") or tc.get("tool_call_id") or "tc-0"),
                        "content": json.dumps({
                            "engine": "duckduckgo",
                            "query": query,
                            "results": ([{"title": data.get("Heading"), "url": data.get("AbstractURL")}]
                                        if data.get("AbstractURL") else []) + [
                                {"title": it.get("Text"), "url": it.get("FirstURL")}
                                for it in (data.get("RelatedTopics") or []) if isinstance(it, dict) and it.get("FirstURL")
                            ][:5]
                        }, ensure_ascii=False),
                    })
            if not tool_msgs:
                break
            # Persist tool results for evidence
            try:
                with open("docs/augmentcode_phase2/raw/kimi_websearch_tool_results_1.json", "w", encoding="utf-8") as f:
                    json.dump(tool_msgs, f, ensure_ascii=False)
            except Exception:
                pass
            messages.extend(tool_msgs)
            follow = prov.chat_completions_create(
                model=os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview"),
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
                _session_id="probe",
                _call_key=f"probe_kimi_tooluse_followup_{depth}",
                _tool_name="probe_kimi_tooluse",
            )
            current_raw = follow.get("raw") if isinstance(follow, dict) else None
            # Persist each step for evidence
            try:
                with open(f"docs/augmentcode_phase2/raw/kimi_websearch_step_{depth}.json", "w", encoding="utf-8") as f:
                    json.dump(follow, f, ensure_ascii=False)
            except Exception:
                pass
        # Final assistant content (if any)
        final_choices = (current_raw or {}).get("choices") or []
        final_msg = (final_choices[0].get("message") if final_choices else {}) or {}
        final_content = final_msg.get("content") or ""
        out = {"content": final_content, "depth": depth}
        try:
            with open("docs/augmentcode_phase2/raw/kimi_websearch_real_1.json", "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False)
        except Exception:
            pass
        print(json.dumps({"final": out}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"tool_loop_error": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

