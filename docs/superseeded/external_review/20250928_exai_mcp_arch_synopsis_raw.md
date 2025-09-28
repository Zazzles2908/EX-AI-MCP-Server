# EXAI MCP Raw Output — Architecture Synopsis

Date: 2025-09-28
Tool: EXAI-WS chat (glm-4.5-flash)
Request: Concise synopsis of observed MCP server architecture (stdio server, WS daemon shim, GLM manager, Kimi files) and main entrypoints.

---

## Raw Response

MCP Server Architecture Synopsis

The system implements a dual-transport MCP architecture with stdio as the primary communication channel and WebSocket for remote access. GLM-4.5-flash serves as the manager, routing requests and coordinating with Kimi for file operations. The design leverages provider-native capabilities rather than implementing custom tools, using a minimal tool registry exposed through workflows. The WebSocket bridge enables stdio-based servers to function in networked environments, while provider routing ensures appropriate task distribution.

Main Runtime Entrypoints:
1. server.py - Main MCP stdio server
2. src/daemon/ws_server.py - WebSocket daemon
3. scripts/ws/run_ws_daemon.py - WebSocket daemon runner
4. scripts/run_ws_shim.py - stdio<->WS bridge script

This architecture maintains clear separation of concerns between management (GLM) and specialized operations (Kimi for files), with flexibility in deployment options.

---

Metadata: model=glm-4.5-flash; provider=glm; temperature=0.3; thinking=minimal
ReqId: 055db0cf-7257-4bd9-8086-1c1ef60797b5
Progress: chat: Starting execution → Request validated → Model/context ready → Generating response

