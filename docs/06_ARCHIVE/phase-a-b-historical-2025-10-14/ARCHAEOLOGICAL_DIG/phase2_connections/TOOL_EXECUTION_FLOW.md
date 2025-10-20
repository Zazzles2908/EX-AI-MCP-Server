# TOOL EXECUTION FLOW MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.2 - Tool Execution Flow Tracing  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Trace how tools are discovered, loaded, and executed from registry to completion.

**Components Analyzed:**
1. **tools/registry.py** - Tool discovery and loading
2. **tools/simple/base.py** - SimpleTool base class (3 simple tools)
3. **tools/workflow/base.py** - WorkflowTool base class (12 workflow tools)
4. **Mixin Integration** - How mixins compose functionality
5. **Expert Analysis** - How external AI validation is triggered

---

## 📊 COMPLETE TOOL EXECUTION FLOW

```
Tool Registry Discovery
    ↓
Tool Loading (Lazy Import)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ TOOL EXECUTION ENTRY: execute(arguments)                    │
│ - SimpleTool.execute() OR WorkflowTool.execute()           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ REQUEST VALIDATION (Pydantic)                               │
│ - SimpleTool: ToolRequest                                   │
│ - WorkflowTool: WorkflowRequest                            │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ SIMPLE TOOL PATH              │ WORKFLOW TOOL PATH          │
│ (chat, activity, challenge)   │ (debug, analyze, codereview)│
├───────────────────────────────┼─────────────────────────────┤
│ 1. Validate request           │ 1. Validate workflow request│
│ 2. Process files              │ 2. Process step data        │
│ 3. Build prompt               │ 3. Consolidate findings     │
│ 4. Call AI provider           │ 4. Check completion         │
│ 5. Format response            │ 5. Call expert analysis     │
│ 6. Return TextContent         │ 6. Return TextContent       │
└───────────────────────────────┴─────────────────────────────┘
    ↓
Response returned to request_handler.py
```

---

## 🔍 COMPONENT 1: Tool Registry (tools/registry.py)

### File Information
- **Path:** `tools/registry.py`
- **Size:** 166 lines
- **Purpose:** Tool discovery, loading, and management
- **Pattern:** Lazy import with error tracking

### Tool Map (TOOL_MAP)
```python
TOOL_MAP: Dict[str, tuple[str, str]] = {
    # Simple Tools (4 total)
    "chat": ("tools.chat", "ChatTool"),
    "activity": ("tools.activity", "ActivityTool"),
    "challenge": ("tools.challenge", "ChallengeTool"),
    "self-check": ("tools.selfcheck", "SelfCheckTool"),
    
    # Workflow Tools (12 total)
    "analyze": ("tools.workflows.analyze", "AnalyzeTool"),
    "debug": ("tools.workflows.debug", "DebugIssueTool"),
    "codereview": ("tools.workflows.codereview", "CodeReviewTool"),
    "refactor": ("tools.workflows.refactor", "RefactorTool"),
    "secaudit": ("tools.workflows.secaudit", "SecauditTool"),
    "planner": ("tools.workflows.planner", "PlannerTool"),
    "tracer": ("tools.workflows.tracer", "TracerTool"),
    "testgen": ("tools.workflows.testgen", "TestGenTool"),
    "consensus": ("tools.workflows.consensus", "ConsensusTool"),
    "thinkdeep": ("tools.workflows.thinkdeep", "ThinkDeepTool"),
    "docgen": ("tools.workflows.docgen", "DocgenTool"),
    "precommit": ("tools.workflows.precommit", "PrecommitTool"),
    
    # Utility Tools (always on)
    "version": ("tools.capabilities.version", "VersionTool"),
    "listmodels": ("tools.capabilities.listmodels", "ListModelsTool"),
    
    # Provider-Specific Tools
    "kimi_upload_and_extract": ("tools.providers.kimi.kimi_upload", "KimiUploadAndExtractTool"),
    "kimi_multi_file_chat": ("tools.providers.kimi.kimi_upload", "KimiMultiFileChatTool"),
    "kimi_intent_analysis": ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool"),
    "kimi_capture_headers": ("tools.providers.kimi.kimi_capture_headers", "KimiCaptureHeadersTool"),
    "kimi_chat_with_tools": ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool"),
    "glm_upload_file": ("tools.providers.glm.glm_files", "GLMUploadFileTool"),
    "glm_web_search": ("tools.providers.glm.glm_web_search", "GLMWebSearchTool"),
    "glm_payload_preview": ("tools.providers.glm.glm_payload_preview", "GLMPayloadPreviewTool"),
    
    # Diagnostic Tools
    "provider_capabilities": ("tools.capabilities.provider_capabilities", "ProviderCapabilitiesTool"),
    "toolcall_log_tail": ("tools.diagnostics.toolcall_log_tail", "ToolcallLogTail"),
    "health": ("tools.diagnostics.health", "HealthTool"),
    "status": ("tools.diagnostics.status", "StatusTool"),
}
```

### Tool Visibility (TOOL_VISIBILITY)
```python
TOOL_VISIBILITY = {
    # Core tools (shown by default)
    "status": "core",
    "chat": "core",
    "planner": "core",
    "thinkdeep": "core",
    "analyze": "core",
    "codereview": "core",
    "refactor": "core",
    "testgen": "core",
    "debug": "core",
    
    # Advanced tools (hidden in lean mode)
    "provider_capabilities": "advanced",
    "listmodels": "advanced",
    "activity": "advanced",
    "version": "advanced",
    # ... (all other tools)
}
```

### Tool Loading Process

**1. Registry Initialization:**
```python
class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
```

**2. Build Tools (Lazy Loading):**
```python
def build_tools(self) -> None:
    # Parse environment configuration
    disabled = {t.strip().lower() for t in os.getenv("DISABLED_TOOLS", "").split(",") if t.strip()}
    lean_mode = os.getenv("LEAN_MODE", "false").strip().lower() == "true"
    
    # Determine active tools
    if lean_mode:
        lean_overrides = {t.strip().lower() for t in os.getenv("LEAN_TOOLS", "").split(",") if t.strip()}
        active = lean_overrides or set(DEFAULT_LEAN_TOOLS)  # Core tools only
    else:
        active = set(TOOL_MAP.keys())  # All tools
    
    # Ensure utilities always on (unless STRICT_LEAN)
    if os.getenv("STRICT_LEAN", "false").strip().lower() != "true":
        active.update({"version", "listmodels"})
    
    # Remove disabled tools
    active = {t for t in active if t not in disabled}
    
    # Hide diagnostics unless explicitly enabled
    if os.getenv("DIAGNOSTICS", "false").strip().lower() != "true":
        active.discard("self-check")
    
    # Load each active tool
    for name in sorted(active):
        self._load_tool(name)
```

**3. Load Individual Tool:**
```python
def _load_tool(self, name: str) -> None:
    module_path, class_name = TOOL_MAP[name]
    try:
        # Lazy import - only import when needed
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        self._tools[name] = cls()  # Instantiate tool
    except Exception as e:
        self._errors[name] = str(e)  # Track errors
```

**4. Get Tool:**
```python
def get_tool(self, name: str) -> Any:
    if name in self._tools:
        return self._tools[name]
    if name in self._errors:
        raise RuntimeError(f"Tool '{name}' failed to load: {self._errors[name]}")
    raise KeyError(f"Tool '{name}' is not registered.")
```

### Configuration Options
- **LEAN_MODE:** Enable lean mode (core tools only)
- **LEAN_TOOLS:** Override default lean tools (comma-separated)
- **DISABLED_TOOLS:** Explicitly disable tools (comma-separated)
- **STRICT_LEAN:** Disable utilities in lean mode
- **DIAGNOSTICS:** Enable diagnostic tools

---

## 🔍 COMPONENT 2: SimpleTool (tools/simple/base.py)

### File Information
- **Path:** `tools/simple/base.py`
- **Size:** ~1,100 lines
- **Purpose:** Base class for simple (non-workflow) tools
- **Inherits From:** BaseTool + 4 Mixins

### Class Hierarchy
```python
class SimpleTool(
    WebSearchMixin,      # Web search instruction generation
    ToolCallMixin,       # Tool call detection and execution
    StreamingMixin,      # Streaming support configuration
    ContinuationMixin,   # Conversation continuation and caching
    BaseTool             # Core tool infrastructure
):
```

### Mixin Composition

**1. WebSearchMixin:**
- Generates web search instructions
- Adds search guidance to prompts
- Configures search parameters

**2. ToolCallMixin:**
- Detects tool calls in responses
- Executes nested tool calls
- Handles tool call results

**3. StreamingMixin:**
- Configures streaming support
- Handles streaming responses
- Manages streaming state

**4. ContinuationMixin:**
- Manages conversation continuation
- Handles continuation_id
- Caches conversation state

**5. BaseTool (inherited):**
- Core tool interface
- Model management
- File handling
- Response formatting

### SimpleTool Execution Flow

**Step 1: Execute Entry Point**
```python
async def execute(self, arguments: dict[str, Any]) -> list:
    # Store arguments for helper methods
    self._current_arguments = arguments
    
    # Validate request using Pydantic model
    request_model = self.get_request_model()  # Returns ToolRequest
    request = request_model(**arguments)
    
    # Continue to step 2...
```

**Step 2: Model Context Resolution**
```python
# Get model context from arguments (injected by request_handler)
model_context = arguments.get("_model_context")
if not model_context:
    # Fallback: resolve model context
    model_context = self._resolve_model_context(arguments, request)
```

**Step 3: File Processing**
```python
# Process files if present
files = self.get_request_files(request)
if files:
    # Expand file paths
    expanded_files = self._expand_file_paths(files)
    # Read file content
    file_content = self._prepare_file_content_for_prompt(expanded_files, model_context)
    # Update request with processed files
    self.set_request_files(request, expanded_files)
```

**Step 4: Prompt Preparation**
```python
# Get system prompt
system_prompt = self.get_system_prompt()

# Get user content
user_content = self.get_request_prompt(request)

# Build complete prompt
prompt = self.build_standard_prompt(
    system_prompt=system_prompt,
    user_content=user_content,
    request=request,
    file_context_title="CONTEXT FILES"
)
```

**Step 5: AI Provider Call**
```python
# Get model provider
provider = self.get_model_provider(model_context.model_name)

# Call AI model
response = await provider.chat_completion(
    model=model_context.model_name,
    messages=[{"role": "user", "content": prompt}],
    temperature=temperature,
    max_tokens=max_tokens,
    stream=stream_enabled
)
```

**Step 6: Response Formatting**
```python
# Format response
formatted_response = self.format_response(response, request)

# Create ToolOutput
output = ToolOutput(
    status="success",
    content=formatted_response,
    metadata={...}
)

# Return as TextContent
return [TextContent(type="text", text=output.model_dump_json())]
```

### Simple Tools (4 total)
1. **chat** - General chat and collaborative thinking
2. **activity** - Activity log viewing
3. **challenge** - Critical analysis forcing
4. **self-check** - Self-diagnostic tool

---

## 🔍 COMPONENT 3: WorkflowTool (tools/workflow/base.py)

### File Information
- **Path:** `tools/workflow/base.py`
- **Size:** ~700 lines
- **Purpose:** Base class for workflow (multi-step) tools
- **Inherits From:** BaseTool + BaseWorkflowMixin

### Class Hierarchy
```python
class WorkflowTool(
    BaseTool,            # Core tool infrastructure
    BaseWorkflowMixin    # Workflow orchestration
):
```

### BaseWorkflowMixin Composition
```python
class BaseWorkflowMixin(
    RequestAccessorMixin,          # Request field extraction
    ConversationIntegrationMixin,  # Thread management
    FileEmbeddingMixin,            # Context-aware file handling
    ExpertAnalysisMixin,           # External model integration
    OrchestrationMixin,            # Main workflow engine
    ABC
):
```

### WorkflowTool Execution Flow

**Step 1: Execute Entry Point (with Timeout)**
```python
async def execute(self, arguments: dict[str, Any]) -> list:
    # Use coordinated timeout from TimeoutConfig
    timeout_default = float(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS)  # 120s
    
    # Adaptive timeout for final steps with expert validation
    req = None
    try:
        req_model = self.get_workflow_request_model()
        req = req_model(**arguments) if req_model else None
    except Exception:
        req = None
    
    # Determine timeout
    timeout = timeout_default
    if req and not req.next_step_required:
        # Final step - allow more time for expert analysis
        timeout = timeout_default * 2  # 240s
    
    # Execute with timeout
    try:
        result = await asyncio.wait_for(
            self.execute_workflow(arguments),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        # Log timeout and return error
        logger.error(f"Workflow tool '{self.get_name()}' timed out after {timeout}s")
        return [TextContent(type="text", text=json.dumps({
            "error": f"Workflow timed out after {timeout}s",
            "partial_results": self._get_partial_results()
        }))]
```

**Step 2: Workflow Orchestration (execute_workflow)**
```python
async def execute_workflow(self, arguments: dict[str, Any]) -> list:
    # Validate workflow request
    req_model = self.get_workflow_request_model()
    request = req_model(**arguments)
    
    # Process step data
    step_data = self._process_step_data(request)
    
    # Consolidate findings
    self._consolidate_findings(step_data)
    
    # Check if work is complete
    if not request.next_step_required:
        # Work complete - call expert analysis
        return await self._finalize_workflow(request)
    else:
        # Work continues - return guidance
        return self._create_continuation_response(request)
```

**Step 3: Process Step Data**
```python
def _process_step_data(self, request) -> dict:
    # Extract step information
    step_number = request.step_number
    findings = request.findings
    confidence = getattr(request, 'confidence', 'medium')
    
    # Handle backtracking
    if hasattr(request, 'backtrack_from_step') and request.backtrack_from_step:
        self._handle_backtrack(request.backtrack_from_step)
    
    # Store step data
    step_data = {
        "step_number": step_number,
        "step": request.step,
        "findings": findings,
        "confidence": confidence,
        "timestamp": time.time()
    }
    
    self.work_history.append(step_data)
    return step_data
```

**Step 4: Consolidate Findings**
```python
def _consolidate_findings(self, step_data: dict) -> None:
    # Update consolidated findings
    self.consolidated_findings.add_finding(step_data["findings"])
    
    # Update files checked
    if hasattr(step_data, 'files_checked'):
        self.consolidated_findings.files_checked.extend(step_data['files_checked'])
    
    # Update relevant files
    if hasattr(step_data, 'relevant_files'):
        self.consolidated_findings.relevant_files.extend(step_data['relevant_files'])
    
    # Update issues found
    if hasattr(step_data, 'issues_found'):
        self.consolidated_findings.issues.extend(step_data['issues_found'])
```

**Step 5: Check Completion Criteria**
```python
def should_call_expert_analysis(self, consolidated_findings) -> bool:
    # Tool-specific implementation
    # Example from DebugTool:
    # return consolidated_findings.confidence == 'certain'
    pass  # Abstract method - must be implemented by subclass
```

**Step 6: Expert Analysis (if complete)**
```python
async def _finalize_workflow(self, request) -> list:
    # Check if expert analysis should be called
    if self.should_call_expert_analysis(self.consolidated_findings):
        # Prepare expert analysis context
        expert_context = self.prepare_expert_analysis_context(self.consolidated_findings)
        
        # Call expert analysis
        expert_response = await self._call_expert_analysis(
            context=expert_context,
            model_name=request.model,
            temperature=request.temperature
        )
        
        # Combine work history + expert analysis
        final_output = self._combine_work_and_expert_analysis(
            work_history=self.work_history,
            expert_response=expert_response
        )
    else:
        # No expert analysis - return work history only
        final_output = self._format_work_history(self.work_history)
    
    return [TextContent(type="text", text=final_output)]
```

**Step 7: Create Continuation Response (if not complete)**
```python
def _create_continuation_response(self, request) -> list:
    # Get required actions for next step
    required_actions = self.get_required_actions(
        step_number=request.step_number + 1,
        confidence=request.confidence,
        findings=request.findings,
        total_steps=request.total_steps
    )
    
    # Create guidance response
    guidance = {
        "status": "continue",
        "current_step": request.step_number,
        "next_step": request.step_number + 1,
        "required_actions": required_actions,
        "progress": f"{request.step_number}/{request.total_steps} steps complete"
    }
    
    return [TextContent(type="text", text=json.dumps(guidance))]
```

### Workflow Tools (12 total)
1. **analyze** - Code analysis workflow
2. **debug** - Systematic debugging
3. **codereview** - Code review workflow
4. **refactor** - Refactoring analysis
5. **secaudit** - Security audit workflow
6. **planner** - Sequential planning
7. **tracer** - Execution tracing
8. **testgen** - Test generation
9. **consensus** - Multi-model consensus
10. **thinkdeep** - Deep thinking workflow
11. **docgen** - Documentation generation
12. **precommit** - Pre-commit validation

---

## 🔍 COMPONENT 4: Mixin Integration

### SimpleTool Mixins (4 total)

**1. WebSearchMixin (tools/simple/mixins/web_search_mixin.py):**
```python
class WebSearchMixin:
    def get_websearch_guidance(self, use_websearch: bool) -> str:
        if not use_websearch:
            return ""
        return """
        WEB SEARCH ENABLED: You can search the web for current information.
        Use web search for: documentation, best practices, current events.
        """
    
    def should_enable_websearch(self, request) -> bool:
        # Check if use_websearch parameter is set
        return getattr(request, 'use_websearch', True)
```

**2. ToolCallMixin (tools/simple/mixins/tool_call_mixin.py):**
```python
class ToolCallMixin:
    def detect_tool_calls(self, response: str) -> list:
        # Parse response for tool call requests
        # Example: <tool_call>{"name": "chat", "args": {...}}</tool_call>
        pass
    
    async def execute_tool_calls(self, tool_calls: list) -> list:
        # Execute detected tool calls
        # Return results
        pass
```

**3. StreamingMixin (tools/simple/mixins/streaming_mixin.py):**
```python
class StreamingMixin:
    def supports_streaming(self) -> bool:
        # Check if tool supports streaming
        return True
    
    def get_streaming_config(self, request) -> dict:
        # Return streaming configuration
        return {"enabled": True, "chunk_size": 1024}
```

**4. ContinuationMixin (tools/simple/mixins/continuation_mixin.py):**
```python
class ContinuationMixin:
    def get_continuation_id(self, request) -> Optional[str]:
        # Extract continuation_id from request
        return getattr(request, 'continuation_id', None)
    
    def save_conversation_state(self, conversation_id: str, state: dict) -> None:
        # Save conversation state for continuation
        pass
    
    def load_conversation_state(self, conversation_id: str) -> Optional[dict]:
        # Load conversation state
        pass
```

### WorkflowTool Mixins (5 total)

**1. RequestAccessorMixin:**
- Safe request field extraction
- Validation helpers
- Type conversion

**2. ConversationIntegrationMixin:**
- Thread management
- Turn storage
- Conversation history

**3. FileEmbeddingMixin:**
- Context-aware file handling
- Token budgeting
- File prioritization

**4. ExpertAnalysisMixin:**
- External model integration
- Fallback handling
- Response parsing

**5. OrchestrationMixin:**
- Main workflow engine
- Step processing
- Progress tracking

---

## 🔍 COMPONENT 5: Expert Analysis Triggering

### When Expert Analysis is Called

**Condition 1: Workflow Complete**
```python
if not request.next_step_required:
    # Work is complete - check if expert analysis needed
    if self.should_call_expert_analysis(self.consolidated_findings):
        # Call expert analysis
        pass
```

**Condition 2: Tool-Specific Criteria**
```python
# Example from DebugTool
def should_call_expert_analysis(self, consolidated_findings) -> bool:
    return consolidated_findings.confidence == 'certain'

# Example from AnalyzeTool
def should_call_expert_analysis(self, consolidated_findings) -> bool:
    return len(consolidated_findings.relevant_files) > 0

# Example from CodeReviewTool
def should_call_expert_analysis(self, consolidated_findings) -> bool:
    return consolidated_findings.confidence in ['very_high', 'certain']
```

### Expert Analysis Execution

**Step 1: Prepare Context**
```python
def prepare_expert_analysis_context(self, consolidated_findings) -> str:
    # Tool-specific context preparation
    # Example from DebugTool:
    context = f"""
    INVESTIGATION SUMMARY:
    {consolidated_findings.get_summary()}
    
    FILES CHECKED: {len(consolidated_findings.files_checked)}
    RELEVANT FILES: {consolidated_findings.relevant_files}
    
    HYPOTHESIS: {consolidated_findings.hypothesis}
    CONFIDENCE: {consolidated_findings.confidence}
    
    FINDINGS:
    {consolidated_findings.get_all_findings()}
    """
    return context
```

**Step 2: Call External Model**
```python
async def _call_expert_analysis(self, context: str, model_name: str, temperature: float) -> str:
    # Get model provider
    provider = self.get_model_provider(model_name)
    
    # Build expert analysis prompt
    system_prompt = self._get_expert_analysis_system_prompt()
    user_prompt = f"{system_prompt}\n\n{context}"
    
    # Call AI model
    response = await provider.chat_completion(
        model=model_name,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=temperature,
        max_tokens=4096
    )
    
    return response
```

**Step 3: Combine Results**
```python
def _combine_work_and_expert_analysis(self, work_history: list, expert_response: str) -> str:
    # Format work history
    work_summary = self._format_work_history(work_history)
    
    # Combine with expert analysis
    final_output = f"""
    === INVESTIGATION WORK ===
    {work_summary}
    
    === EXPERT ANALYSIS ===
    {expert_response}
    
    === RECOMMENDATIONS ===
    [Generated from expert analysis]
    """
    
    return final_output
```

---

## ✅ TASK 2.2 COMPLETE

**Deliverable:** TOOL_EXECUTION_FLOW.md ✅

**Next Task:** Task 2.3 - Provider Integration Mapping

**Time Taken:** ~45 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All tool execution flows mapped with mixin integration and expert analysis

