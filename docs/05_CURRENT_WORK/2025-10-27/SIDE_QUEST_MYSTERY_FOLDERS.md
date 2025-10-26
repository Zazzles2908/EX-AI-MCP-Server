# Side Quest: Mystery Folders Investigation

**Date**: 2025-10-27  
**Status**: ✅ Solved

---

## 🔍 **MYSTERY**

Two mysterious folders discovered in `docs/System_layout/_raw/`:
- `synthesis_hop_test_out/`
- `routeplan_budget_test_out/`

**Question**: Why do these folders exist and what created them?

---

## 🕵️ **INVESTIGATION**

### **Folder Contents**

**`synthesis_hop_test_out/2025-10-26.jsonl`**:
```json
{"event": "synthesis_hop", "ts": "2025-10-26T13:40:19Z", "primary": "glm-4.5-flash", "chosen": "glm-4.5-flash", "reason": "secondary synthesis hop for improved finalization", "hint": false}
{"event": "route_plan", "ts": "2025-10-26T13:40:19Z", "requested": "auto", "chosen": "glm-4.5-flash", "reason": "auto_preferred", "provider": "GLM", "meta": {"hint": false, "synthesis": {"enabled": true, "model": "glm-4.5-flash", "reason": "secondary synthesis hop for improved finalization"}}}
{"event": "synthesis_hop", "ts": "2025-10-26T13:40:19Z", "chosen": "glm-4.5-flash", "primary": "glm-4.5-flash", "reason": "secondary synthesis hop for improved finalization"}
```

**`routeplan_budget_test_out/2025-10-26.jsonl`**:
```json
{"event": "route_plan", "ts": "2025-10-26T13:40:13Z", "requested": "auto", "chosen": "glm-4.5-flash", "reason": "auto_hint_applied", "provider": "GLM", "meta": {"hint": true, "budget": 0.03}}
```

---

## ✅ **SOLUTION**

### **What Are These Folders?**

These are **test output directories** created by pytest tests for the model routing system.

### **Created By**

**Test File 1**: `tests/phase5/test_synthesis_hop.py`
```python
def test_synthesis_hop_logged(monkeypatch):
    # Enable synthesis and routeplan log dir
    monkeypatch.setenv("SYNTHESIS_ENABLED", "true")
    from pathlib import Path
    outdir = Path("docs/System_layout/_raw/synthesis_hop_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ROUTEPLAN_LOG_DIR", str(outdir))
    # ... test code ...
```

**Test File 2**: `tests/phase5/test_flag_propagation_and_budget.py`
```python
def test_budget_filters_candidate_order(monkeypatch):
    # Arrange model costs and log dir
    from pathlib import Path
    outdir = Path("docs/System_layout/_raw/routeplan_budget_test_out")
    outdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ROUTEPLAN_LOG_DIR", str(outdir))
    # ... test code ...
```

### **Purpose**

These tests verify the **model routing and synthesis system**:

1. **Synthesis Hop Testing**: Tests that the synthesis hop feature (secondary model consultation for improved finalization) is properly logged
2. **Budget-Based Routing**: Tests that budget constraints correctly influence model selection (choosing cheaper models when budget is limited)

### **Logging Mechanism**

The tests use the observability system in `utils/observability.py`:

```python
def append_routeplan_jsonl(event: dict) -> None:
    """Append a single JSON line capturing route plan / decision details.
    Writes to logs/routeplan/<YYYY-MM-DD>.jsonl (configurable via ROUTEPLAN_LOG_DIR).
    """
    base = Path(os.getenv("ROUTEPLAN_LOG_DIR", "logs/routeplan"))
    # ... writes JSONL events ...

def append_synthesis_hop_jsonl(event: dict) -> None:
    """Append a synthesis hop record under logs/routeplan as well for timeline continuity."""
    base = Path(os.getenv("ROUTEPLAN_LOG_DIR", "logs/routeplan"))
    # ... writes JSONL events ...
```

---

## 📊 **WHAT THE DATA SHOWS**

### **Synthesis Hop Events**

The synthesis hop feature enables a **two-stage model consultation**:
1. **Primary Model**: Handles the main request (e.g., `glm-4.5-flash`)
2. **Secondary Model**: Reviews and improves the finalization (synthesis hop)

**Benefits**:
- Improved response quality through multi-model collaboration
- Cost optimization (use fast model for primary, quality model for synthesis)
- Better handling of complex requests

### **Budget-Based Routing**

The budget routing feature enables **cost-aware model selection**:
- When `budget: 0.03` is specified, the router selects cheaper models
- In the test, `glm-4.5-flash` ($0.02) was chosen over `kimi-k2-0711-preview` ($0.50)
- This ensures cost constraints are respected while maintaining functionality

---

## 🧹 **CLEANUP RECOMMENDATION**

### **Should These Folders Be Deleted?**

**No** - These are legitimate test artifacts that should be kept for:
1. **Test Verification**: Confirms tests are running and producing expected output
2. **Debugging**: Helps debug routing and synthesis issues
3. **Historical Record**: Shows when tests were last run

### **Should They Be Gitignored?**

**Yes** - Test output should not be committed to version control.

**Recommendation**: Add to `.gitignore`:
```gitignore
# Test output directories
docs/System_layout/_raw/synthesis_hop_test_out/
docs/System_layout/_raw/routeplan_budget_test_out/
docs/System_layout/_raw/routeplan_test_out/
```

---

## 📝 **RELATED FILES**

### **Test Files**:
- `tests/phase5/test_synthesis_hop.py` - Synthesis hop logging test
- `tests/phase5/test_flag_propagation_and_budget.py` - Budget routing test
- `tests/phase3/test_routeplan_jsonl.py` - Route plan JSONL test

### **Implementation Files**:
- `utils/observability.py` - JSONL logging functions
- `src/router/service.py` - Model routing service
- `src/providers/registry.py` - Model provider registry

---

## 🎯 **CONCLUSION**

**Mystery Solved!** ✅

These folders are **test output directories** created by pytest tests for the model routing system. They contain JSONL logs that verify:
1. Synthesis hop feature is working correctly
2. Budget-based routing selects appropriate models
3. Observability logging captures routing decisions

**Action Items**:
1. ✅ Document findings (this file)
2. ⏳ Add test output directories to `.gitignore`
3. ⏳ Consider adding cleanup script to remove old test outputs

**No Issues Found** - This is expected behavior from a well-tested routing system!

