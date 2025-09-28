import os
import json
from pathlib import Path

from utils.observability import append_routeplan_jsonl


def test_append_routeplan_jsonl_writes_file(monkeypatch):
    outdir = Path("docs/System_layout/_raw/routeplan_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ROUTEPLAN_LOG_DIR", str(outdir))

    evt = {"requested": "auto", "chosen": "glm-4.5-flash", "reason": "auto_preferred", "provider": "ZAI"}
    append_routeplan_jsonl(evt)

    files = list(outdir.glob("*.jsonl"))
    assert files, "no JSONL emitted"
    content = files[0].read_text(encoding="utf-8")
    # Ensure at least one line JSON decodes and contains our fields
    line = content.strip().splitlines()[-1]
    data = json.loads(line)
    assert data.get("requested") == "auto"
    assert data.get("chosen") == "glm-4.5-flash"

