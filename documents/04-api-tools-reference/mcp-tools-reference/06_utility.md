# MCP Utility Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 2 Utility Tools available in the EX-AI MCP Server. These tools provide system health monitoring and provider status information.

---

## 📚 Tool Categories

### 🛠️ Utility Tools (2 Total)
- **health_check** - System health verification
- **list_providers** - Show available providers

---

## 💾 Tool Details

### 1. health_check

**Description:** Verify system health and status

**Parameters:**
- `checks` (array, optional) - Specific checks to perform
- `detailed` (boolean, optional) - Return detailed diagnostics

**Example Usage:**
```python
# Basic health check
health = exai_mcp.health_check()

# Detailed check
health = exai_mcp.health_check(
    detailed=True,
    checks=["database", "providers", "websocket"]
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-11-10T10:00:00Z",
    "uptime": 3600,
    "version": "2.3.0",
    "components": {
      "database": {
        "status": "healthy",
        "latency": 15
      },
      "providers": {
        "glm": {
          "status": "healthy",
          "response_time": 1.2
        },
        "kimi": {
          "status": "healthy",
          "response_time": 2.1
        }
      },
      "websocket": {
        "status": "healthy",
        "connections": 5
      }
    }
  }
}
```

---

### 2. list_providers

**Description:** Show available AI providers and models

**Parameters:**
- `format` (string, optional) - Output format: 'summary', 'detailed'

**Example Usage:**
```python
# List providers
providers = exai_mcp.list_providers()

# Detailed view
providers = exai_mcp.list_providers(
    format="detailed"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "providers": [
      {
        "name": "glm",
        "models": [
          {
            "id": "glm-4.6",
            "context_length": 128000,
            "max_output": 8000,
            "capabilities": ["chat", "stream", "batch"]
          }
        ],
        "status": "active"
      },
      {
        "name": "kimi",
        "models": [
          {
            "id": "moonshot-v1-128k",
            "context_length": 128000,
            "max_output": 8000,
            "capabilities": ["chat", "file", "vision"]
          }
        ],
        "status": "active"
      }
    ]
  }
}
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Utility Tools Reference**
