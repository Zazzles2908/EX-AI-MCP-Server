# Upgrade Roadmap: zai-sdk v0.0.4 Integration

**Version:** 2.0
**Last Updated:** 2025-10-02
**Project Status:** Wave 2 - Synthesis & UX Improvements (IN PROGRESS)

---

## Project Overview

### Objective

Upgrade EX-AI-MCP-Server from zai-sdk v0.0.3.3 to v0.0.4, integrate GLM-4.6 with 200K context window, and implement new features (video generation, assistant API, character role-playing) for international users accessing api.z.ai.

**Key Finding:** NO BREAKING CHANGES - zai-sdk v0.0.4 is 100% backward compatible

### Timeline

**Start Date:** 2025-10-01
**Target Completion:** 2025-10-15
**Current Phase:** Wave 2 (Synthesis & UX Improvements)
**Wave 1 Status:** ✅ COMPLETE (100%)

---

## Wave-Based Execution Plan

### Wave 1: Foundation (Research + Independent Docs) - ✅ COMPLETE

**Status:** ✅ 100% Complete

**Track A: Research (CRITICAL PATH)**
- ✅ Task 2.1: Research zai-sdk latest version (v0.0.4)
- ✅ Task 2.2: Research GLM-4.6 specifications (200K context, $0.60/$2.20 pricing)
- ✅ Task 2.3: Research api.z.ai endpoints (comprehensive API documentation)
- ✅ Task 2.4: Breaking changes analysis - **NO BREAKING CHANGES** (100% backward compatible)
- ✅ Task 2.5: New features documentation (CogVideoX-2, Assistant API, CharGLM-3)

**Track B: Independent Documentation**
- ✅ Task 1.1: Create `docs/guides/tool-selection-guide.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.2: Create `docs/guides/parameter-reference.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.3: Create `docs/guides/web-search-guide.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.4: Create `docs/guides/query-examples.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.5: Create `docs/guides/troubleshooting.md` (validated with codereview_EXAI-WS)

**Validation Checkpoint:**
- ✅ All documentation validated with `codereview_EXAI-WS`
- ✅ Research findings verified against official sources (web-search)
- ✅ All deliverables reviewed with `analyze_EXAI-WS` (100% quality metrics)
- ✅ **Decision: PROCEED TO WAVE 2**

**Deliverables:** 24 files (~290KB documentation)

---

### Wave 2: Synthesis & UX (Research Synthesis + UX Improvements)

**Status:** IN PROGRESS (Epic 2.1 COMPLETE)

**Epic 2.1: Research Synthesis & Documentation Rewrite** ✅ COMPLETE
- ✅ Synthesize all Wave 1 research findings
- ✅ Create comprehensive research synthesis document (wave2-research-synthesis.md)
- ✅ Create updated implementation plan (wave2-implementation-plan.md)
- ✅ Document NO BREAKING CHANGES finding
- ✅ Document GLM-4.6 specifications (200K context, 355B/32B MoE)
- ✅ Document Kimi K2 specifications (256K context, 1T/32B MoE)
- ✅ Document new features (CogVideoX-2, Assistant API, CharGLM-3)

**Epic 2.2: Web Search Prompt Injection Fix** (HIGH PRIORITY)
- Fix chat_EXAI-WS web search issue
- Implement context-aware search triggers
- Test with various query types

**Epic 2.3: EXAI Tool UX Improvements**
- Implement dynamic context-aware messaging (continuation_id)
- Improve path validation error messages
- Add flexible tool parameters

**Epic 2.4: Diagnostic Tools & Logging**
- Create diagnostic tools for debugging
- Add comprehensive logging
- Implement progress indicators

**Epic 2.5: Wave 2 Validation & Testing**
- Test all UX improvements
- Validate web search fix
- Ensure no regressions
- **Decision Gate:** Proceed to Wave 3?

**Validation Checkpoint:**
- Review synthesized documentation ✅
- Test UX improvements (pending)
- Verify web search fix works correctly (pending)

---

### Wave 3: Core SDK Upgrade (Requirements + Provider + GLM-4.6)

**Status:** Not Started

**Tasks:**
- Task 5.1: Update `requirements.txt` (zai-sdk>=0.0.4)
- Task 5.2: Update `src/providers/glm_chat.py` for GLM-4.6
- Task 5.3: Implement 200K context window support
- Task 5.4: Update pricing configuration
- Task 5.5: Test streaming with new SDK
- Task 5.6: Test tool calling with new SDK
- Task 5.7: Verify backward compatibility

**Validation Checkpoint:**
- Run smoke tests with GLM-4.6
- Verify streaming works
- Verify tool calling works
- Confirm backward compatibility

---

### Wave 4: New Features (Video + Assistant + Character RP)

**Status:** Not Started

**Video Generation (CogVideoX-2):**
- Task 6.1: Implement video generation endpoint
- Task 6.2: Add async task polling
- Task 6.3: Create video generation tool
- Task 6.4: Add video generation examples

**Assistant API:**
- Task 7.1: Implement assistant conversation endpoint
- Task 7.2: Add metadata and attachment support
- Task 7.3: Create assistant tool
- Task 7.4: Add assistant examples

**Character Role-Playing (CharGLM-3):**
- Task 8.1: Implement character RP endpoint
- Task 8.2: Add meta parameter support
- Task 8.3: Create character RP tool
- Task 8.4: Add character RP examples

**Validation Checkpoint:**
- Test each new feature independently
- Verify integration with existing system
- Validate examples work correctly

---

### Wave 5: Testing & Validation

**Status:** Not Started

**Tasks:**
- Task 9.1: Create comprehensive test suite
- Task 9.2: Run integration tests
- Task 9.3: Perform security audit
- Task 9.4: Load testing and performance validation
- Task 9.5: Verify turnkey deployment
- Task 9.6: Test all documentation examples

**Validation Checkpoint:**
- All tests passing
- No security vulnerabilities
- Performance meets requirements
- Turnkey deployment verified

---

### Wave 6: Finalization (README + Sign-off)

**Status:** Not Started

**Tasks:**
- Task 10.1: Update main README.md
- Task 10.2: Create release notes
- Task 10.3: Update changelog
- Task 10.4: Final documentation review
- Task 10.5: Create upgrade guide for existing users
- Task 10.6: Tag release and push to GitHub

**Validation Checkpoint:**
- Final review complete
- All documentation accurate
- Release notes comprehensive
- Ready for production

---

## Research Findings (Wave 1)

### zai-sdk v0.0.4 (Task 2.1)

**Release Date:** September 30, 2025  
**Current Version:** v0.0.3.3  
**Upgrade Path:** 0.0.3.3 → 0.0.4

**Key Features:**
- Chat Completions (standard, streaming, tool calling, character RP, multimodal)
- Embeddings
- Video Generation (CogVideoX-2)
- Audio Processing
- Assistant API
- Web Search integration
- File Management
- Content Moderation
- Image Generation

**Installation:**
```bash
pip install zai-sdk>=0.0.4
```

**GitHub:** https://github.com/zai-org/z-ai-sdk-python  
**Python Support:** 3.8, 3.9, 3.10, 3.11, 3.12

---

### GLM-4.6 Specifications (Task 2.2)

**Release Date:** September 30, 2025

**Key Improvements:**
- **Context Window:** 200,000 tokens (expanded from 128K)
- **Pricing:** $0.60 input / $2.20 output per million tokens (1/5th cost of Claude Sonnet 4)
- **Performance:** Near parity with Claude Sonnet 4 (48.6% win rate)
- **Token Efficiency:** ~15% fewer tokens than GLM-4.5
- **Capabilities:** Advanced agentic abilities, superior coding, advanced reasoning, refined writing

**Benchmarks:**
- Near parity with Claude Sonnet 4
- Lags behind Claude Sonnet 4.5 in coding tasks
- Superior agentic abilities
- Advanced reasoning capabilities

**Official Documentation:** https://docs.z.ai/guides/llm/glm-4.6

---

### api.z.ai Endpoints (Task 2.3)

**Base URL:** `https://api.z.ai/api/paas/v4/`

**Authentication:** Bearer token (`Authorization: Bearer <token>`)

**Main Endpoints:**

1. **Chat Completions:** `POST /paas/v4/chat/completions`
   - Multimodal inputs (text, images, audio, video, files)
   - Streaming support
   - Tool calling (function, web search, retrieval)
   - Models: glm-4.6, glm-4.5, glm-4.5-air, glm-4.5-x, glm-4.5-airx, glm-4.5-flash

2. **Video Generation:** `POST /paas/v4/videos/generations` (async)
   - Model: cogvideox-2
   - Text-to-video and image-to-video
   - Customizable quality, FPS, size
   - Audio support

3. **Web Search Tool:** Integrated into chat completions
   - Search engines: search_pro_jina (default), search_pro_bing
   - Recency filters, domain whitelisting
   - Content size control, result sequencing

4. **Assistant API:** `POST /paas/v4/assistant/conversation`
   - Model: glm-4-assistant
   - Structured conversations
   - Metadata and attachments

5. **File Upload:** `POST /paas/v4/files/upload`
   - Multimodal chat support
   - Document analysis

6. **Embeddings:** Generate text embeddings
   - Configurable dimensions
   - Batch processing

**OpenAI Compatibility:**
- Full OpenAI-compatible API interface
- Drop-in replacement for OpenAI API
- Compatible with Claude Code, Kilo Code, Roo Code, Cline

---

## Breaking Changes (Task 2.4 - PENDING)

**To Be Determined:**
- API signature changes
- Parameter deprecations
- Response format changes
- Migration steps

**Analysis Method:**
- Use `analyze_EXAI-WS` to compare SDK versions
- Review zai-sdk changelog
- Test backward compatibility

---

## New Features Documentation (Task 2.5 - PENDING)

### CogVideoX-2 (Video Generation)

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Examples (text-to-video, image-to-video)
- Best practices

### Assistant API

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Conversation management
- Examples

### CharGLM-3 (Character Role-Playing)

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Character creation
- Examples

---

## Known Issues

### Web Search Prompt Injection (Wave 2 Fix)

**Issue:** chat_EXAI-WS with `use_websearch=true` responds with "SEARCH REQUIRED: Please immediately perform a web search..." instead of autonomously executing searches.

**Root Cause:** System prompt not sufficiently agentic to trigger autonomous web search behavior.

**Workaround:** Use web-search tool directly for now.

**Planned Fix:** Update chat tool system prompts in Wave 2 (UX Improvements).

**Impact:** Slows research tasks but doesn't block progress.

---

## Success Criteria

### Wave 1 (Current)
- ✅ All research findings documented with accurate sources
- ⏳ 5 user guides created and validated with codereview_EXAI-WS
- ⏳ Wave 1 validation checkpoint passed
- ⏳ Ready to proceed to Wave 2

### Wave 2
- Research synthesis complete
- UX improvements implemented
- Web search issue fixed
- Documentation updated

### Wave 3
- zai-sdk v0.0.4 installed
- GLM-4.6 integrated
- 200K context window working
- Backward compatibility verified

### Wave 4
- Video generation working
- Assistant API working
- Character RP working
- All examples tested

### Wave 5
- All tests passing
- No security vulnerabilities
- Performance validated
- Turnkey deployment verified

### Wave 6
- Documentation complete
- Release notes published
- Upgrade guide available
- Production ready

---

## Dependencies

### External Dependencies
- zai-sdk v0.0.4 (PyPI)
- Z.ai API access (api.z.ai)
- GitHub repository access

### Internal Dependencies
- Phase 0: Architecture & Design (COMPLETE)
- Phase 1: EXAI Recommendations + Dynamic Step Management (COMPLETE)
- Phase 1 Follow-Up: Meta-validation fixes (COMPLETE)

---

## Risk Assessment

### High Risk
- Breaking changes in zai-sdk v0.0.4 (mitigation: thorough testing)
- Web search integration issues (mitigation: Wave 2 fix planned)

### Medium Risk
- New feature integration complexity (mitigation: incremental implementation)
- Backward compatibility (mitigation: comprehensive testing)

### Low Risk
- Documentation accuracy (mitigation: EXAI validation)
- Performance regression (mitigation: load testing)

---

## Next Steps

### Immediate (Wave 1 Completion)
1. Complete Task 2.4: Identify breaking changes using analyze_EXAI-WS
2. Complete Task 2.5: Document new features using chat_EXAI-WS with web search
3. Create 5 user guides (Tasks 1.1-1.5)
4. Validate all documentation with codereview_EXAI-WS
5. Push Wave 1 changes to GitHub

### Short-term (Wave 2)
1. Synthesize research findings
2. Fix web search prompt injection issue
3. Rewrite upgrade documentation
4. Improve UX

### Medium-term (Waves 3-4)
1. Upgrade to zai-sdk v0.0.4
2. Integrate GLM-4.6
3. Implement new features

### Long-term (Waves 5-6)
1. Comprehensive testing
2. Final documentation
3. Release preparation

---

## Progress Tracking

**Overall Progress:** 15% (Wave 1: 60%, Waves 2-6: 0%)

**Completed:**
- ✅ Preliminary Step: Current state analysis
- ✅ Task 2.1: zai-sdk version research
- ✅ Task 2.2: GLM-4.6 specifications research
- ✅ Task 2.3: api.z.ai endpoints research

**In Progress:**
- ⏳ Task 2.4: Breaking changes identification
- ⏳ Task 2.5: New features documentation
- ⏳ Tasks 1.1-1.5: User guides creation

**Pending:**
- Waves 2-6 (all tasks)

---

**Last Updated:** 2025-10-02  
**Next Review:** After Wave 1 completion  
**Document Owner:** Development Team

