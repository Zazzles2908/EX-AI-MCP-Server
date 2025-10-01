# AI Manager for Dynamic Step Allocation - Design Document

**Date:** 2025-10-01  
**Purpose:** Design system where AI manager (GLM-4.5-flash) dynamically determines optimal step count  
**Status:** ✅ DESIGN COMPLETE

---

## Executive Summary

This document proposes an **AI Manager system** that uses GLM-4.5-flash to intelligently determine the optimal number of steps for workflow tools based on request complexity, code/file amount, and investigation goals.

**Key Innovation:** Replace manual step estimation with intelligent, complexity-aware step allocation that adapts to the task at hand.

---

## Design Philosophy

### Core Principles

1. **Intelligent Routing:** GLM-4.5-flash excels at fast, intelligent routing decisions
2. **Complexity-Aware:** Different tasks need different investigation depths
3. **Goal-Oriented:** Steps should serve the investigation goal, not arbitrary counts
4. **Adaptive:** Allow mid-workflow adjustments based on progress
5. **Backward Compatible:** Existing workflows continue to work

### Design Goals

- ✅ Consistent step allocation across similar tasks
- ✅ Reduced manual guesswork for AI agents
- ✅ Faster execution for simple tasks
- ✅ Deeper investigation for complex tasks
- ✅ Token efficiency through smart planning

---

## Architecture Overview

### System Components

```
User Request
    ↓
AI Manager (GLM-4.5-flash)
    ├─→ Complexity Assessment
    ├─→ Step Count Determination
    ├─→ Investigation Strategy
    └─→ Workflow Execution Plan
        ↓
Workflow Tool (analyze, debug, etc.)
    ├─→ Execute Steps
    ├─→ Self-Assessment
    └─→ Dynamic Adjustment (if needed)
        ↓
Results
```

### AI Manager Responsibilities

1. **Analyze Request Complexity**
   - Simple: 1-2 files, straightforward question → 2-3 steps
   - Medium: 3-10 files, moderate complexity → 3-5 steps
   - Complex: 10+ files, architectural analysis → 5-7 steps
   - Very Complex: System-wide investigation → 7-10 steps

2. **Determine Optimal Step Count**
   - Based on: file count, code size, question type, tool type
   - Output: `recommended_total_steps` with rationale

3. **Provide Investigation Strategy**
   - Suggest what to investigate in each step
   - Identify key areas of focus
   - Recommend investigation order

4. **Monitor Progress** (Optional)
   - Track confidence evolution
   - Suggest early termination if appropriate
   - Recommend additional steps if needed

---

## Implementation Design

### Phase 1: AI Manager Integration (Minimal Viable Product)

#### A. New Tool: `plan_workflow` (Simple Tool)

**Purpose:** AI manager analyzes request and recommends step count

**Input:**
```python
{
    "tool_name": "analyze",  # Which workflow tool
    "user_request": "Analyze the authentication system",
    "file_count": 5,
    "code_size_estimate": "medium",  # small/medium/large
    "complexity_hints": ["security-critical", "multi-module"]
}
```

**Output:**
```python
{
    "recommended_total_steps": 4,
    "rationale": "Medium complexity: 5 files, security-critical analysis requires thorough investigation",
    "investigation_strategy": [
        "Step 1: Map authentication flow and identify entry points",
        "Step 2: Analyze security mechanisms and validation logic",
        "Step 3: Review session management and token handling",
        "Step 4: Assess overall security posture and provide recommendations"
    ],
    "complexity_assessment": "medium",
    "confidence": "high"
}
```

**Implementation:**
```python
# tools/capabilities/plan_workflow.py
class PlanWorkflowTool(BaseTool):
    def get_name(self) -> str:
        return "plan_workflow"
    
    async def execute(self, arguments: dict) -> list:
        # Use GLM-4.5-flash to analyze and recommend
        prompt = self._build_planning_prompt(arguments)
        response = await self.call_model(prompt, model="glm-4.5-flash")
        return self._parse_plan(response)
```

#### B. Workflow Tool Enhancement

**Modify `execute_workflow()` to accept AI manager recommendations:**

```python
async def execute_workflow(self, arguments: dict) -> list:
    request = self.get_workflow_request_model()(**arguments)
    
    # NEW: Check for AI manager recommendation
    if hasattr(request, 'ai_manager_plan') and request.ai_manager_plan:
        # Use AI manager's recommended steps
        request.total_steps = request.ai_manager_plan.get('recommended_total_steps', request.total_steps)
        self.investigation_strategy = request.ai_manager_plan.get('investigation_strategy', [])
    
    # Continue with normal workflow...
```

#### C. System Prompt Enhancement

**Add AI manager guidance to workflow prompts:**

```python
AI MANAGER INTEGRATION
When starting a workflow investigation, you may receive an AI manager plan with:
- recommended_total_steps: Suggested number of steps based on complexity
- investigation_strategy: Recommended approach for each step
- complexity_assessment: Task complexity (simple/medium/complex/very_complex)

Use this guidance to structure your investigation efficiently. You may adjust total_steps
if you discover the task is more/less complex than initially assessed.
```

### Phase 2: Confidence-Based Early Termination

#### A. Confidence Thresholds

**Allow early termination when confidence is high:**

```python
def should_terminate_early(self, request) -> bool:
    """Check if workflow can terminate early based on confidence."""
    confidence = self.get_request_confidence(request)
    
    # Terminate early if certain and at least 2 steps completed
    if confidence == "certain" and request.step_number >= 2:
        return True
    
    # Terminate early if very_high confidence and at least 3 steps completed
    if confidence == "very_high" and request.step_number >= 3:
        return True
    
    return False
```

#### B. Workflow Modification

```python
async def execute_workflow(self, arguments: dict) -> list:
    request = self.get_workflow_request_model()(**arguments)
    
    # NEW: Check for early termination
    if self.should_terminate_early(request):
        logger.info(f"{self.get_name()}: Early termination - high confidence reached")
        request.next_step_required = False
        return await self.handle_work_completion(response_data, request, arguments)
    
    # Continue with normal workflow...
```

### Phase 3: Mid-Workflow Step Adjustment

#### A. Step Increase Request

**Allow tools to request additional steps:**

```python
def request_additional_steps(self, current_request, additional_steps: int, reason: str):
    """Request additional investigation steps mid-workflow."""
    new_total = current_request.total_steps + additional_steps
    logger.info(f"{self.get_name()}: Requesting {additional_steps} additional steps. Reason: {reason}")
    current_request.total_steps = new_total
    return new_total
```

#### B. System Prompt Enhancement

```python
DYNAMIC STEP ADJUSTMENT
If you discover the investigation requires more steps than initially planned:
1. Set next_step_required=true
2. Increase total_steps to reflect the new estimate
3. Provide clear rationale in findings for why additional steps are needed

Example: "Investigation revealed additional complexity in the caching layer.
Increasing total_steps from 4 to 6 to thoroughly analyze cache invalidation logic."
```

---

## Complexity Assessment Matrix

### File Count Heuristics

| Files | Complexity | Recommended Steps | Rationale |
|-------|-----------|-------------------|-----------|
| 1-2 | Simple | 2-3 | Quick focused review |
| 3-5 | Medium | 3-4 | Moderate investigation |
| 6-10 | Medium-High | 4-5 | Multi-module analysis |
| 11-20 | Complex | 5-7 | System-wide investigation |
| 21+ | Very Complex | 7-10 | Comprehensive audit |

### Question Type Heuristics

| Question Type | Complexity | Step Modifier | Example |
|--------------|-----------|---------------|---------|
| "How does X work?" | Simple | +0 | Understanding single component |
| "Review X for issues" | Medium | +1 | Code review with analysis |
| "Analyze X architecture" | Complex | +2 | Architectural assessment |
| "Debug X problem" | Variable | +0 to +3 | Depends on problem complexity |
| "Security audit X" | Complex | +2 | Thorough security analysis |

### Tool-Specific Baselines

| Tool | Baseline Steps | Typical Range | Notes |
|------|---------------|---------------|-------|
| analyze | 5 | 3-7 | Strategic analysis |
| debug | 4 | 2-8 | Varies by bug complexity |
| codereview | 3 | 2-5 | Focused code review |
| precommit | 3 | 2-4 | Pre-commit validation |
| refactor | 4 | 3-6 | Refactoring analysis |
| secaudit | 5 | 4-8 | Security assessment |
| testgen | 3 | 2-5 | Test generation |
| thinkdeep | 4 | 3-7 | Deep reasoning |
| tracer | 3 | 2-5 | Code tracing |
| planner | 5 | 3-10 | Planning varies widely |
| consensus | Dynamic | N models | One step per model |
| docgen | Dynamic | 1 + N files | One step per file |

---

## Implementation Roadmap

### Phase 1: MVP (Week 1)
- ✅ Create `plan_workflow` tool
- ✅ Add AI manager prompt template
- ✅ Integrate with workflow tools (optional parameter)
- ✅ Test with analyze and debug tools
- ✅ Document usage patterns

### Phase 2: Confidence-Based Termination (Week 2)
- ✅ Implement `should_terminate_early()` logic
- ✅ Update system prompts with early termination guidance
- ✅ Test across all workflow tools
- ✅ Monitor token savings

### Phase 3: Dynamic Adjustment (Week 3)
- ✅ Implement `request_additional_steps()` logic
- ✅ Update system prompts with adjustment guidance
- ✅ Test complex scenarios requiring step increases
- ✅ Validate backward compatibility

### Phase 4: Optimization (Week 4)
- ✅ Analyze usage patterns and adjust heuristics
- ✅ Fine-tune complexity assessment
- ✅ Optimize AI manager prompts
- ✅ Document best practices

---

## Benefits & Impact

### Expected Improvements

1. **Consistency:** ±20% variance → ±5% variance in step counts for similar tasks
2. **Efficiency:** 15-25% reduction in unnecessary steps for simple tasks
3. **Quality:** 10-15% improvement in investigation depth for complex tasks
4. **Token Savings:** 10-20% reduction in total tokens through smart planning
5. **User Experience:** Faster results for simple tasks, thorough analysis for complex tasks

### Backward Compatibility

- ✅ Existing workflows continue to work without AI manager
- ✅ AI manager is optional enhancement, not requirement
- ✅ Manual step specification still supported
- ✅ No breaking changes to existing tools

---

## Next Steps

1. ✅ **Current Architecture Documented** (Complete)
2. ✅ **AI Manager Design** (THIS DOCUMENT)
3. ⏳ **Agentic Enhancement Design** (Next)
4. ⏳ **Implementation** (Next)

---

**Document Status:** ✅ DESIGN COMPLETE  
**Last Updated:** 2025-10-01  
**Next Document:** Agentic Enhancement System Design

