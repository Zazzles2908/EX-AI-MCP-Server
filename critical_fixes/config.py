"""Configuration for EX-AI-MCP-Server"""

import os

# Context Engineering
CONTEXT_ENGINEERING = os.getenv("CONTEXT_ENGINEERING", "false").lower() == "true"

# Model defaults
FAST_MODEL_DEFAULT = os.getenv("FAST_MODEL_DEFAULT", "glm-4.5-flash")
LONG_MODEL_DEFAULT = os.getenv("LONG_MODEL_DEFAULT", "kimi-k2-0711-preview")

# Router configuration
ROUTER_DIAGNOSTICS_ENABLED = os.getenv("ROUTER_DIAGNOSTICS_ENABLED", "false").lower() == "true"
ROUTER_CACHE_TTL = int(os.getenv("ROUTER_CACHE_TTL", "300"))
ROUTER_LOG_LEVEL = os.getenv("ROUTER_LOG_LEVEL", "INFO")
