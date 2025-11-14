# 🤖 Smart Routing Implementation Prompt

**CONTEXT**: You are working on the EX-AI-MCP-Server which has a **layered architecture** for AI model routing. The previous agent broke the system because it didn't understand this architecture. You must work **within** the existing design patterns, not replace them.

## 🎯 ARCHITECTURE YOU MUST UNDERSTAND

### **Layer 1: ModelProviderRegistry** (`src/providers/registry.py`)
```python
# This is the central registry - DON'T REPLACE IT
ModelProviderRegistry:
├── get_provider(model_name) → Returns provider instance
├── get_provider_for_model(model_name) → Auto-detects provider
├── get_available_models() → Returns all available models
└── call_with_fallback() → Built-in fallback logic
```

### **Layer 2: Provider Capabilities** (`src/providers/base.py`)
```python
# Each model has SPECIFIC capabilities - CHECK THEM
ModelCapabilities:
├── context_window: int          # Max input tokens
├── max_output_tokens: int       # Max response tokens  
├── supports_images: bool        # Can handle images
├── supports_function_calling: bool  # Can use tools
├── supports_extended_thinking: bool # Has reasoning mode
├── supports_streaming: bool     # Can stream responses
└── temperature_constraint: TemperatureConstraint  # Valid range
```

### **Layer 3: Provider Implementations**
```python
# GLM Provider (ZhipuAI) - src/providers/glm_provider.py
# KIMI Provider (Moonshot) - src/providers/kimi.py
# Each has DIFFERENT parameter handling
```

### **Layer 4: Smart Routing** (`src/router/service.py`)
```python
# Current routing is too simple - enhance it
RouterService.choose_model():
├── Fast default: "glm-4.5-flash"
├── Long default: "kimi-k2-0711-preview" 
└── Problem: Ignores task requirements!
```

## 🚨 WHAT NOT TO DO

**❌ NEVER:**
1. Replace or bypass `ModelProviderRegistry`
2. Ignore `ModelCapabilities` when routing
3. Hardcode model names without checking availability
4. Assume all parameters work with all models
5. Change the provider interface contracts

**✅ ALWAYS:**
1. Use the existing registry pattern
2. Check capabilities before applying parameters
3. Honor provider-specific parameter formatting
4. Work within the existing routing infrastructure
5. Test with both GLM and Kimi providers

## 🔧 IMPLEMENTATION APPROACH

### **Phase 1: Enhance Existing RouterService**

**Current Problem** in `src/router/service.py`:
```python
# Line 418-420: TOO SIMPLISTIC
for candidate in [self._fast_default, self._long_default]:
    prov = get_registry_instance().get_provider_for_model(candidate)
    if prov is not None:
```

**Required Fix**: Replace with capability-aware selection:
```python
def choose_model_smart(self, requested: Optional[str], task_context: Dict[str, Any] = None) -> RouteDecision:
    """
    Enhanced model selection with capability awareness.
    
    Args:
        requested: User-requested model or "auto"
        task_context: Dict with task requirements (context_needed, needs_images, etc.)
    """
    # Honor explicit requests
    if requested and requested.lower() != "auto":
        return self._handle_explicit_request(requested)
    
    # Auto-select based on task requirements
    return self._select_best_model(task_context or {})
```

### **Phase 2: Add Capability Checking**

**Create new method** in `RouterService`:
```python
def _check_model_capability(self, model_name: str, requirement: str, task_context: Dict[str, Any]) -> bool:
    """Check if model meets specific requirement."""
    provider = get_registry_instance().get_provider_for_model(model_name)
    if not provider:
        return False
        
    capabilities = provider.get_capabilities(model_name)
    
    if requirement == "supports_images":
        return capabilities.supports_images and "images" in task_context
    elif requirement == "extended_thinking":
        return capabilities.supports_extended_thinking
    elif requirement == "context_needed":
        needed = task_context.get("context_needed", 0)
        return capabilities.context_window >= needed
    elif requirement == "budget_tier":
        return self._check_budget_compatibility(model_name, task_context.get("budget_tier", "normal"))
    
    return True
```

### **Phase 3: Provider Parameter Validation**

**Create new method** in `RouterService`:
```python
def _validate_provider_parameters(self, model_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Filter and validate parameters for the target provider."""
    provider = get_registry_instance().get_provider_for_model(model_name)
    if not provider:
        return params
        
    capabilities = provider.get_capabilities(model_name)
    provider_type = provider.get_provider_type()
    
    # Filter unsupported parameters
    filtered_params = params.copy()
    
    # Remove thinking parameter for models that don't support it
    if not capabilities.supports_extended_thinking and "thinking" in filtered_params:
        filtered_params.pop("thinking")
        logger.debug(f"Removed 'thinking' parameter for {model_name} (not supported)")
    
    # Remove image parameters for non-vision models
    if not capabilities.supports_images:
        image_keys = ["image_url", "image_data", "images"]
        for key in image_keys:
            if key in filtered_params:
                filtered_params.pop(key)
                logger.debug(f"Removed '{key}' parameter for {model_name} (no vision support)")
    
    # Provider-specific parameter formatting
    if provider_type == ProviderType.GLM:
        return self._format_glm_parameters(filtered_params)
    elif provider_type == ProviderType.KIMI:
        return self._format_kimi_parameters(filtered_params)
    
    return filtered_params
```

### **Phase 4: Smart Selection Logic**

**Replace auto-selection** with intelligent routing:
```python
def _select_best_model(self, task_context: Dict[str, Any]) -> RouteDecision:
    """Select best model based on task requirements."""
    
    # Get all available models
    available_models = get_registry_instance().get_available_models()
    
    # Analyze requirements
    needs_images = task_context.get("needs_images", False)
    needs_thinking = task_context.get("needs_thinking", False)
    context_needed = task_context.get("context_needed", 8000)
    budget_tier = task_context.get("budget_tier", "normal")
    
    # Filter candidates by capabilities
    candidates = []
    for model_name in available_models:
        provider = get_registry_instance().get_provider_for_model(model_name)
        if not provider:
            continue
            
        capabilities = provider.get_capabilities(model_name)
        
        # Check basic compatibility
        if capabilities.context_window < context_needed:
            continue
        if needs_images and not capabilities.supports_images:
            continue
        
        # Calculate suitability score
        score = self._calculate_model_score(model_name, task_context)
        candidates.append((score, model_name, provider))
    
    # Select best candidate
    if not candidates:
        # Fallback to current simple logic
        return self._fallback_to_default()
    
    # Return highest scoring model
    best_score, best_model, best_provider = max(candidates, key=lambda x: x[0])
    return RouteDecision(
        requested="auto",
        chosen=best_model,
        reason="smart_selection",
        provider=best_provider.get_provider_type().name
    )
```

## 📋 SPECIFIC DELIVERABLES

### **1. Update RouterService** (`src/router/service.py`)
- [ ] Add `choose_model_smart()` method with task context support
- [ ] Add `_check_model_capability()` for requirement validation
- [ ] Add `_validate_provider_parameters()` for parameter filtering
- [ ] Add `_format_glm_parameters()` for GLM-specific formatting
- [ ] Add `_format_kimi_parameters()` for Kimi-specific formatting
- [ ] Enhance `_select_best_model()` with intelligent scoring

### **2. Update MCP Server** (`src/daemon/mcp_server.py`)
- [ ] Route tool calls through smart selection
- [ ] Pass task context to routing decisions
- [ ] Validate parameters before provider calls

### **3. Add Task Context Detection**
- [ ] Create helper to analyze prompt/context for requirements
- [ ] Detect if images are being used
- [ ] Estimate context length needed
- [ ] Determine if extended thinking is beneficial

## 🧪 TESTING REQUIREMENTS

**Test Cases to Verify**:
1. **Image task routing**: Images should only go to vision-capable models
2. **Thinking mode routing**: GLM thinking parameter filtered for non-thinking models
3. **Context length routing**: Long prompts route to large context models
4. **Budget optimization**: Budget tasks prefer cost-effective models
5. **Fallback behavior**: System still works if smart routing fails
6. **Parameter compatibility**: No "unsupported parameter" errors

**Test Commands**:
```bash
# Test with different model requests
python -m tools.capabilities.listmodels
python -c "from src.router.service import RouterService; print(RouterService().choose_model_smart('auto', {'needs_images': True}))"
```

## ⚠️ CRITICAL SUCCESS CRITERIA

- [ ] **NO BREAKING CHANGES** to existing provider interfaces
- [ ] **BACKWARD COMPATIBILITY** with current simple routing
- [ ] **Capability-aware routing** respects ModelCapabilities
- [ ] **Parameter validation** prevents provider errors
- [ ] **Performance maintained** with efficient caching
- [ ] **Both GLM and Kimi** work correctly
- [ ] **Smart routing enhances** rather than replaces existing logic

## 🎯 SUCCESS METRICS

After implementation, you should see:
1. Better model selection based on actual task needs
2. No more "unsupported parameter" errors
3. Proper handling of thinking mode for GLM vs Kimi
4. Vision tasks routed to vision-capable models
5. Budget considerations in model selection
6. Maintained system stability and performance

**Remember**: You're **enhancing** the existing system, not **replacing** it. Work within the established patterns and the system will be more robust, not broken.
