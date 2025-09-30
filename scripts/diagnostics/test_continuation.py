import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import uuid

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.server.handlers import handle_call_tool  # type: ignore


async def main():
    # Pre-create a thread for continuation using conversation memory
    from utils.conversation_memory import create_thread
    cont_id = create_thread("chat", initial_request={})
    out = {
        "cont_id": cont_id,
        "turns": []
    }

    # Turn 1
    args1 = {
        "prompt": "Turn 1: say 'ready' briefly and offer to continue.",
        "model": "auto",
        "continuation_id": cont_id,
        "use_websearch": False,
        "stream": False,
    }
    res1 = await handle_call_tool("chat", args1)
    out["turns"].append({
        "args": args1,
        "result_types": [getattr(x, "type", type(x).__name__) for x in (res1 or [])],
        "text_preview": (res1[-1].text[:200] if res1 and hasattr(res1[-1], "text") else None),
    })

    # Turn 2
    args2 = {
        "prompt": "Reply with just `ACK`.",
        "model": "auto",
        "continuation_id": cont_id,
        "use_websearch": False,
        "stream": False,
    }
    res2 = await handle_call_tool("chat", args2)
    out["turns"].append({
        "args": args2,
        "result_types": [getattr(x, "type", type(x).__name__) for x in (res2 or [])],
        "text_preview": (res2[-1].text[:200] if res2 and hasattr(res2[-1], "text") else None),
    })

    # Naive assertion: last response contains 'ACK'
    ok = False
    if res2 and hasattr(res2[-1], "text"):
        txt = (res2[-1].text or "").upper()
        ok = "ACK" in txt
    out["assertions"] = {"contains_ACK": ok}

    # Save evidence
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest_dir = ROOT / "docs" / "augmentcode_phase2" / "raw"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"continuation_unit_test_{ts}.json"
    with dest.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Saved: {dest}")


if __name__ == "__main__":
    asyncio.run(main())

