# Wave 2 - Agentic Architecture Analysis

**Date:** 2025-10-03  
**Priority:** 🔴 CRITICAL  
**Status:** 🚧 IN PROGRESS - Investigation Complete, Solutions Pending

---

## 🚨 CRITICAL ISSUE: "Capped" Architecture Limiting Agentic Behavior

### Problem Statement

The current architecture **artificially constrains** AI autonomy and prevents true agentic behavior through:
1. **Rigid workflow structures** - Fixed step counts, mandatory fields
2. **Over-engineered abstractions** - Multiple layers preventing flexibility
3. **Limited autonomy** - Predetermined workflows, no dynamic goal setting
4. **Missing agentic features** - No self-modification, cross-tool collaboration, or emergent behavior

---

## 📊 Evidence of "Capped" Architecture

### 1. Rigid Workflow Structure

**File:** `tools/shared/base_models.py` lines 119-142

```python
class BaseWorkflowRequest(ToolRequest):
    # RIGID: Forces predetermined step-by-step pattern
    step: str = Field(..., description=WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., ge=1, description=WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., ge=1, description=WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])
```

**Problems:**
- ❌ `total_steps` must be specified upfront - prevents adaptive planning
- ❌ `step_number` enforces linear progression - no branching or backtracking
- ❌ `next_step_required` is binary - no nuanced decision-making
- ❌ All fields are **required** (`Field(...)`) - no flexibility

**Impact:** Tools cannot adapt mid-workflow, adjust plans dynamically, or explore emergent solutions.

---

### 2. Fixed Step Counts

**File:** `docs/upgrades/international-users/exai-tool-ux-issues.md` lines 450-463

```markdown
### 4.1 Pattern 1: Fixed Step Counts

**Rigid Behavior:**
- Requires `total_steps` to be specified upfront
- Difficult to adjust mid-workflow
- Forces artificial step boundaries

**Expected Flexible Behavior:**
- Allow dynamic step adjustment
- Support "unknown" total steps
- Auto-determine steps based on complexity
```

**Evidence:** This is a **documented UX issue** (Epic 1.3.4) that was identified but not yet fixed.

---

### 3. Mandatory "Required Actions"

**File:** `tools/workflows/debug.py` lines 279-288

```python
def get_required_actions(self, step_number: int, confidence: str, findings: str, total_steps: int) -> list[str]:
    """Define required actions for each investigation phase."""
    if step_number == 1:
        # RIGID: Predetermined actions for each step
        return [
            "Search for code related to the reported issue or symptoms",
            "Examine relevant files and understand the current implementation",
            "Understand the project structure and locate relevant modules",
            "Identify how the affected functionality is supposed to work",
        ]
```

**Problems:**
- ❌ Actions are **predetermined** per step number
- ❌ No adaptation based on findings or context
- ❌ Forces linear investigation path
- ❌ Prevents creative problem-solving

**Impact:** AI cannot explore alternative approaches, follow unexpected leads, or adapt investigation strategy.

---

### 4. Over-Engineered Abstraction Layers

**File:** `tools/shared/base_tool.py` lines 42-91

```python
class BaseTool(
    BaseToolCore,
    ModelManagementMixin,
    FileHandlingMixin,
    ResponseFormattingMixin,
    ABC
):
    """
    Multiple inheritance creates rigid boundaries
    """
```

**Problems:**
- ❌ 4 layers of abstraction (Core + 3 Mixins)
- ❌ Each mixin has fixed responsibilities
- ❌ Difficult to add cross-cutting concerns
- ❌ Prevents tools from evolving beyond defined roles

**Impact:** Tools are locked into predetermined patterns, cannot adapt behavior dynamically.

---

## 🎯 What's Missing for True Agency

### 1. Dynamic Goal Setting
**Current:** Fixed objectives defined in tool schemas  
**Needed:** Tools that can:
- Assess situation and determine what needs to be done
- Prioritize goals based on context
- Adjust objectives mid-execution

### 2. Self-Modification
**Current:** Fixed behavior patterns  
**Needed:** Tools that can:
- Learn from experience
- Modify their own approach based on results
- Adapt strategies dynamically

### 3. Cross-Tool Collaboration
**Current:** Tools operate in isolation  
**Needed:** Tools that can:
- Call other tools organically
- Share context and findings
- Collaborate on complex problems

### 4. Emergent Behavior
**Current:** Everything is predefined  
**Needed:** Tools that can:
- Discover unexpected solutions
- Create novel approaches
- Exhibit creativity beyond programmed scope

---

## 🔧 Proposed Solutions

### Phase 1: Remove Rigid Constraints (IMMEDIATE)

**1.1 Make `total_steps` Optional**
```python
# Before (RIGID)
total_steps: int = Field(..., ge=1, description="...")

# After (FLEXIBLE)
total_steps: Optional[int] = Field(None, description="Estimated steps (optional - can be adjusted dynamically)")
```

**1.2 Add Dynamic Step Adjustment**
```python
# New field
allow_dynamic_steps: bool = Field(True, description="Allow step count to change mid-workflow")
```

**1.3 Remove Mandatory "Required Actions"**
```python
# Before (RIGID)
def get_required_actions(self, step_number: int, ...) -> list[str]:
    return ["Action 1", "Action 2", ...]  # Predetermined

# After (FLEXIBLE)
def suggest_actions(self, context: dict) -> list[str]:
    # AI determines actions based on context
    return self._adaptive_action_planning(context)
```

---

### Phase 2: Enable Adaptive Workflows (SHORT-TERM)

**2.1 Add Confidence-Based Branching**
```python
class AdaptiveWorkflowRequest(BaseWorkflowRequest):
    # Allow branching based on confidence
    branch_if_low_confidence: Optional[str] = Field(None, description="Alternative path if confidence < threshold")
    confidence_threshold: float = Field(0.7, description="Threshold for branching")
```

**2.2 Support Backtracking**
```python
# Already exists in some tools (debug, codereview)
backtrack_from_step: Optional[int] = Field(None, description="Step to backtrack from")

# Extend to ALL workflow tools
```

**2.3 Enable Mid-Workflow Goal Adjustment**
```python
class DynamicGoal(BaseModel):
    original_goal: str
    current_goal: str
    adjustment_reason: str
    adjusted_at_step: int
```

---

### Phase 3: True Agentic Features (MEDIUM-TERM)

**3.1 Cross-Tool Collaboration**
```python
class AgenticTool(BaseTool):
    async def collaborate_with(self, other_tool: str, context: dict) -> dict:
        """Call another tool organically"""
        pass
    
    async def share_findings(self, findings: dict) -> None:
        """Share findings with other tools"""
        pass
```

**3.2 Self-Modification**
```python
class LearningTool(AgenticTool):
    def learn_from_result(self, result: dict, success: bool) -> None:
        """Adjust behavior based on results"""
        pass
    
    def get_adaptive_strategy(self, context: dict) -> Strategy:
        """Determine strategy based on learned patterns"""
        pass
```

**3.3 Emergent Behavior Support**
```python
class EmergentTool(LearningTool):
    def explore_alternatives(self, current_approach: str) -> list[str]:
        """Generate novel approaches"""
        pass
    
    def synthesize_solution(self, findings: list[dict]) -> dict:
        """Create unexpected solutions from findings"""
        pass
```

---

## 📋 Implementation Roadmap

### Wave 2 - Epic 2.3: Remove Rigid Constraints (IMMEDIATE)
- [ ] Make `total_steps` optional in BaseWorkflowRequest
- [ ] Add `allow_dynamic_steps` flag
- [ ] Remove mandatory "required_actions" from all workflow tools
- [ ] Add adaptive action planning
- [ ] Update all workflow tool schemas

### Wave 3 - Epic 3.1: Enable Adaptive Workflows
- [ ] Add confidence-based branching
- [ ] Extend backtracking to all workflow tools
- [ ] Enable mid-workflow goal adjustment
- [ ] Add dynamic step count adjustment

### Wave 4 - Epic 4.1: True Agentic Features
- [ ] Implement cross-tool collaboration
- [ ] Add self-modification capabilities
- [ ] Enable emergent behavior support
- [ ] Create learning/adaptation mechanisms

---

## ⚠️ Constraints to Maintain

While removing rigidity, we must maintain:
- ✅ **Predictability** - Core behavior should be reliable
- ✅ **Safety** - Prevent runaway processes
- ✅ **Debuggability** - Maintain clear execution traces
- ✅ **User Control** - Allow users to override agentic behavior

---

## 🎯 Success Criteria

**Phase 1 (Immediate):**
- [ ] Workflow tools can adjust step counts mid-execution
- [ ] "Required actions" are suggestions, not mandates
- [ ] Tools can explore alternative approaches

**Phase 2 (Short-term):**
- [ ] Tools can branch based on confidence
- [ ] Mid-workflow goal adjustment works
- [ ] Backtracking available in all workflow tools

**Phase 3 (Medium-term):**
- [ ] Tools can collaborate organically
- [ ] Self-modification improves results over time
- [ ] Emergent solutions appear in complex problems

---

**Next Steps:** Begin Phase 1 implementation immediately to remove rigid constraints and enable adaptive workflows.

