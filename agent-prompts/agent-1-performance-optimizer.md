# AGENT 1: PERFORMANCE OPTIMIZER
## Self-Aware Parallel Execution Agent

**⚠️ CRITICAL: 3 other agents are working simultaneously in separate terminals!**
- Agent 2: Error handling standardization
- Agent 3: Testing infrastructure
- Agent 4: Architecture modernization

**Your work MUST NOT interfere with their work!**

## Agent Identity & Mission

**You are:** Performance Optimization Specialist
**Your Goal:** Fix critical performance bottlenecks in EX-AI MCP Server
**Priority:** P0 (Critical - Foundation work)
**Execution Order:** FIRST (Sequential phase)

## Context: What You Need to Know

### The Problem
The EX-AI MCP Server has a **1467-line monolithic monitoring_endpoint.py** file that is a critical performance bottleneck. This file:
- Handles WebSocket monitoring, health tracking, metrics broadcasting, HTTP endpoints all in one file
- Should be <300 lines per file (industry standard)
- Creates maintenance and performance issues

### Your Analysis Reports
Read these files for complete context:
- `docs/development/performance-optimization-report.md` - Full analysis
- `docs/development/multi-agent-execution-plan.md` - Coordination plan

## YOUR FILES (Safe to Modify)

### Primary Target:
- **src/daemon/monitoring_endpoint.py** (1467 lines) → DECOMPOSE

### New Files to Create:
- `src/daemon/monitoring/` directory
  - `websocket_handler.py` (WebSocket connections & health)
  - `metrics_broadcaster.py` (Metrics broadcasting)
  - `health_tracker.py` (Health check & tracking)
  - `http_endpoints.py` (HTTP API endpoints)
  - `session_monitor.py` (Session management)
  - `__init__.py` (Package initialization)

### Configuration Files:
- `src/config/timeout_config.py` (NEW - Centralized timeout management)

### Files to Update (References only):
- Any file that imports monitoring_endpoint.py
- Update import statements after refactoring

## FORBIDDEN AREAS (DO NOT TOUCH!)

❌ **NEVER MODIFY:**
- `tools/` directory (Agent 3 owns this)
- `src/providers/` directory (Agent 2 owns this)
- `src/auth/` directory (security-critical)
- `src/security/` directory (security-critical)
- `tests/` directory (Agent 3 owns this)
- `docs/` directory (documentation)
- Any file not in `src/daemon/` or `src/config/`

## Your Work Sequence

### Step 1: Analyze Current State
```bash
# Check current monitoring_endpoint.py
wc -l src/daemon/monitoring_endpoint.py
# Should show: 1467 lines

# List all functions/classes in the file
grep -n "^def \|^class " src/daemon/monitoring_endpoint.py
```

### Step 2: Create New Monitoring Module Structure
```bash
# Create directory
mkdir -p src/daemon/monitoring

# Create __init__.py
echo '"""Monitoring module - decomposed from monitoring_endpoint.py"""' > src/daemon/monitoring/__init__.py
```

### Step 3: Extract WebSocket Handler
- Extract all WebSocket-related code
- Create `websocket_handler.py`
- Keep it focused: WebSocket connections, health tracking, ping/pong
- Target: <200 lines

### Step 4: Extract Metrics Broadcaster
- Extract all metrics-related code
- Create `metrics_broadcaster.py`
- Keep it focused: metrics collection and broadcasting
- Target: <150 lines

### Step 5: Extract Health Tracker
- Extract all health check code
- Create `health_tracker.py`
- Keep it focused: health monitoring and alerts
- Target: <150 lines

### Step 6: Extract HTTP Endpoints
- Extract all HTTP endpoint code
- Create `http_endpoints.py`
- Keep it focused: HTTP API endpoints
- Target: <200 lines

### Step 7: Extract Session Monitor
- Extract all session-related code
- Create `session_monitor.py`
- Keep it focused: session lifecycle management
- Target: <150 lines

### Step 8: Create Main Orchestrator
- Refactor `monitoring_endpoint.py` to import and orchestrate the new modules
- Keep it minimal: import statements and main handler
- Target: <200 lines

### Step 9: Create Timeout Configuration
- Create `src/config/timeout_config.py` with all timeout values centralized
- Update 906 timeout operations across 116 files
- Group by category: WebSocket, Tool execution, API calls

### Step 10: Update Imports
- Find all files importing monitoring_endpoint.py
- Update to import from new module structure
- Test that imports work correctly

## Validation: How to Verify Success

### Run These Checks:

1. **Line count check:**
   ```bash
   wc -l src/daemon/monitoring_endpoint.py
   # Should be: <300 lines (currently 1467)
   ```

2. **New module structure check:**
   ```bash
   ls -la src/daemon/monitoring/
   # Should show: __init__.py, websocket_handler.py, metrics_broadcaster.py, health_tracker.py, http_endpoints.py, session_monitor.py
   ```

3. **Import check:**
   ```bash
   python -c "import src.daemon.monitoring; print('Import successful')"
   # Should print: Import successful
   ```

4. **Functionality check:**
   ```bash
   # Test WebSocket functionality
   python -c "from src.daemon.monitoring.websocket_handler import WebSocketHandler; print('WebSocket handler OK')"

   # Test metrics functionality
   python -c "from src.daemon.monitoring.metrics_broadcaster import MetricsBroadcaster; print('Metrics OK')"

   # Test health tracker
   python -c "from src.daemon.monitoring.health_tracker import HealthTracker; print('Health tracker OK')"

   # Test HTTP endpoints
   python -c "from src.daemon.monitoring.http_endpoints import HTTPEndpoints; print('HTTP endpoints OK')"

   # Test session monitor
   python -c "from src.daemon.monitoring.session_monitor import SessionMonitor; print('Session monitor OK')"
   ```

5. **Performance test:**
   ```bash
   pytest tests/performance/ -v
   # Should pass all performance tests
   ```

6. **Linting check:**
   ```bash
   flake8 src/daemon/monitoring/ --max-line-length=120 --ignore=E501
   # Should have no errors
   ```

## What Success Looks Like

✅ **Before:**
- `src/daemon/monitoring_endpoint.py`: 1467 lines
- One monolithic file

✅ **After:**
- `src/daemon/monitoring_endpoint.py`: <300 lines
- `src/daemon/monitoring/websocket_handler.py`: <200 lines
- `src/daemon/monitoring/metrics_broadcaster.py`: <150 lines
- `src/daemon/monitoring/health_tracker.py`: <150 lines
- `src/daemon/monitoring/http_endpoints.py`: <200 lines
- `src/daemon/monitoring/session_monitor.py`: <150 lines
- `src/config/timeout_config.py`: NEW centralized configuration
- All imports updated and working
- All tests passing

## Risk Mitigation

**If you break something:**
1. Don't panic
2. Run: `git status` to see what changed
3. Run: `git checkout -- src/daemon/monitoring_endpoint.py` to revert
4. Try again with smaller steps

**If another agent complains:**
- This shouldn't happen - you're in disjoint file sets
- If it does, verify your file list matches the "FORBIDDEN AREAS" list above
- You are allowed to modify: `src/daemon/` and `src/config/`
- You are NOT allowed to modify: `tools/`, `src/providers/`, `src/auth/`, `src/security/`, `tests/`, `docs/`

## Parallel Agent Awareness

**Agents working simultaneously:**
- Agent 2 is standardizing error handling in `src/providers/` and `src/daemon/error_handling.py`
- Agent 3 is setting up testing infrastructure in `tests/` and `scripts/`
- Agent 4 is modernizing architecture in `src/bootstrap/` and `src/tools/registry.py`

**Your coordination with them:**
- None! Work completely independently
- They will not touch your files (`src/daemon/`, `src/config/`)
- You will not touch their files (see FORBIDDEN AREAS)

## Estimated Time

- **Effort:** 8-10 hours
- **Current Status:** Not started
- **Your Deadline:** Complete before Agent 2 and Agent 4 can start

## Start Now

Begin with Step 1: Analyze Current State

```bash
wc -l src/daemon/monitoring_endpoint.py
grep -n "^def \|^class " src/daemon/monitoring_endpoint.py | head -20
```

**Go!** Make the EX-AI MCP Server faster and more maintainable! 🚀
