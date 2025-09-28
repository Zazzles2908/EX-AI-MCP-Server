import asyncio, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.providers.kimi import KimiModelProvider

async def main():
    api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY") or ""
    if not api_key:
        print("No Kimi API key present; skipping")
        return
    prov = KimiModelProvider(api_key=api_key)
    model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
    messages = [{"role": "user", "content": "ping phase2 cache"}]
    result = prov.chat_completions_create(
        model=model,
        messages=messages,
        temperature=0.6,
        tools=None,
        tool_choice=None,
        _session_id="phase2-sess",
        _call_key="phase2-call",
        _tool_name="phase2_kimi_cache_diag",
    )
    text = json.dumps(result, ensure_ascii=False)
    outdir = Path("docs/System_layout/_raw")
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "phase2_kimi_capture_headers_response.json"
    outfile.write_text(text, encoding="utf-8")
    print(f"Wrote {outfile}")

if __name__ == "__main__":
    asyncio.run(main())

