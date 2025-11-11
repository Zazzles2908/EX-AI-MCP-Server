# EXAI-MCP Server - Clean Architecture Design
**Date:** 2025-11-12
**Status:** Architecture Specification

---

## 🔍 **CURRENT STATE ANALYSIS**

### What Works ✅
- **Docker Daemon**: Running on port 3010 (WebSocket responding)
- **17 Tools Loaded**: Successfully registered in daemon
- **MiniMax Config**: Fixed (`MINIMAX_M2_KEY` properly set)
- **Cleanup System**: Process management in place

### What's Broken ❌
- **WebSocket Shim**: NOT running (port 3005 is free)
- **Claude Code Connection**: Cannot reach MCP server
- **Port Conflicts**: Multiple shim processes trying to bind

### Root Cause 🎯
The WebSocket Shim that bridges **Claude Code ↔ EXAI Daemon** is not running on port 3005, so Claude Code cannot connect to any MCP servers.

---

## 🏗️ **RECOMMENDED ARCHITECTURE**

### Clean Connection Flow

```
┌────────────────────┐
│   Claude Code      │
│   (MCP Client)     │
└──────────┬─────────┘
           │
           │ .mcp.json config
           │ (points to port 3005)
           ▼
┌────────────────────┐
│  WebSocket Shim    │ ← SINGLE INSTANCE (port 3005)
│  run_ws_shim.py    │   - Protocol translator
│                    │   - MCP ↔ EXAI protocol
└──────────┬─────────┘
           │
           │ WebSocket (port 3010)
           ▼
┌────────────────────┐
│  EXAI Daemon       │ ← Docker Container
│  (Port 3010↔8079)  │   - WebSocket server
│                    │   - 17 tools loaded
└──────────┬─────────┘
           │
           ▼
    ┌──────┴──────┐
    ▼             ▼
GLM/KIMI      MiniMax M2
APIs          Router
```

### Port Allocation

| Component | Port | Protocol | Purpose |
|-----------|------|----------|---------|
| **WebSocket Shim** | 3005 | WebSocket | MCP client connections |
| **EXAI Daemon** | 3010↔8079 | WebSocket | Internal daemon (Docker map) |
| **Health Check** | 3002 | HTTP | Daemon health monitoring |

---

## 🎯 **CRITICAL DESIGN PRINCIPLES**

### 1. **Single Shim Instance**
```python
# Only ONE shim process should run on port 3005
# Prevent multiple instances from binding
```

### 2. **Port Lock Management**
```python
# Check if port 3005 is available before binding
# If occupied, find and terminate old process
# Or use a different port
```

### 3. **Graceful Shutdown**
```python
# Use signal handlers to clean up properly
# Kill entire process group on exit
# Prevent orphaned processes
```

### 4. **Health Monitoring**
```python
# Monitor shim health
# Auto-restart if it dies
# Report status to daemon
```

---

## 📋 **IMPLEMENTATION PLAN**

### Phase 1: Fix Shim Startup

**File: `scripts/runtime/run_ws_shim.py`**

```python
#!/usr/bin/env python
"""
EXAI MCP WebSocket Shim - Protocol Translator
Bridges standard MCP protocol <-> EXAI custom WebSocket protocol.

CLEAN ARCHITECTURE:
- Single instance management
- Port conflict resolution
- Graceful shutdown
- Health monitoring
"""

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path

# Setup paths
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root))

import websockets
from dotenv import load_dotenv

# Load environment
env_file = os.getenv('ENV_FILE', '.env')
load_dotenv(env_file)

logger = logging.getLogger(__name__)

# Configuration
SHIM_HOST = "127.0.0.1"
SHIM_PORT = 3005  # FIXED: Always use 3005
DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3010"))

# Global shutdown flag
_shutting_down = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutting_down
    logger.info(f"Received signal {signum}, initiating shutdown...")
    _shutting_down = True
    os.killpg(0, signal.SIGTERM)  # Kill process group
    sys.exit(0)

async def check_port_available(host, port):
    """Check if a port is available for binding."""
    try:
        server = await asyncio.start_server(
            lambda: None, host, port
        )
        server.close()
        await server.wait_closed()
        return True
    except OSError:
        return False

async def find_free_port(start_port=3005, max_tries=10):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        if await check_port_available(SHIM_HOST, port):
            return port
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_tries}")

class MCPShimProtocol:
    """Protocol handler for MCP <-> Custom translation."""

    def __init__(self, client_ws):
        self.client_ws = client_ws
        self.daemon_ws = None
        self.running = True

    async def connect_to_daemon(self):
        """Establish connection to EXAI daemon."""
        daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
        logger.info(f"Connecting to EXAI daemon at {daemon_uri}...")

        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.daemon_ws = await asyncio.wait_for(
                    websockets.connect(daemon_uri),
                    timeout=10
                )
                logger.info("✓ Connected to EXAI daemon")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        logger.error("✗ Failed to connect to daemon after all retries")
        return False

    async def run(self):
        """Main protocol execution loop."""
        # Connect to daemon
        if not await self.connect_to_daemon():
            raise Exception("Failed to connect to daemon")

        # Start message forwarding tasks
        tasks = [
            asyncio.create_task(self.handle_client_messages()),
            asyncio.create_task(self.handle_daemon_messages())
        ]

        # Wait for completion or shutdown
        try:
            await asyncio.gather(*tasks)
        finally:
            self.running = False
            # Cleanup
            if self.daemon_ws:
                await self.daemon_ws.close()

async def handle_client(ws: websockets.WebSocketServerProtocol, path: str):
    """Handle new WebSocket client connections."""
    client_id = id(ws)
    logger.info(f"[{client_id}] New MCP client connected")

    try:
        protocol = MCPShimProtocol(ws)
        await protocol.run()
    except Exception as e:
        logger.error(f"[{client_id}] Error: {e}")
    finally:
        logger.info(f"[{client_id}] Client disconnected")

async def main():
    """Main shim entry point."""
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    logger.info("=" * 60)
    logger.info("EXAI MCP Shim Starting (Clean Architecture)")
    logger.info("=" * 60)

    # Check port availability
    port_available = await check_port_available(SHIM_HOST, SHIM_PORT)
    if not port_available:
        logger.warning(f"Port {SHIM_PORT} is busy, finding free port...")
        free_port = await find_free_port()
        logger.info(f"Using port {free_port} instead")
        # Note: Would need to update .mcp.json or use environment variable
    else:
        free_port = SHIM_PORT

    # Set process group for cleanup
    try:
        os.setpgrp()
    except Exception as e:
        logger.warning(f"Could not set process group: {e}")

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start WebSocket server
    logger.info(f"Listening on {SHIM_HOST}:{free_port}")
    logger.info(f"Daemon: {DAEMON_HOST}:{DAEMON_PORT}")
    logger.info("=" * 60)

    try:
        async with websockets.serve(handle_client, SHIM_HOST, free_port):
            logger.info("✓ MCP Shim ready - waiting for connections...")
            # Keep alive
            await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Shim fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shim stopped by user")
    except Exception as e:
        logger.error(f"Shim fatal error: {e}", exc_info=True)
        sys.exit(1)
```

### Phase 2: Startup Script

**File: `scripts/runtime/start_exai_mcp.sh`**

```bash
#!/bin/bash
# EXAI-MCP Startup Script
# Ensures clean startup with proper cleanup

set -e

echo "=== Starting EXAI MCP Server ==="

# 1. Clean up any old shim processes
echo "Cleaning up old processes..."
pkill -f "run_ws_shim.py" 2>/dev/null || true
sleep 2

# 2. Check if Docker daemon is running
echo "Checking Docker daemon..."
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    exit 1
fi

# 3. Check if EXAI daemon container is running
echo "Checking EXAI daemon..."
if ! docker ps | grep -q exai-mcp-daemon; then
    echo "Starting EXAI daemon..."
    docker-compose up -d exai-mcp-daemon
    sleep 5
fi

# 4. Wait for daemon to be ready
echo "Waiting for daemon to be ready..."
for i in {1..30}; do
    if timeout 1 bash -c "</dev/tcp/127.0.0.1/3010" 2>/dev/null; then
        echo "✓ Daemon is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Daemon did not become ready"
        exit 1
    fi
    sleep 1
done

# 5. Start WebSocket shim
echo "Starting WebSocket shim..."
python scripts/runtime/run_ws_shim.py &
SHIM_PID=$!

echo "✓ EXAI MCP Server started (Shim PID: $SHIM_PID)"

# 6. Monitor shim
trap "echo 'Shutting down...'; kill $SHIM_PID; wait $SHIM_PID 2>/dev/null; exit 0" SIGTERM SIGINT

wait $SHIM_PID
```

### Phase 3: Systemd Service (Optional)

**File: `scripts/runtime/exai-mcp.service`**

```ini
[Unit]
Description=EXAI MCP WebSocket Shim
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=exai
WorkingDirectory=/path/to/EX-AI-MCP-Server
ExecStart=/usr/bin/python scripts/runtime/run_ws_shim.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Cleanup on stop
KillMode=process-group
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Phase 4: Health Check Integration

**File: `scripts/runtime/health_check.py`**

```python
#!/usr/bin/env python
"""EXAI-MCP Health Check Script"""

import asyncio
import json
import websockets
import sys

async def check_shim():
    """Check WebSocket shim health."""
    try:
        async with websockets.connect('ws://127.0.0.1:3005', timeout=5) as ws:
            # Send ping
            await ws.ping()
            return True
    except Exception as e:
        print(f"Shim unhealthy: {e}")
        return False

async def check_daemon():
    """Check daemon health."""
    try:
        async with websockets.connect('ws://127.0.0.1:3010', timeout=5) as ws:
            await ws.ping()
            return True
    except Exception as e:
        print(f"Daemon unhealthy: {e}")
        return False

async def main():
    shim_healthy = await check_shim()
    daemon_healthy = await check_daemon()

    if shim_healthy and daemon_healthy:
        print("✓ EXAI-MCP is healthy")
        sys.exit(0)
    else:
        print("✗ EXAI-MCP is unhealthy")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
```

---

## 🔄 **OPERATIONAL WORKFLOW**

### Starting the System

```bash
# Option 1: Manual
cd C:/Project/EX-AI-MCP-Server
bash scripts/runtime/start_exai_mcp.sh

# Option 2: Docker Compose
docker-compose up -d
docker-compose up -d cleanup-service  # Start cleanup service

# Option 3: Systemd (Linux)
sudo systemctl enable exai-mcp
sudo systemctl start exai-mcp
```

### Verification

```bash
# Check ports
netstat -tlnp | grep -E ":3005|:3010"

# Check processes
ps aux | grep run_ws_shim | grep -v grep

# Test health
python scripts/runtime/health_check.py

# Check daemon
curl http://127.0.0.1:3002/health
```

### Monitoring

```bash
# View shim logs
tail -f logs/shim.log

# View daemon logs
docker-compose logs -f exai-mcp-daemon

# Check cleanup service
docker-compose logs -f cleanup-service
```

---

## 🛡️ **FAILURE PREVENTION**

### 1. Port Conflict Resolution
- Check if port 3005 is available before binding
- If occupied, find free port or kill old process
- Prevent multiple shim instances

### 2. Daemon Availability
- Retry daemon connection up to 5 times
- Wait up to 30 seconds for daemon startup
- Clear error messages for debugging

### 3. Graceful Shutdown
- Signal handlers for SIGTERM/SIGINT
- Kill entire process group
- Close WebSocket connections properly

### 4. Auto-Recovery
- Systemd restart policy
- Docker health checks
- Cleanup service monitoring

### 5. Process Management
- Use process groups
- Prevent orphaned children
- Integration with cleanup scripts

---

## 📊 **INTEGRATION WITH CLEANUP SYSTEM**

### Prevent Bloat
- WebSocket shim uses process groups
- Signal handlers for cleanup
- No orphaned processes

### Automated Maintenance
- Cleanup service kills old shims
- Daily Task Scheduler cleanup
- Monitoring and alerting

### Health Monitoring
- Health check endpoint
- Log rotation
- Process count monitoring

---

## ✅ **SUCCESS CRITERIA**

1. ✓ **Single WebSocket shim** running on port 3005
2. ✓ **Claude Code connects** successfully via MCP
3. ✓ **17 tools accessible** through MCP protocol
4. ✓ **MiniMax M2 routing** functional
5. ✓ **Graceful shutdown** with no orphaned processes
6. ✓ **Health monitoring** reporting status
7. ✓ **Integration** with cleanup system
8. ✓ **Auto-recovery** on failures

---

## 🎯 **NEXT STEPS**

1. **Deploy Phase 1**: Fix WebSocket shim startup
2. **Test Connection**: Verify Claude Code can connect
3. **Deploy Cleanup**: Start cleanup service
4. **Monitor**: Set up health checks
5. **Document**: Update operational guides

---

**Status**: Ready for Implementation
**Estimated Time**: 2-4 hours
**Priority**: P0 (Critical - blocks all MCP functionality)
