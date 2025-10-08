# zai-sdk Upgrade Documentation - International Users

**Target Audience:** International/Overseas users (NOT mainland China)  
**SDK Package:** `zai-sdk` (NOT `zhipuai`)  
**API Platform:** https://api.z.ai/api/paas/v4/  
**Documentation:** https://docs.z.ai/  
**Status:** 🚧 IN PROGRESS - Research and planning phase

---

## 📋 Document Index

### 01-scope-gaps-identified.md ✅ COMPLETE
**Purpose:** Identifies gaps in EXAI tooling discovered during systematic testing  
**Status:** Complete - 4 gaps identified  
**Key Findings:**
- Native web search not working in chat tool (HIGH priority fix)
- EXAI workflow tools require manual investigation (by design)
- No autonomous web research tool available
- Requires absolute file paths

**Action Required:** Fix native web search before proceeding with upgrade

---

### 02-glm-4.6-and-zai-sdk-research-NEEDS-UPDATE.md ⚠️ NEEDS UPDATE
**Purpose:** Research on GLM-4.6 model and zai-sdk features  
**Status:** OUTDATED - Contains inaccuracies  
**Issues:**
- Did not use native web search (used training data)
- Missing dual SDK clarification (zhipuai vs zai-sdk)
- Incorrect GLM-4.6 release date
- Incorrect context length (128K vs 200K)
- Missing video generation, assistant API, character RP

**Action Required:** Rewrite with corrected information for international users

---

### 03-implementation-plan-NEEDS-UPDATE.md ⚠️ NEEDS UPDATE
**Purpose:** 5-phase implementation plan for zai-sdk upgrade  
**Status:** OUTDATED - Based on incorrect research  
**Issues:**
- Based on document 02 which has inaccuracies
- Missing new features (video, assistant, character RP)
- Needs clarification for international users
- Missing scope gap fixes in implementation phases

**Action Required:** Rewrite based on corrected research and scope gaps

---

### 04-critical-corrections.md ✅ REFERENCE
**Purpose:** Documents all errors found in initial research  
**Status:** Complete - Reference document  
**Key Corrections:**
- Dual SDK packages (zhipuai for China, zai-sdk for international)
- GLM-4.6 released Sept 30, 2025 (not July)
- Context length is 200K tokens (not 128K)
- Video generation, assistant API, character RP features

**Use:** Reference when updating documents 02 and 03

---

### 05-summary-corrections.md ✅ REFERENCE
**Purpose:** Executive summary of what was missed  
**Status:** Complete - Reference document  
**Key Points:**
- Comparison table of errors vs corrections
- Lessons learned
- What to fix in other documents

**Use:** Quick reference for understanding mistakes

---

## 🎯 Current Status

### ✅ Completed
1. Systematic testing of EXAI tools
2. Identification of scope gaps
3. Documentation of errors in initial research
4. Organization of documents with clear naming

### ⏳ In Progress
1. Fixing native web search in chat tool
2. Comprehensive research using working tools
3. Rewriting documents 02 and 03 with corrections

### ❌ Not Started
1. Implementation of zai-sdk upgrade
2. Testing of new features
3. Migration of existing code

---

## 🚨 Critical Issues to Resolve

### Priority 1: Fix Native Web Search
**Issue:** chat_EXAI-WS with use_websearch=true doesn't perform web browsing  
**Impact:** Cannot use EXAI tools for research  
**Status:** Identified, needs debugging  
**Files:** `tools/chat.py`, `src/providers/capabilities.py`, `src/providers/glm_chat.py`

### Priority 2: Update Research Documents
**Issue:** Documents 02 and 03 contain inaccuracies  
**Impact:** Cannot proceed with implementation using wrong information  
**Status:** Corrections documented, rewrite needed  
**Dependencies:** Should use working web search for verification

### Priority 3: Create Implementation Checklist
**Issue:** Need comprehensive checklist including scope gap fixes  
**Impact:** Implementation may miss critical steps  
**Status:** Waiting for corrected research  
**Dependencies:** Requires updated documents 02 and 03

---

## 📦 Package Information

### For International Users (THIS PROJECT)
```bash
# Current version in requirements.txt
zai-sdk>=0.0.3.3

# Latest version (as of Sept 30, 2025)
zai-sdk==0.0.4
```

**Client Initialization:**
```python
from zai import ZaiClient

client = ZaiClient(
    api_key="your-api-key",
    base_url="https://api.z.ai/api/paas/v4/"
)
```

### For Mainland China Users (NOT THIS PROJECT)
```bash
# Different package!
zhipuai==2.1.5.20250825
```

**Client Initialization:**
```python
from zhipuai import ZhipuAI

client = ZhipuAI(
    api_key="your-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
```

**⚠️ IMPORTANT:** We are using `zai-sdk` for international users, NOT `zhipuai`!

---

## 🔧 Environment Configuration

### Current Configuration (.env)
```bash
# International API endpoint
GLM_API_KEY=<your-key>
GLM_API_URL=https://api.z.ai/api/paas/v4

# Web browsing enabled
GLM_ENABLE_WEB_BROWSING=true

# Default model
DEFAULT_MODEL=glm-4.5-flash
```

### After Upgrade
```bash
# Same configuration, but with access to:
# - GLM-4.6 model (200K context)
# - Video generation (CogVideoX-2)
# - Assistant API
# - Character role-playing (CharGLM-3)
```

---

## 🎯 Models Available (International Platform)

### Current Models
- `glm-4.5` - Full model, 128K context
- `glm-4.5-flash` - Fast inference, 128K context
- `glm-4.5-air` - Lightweight, 128K context
- `glm-4.5v` - Vision model, 128K context
- `glm-4` - Previous generation
- `glm-4v` - Previous generation vision

### New Models (After Upgrade)
- `glm-4.6` - Latest flagship, **200K context** 🆕
- `cogvideox-2` - Video generation 🆕
- `charglm-3` - Character role-playing 🆕
- `glm-4-assistant` - Assistant API 🆕

---

## 📚 Official Resources

### For International Users
- **Platform:** https://z.ai/
- **API Docs:** https://docs.z.ai/
- **SDK GitHub:** https://github.com/THUDM/z-ai-sdk-python
- **Blog:** https://z.ai/blog/
- **Base URL:** https://api.z.ai/api/paas/v4/

### For Mainland China Users (Reference Only)
- **Platform:** https://open.bigmodel.cn/
- **SDK Package:** `zhipuai` (different from ours!)
- **Base URL:** https://open.bigmodel.cn/api/paas/v4/

---

## 🔄 Next Steps

### Immediate Actions
1. **Fix native web search** in chat_EXAI-WS tool
   - Debug tool schema injection
   - Test with glm_payload_preview
   - Verify web_search tool reaches API

2. **Conduct comprehensive research** using working tools
   - Use web-search and web-fetch (Augment tools)
   - Verify all information from official sources
   - Document findings for international users

3. **Rewrite documents 02 and 03**
   - Use corrected information from document 04
   - Focus on international users (zai-sdk, api.z.ai)
   - Include new features (video, assistant, character RP)
   - Add scope gap fixes to implementation plan

### Medium-Term Actions
1. Create detailed implementation checklist
2. Test new features with current setup
3. Plan migration strategy
4. Update provider code for new SDK

### Long-Term Actions
1. Implement zai-sdk upgrade
2. Add video generation support
3. Add assistant API support
4. Add character role-playing support
5. Update documentation
6. Test all features

---

## ⚠️ Important Notes

### For International Users
- ✅ Use `zai-sdk` package
- ✅ Use `api.z.ai` base URL
- ✅ Use `ZaiClient` class
- ✅ Follow this documentation

### NOT For Mainland China Users
- ❌ Do NOT use `zhipuai` package
- ❌ Do NOT use `open.bigmodel.cn` base URL
- ❌ Do NOT use `ZhipuAI` class
- ❌ This documentation is NOT for you

### Dual SDK Awareness
- There are TWO separate SDK packages
- They have different version numbers
- They use different base URLs
- They have different client classes
- Choose based on your region

---

## 📊 Progress Tracking

| Phase | Status | Documents | Action Required |
|-------|--------|-----------|-----------------|
| Research | ⚠️ PARTIAL | 01, 04, 05 | Fix web search, redo research |
| Planning | ❌ BLOCKED | 02, 03 | Rewrite with corrections |
| Implementation | ❌ NOT STARTED | TBD | Wait for planning |
| Testing | ❌ NOT STARTED | TBD | Wait for implementation |
| Documentation | ⏳ IN PROGRESS | This folder | Ongoing |

---

## 🎯 Success Criteria

### Research Phase Complete When:
- [ ] Native web search working in EXAI tools
- [ ] All information verified from official sources
- [ ] Documents 02 and 03 rewritten and accurate
- [ ] Implementation plan includes scope gap fixes

### Planning Phase Complete When:
- [ ] Detailed implementation checklist created
- [ ] All new features documented
- [ ] Migration strategy defined
- [ ] Testing strategy defined

### Implementation Phase Complete When:
- [ ] zai-sdk upgraded to latest version
- [ ] All new features implemented
- [ ] All tests passing
- [ ] Documentation updated

---

**Last Updated:** 2025-10-01  
**Maintained By:** Augment Agent  
**For:** International Users (api.z.ai, zai-sdk)  
**Status:** 🚧 Research and Planning Phase

