File Relocation Plan (safe, non‑breaking)

Targets
- intelligent_router.py -> src/server/router/intelligent_router.py
- providers.py -> src/providers/providers.py
- remote_server.py -> src/server/remote/remote_server.py

Approach
1) Create destination packages with __init__.py
2) Add import shims (temporary):
   - Keep root files importing from new module paths, or create thin facades in new paths that re-export root (phase 1)
3) Update in-repo imports to prefer new module paths
4) After validation and PR merge, remove root files (phase 2 cleanup)

Rationale
- Avoids breaking existing clients; enables gradual adoption.

Next steps
- Create packages and wrappers; update imports; open PR.

