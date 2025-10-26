# Future Improvements Backlog

**Created:** 2025-10-21  
**Purpose:** Track non-critical improvements identified during Phase 1 implementation

---

## Phase 1.3: Provider-Aware Prompt Optimization - Deferred Items

### 1. Advanced Metrics Collection (Priority 2)

**Current State:**
- Basic fallback logging implemented (1 line)
- Logs to standard Python logger

**Future Enhancement:**
- Integrate with Supabase for persistent metrics tracking
- Track variant usage statistics by provider and tool
- Monitor token efficiency improvements over time
- Dashboard for variant performance comparison

**Implementation Approach:**
```python
# Add to systemprompts/prompt_registry.py
class PromptMetrics:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def record_variant_usage(self, tool_name, provider, variant_used, fallback):
        self.supabase.table('prompt_metrics').insert({
            'tool_name': tool_name,
            'provider': provider,
            'variant_used': variant_used,
            'fallback_occurred': fallback,
            'timestamp': datetime.now()
        }).execute()
```

**Estimated Effort:** 4-6 hours  
**Dependencies:** Supabase schema design for prompt_metrics table

---

### 2. Configuration Management (Priority 2)

**Current State:**
- Hardcoded variant selection logic
- No environment-specific configuration

**Future Enhancement:**
- Environment-specific provider preferences (dev vs prod)
- Variant weighting for A/B testing
- Dynamic variant selection based on performance metrics

**Implementation Approach:**
```python
# Add to systemprompts/prompt_registry.py
class PromptConfig:
    def __init__(self):
        self.config = self._load_from_env()
    
    def _load_from_env(self):
        return {
            "development": {"default_provider": "KIMI"},
            "production": {"default_provider": "AUTO"},
            "variant_weights": {"kimi": 0.5, "glm": 0.5}  # A/B testing
        }
```

**Estimated Effort:** 3-4 hours  
**Dependencies:** Environment configuration system

---

### 3. Automated Variant Validation (Priority 3)

**Current State:**
- Manual testing of variant equivalence
- No automated validation framework

**Future Enhancement:**
- Automated testing to ensure variants maintain functional equivalence
- Performance regression testing
- Language validation for Chinese variants

**Implementation Approach:**
```python
# tests/test_prompt_variants.py
def test_variant_equivalence():
    registry = get_registry()
    test_cases = load_test_cases()
    
    for tool_name in registry.get_available_tools():
        base = registry.get_prompt(tool_name, ProviderType.AUTO)
        kimi = registry.get_prompt(tool_name, ProviderType.KIMI)
        glm = registry.get_prompt(tool_name, ProviderType.GLM)
        
        # Verify all variants produce equivalent results
        assert_functional_equivalence(base, kimi, test_cases)
        assert_functional_equivalence(base, glm, test_cases)
```

**Estimated Effort:** 6-8 hours  
**Dependencies:** Test case library, equivalence testing framework

---

### 4. Health Checks (Priority 2)

**Current State:**
- No health check endpoint for variant availability

**Future Enhancement:**
- Health check endpoint to verify all variants are accessible
- Monitoring dashboard integration
- Alerting for missing or broken variants

**Implementation Approach:**
```python
# Add to systemprompts/prompt_registry.py
def health_check(self) -> Dict[str, Any]:
    """Verify all variants are accessible and valid."""
    status = {"healthy": True, "issues": []}
    
    for tool_name in self.get_available_tools():
        for provider in [ProviderType.KIMI, ProviderType.GLM]:
            try:
                prompt = self.get_prompt(tool_name, provider)
                if not prompt or len(prompt) < 100:
                    status["healthy"] = False
                    status["issues"].append(f"{tool_name}/{provider.value}: suspiciously short")
            except Exception as e:
                status["healthy"] = False
                status["issues"].append(f"{tool_name}/{provider.value}: {str(e)}")
    
    return status
```

**Estimated Effort:** 2-3 hours  
**Dependencies:** Monitoring infrastructure

---

### 5. Dynamic Variant Optimization (Priority 3)

**Current State:**
- Static variants defined at module load time
- No runtime optimization

**Future Enhancement:**
- ML-based prompt optimization
- Performance-based variant selection
- Automatic A/B testing with statistical significance

**Implementation Approach:**
```python
# Future: systemprompts/variant_optimizer.py
class VariantOptimizer:
    def __init__(self, metrics_collector):
        self.metrics = metrics_collector
    
    def select_optimal_variant(self, tool_name, provider):
        # Analyze historical performance
        performance = self.metrics.get_variant_performance(tool_name, provider)
        
        # Select best performing variant
        return max(performance, key=lambda v: v['success_rate'] / v['avg_tokens'])
```

**Estimated Effort:** 2-3 weeks  
**Dependencies:** ML infrastructure, extensive metrics collection

---

### 6. Prompt Versioning and Rollback (Priority 3)

**Current State:**
- No version control for prompts
- No rollback capability

**Future Enhancement:**
- Version tracking for all prompt changes
- Rollback to previous versions
- Change history and audit trail

**Implementation Approach:**
```python
# Future: systemprompts/version_manager.py
class PromptVersionManager:
    def version_prompt(self, tool: str, provider: str, prompt: str) -> str:
        version = self.get_next_version(tool, provider)
        self.store_version(tool, provider, version, prompt)
        return version
    
    def rollback_to_version(self, tool: str, provider: str, version: str):
        prompt = self.get_version(tool, provider, version)
        self.set_active_prompt(tool, provider, prompt)
```

**Estimated Effort:** 1-2 weeks  
**Dependencies:** Supabase schema for version storage

---

## Summary

**Total Deferred Items:** 6  
**Estimated Total Effort:** 4-6 weeks  
**Priority Breakdown:**
- Priority 2 (Short Term): 4 items (13-17 hours)
- Priority 3 (Medium Term): 2 items (3-5 weeks)

**Recommendation:** Address Priority 2 items in next sprint after Phase 1 completion. Priority 3 items can be scheduled for future quarters based on business value and resource availability.

