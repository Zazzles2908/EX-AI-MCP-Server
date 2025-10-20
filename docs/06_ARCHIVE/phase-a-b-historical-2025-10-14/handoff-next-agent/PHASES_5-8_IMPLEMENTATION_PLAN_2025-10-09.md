# Phases 5-8 Implementation Plan

**Date:** 2025-10-09 14:15 AEDT (Melbourne, Australia)  
**Status:** Planning  
**Branch:** `refactor/orchestrator-sync-v2.0.2`

---

## User-Provided Resources

The user collected comprehensive documentation and code examples in:
`c:\Project\EX-AI-MCP-Server\docs\handoff-next-agent\user_info_collected\`

**Files:**
1. **embeddings.py** - ZAI SDK embeddings implementation
2. **web_search.py** - ZAI SDK web search implementation
3. **completions.py** - ZAI SDK completions implementation
4. **async_completions.py** - ZAI SDK async completions
5. **glm_4.6_tir_guide.md** - GLM-4.6 Tool-Integrated Reasoning guide
6. **tool_call_guidance.md** - Kimi-K2 tool calling guide
7. **deploy_guidance.md** - Kimi-K2 deployment guide

---

## Phase 5: GLM Embeddings Implementation

### Current Status
- No GLM embeddings provider exists
- User wants GLM embeddings for robustness
- ZAI SDK has embeddings support (see embeddings.py)

### Implementation Plan

**1. Create GLMEmbeddingsProvider**

File: `src/providers/glm_embeddings_provider.py`

```python
from typing import List, Optional, Union
from zhipuai import ZhipuAI
import os

class GLMEmbeddingsProvider:
    """GLM Embeddings Provider using ZhipuAI SDK
    
    Supports:
    - embedding-3 model (8192 dimensions)
    - embedding-2 model (1024 dimensions)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        self.base_url = base_url or os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
        
        self.client = ZhipuAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def create_embeddings(
        self,
        input: Union[str, List[str]],
        model: str = "embedding-3",
        dimensions: Optional[int] = None,
        encoding_format: str = "float",
        user: Optional[str] = None
    ):
        """Create embeddings using GLM API
        
        Args:
            input: Text or list of texts to embed
            model: Model name (embedding-3 or embedding-2)
            dimensions: Number of dimensions (optional)
            encoding_format: Format for encoding (float or base64)
            user: User identifier (optional)
        """
        return self.client.embeddings.create(
            input=input,
            model=model,
            dimensions=dimensions,
            encoding_format=encoding_format,
            user=user
        )
```

**2. Add Environment Variables**

Add to `.env` and `.env.example`:
```bash
# GLM EMBEDDINGS CONFIGURATION
GLM_EMBEDDINGS_MODEL=embedding-3  # Options: embedding-3 (8192 dims), embedding-2 (1024 dims)
GLM_EMBEDDINGS_DIMENSIONS=8192    # Default dimensions for embedding-3
```

**3. Create Test Script**

File: `scripts/test_glm_embeddings.py`

```python
from src.providers.glm_embeddings_provider import GLMEmbeddingsProvider

def test_glm_embeddings():
    provider = GLMEmbeddingsProvider()
    
    # Test single text
    result = provider.create_embeddings(
        input="Hello, world!",
        model="embedding-3"
    )
    print(f"Single embedding dimensions: {len(result.data[0].embedding)}")
    
    # Test multiple texts
    result = provider.create_embeddings(
        input=["Hello", "World"],
        model="embedding-3"
    )
    print(f"Multiple embeddings count: {len(result.data)}")

if __name__ == "__main__":
    test_glm_embeddings()
```

**4. Update Documentation**

Update `docs/system-reference/` with GLM embeddings capabilities.

---

## Phase 6: Timestamp Improvements

### Current Status
- Logs use UTC timestamps
- User wants Melbourne/AEDT timezone
- User wants human-readable timestamps

### Implementation Plan

**1. Create Timezone Utility**

File: `src/utils/timezone.py`

```python
from datetime import datetime
import pytz

MELBOURNE_TZ = pytz.timezone('Australia/Melbourne')

def get_melbourne_timestamp() -> str:
    """Get current timestamp in Melbourne/AEDT timezone
    
    Returns:
        ISO 8601 timestamp with Melbourne timezone
        Example: 2025-10-09T14:15:30+11:00
    """
    return datetime.now(MELBOURNE_TZ).isoformat()

def get_human_readable_timestamp() -> str:
    """Get human-readable timestamp in Melbourne timezone
    
    Returns:
        Human-readable timestamp
        Example: 2025-10-09 14:15:30 AEDT
    """
    now = datetime.now(MELBOURNE_TZ)
    tz_name = now.strftime('%Z')  # AEDT or AEST
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}"
```

**2. Update provider_registry_snapshot.json Format**

Add timestamps to snapshot:
```json
{
  "generated_at": "2025-10-09T14:15:30+11:00",
  "generated_at_human": "2025-10-09 14:15:30 AEDT",
  "providers": {...},
  "models": {...}
}
```

**3. Update Log Files**

Add Melbourne timestamps to all log entries.

---

## Phase 7: .env Restructuring

### Current Status
- .env has 89 missing variables (from audit)
- Variables not organized by category
- .env.example needs detailed explanations

### Implementation Plan

**1. Reorganize .env by Category**

Categories:
- API Keys & Authentication
- GLM/ZhipuAI Configuration
- Kimi/Moonshot Configuration
- Feature Flags
- Server Configuration
- Logging Configuration
- Tool Configuration
- Advanced Settings

**2. Add One-Line Comments to .env**

```bash
# === API KEYS & AUTHENTICATION ===
GLM_API_KEY=xxx  # ZhipuAI API key for GLM models
KIMI_API_KEY=xxx  # Moonshot API key for Kimi models

# === GLM CONFIGURATION ===
GLM_BASE_URL=https://api.z.ai/api/paas/v4  # GLM API endpoint (z.ai is 3x faster)
GLM_ENABLE_WEB_BROWSING=true  # Enable web search for all GLM models
```

**3. Expand .env.example with Detailed Explanations**

```bash
# === API KEYS & AUTHENTICATION ===
# GLM_API_KEY: Your ZhipuAI API key
#   - Get from: https://open.bigmodel.cn/usercenter/apikeys
#   - Required for: All GLM models (glm-4.6, glm-4.5, etc.)
#   - Format: 32-character hex string + dot + 16-character base64
GLM_API_KEY=your_glm_api_key_here
```

**4. Add Missing 89 Variables**

Review `scripts/audit/audit_env_vars.py` findings and add all missing variables.

---

## Phase 8: Documentation Cleanup

### Current Status
- Many dates show 2025-01-08 (should be 2025-10-09)
- Contradictions between docs
- Outdated information

### Implementation Plan

**1. Fix All Dates**

Search and replace:
- `2025-01-08` → `2025-10-09`
- Add verification dates to all technical claims

**2. Remove Contradictions**

Consolidate information from:
- `docs/architecture/core-systems/`
- `docs/handoff-next-agent/`
- `docs/system-reference/`

**3. Update with Correct Information**

Based on Phases 1-4 findings:
- All GLM models support web search
- Correct model names (no glm-4-plus or glm-4-flash)
- Correct API endpoints (z.ai, moonshot.ai)
- SDK clients are initialized (not None)

**4. Consolidate Documentation**

Merge redundant files, remove outdated notes, update with current design intent.

---

## EXAI MCP Bug Investigation

### Issue Found
When calling `codereview_EXAI-WS` and `debug_EXAI-WS`:
```
Error: "cannot access local variable 'time' where it is not associated with a value"
```

### Analysis (from glm-4.5-flash)
- Bug in EXAI MCP server implementation
- Python scoping issue with variable named 'time'
- Likely naming conflict with Python's built-in `time` module
- Only affects codereview and debug tools (chat works fine)
- Introduced in recent changes (possibly Phase 4)

### Recommended Actions
1. Examine codereview and debug tool implementations
2. Check for variable scoping issues related to 'time'
3. Review recent commits that modified these tools
4. Create minimal test case to reproduce error

---

## Implementation Order

1. ✅ Phase 1: Model Name Corrections (COMPLETE)
2. ✅ Phase 2: URL Audit & Replacement (COMPLETE)
3. ✅ Phase 3: GLM Web Search Fix (COMPLETE)
4. ✅ Phase 4: HybridPlatformManager SDK Clients (COMPLETE)
5. ⏳ Phase 5: GLM Embeddings Implementation (NEXT)
6. ⏳ Phase 6: Timestamp Improvements
7. ⏳ Phase 7: .env Restructuring
8. ⏳ Phase 8: Documentation Cleanup

---

**Ready to proceed with Phase 5!**

**Last Updated:** 2025-10-09 14:15 AEDT

