# Why two entry ports: stdio MCP and WS daemon

## Short answer
- Stdio MCP is the canonical MCP transport used by IDE clients (e.g., VSCode Augment). It is simple, portable, and follows MCP reference server patterns.
- The WS daemon is an optional shim that exposes the same tool registry over WebSocket for environments where stdio is inconvenient or where we want session control, capacity limits, and lighter client integrations.
- Both paths converge on the same execution boundary: `src/server/handlers/request_handler.handle_call_tool`. There are not two business-logic stacks.

## When each is useful
- Stdio MCP (primary)
  - Default for IDE integrations and tooling that already speaks MCP over stdio
  - Minimal network surface; easy local dev; fewer moving parts
- WS daemon (secondary, optional)
  - Remote clients that cannot launch a stdio subprocess
  - Centralized concurrency control (global/provider/session semaphores)
  - Long-running sessions with heartbeats and duplicate-call coalescing
  - Easier proxying across machines/containers without IDE coupling

## Flow overview
```mermaid
graph TD
  A[MCP Client (stdio)]-->B[server.py]
  A2[WS Client]-->C[src/daemon/ws_server.py]
  B-->D[handlers/request_handler]
  C-->D
  D-->E[ToolMap & Providers]
  E-->F[tool.execute to provider]
```

## Rationale
- Separation of transport (stdio vs WS) from execution keeps logic composable and testable.
- The WS shim exists for operational flexibility without duplicating provider logic.
- If desired, we can hard-disable WS in production by not starting the daemon; the code remains isolated.

