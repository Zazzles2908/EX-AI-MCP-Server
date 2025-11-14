# 07 - Smart Routing Documentation

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

---

## 🎯 Smart Routing Overview

The EX-AI MCP Server features an intelligent routing system that dynamically selects optimal providers and models based on tool requirements and provider capabilities.

### What is Smart Routing?

Smart routing is the system's ability to:
- Match tool requirements with provider capabilities
- Automatically select the best model for each task
- Optimize execution paths based on request features
- Prevent compatibility errors (e.g., Kimi + web search)
- Enable cost-aware and performance-optimized routing

---

## 📚 Documentation Structure

### 📊 [Smart Routing Analysis](SMART_ROUTING_ANALYSIS.md)
**Comprehensive analysis of the routing system architecture and implementation gap**

This document provides:
- **Executive Summary** - The critical routing gap problem
- **Current Architecture** - What routing is actually being used
- **CapabilityRouter Design** - The sophisticated system that exists but isn't used
- **Gap Analysis** - Why design and implementation are disconnected
- **Tool Analysis** - All 33 tools and their routing characteristics
- **Critical Issues** - Web search bug and other compatibility problems
- **Integration Opportunities** - Where to connect the missing pieces
- **Implementation Roadmap** - 5-phase plan with specific tasks and timelines

**Start here if you want to understand the routing system comprehensively.**

### 🧠 [MiniMax M2 Smart Router Proposal](MINIMAX_M2_SMART_ROUTER_PROPOSAL.md)
**Revolutionary approach: Replace 2,500 lines of routing code with 150 lines using MiniMax M2**

This document proposes:
- **The Problem** - Current routing has ~2,500 lines of complex, hardcoded logic
- **The Solution** - Use MiniMax M2 (Agent-focused model) for intelligent routing
- **Architecture** - Simple router module + 1 API call = smart routing
- **Benefits** - 94% code reduction, intelligent adaptation, easier maintenance
- **Implementation** - Complete code examples and configuration
- **Cost Analysis** - ~$0.01 per decision vs. 8-14 days development
- **Comparison** - Current vs. MiniMax M2 system side-by-side
- **Future Enhancements** - Learning mode, cost-aware routing, A/B testing

**Key Insight:** MiniMax M2 is built for Agent workflows - perfect for smart routing!

**Read this if you want to dramatically simplify and smarten the routing system.**

### 🏗️ [Comprehensive Codebase Analysis](COMPREHENSIVE_CODEBASE_ANALYSIS.md)
**Complete dismantling plan: 65,000+ lines → 1,400 lines (98% reduction)**

This document provides:
- **Codebase Overview** - 6,070 files, 150,000+ lines, deep analysis
- **Provider Analysis** - GLM & Kimi actual capabilities, file by file breakdown
- **Architectural Issues** - Provider chaos, tool bloat, configuration madness
- **Provider Reality** - What GLM and Kimi actually support (web search, vision, etc.)
- **Detailed Checklist** - 10-week dismantling plan with specific files to remove
- **Target Architecture** - 1 orchestrator + 1 router + 2 providers = entire system
- **File Elimination List** - Exactly what to remove, merge, create, simplify
- **Success Metrics** - 98% code reduction, 95% fewer files, true AI assistance

**Key Insight:** Instead of fixing routing, we eliminate the need for it!

**Read this to understand the full scope and build a comprehensive refactoring plan.**

### 🔧 [Corrected Analysis with EXAI MCP](CORRECTED_ANALYSIS.md)
**Updated analysis with EXAI-MCP integration and corrected provider capabilities**

This document provides:
- **Corrected Context Windows** - GLM-4.6: 200K, Kimi K2: 256K (not 128K)
- **EXAI MCP Integration** - 29 tools via WebSocket, orchestrator approach
- **Updated Architecture** - MCP Client → EXAI Orchestrator → Smart Router → Providers
- **Implementation Plan** - 3-phase approach with specific timelines
- **Z.AI SDK** - Confirmed usage of zai-sdk>=0.0.4
- **Key Insight** - Smarten existing EXAI MCP interface instead of dismantling

**Read this to understand the corrected vision with EXAI-MCP integration.**

### 🧠 [True Intelligence Vision](TRUE_INTELLIGENCE_VISION.md)
**Vision for truly intelligent system: users describe goals, system handles execution**

This document provides:
- **True Intelligence Definition** - Users say WHAT, system handles HOW
- **EXAI-MCP Opportunity** - 29 tools with intelligent orchestrator
- **Architecture Components** - Intent recognition, tool orchestration, natural language interface
- **Implementation Phases** - 5 phases from basic orchestrator to true intelligence
- **User Experience Flow** - Before (12+ interactions) vs After (2 interactions)
- **Success Metrics** - Task completion, time to solution, user satisfaction

**Key Insight:** True intelligence means users never choose tools!

**Read this to understand the future vision of intelligent AI assistance.**

### ✅ [Implementation Checklist](IMPLEMENTATION_CHECKLIST.md)
**Complete step-by-step implementation guide with timelines and success criteria**

This document provides:
- **Phase 1** - Fix provider capabilities (context windows, web search)
- **Phase 2** - Build EXAI-MCP orchestrator (intent recognition, tool chaining)
- **Phase 3** - MiniMax M2 smart router (2,500 lines → 150 lines)
- **Phase 4** - Testing & deployment (gradual rollout, monitoring)
- **Detailed File Changes** - Create, modify, remove operations
- **Risk Mitigation** - 5 major risks with mitigation strategies
- **Success Metrics** - User experience, system performance, business impact

**Read this to execute the implementation plan.**

---

## 🎓 Quick Reference

### Current Routing System
- **Location:** `src/providers/registry_selection.py`
- **Method:** Simple 3-category fallback chains
- **Categories:**
  - `FAST_RESPONSE` → GLM-4.6 only
  - `EXTENDED_REASONING` → Kimi K2 models only
  - `BALANCED` → GLM-4.5 series

### CapabilityRouter System
- **Location:** `src/providers/capability_router.py`
- **Method:** Capability-aware intelligent routing
- **Features:**
  - 7 execution paths (DIRECT, STANDARD, STREAMING, THINKING, VISION, FILE_UPLOAD, TOOL_CALLING)
  - Provider capability matrices
  - Tool requirement specifications
  - Dynamic provider selection

---

## 🔍 Key Concepts

### Execution Paths
Smart routing determines the optimal execution path based on request features:

| Execution Path | Trigger | Purpose |
|---------------|---------|---------|
| **DIRECT** | Utility tools (no AI needed) | Bypass model entirely |
| **STANDARD** | Basic model execution | Standard AI model call |
| **STREAMING** | Streaming requested + supported | Real-time response streaming |
| **THINKING** | Deep reasoning required | Advanced reasoning mode |
| **VISION** | Images present | Image processing capabilities |
| **FILE_UPLOAD** | Files attached | File handling and processing |
| **TOOL_CALLING** | Function calling needed | Tool invocation support |

### Provider Capabilities
**Kimi (Moonshot):**
- ✅ Streaming, Thinking Mode, File Uploads, Vision, Tool Calling
- ❌ **Web Search** (critical limitation)
- 128K context window

**GLM (ZhipuAI):**
- ✅ Streaming, Thinking Mode, File Uploads, Vision, Tool Calling, **Web Search**
- 128K context window

---

## 🚨 Critical Issues

### 1. Web Search Bug
**Problem:** Kimi does not support web search, but tools can route web search requests to Kimi via simple categories.

**Impact:** Runtime errors when web search is used with Kimi.

**Fix:** Use `CapabilityRouter.get_optimal_provider()` for web search → routes to GLM automatically.

### 2. Unused CapabilityRouter
**Problem:** 441-line sophisticated routing system is virtually unused.

**Impact:** Tools use simple hardcoded fallback chains instead of intelligent routing.

**Fix:** Integrate CapabilityRouter into tool execution flow.

### 3. Missing Request Validation
**Problem:** No validation that provider can handle request before API calls.

**Impact:** Runtime errors for incompatible tool-provider combinations.

**Fix:** Add `CapabilityRouter.validate_request()` before provider selection.

---

## 💡 Implementation Roadmap

### Phase 1: Critical Web Search Fix (1-2 days)
- [ ] Fix web search routing to prevent Kimi + web search errors
- [ ] Test all tools that use web search
- [ ] Update tool requirements for web search

### Phase 2: Auto Mode Integration (2-3 days)
- [ ] Connect CapabilityRouter to model selection
- [ ] Update SimpleTool to use intelligent routing
- [ ] Add validation before provider calls

### Phase 3: Request Validation (2-3 days)
- [ ] Implement capability validation
- [ ] Add feature-specific routing
- [ ] Test with all tool categories

### Phase 4: Execution Path Optimization (3-4 days)
- [ ] Implement ExecutionPath routing
- [ ] Add cost-aware selection
- [ ] Performance optimization

### Phase 5: Documentation & Cleanup (1-2 days)
- [ ] Document routing behavior
- [ ] Clean up legacy code
- [ ] Add monitoring and telemetry

**Total Effort:** 8-14 days

---

## 🔗 Related Documentation

- **[01 - Architecture Overview](../01-architecture-overview/)** - System architecture
- **[04 - API & Tools Reference](../04-api-tools-reference/)** - Tool documentation
- **[05 - Operations & Management](../05-operations-management/)** - Monitoring and troubleshooting

---

## 👥 Contributing

When working on routing improvements:

1. **Always use CapabilityRouter** for new provider features
2. **Add ToolRequirements** for any new tools
3. **Update provider capabilities** when providers add features
4. **Test with all tool categories** to ensure compatibility
5. **Document routing decisions** for future reference

---

**Smart routing is the key to efficient, error-free AI model utilization. This documentation provides everything you need to understand and improve the routing system.**
