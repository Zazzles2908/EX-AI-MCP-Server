# 🔧 Daemon and MCP Testing Guide

**Purpose:** Guide for testing both daemon and MCP modes  
**Date:** 2025-10-05  
**Status:** ✅ Complete

---

## 📊 DUAL TESTING ARCHITECTURE

### Two Independent Testing Systems

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: MCP Integration Tests (tests/ directory)          │
│  ✅ ALREADY EXISTS - 40+ test files                         │
├─────────────────────────────────────────────────────────────┤
│  • Tests MCP protocol compliance                             │
│  • Tests stdio mode (direct server.py)                       │
│  • Tests WebSocket daemon mode (daemon + shim)               │
│  • Tests tool registration and discovery                     │
│  • Tests routing and configuration                           │
│  • Uses pytest framework                                     │
│  • Coverage: ~60%                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Provider API Tests (tool_validation_suite/)       │
│  ✅ NOW COMPLETE - 36 test files                            │
├─────────────────────────────────────────────────────────────┤
│  • Tests provider APIs directly (bypasses MCP)               │
│  • Tests Kimi and GLM API integration                        │
│  • Tests file upload, web search, conversations              │
│  • Tests cost tracking and performance                       │
│  • Uses custom TestRunner framework                          │
│  • Coverage: +25% (total 85%)                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 RUNNING DAEMON FOR TESTS

### Option 1: Start Daemon Manually (Recommended for Testing)

**Terminal 1 - Start Daemon:**
```powershell
# Start the WebSocket daemon
python scripts/run_ws_daemon.py
```

**Expected Output:**
```
WebSocket daemon starting on ws://127.0.0.1:8765
Server ready and listening...
```

**Terminal 2 - Run Tests:**
```powershell
# Run MCP integration tests
python run_tests.py

# Or run provider API tests
cd tool_validation_suite
python scripts/run_all_tests.py
```

### Option 2: Start Daemon in Background (Windows)

```powershell
# Start daemon in background
Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\scripts\ws_start.ps1" -WindowStyle Hidden

# Wait a few seconds for daemon to start
Start-Sleep -Seconds 5

# Run tests
python run_tests.py
```

### Option 3: Use Restart Script (From User Rules)

```powershell
# Restart daemon (kills existing and starts new)
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

---

## 🧪 TESTING SCENARIOS

### Scenario 1: Provider API Tests (No Daemon Required)

**What:** Tests provider APIs directly  
**Daemon:** Not required  
**Location:** `tool_validation_suite/`

```powershell
cd tool_validation_suite
python scripts/run_all_tests.py
```

**Tests:**
- Direct Kimi API calls
- Direct GLM API calls
- File upload functionality
- Web search activation
- Conversation management
- Cost tracking
- Performance monitoring

**Coverage:** Provider integration, feature activation

---

### Scenario 2: MCP Integration Tests (Daemon Optional)

**What:** Tests MCP protocol and tool registration  
**Daemon:** Optional (tests both stdio and daemon modes)  
**Location:** `tests/`

```powershell
# Run all MCP tests
python run_tests.py

# Run specific category
python run_tests.py --category mcp_protocol
python run_tests.py --category routing
python run_tests.py --category providers
```

**Tests:**
- MCP protocol compliance
- Tool registration
- Routing logic
- Configuration
- Both stdio and WebSocket modes

**Coverage:** MCP layer, routing, configuration

---

### Scenario 3: End-to-End Tests (Daemon Required)

**What:** Tests full stack from MCP client to provider  
**Daemon:** Required  
**Location:** `tests/phase8/`

**Terminal 1:**
```powershell
python scripts/run_ws_daemon.py
```

**Terminal 2:**
```powershell
python run_tests.py --category e2e
```

**Tests:**
- Full workflow: MCP client → daemon → shim → tools → providers
- WebSocket communication
- Multi-turn conversations
- File handling through MCP
- Error propagation

**Coverage:** Full stack integration

---

## 📋 TESTING CHECKLIST

### Before Running Tests

- [ ] API keys set in `.env`
  - `MOONSHOT_API_KEY` (for Kimi)
  - `ZHIPUAI_API_KEY` (for GLM)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment verified (`python tool_validation_suite/scripts/setup_test_environment.py`)

### For Provider API Tests (No Daemon)

- [ ] Navigate to `tool_validation_suite/`
- [ ] Run `python scripts/run_all_tests.py`
- [ ] Review results in `results/latest/`

### For MCP Integration Tests (Daemon Optional)

- [ ] Optionally start daemon (`python scripts/run_ws_daemon.py`)
- [ ] Run `python run_tests.py`
- [ ] Review pytest output

### For End-to-End Tests (Daemon Required)

- [ ] Start daemon in Terminal 1
- [ ] Verify daemon is running (check output)
- [ ] Run E2E tests in Terminal 2
- [ ] Stop daemon when done (Ctrl+C)

---

## 🔍 DAEMON STATUS VERIFICATION

### Check if Daemon is Running

```powershell
# Check if process is running
Get-Process python | Where-Object {$_.CommandLine -like "*run_ws_daemon*"}

# Or try to connect
Test-NetConnection -ComputerName 127.0.0.1 -Port 8765
```

### Expected Output (Running):
```
ComputerName     : 127.0.0.1
RemoteAddress    : 127.0.0.1
RemotePort       : 8765
InterfaceAlias   : Loopback Pseudo-Interface 1
SourceAddress    : 127.0.0.1
TcpTestSucceeded : True
```

### Expected Output (Not Running):
```
TcpTestSucceeded : False
```

---

## 🛠️ TROUBLESHOOTING

### Daemon Won't Start

**Issue:** Port already in use

```powershell
# Find process using port 8765
netstat -ano | findstr :8765

# Kill process (replace PID)
taskkill /PID <PID> /F

# Restart daemon
python scripts/run_ws_daemon.py
```

**Issue:** Module import errors

```powershell
# Verify dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Tests Fail to Connect to Daemon

**Issue:** Daemon not running

```powershell
# Start daemon first
python scripts/run_ws_daemon.py

# Wait for "Server ready" message
# Then run tests in another terminal
```

**Issue:** Wrong port

```powershell
# Check daemon configuration
# Default: ws://127.0.0.1:8765

# Verify in tests/conftest.py or test files
```

### Provider API Tests Fail

**Issue:** API keys not set

```powershell
# Check .env file
cat .env

# Or set environment variables
$env:MOONSHOT_API_KEY = "your_key"
$env:ZHIPUAI_API_KEY = "your_key"
```

**Issue:** Network/API errors

```powershell
# Test API connectivity
python -c "
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv('MOONSHOT_API_KEY'),
    base_url='https://api.moonshot.ai/v1'
)

response = client.chat.completions.create(
    model='kimi-k2-0905-preview',
    messages=[{'role': 'user', 'content': 'test'}]
)
print(response.choices[0].message.content)
"
```

---

## 📊 RECOMMENDED TESTING WORKFLOW

### Full System Validation

**Step 1: Provider API Tests (1-2 hours)**
```powershell
cd tool_validation_suite
python scripts/setup_test_environment.py
python scripts/run_all_tests.py
```

**Step 2: MCP Integration Tests (30 min)**
```powershell
cd ..
python run_tests.py --category unit
python run_tests.py --category integration
```

**Step 3: End-to-End Tests (30 min)**
```powershell
# Terminal 1
python scripts/run_ws_daemon.py

# Terminal 2
python run_tests.py --category e2e
```

**Step 4: Review Results**
```powershell
# Provider API results
cat tool_validation_suite/results/latest/reports/VALIDATION_REPORT.md

# MCP test results
# Check pytest output in terminal
```

**Total Time:** 2-3 hours  
**Expected Cost:** $3-6 USD (provider API tests only)  
**Coverage:** 85%+ overall system

---

## ✅ SUCCESS CRITERIA

### Provider API Tests

- [ ] All 36 test scripts execute
- [ ] 90%+ pass rate
- [ ] Cost under $5 USD
- [ ] No critical errors
- [ ] GLM Watcher observations generated

### MCP Integration Tests

- [ ] All pytest tests pass
- [ ] Both stdio and daemon modes work
- [ ] Tool registration successful
- [ ] Routing logic correct

### End-to-End Tests

- [ ] Daemon starts successfully
- [ ] WebSocket connection established
- [ ] Full workflow completes
- [ ] Multi-turn conversations work
- [ ] File handling works

---

**Daemon and MCP Testing Guide Complete** ✅  
**Date:** 2025-10-05  
**Ready for comprehensive system validation!** 🚀

