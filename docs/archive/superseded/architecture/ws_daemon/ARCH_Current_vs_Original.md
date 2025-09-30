# WS Daemon Architecture: Original Intent vs Current State

Date: 2025-09-28
Owner: EX-AI-MCP-Server

## Summary
- Original intent (per WS_Daemon_Skeleton.md & Operations_Runbook):
  - Run a single local WebSocket daemon (loopback) that multiplexes many client sessions
  - Each MCP client uses a stdio shim that forwards JSON-RPC over WebSocket to the daemon
  - Benefits: multi-client concurrency, warm caches, central quotas/backpressure, still stdio-compatible for IDEs
- Current state (verified):
  - scripts/run_ws_daemon.py launches src/daemon/ws_server.py
  - scripts/run_ws_shim.py is a proper MCP stdio server that connects to the daemon (see examples/claude.mcp.json)
  - Docs in docs/architecture/ws_daemon/* match the original intent

Conclusion: Current implementation matches the original design direction. Small deltas are mostly around polishing docs/diagrams and reinforcing that WS is P0 in this deployment.

## Interconnection (strict Mermaid)
```mermaid
graph TD
  C1[Client app (VS Code, CLI, Claude)] --> S[Stdio shim (MCP stdio)]
  S -->|JSON-RPC over WS| D[WS daemon]
  D --> H[Server core: request_handler]
  H --> T[Tools + Provider Registry]
  T --> P[Providers (GLM/Kimi/...)]
```

## Why not daemon->stdio inversion?
- Inversion would make the WS layer act as a client of a stdio MCP server inside the same machine. That adds an extra hop and process management layer without clear benefits.
- Current design keeps a single in-process execution boundary for all transports and avoids re-serializing within the same host.

## Notes
- examples/claude.mcp.json already points stdio to run_ws_shim.py with EXAI_WS_HOST/PORT env → aligns with this model
- scripts/ws_start.ps1 likely wraps run_ws_daemon/run_ws_shim startup (see scripts/ws/README.md)

