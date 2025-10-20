# INTEGRATION PATTERNS
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.9 - Integration Pattern Documentation  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Document common integration patterns used throughout the EX-AI-MCP-Server system.

**Patterns Identified:**
1. Mixin Composition Pattern
2. Facade Pattern
3. Registry Pattern
4. Provider Abstraction Pattern
5. Schema Builder Pattern
6. Best-Effort Pattern
7. Lazy Loading Pattern
8. Timeout Coordination Pattern

---

## 🔧 PATTERN 1: MIXIN COMPOSITION

**Purpose:** Compose functionality from multiple specialized mixins

**Where Used:**
- SimpleTool (4 mixins)
- WorkflowTool (5 mixins via BaseWorkflowMixin)
- BaseTool (3 mixins)

**Example:**
```python
class SimpleTool(
    WebSearchMixin,      # Web search guidance
    ToolCallMixin,       # Tool call detection
    StreamingMixin,      # Streaming support
    ContinuationMixin,   # Conversation continuation
    BaseTool             # Core tool infrastructure
):
    pass
```

**Benefits:**
- **Separation of Concerns:** Each mixin handles one responsibility
- **Reusability:** Mixins can be used by multiple classes
- **Testability:** Each mixin can be tested independently
- **Maintainability:** Changes to one mixin don't affect others

**Drawbacks:**
- **Complexity:** Multiple inheritance can be confusing
- **Method Resolution Order:** Need to understand MRO
- **Debugging:** Harder to trace method calls

---

## 🔧 PATTERN 2: FACADE PATTERN

**Purpose:** Provide simplified interface while delegating to internal modules

**Where Used:**
- SimpleTool (planned for Phase 3 refactoring)
- BaseTool (delegates to mixins)

**Example (Planned for Phase 3):**
```python
class SimpleTool(...):
    """Facade that delegates to conceptual modules"""
    
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title):
        from tools.simple.preparation.prompt import PromptBuilder
        return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)
    
    def get_request_prompt(self, request):
        from tools.simple.intake.accessor import RequestAccessor
        return RequestAccessor.get_prompt(request)
```

**Benefits:**
- **Backward Compatibility:** Public interface unchanged
- **Internal Refactoring:** Can reorganize without breaking clients
- **Lazy Loading:** Modules loaded only when needed
- **Clear Separation:** Interface vs implementation

**Drawbacks:**
- **Indirection:** Extra layer between caller and implementation
- **Import Overhead:** Lazy imports add small overhead

---

## 🔧 PATTERN 3: REGISTRY PATTERN

**Purpose:** Centralized registration and lookup of components

**Where Used:**
- Tool Registry (tools/registry.py)
- Provider Registry (src/providers/registry_core.py)

**Example:**
```python
class ToolRegistry:
    _instance = None
    _tools = {}
    
    TOOL_MAP = {
        "chat": ("tools.chat", "ChatTool"),
        "debug": ("tools.workflows.debug", "DebugIssueTool"),
        # ... 30+ tools
    }
    
    def get_tool(self, name: str):
        if name not in self._tools:
            self._load_tool(name)  # Lazy load
        return self._tools[name]
```

**Benefits:**
- **Centralized Management:** Single source of truth
- **Lazy Loading:** Tools loaded on demand
- **Error Tracking:** Failed loads tracked separately
- **Extensibility:** Easy to add new tools

**Drawbacks:**
- **Global State:** Singleton pattern
- **Tight Coupling:** All tools must be registered

---

## 🔧 PATTERN 4: PROVIDER ABSTRACTION

**Purpose:** Abstract AI provider differences behind common interface

**Where Used:**
- ModelProvider base class
- KimiModelProvider, GLMModelProvider
- OpenAICompatibleProvider

**Example:**
```python
class ModelProvider(ABC):
    @abstractmethod
    def generate_content(self, prompt, model_name, **kwargs) -> ModelResponse:
        pass
    
    @abstractmethod
    def supports_model(self, model_name: str) -> bool:
        pass

class KimiModelProvider(OpenAICompatibleProvider):
    def generate_content(self, prompt, model_name, **kwargs):
        # Kimi-specific implementation
        return kimi_chat.generate_content(...)

class GLMModelProvider(ModelProvider):
    def generate_content(self, prompt, model_name, **kwargs):
        # GLM-specific implementation (dual SDK/HTTP)
        return glm_chat.generate_content(...)
```

**Benefits:**
- **Provider Independence:** Tools don't know which provider
- **Easy Switching:** Change provider without changing tools
- **Consistent Interface:** All providers return ModelResponse
- **Fallback Support:** Can try multiple providers

**Drawbacks:**
- **Lowest Common Denominator:** Interface limited to common features
- **Provider-Specific Features:** Hard to expose unique features

---

## 🔧 PATTERN 5: SCHEMA BUILDER

**Purpose:** Automatic JSON schema generation from tool definitions

**Where Used:**
- SchemaBuilder (tools/shared/schema_builders.py)
- WorkflowSchemaBuilder (tools/workflow/schema_builders.py)

**Example:**
```python
class SchemaBuilder:
    COMMON_FIELD_SCHEMAS = {
        "model": {...},
        "temperature": {...},
        "thinking_mode": {...},
    }
    
    @staticmethod
    def build_schema(tool) -> dict:
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Add tool-specific fields
        schema["properties"].update(tool.get_tool_fields())
        
        # Add common fields
        schema["properties"].update(SchemaBuilder.COMMON_FIELD_SCHEMAS)
        
        # Add required fields
        schema["required"] = tool.get_required_fields()
        
        return schema
```

**Benefits:**
- **DRY:** Common fields defined once
- **Consistency:** All tools use same schema format
- **Automatic:** No manual schema writing
- **Type Safety:** Pydantic validation

**Drawbacks:**
- **Less Flexible:** Hard to customize for special cases
- **Magic:** Schema generation not always obvious

---

## 🔧 PATTERN 6: BEST-EFFORT

**Purpose:** Never break main flow due to auxiliary operations

**Where Used:**
- Observability (utils/observability.py)
- Progress tracking (utils/progress.py)
- Caching (utils/cache.py)

**Example:**
```python
def record_token_usage(provider, model, input_tokens, output_tokens):
    try:
        _write_jsonl({
            "event": "token_usage",
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        })
    except Exception:
        # Observability must never break flows
        pass

def send_progress(message, level="info"):
    if not _stream_enabled():
        return
    
    try:
        _logger.info(f"[PROGRESS] {message}")
        # ... emit to MCP
    except Exception:
        # Never allow progress emission to break tool execution
        pass
```

**Benefits:**
- **Reliability:** Main flow never fails due to auxiliary operations
- **Graceful Degradation:** System works even if observability fails
- **User Experience:** No errors from non-critical features

**Drawbacks:**
- **Silent Failures:** Errors in auxiliary operations not visible
- **Debugging:** Hard to know when observability is broken

---

## 🔧 PATTERN 7: LAZY LOADING

**Purpose:** Load components only when needed

**Where Used:**
- Tool Registry (tools/registry.py)
- Provider Registry (src/providers/registry_core.py)
- Module imports (lazy imports in methods)

**Example:**
```python
class ToolRegistry:
    def get_tool(self, name: str):
        # Check if already loaded
        if name in self._tools:
            return self._tools[name]
        
        # Lazy load on first access
        if name not in TOOL_MAP:
            raise ValueError(f"Unknown tool: {name}")
        
        module_path, class_name = TOOL_MAP[name]
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        self._tools[name] = cls()  # Instantiate and cache
        
        return self._tools[name]
```

**Benefits:**
- **Faster Startup:** Don't load all tools at startup
- **Memory Efficiency:** Only load what's used
- **Error Isolation:** Failed loads don't prevent startup

**Drawbacks:**
- **First-Call Latency:** First use of tool is slower
- **Import Errors:** Errors only discovered at runtime

---

## 🔧 PATTERN 8: TIMEOUT COORDINATION

**Purpose:** Coordinated timeout hierarchy across layers

**Where Used:**
- Workflow tools (120s base, 240s final step)
- Daemon (180s = 1.5x workflow)
- Shim (240s = 2x workflow)

**Example:**
```python
# config.py
class TimeoutConfig:
    WORKFLOW_TOOL_TIMEOUT_SECS = 120  # Base timeout
    DAEMON_TIMEOUT_SECS = 180         # 1.5x workflow
    SHIM_TIMEOUT_SECS = 240           # 2x workflow

# tools/workflow/base.py
async def execute(self, arguments):
    timeout_default = float(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS)
    timeout = timeout_default * 2 if final_step else timeout_default
    
    try:
        result = await asyncio.wait_for(
            self.execute_workflow(arguments),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        # Return error with partial results
        pass
```

**Benefits:**
- **Predictable Behavior:** Timeouts coordinated across layers
- **Grace Period:** Each layer has buffer for cleanup
- **No Cascading Timeouts:** Outer layers wait longer than inner

**Drawbacks:**
- **Configuration Complexity:** Must maintain timeout hierarchy
- **Hard to Tune:** Finding right values requires testing

---

## 📊 PATTERN USAGE SUMMARY

| Pattern | Usage Count | Complexity | Benefit |
|---------|-------------|------------|---------|
| Mixin Composition | 3 classes | HIGH | Separation of concerns |
| Facade | 1 class (planned) | MEDIUM | Backward compatibility |
| Registry | 2 registries | MEDIUM | Centralized management |
| Provider Abstraction | 2 providers | MEDIUM | Provider independence |
| Schema Builder | 2 builders | LOW | DRY, consistency |
| Best-Effort | 10+ functions | LOW | Reliability |
| Lazy Loading | 2 registries | LOW | Performance |
| Timeout Coordination | 3 layers | MEDIUM | Predictable behavior |

---

## 🎯 PATTERN RECOMMENDATIONS

### For Phase 3 Refactoring

**1. Use Facade Pattern for SimpleTool**
- Keep public interface unchanged
- Delegate to internal modules
- Enable incremental refactoring

**2. Maintain Mixin Composition**
- Don't flatten mixins into base classes
- Keep separation of concerns
- Document mixin responsibilities

**3. Preserve Registry Pattern**
- Centralized tool/provider management works well
- Lazy loading is efficient
- Error tracking is valuable

**4. Keep Best-Effort Pattern**
- Observability and progress should never break flows
- Silent failures are acceptable for auxiliary operations

**5. Document Timeout Coordination**
- Make timeout hierarchy explicit
- Add configuration validation
- Document grace periods

---

## ✅ TASK 2.9 COMPLETE

**Deliverable:** INTEGRATION_PATTERNS.md ✅

**Key Findings:**
- 8 integration patterns identified and documented
- Pattern usage summary created
- Recommendations for Phase 3 provided
- Benefits and drawbacks analyzed

**Next Task:** Task 2.10 - Phase 2 Summary & Call Graph (FINAL TASK!)

**Time Taken:** ~30 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All integration patterns documented with usage examples and recommendations

