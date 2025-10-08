# Setup Guide - Tool Validation Suite

**Time:** 10 minutes
**Last Updated:** 2025-10-05

---

## 📋 Prerequisites

- Python 3.12+
- API keys: Kimi (Moonshot), GLM (ZhipuAI)
- WebSocket daemon running

---

## 🚀 Setup Steps

### 1. Configure API Keys

Edit `.env.testing`:

```bash
# Kimi API
KIMI_API_KEY=your_kimi_key_here
KIMI_BASE_URL=https://api.moonshot.ai/v1

# GLM API
GLM_API_KEY=your_glm_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### 2. Start WebSocket Daemon

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Expected:** "Starting WS daemon on ws://127.0.0.1:8765"

### 3. Verify Setup

```powershell
python tool_validation_suite/tests/MCP_TEST_TEMPLATE.py
```

**Expected:** "Passed: 3 (100.0%)"

---

## 🆘 Troubleshooting

**Connection refused:** Daemon not running - start it first
**API errors:** Check API keys in `.env.testing`
**Tests fail:** Check `logs/ws_daemon.log` for errors

---

## ✅ Setup Complete

**Next:** Run tests with `python tool_validation_suite/tests/MCP_TEST_TEMPLATE.py`

