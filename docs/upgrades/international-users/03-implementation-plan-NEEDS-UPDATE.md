# Z.ai SDK 0.0.4 Upgrade - Implementation Plan

**Date:** 2025-10-01  
**Planned By:** Augment Agent with EXAI Planner  
**Target:** Upgrade from zai-sdk 0.0.3.3 to 0.0.4 and integrate GLM-4.6

---

## Overview

This document outlines the complete implementation plan for upgrading the EX-AI-MCP-Server to use zai-sdk 0.0.4 and integrate the new GLM-4.6 model along with other enhancements.

---

## Pre-Flight Checklist

- [x] Server is running
- [x] On main branch with clean working tree
- [x] gh-mcp tools available and configured
- [x] External test directory configured
- [x] .env file secured (in .gitignore)
- [ ] Feature branch created
- [ ] Dependencies updated
- [ ] SDK installed

---

## Implementation Phases

```
Phase 1: Foundation & Preparation (30 min)
    |
    v
Phase 2: SDK Integration (2 hours)
    |
    v
Phase 3: Model Registry Updates (1 hour)
    |
    v
Phase 4: Feature Enhancements (3 hours)
    |
    v
Phase 5: Testing & Documentation (2 hours)
    |
    v
COMPLETE
```

---

## Phase 1: Foundation & Preparation

### Objectives
- Create isolated feature branch
- Update dependencies
- Install new SDK
- Create backups

### Tasks

#### 1.1. Create Feature Branch
```bash
# Use gh-mcp to create branch
gh_branch_checkout_gh-mcp(
    branch="feature/zai-sdk-0.0.4-upgrade",
    path="c:\\Project\\EX-AI-MCP-Server"
)
```

#### 1.2. Update requirements.txt
```diff
- zai-sdk>=0.0.3.3
+ zai-sdk>=0.0.4
```

#### 1.3. Install New SDK
```bash
pip install --upgrade zai-sdk==0.0.4
```

#### 1.4. Review SDK Changelog
- Check GitHub releases: https://github.com/THUDM/z-ai-sdk-python/releases
- Review breaking changes
- Note new features

#### 1.5. Create Backups
```bash
# Backup critical files
cp src/providers/glm.py src/providers/glm_BACKUP_pre_0.0.4.py
cp src/providers/glm_config.py src/providers/glm_config_BACKUP_pre_0.0.4.py
cp src/providers/glm_chat.py src/providers/glm_chat_BACKUP_pre_0.0.4.py
```

#### 1.6. Restart Server
```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Acceptance Criteria
- [ ] Feature branch created and checked out
- [ ] New SDK installed successfully (verify with `pip show zai-sdk`)
- [ ] Backup files created
- [ ] No uncommitted changes
- [ ] Server running successfully

---

## Phase 2: SDK Integration

### Objectives
- Integrate new ZaiClient/ZhipuAiClient classes
- Update configuration for new SDK
- Maintain backward compatibility
- Update error handling

### Files to Modify

#### 2.1. src/providers/glm.py
**Changes:**
- Add imports for new client classes
- Integrate ZaiClient for international endpoint
- Integrate ZhipuAiClient for China endpoint
- Update client initialization logic
- Add fallback to old zhipuai SDK if needed

**Example:**
```python
from zai import ZaiClient, ZhipuAiClient
import zai

# Client initialization
if use_international_endpoint:
    client = ZaiClient(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries
    )
else:
    client = ZhipuAiClient(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries
    )
```

#### 2.2. src/providers/glm_config.py
**Changes:**
- Add configuration for new SDK options
- Add endpoint selection (international vs China)
- Add timeout and retry configurations
- Update default values

**New Config Options:**
```python
GLM_USE_INTERNATIONAL_ENDPOINT = os.getenv("GLM_USE_INTERNATIONAL_ENDPOINT", "true").lower() == "true"
GLM_SDK_TIMEOUT = float(os.getenv("GLM_SDK_TIMEOUT", "300.0"))
GLM_SDK_MAX_RETRIES = int(os.getenv("GLM_SDK_MAX_RETRIES", "3"))
GLM_SDK_CONNECT_TIMEOUT = float(os.getenv("GLM_SDK_CONNECT_TIMEOUT", "8.0"))
```

#### 2.3. src/providers/glm_chat.py
**Changes:**
- Update client initialization calls
- Update error handling for new exceptions
- Ensure streaming compatibility
- Test response parsing

**Error Handling:**
```python
try:
    response = client.chat.completions.create(...)
except zai.APIStatusError as err:
    logger.error(f"API Status Error: {err}")
    raise
except zai.APITimeoutError as err:
    logger.error(f"Request Timeout: {err}")
    raise
except Exception as err:
    logger.error(f"Unexpected Error: {err}")
    raise
```

#### 2.4. Testing
```python
# Test via EXAI MCP chat tool
chat_EXAI-WS(
    prompt="Test GLM-4.6 with new SDK",
    model="glm-4.6"
)
```

#### 2.5. Server Restart
```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Acceptance Criteria
- [ ] New SDK clients integrated
- [ ] Existing functionality preserved
- [ ] Error handling updated
- [ ] Basic chat works via MCP
- [ ] No breaking changes to existing tools

---

## Phase 3: Model Registry Updates

### Objectives
- Add GLM-4.6 to model registry
- Add GLM-4.5-Air and GLM-4.5V
- Update model capabilities metadata
- Configure context lengths

### Files to Modify

#### 3.1. src/providers/registry_config.py
**Add New Models:**

```python
# GLM-4.6 - Flagship model
{
    "name": "glm-4.6",
    "provider": "glm",
    "context_length": 128000,
    "capabilities": ["chat", "function_calling", "web_search", "reasoning", "coding", "agentic"],
    "description": "GLM-4.6 flagship model with 355B total params, 32B active. Hybrid reasoning with thinking mode.",
    "parameters": {
        "total_params": "355B",
        "active_params": "32B",
        "architecture": "MoE"
    }
},

# GLM-4.5-Air - Fast and cost-effective
{
    "name": "glm-4.5-air",
    "provider": "glm",
    "context_length": 128000,
    "capabilities": ["chat", "function_calling", "web_search", "reasoning", "coding"],
    "description": "GLM-4.5-Air with 106B total params, 12B active. Fast responses, cost-effective.",
    "parameters": {
        "total_params": "106B",
        "active_params": "12B",
        "architecture": "MoE"
    }
},

# GLM-4.5V - Vision model
{
    "name": "glm-4.5v",
    "provider": "glm",
    "context_length": 128000,
    "capabilities": ["chat", "vision", "multimodal", "image_understanding"],
    "description": "GLM-4.5V vision model for image understanding and visual reasoning.",
    "parameters": {
        "modality": "vision"
    }
}
```

#### 3.2. Update .env.example
**Add New Configuration Options:**

```bash
# -------- GLM (ZhipuAI/Z.ai) Provider Settings --------
# Use international endpoint (true) or China endpoint (false)
GLM_USE_INTERNATIONAL_ENDPOINT=true

# SDK Configuration
GLM_SDK_TIMEOUT=300.0
GLM_SDK_MAX_RETRIES=3
GLM_SDK_CONNECT_TIMEOUT=8.0

# Default model for GLM provider
GLM_DEFAULT_MODEL=glm-4.6

# Available models: glm-4.6, glm-4.5, glm-4.5-air, glm-4.5v, glm-4-assistant
```

#### 3.3. Testing
```python
# Test model access via MCP
chat_EXAI-WS(
    prompt="Test GLM-4.6 model",
    model="glm-4.6"
)

chat_EXAI-WS(
    prompt="Test GLM-4.5-Air model",
    model="glm-4.5-air"
)
```

#### 3.4. Server Restart
```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Acceptance Criteria
- [ ] All new models in registry
- [ ] Correct context lengths configured (128K)
- [ ] Models accessible via MCP
- [ ] .env.example updated
- [ ] Documentation reflects new models

---

## Phase 4: Feature Enhancements

### Objectives
- Implement assistant API support
- Enhance video generation capabilities
- Update streaming for new SDK
- Add multimodal support

### Tasks

#### 4.1. Assistant API Support
**Create:** `src/providers/glm_assistant.py`

```python
def assistant_conversation(
    client,
    assistant_id: str,
    model: str,
    messages: list,
    stream: bool = False,
    **kwargs
):
    """
    Wrapper for assistant conversation API
    """
    response = client.assistant.conversation(
        assistant_id=assistant_id,
        model=model,
        messages=messages,
        stream=stream,
        **kwargs
    )
    return response
```

#### 4.2. Video Generation Support
**Update:** `src/providers/glm_files.py` or create `src/providers/glm_video.py`

```python
def generate_video(
    client,
    model: str,
    prompt: str,
    quality: str = "quality",
    with_audio: bool = True,
    size: str = "1920x1080",
    fps: int = 30,
    **kwargs
):
    """
    Generate video using GLM video models
    """
    response = client.videos.generations(
        model=model,
        prompt=prompt,
        quality=quality,
        with_audio=with_audio,
        size=size,
        fps=fps,
        **kwargs
    )
    return response

def retrieve_video_result(client, video_id: str):
    """
    Retrieve video generation result
    """
    return client.videos.retrieve_videos_result(id=video_id)
```

#### 4.3. Streaming Updates
**Update:** `src/providers/glm_chat.py`

- Ensure streaming works with new SDK
- Test chunk parsing
- Verify metadata handling

#### 4.4. Multimodal Support
**Update:** `src/providers/glm_chat.py`

- Add image encoding utilities
- Support base64 image inputs
- Handle multimodal message formats

### Acceptance Criteria
- [ ] Assistant API functional
- [ ] Video generation works
- [ ] Streaming compatible with new SDK
- [ ] Multimodal chat supported
- [ ] All features tested via MCP

---

## Phase 5: Testing & Documentation

### Objectives
- Create comprehensive test suite
- Validate all models via EXAI MCP tools
- Complete documentation
- Final validation

### Tasks

#### 5.1. Create Test Suite
**Location:** External test directory

```python
# test_glm_4_6.py
def test_glm_4_6_chat():
    """Test GLM-4.6 basic chat"""
    pass

def test_glm_4_6_streaming():
    """Test GLM-4.6 streaming"""
    pass

def test_glm_4_6_function_calling():
    """Test GLM-4.6 function calling"""
    pass

def test_glm_4_5_air():
    """Test GLM-4.5-Air model"""
    pass

def test_glm_4_5v_vision():
    """Test GLM-4.5V vision capabilities"""
    pass
```

#### 5.2. Validate via EXAI MCP
```python
# Test each model
for model in ["glm-4.6", "glm-4.5-air", "glm-4.5v"]:
    chat_EXAI-WS(
        prompt=f"Test {model} functionality",
        model=model
    )
```

#### 5.3. Documentation Files
- [x] `docs/upgrades/glm-4.6-and-sdk-changes.md` - Research findings
- [x] `docs/upgrades/zai-sdk-upgrade-implementation-plan.md` - This file
- [ ] Update main README.md if needed

#### 5.4. Final Validation
- [ ] All tests pass
- [ ] No credential leaks in commits
- [ ] All documentation complete
- [ ] Server stable

#### 5.5. Commit Changes
```bash
# Use gh-mcp to commit
gh_branch_push_gh-mcp(
    path="c:\\Project\\EX-AI-MCP-Server",
    message="feat: upgrade to zai-sdk 0.0.4 and add GLM-4.6 support"
)
```

### Acceptance Criteria
- [ ] All tests pass
- [ ] Documentation complete and accurate
- [ ] Changes committed to feature branch
- [ ] Ready for PR or merge

---

## Rollback Plan

If critical issues are encountered:

1. **Immediate Rollback:**
   ```bash
   git checkout main
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
   ```

2. **Restore Backups:**
   ```bash
   cp src/providers/glm_BACKUP_pre_0.0.4.py src/providers/glm.py
   cp src/providers/glm_config_BACKUP_pre_0.0.4.py src/providers/glm_config.py
   cp src/providers/glm_chat_BACKUP_pre_0.0.4.py src/providers/glm_chat.py
   ```

3. **Downgrade SDK:**
   ```bash
   pip install zai-sdk==0.0.3.3
   ```

4. **Document Issues:**
   Create `docs/upgrades/issues-encountered.md` with details

---

## Success Metrics

- [ ] All existing MCP tools continue to work
- [ ] New models (GLM-4.6, GLM-4.5-Air, GLM-4.5V) accessible
- [ ] Streaming functions properly
- [ ] No credential leaks in commits
- [ ] Documentation complete and accurate
- [ ] Server stable and performant

---

## Next Steps

After successful implementation:

1. Test in production-like environment
2. Monitor performance and error rates
3. Gather user feedback
4. Plan for additional feature integration
5. Consider PR to main branch

---

**Status:** READY FOR EXECUTION  
**Last Updated:** 2025-10-01  
**Estimated Total Time:** 8.5 hours

