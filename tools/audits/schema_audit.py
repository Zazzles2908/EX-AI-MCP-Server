#!/usr/bin/env python3
"""
Schema Audit Tool

Validates tool input schemas for MCP compliance.

ARCHITECTURE NOTE (v2.0.2+):
- This module delegates to singleton registry via src/server/registry_bridge
- NEVER instantiate ToolRegistry directly - always use get_registry()
- registry_bridge.build() is idempotent and delegates to src/bootstrap/singletons
- Ensures TOOLS is SERVER_TOOLS identity check always passes
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure repository src/ is on sys.path
ROOT = Path(__file__).resolve().parents[2]
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import tool registry lazily to avoid side effects when unavailable
try:
    from server.registry_bridge import get_registry  # type: ignore
except Exception as e:
    print(json.dumps({"status": "error", "message": f"failed to import registry bridge: {e}"}))
    raise

REQUIRED_SCHEMA = "http://json-schema.org/draft-07/schema#"


def _contains_nullable(obj: Any) -> bool:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "nullable":
                return True
            if _contains_nullable(v):
                return True
    elif isinstance(obj, list):
        return any(_contains_nullable(x) for x in obj)
    return False


def audit() -> Dict[str, Any]:
    issues = []
    ok = 0
    reg = get_registry()
    # Idempotent guard: build() delegates to singleton, safe to call multiple times
    reg.build()
    for name, tool in reg.list_tools().items():
        try:
            schema = tool.get_input_schema()  # type: ignore
        except Exception as e:
            issues.append({"tool": name, "error": f"get_input_schema failed: {e}"})
            continue
        s = schema or {}
        # Checks
        if s.get("$schema") != REQUIRED_SCHEMA:
            issues.append({"tool": name, "issue": "missing_or_wrong_$schema", "value": s.get("$schema")})
        if s.get("type") != "object":
            issues.append({"tool": name, "issue": "root_type_not_object", "value": s.get("type")})
        if s.get("additionalProperties") is not False:
            issues.append({"tool": name, "issue": "additionalProperties_not_false", "value": s.get("additionalProperties")})
        if _contains_nullable(s):
            issues.append({"tool": name, "issue": "contains_nullable_keyword"})
        if not any(i.get("tool") == name for i in issues):
            ok += 1
    return {"status": "ok", "ok_tools": ok, "issues": issues}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))

