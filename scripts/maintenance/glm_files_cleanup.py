#!/usr/bin/env python
"""
Wrapper entrypoint for GLM (Z.ai) files cleanup utility.

This keeps backwards compatibility while relocating the runnable entry under scripts/maintenance/.
Delegates to tools/providers/glm/glm_files_cleanup.py:main().
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env if present for convenience
try:
    from dotenv import load_dotenv  # type: ignore
    _env = REPO_ROOT / ".env"
    if _env.exists():
        load_dotenv(str(_env))
except Exception:
    pass


def main() -> int:
    # Import and delegate
    from tools.providers.glm.glm_files_cleanup import main as _main  # type: ignore
    return _main()


if __name__ == "__main__":
    raise SystemExit(main())

