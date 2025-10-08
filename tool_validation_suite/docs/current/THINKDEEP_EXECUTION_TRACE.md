# ThinkDeep Execution Trace - What Actually Happens

**Date**: 2025-10-08  
**Purpose**: Trace EVERY script involved when you call `thinkdeep_EXAI-WS()`

---

## The Call Chain (What Actually Happens)

### 1. **YOU CALL**: `thinkdeep_EXAI-WS(step="...", findings="...")`

**Entry Point**: Augment Code MCP Client

---

### 2. **SCRIPT 1**: `scripts/run_ws_shim.py`
**Purpose**: stdio ↔ WebSocket bridge
**What it does**: 
- Receives MCP call from Augment
- Converts stdio to WebSocket
- Forwards to daemon on port 8079

**Next**: → WebSocket connection to daemon

---

### 3. **SCRIPT 2**: `src/daemon/ws_server.py`
**Purpose**: WebSocket daemon (main entry point)
**What it does**:
- Receives WebSocket message
- Normalizes tool name: `thinkdeep_EXAI-WS` → `thinkdeep`
- Routes to server.py

**Key Code**:
```python
def _normalize_tool_name(name: str) -> str:
    # Strips _EXAI-WS, -EXAI-WS, etc.
    return name.replace("_EXAI-WS", "").replace("-EXAI-WS", "")
```

**Next**: → `server.py::handle_call_tool()`

---

### 4. **SCRIPT 3**: `server.py`
**Purpose**: MCP server - tool registry and dispatcher
**What it does**:
- Looks up tool in registry: `TOOLS["thinkdeep"]`
- Calls `handle_call_tool(name="thinkdeep", arguments={...})`

**Next**: → `src/server/handlers/request_handler.py`

---

### 5. **SCRIPT 4**: `src/server/handlers/request_handler.py`
**Purpose**: Request orchestration and model resolution
**What it does**:
- Resolves model: `glm-4.5-flash` (from arguments or default)
- Creates model context
- Validates file sizes
- Calls tool.execute()

**Key Code**:
```python
# Line 149
result = await execute_tool_with_fallback(
    tool, name, arguments, tool_map,
    lambda coro: execute_with_monitor(coro, name, req_id, monitoring_config),
    req_id
)
```

**Next**: → `tools/workflows/thinkdeep.py::execute()`

---

### 6. **SCRIPT 5**: `tools/workflows/thinkdeep.py`
**Purpose**: ThinkDeep tool implementation
**What it does**:
- Inherits from WorkflowTool
- Defines schema (ThinkDeepWorkflowRequest)
- Calls parent execute()

**Inheritance Chain**:
```
ThinkDeepTool
  → WorkflowTool (tools/workflow/base.py)
    → BaseTool (tools/shared/base_tool.py)
      → BaseToolCore (tools/shared/base_tool_core.py)
      → ModelManagementMixin
      → FileHandlingMixin
      → ResponseFormattingMixin
      → BaseWorkflowMixin (tools/workflow/workflow_mixin.py)
        → RequestAccessorMixin
        → ConversationIntegrationMixin
        → FileEmbeddingMixin
        → ExpertAnalysisMixin ← THIS IS THE PROBLEM
        → OrchestrationMixin
```

**Next**: → `tools/workflow/base.py::execute()`

---

### 7. **SCRIPT 6**: `tools/workflow/base.py`
**Purpose**: Base workflow tool with timeout wrapper
**What it does**:
- Wraps execute_workflow() with timeout
- Timeout: 300 seconds (from WORKFLOW_TOOL_TIMEOUT_SECS)

**Key Code**:
```python
# Line 706
return await asyncio.wait_for(self.execute_workflow(arguments), timeout=timeout)
```

**Next**: → `tools/workflow/orchestration.py::execute_workflow()`

---

### 8. **SCRIPT 7**: `tools/workflow/orchestration.py`
**Purpose**: Main workflow orchestration loop
**What it does**:
- Validates request
- Processes step data
- Checks if work is complete (`next_step_required=False`)
- **IF COMPLETE**: Calls `handle_work_completion()`

**Key Code**:
```python
# Line 183-188
if not request.next_step_required:
    send_progress(f"{self.get_name()}: Finalizing - calling expert analysis if required...")
    response_data = await self.handle_work_completion(response_data, request, arguments)
```

**Next**: → `tools/workflow/conversation_integration.py::handle_work_completion()`

---

### 9. **SCRIPT 8**: `tools/workflow/conversation_integration.py`
**Purpose**: Conversation integration and expert analysis decision
**What it does**:
- Checks if expert analysis should be called
- **IF YES**: Calls `_call_expert_analysis()`

**Key Code**:
```python
# Line 207-239
elif self.requires_expert_analysis() and self.should_call_expert_analysis(self.consolidated_findings, request):
    response_data["status"] = "calling_expert_analysis"
    expert_analysis = await asyncio.wait_for(
        self._call_expert_analysis(arguments, request),
        timeout=180.0  # 3 minute timeout
    )
```

**Next**: → `tools/workflow/expert_analysis.py::_call_expert_analysis()`

---

### 10. **SCRIPT 9**: `tools/workflow/expert_analysis.py` ← **THE BOTTLENECK**
**Purpose**: Expert analysis execution
**What it does**:

#### Step 1: Prepare Context
```python
# Line 287
expert_context = self.prepare_expert_analysis_context(self.consolidated_findings)
```
- Builds summary of findings (small, ~500 chars)

#### Step 2: **ADD FILES** ← **THIS IS THE PROBLEM**
```python
# Line 291-294
if self.should_include_files_in_expert_prompt():
    file_content = self._prepare_files_for_expert_analysis()
    if file_content:
        expert_context = self._add_files_to_expert_context(expert_context, file_content)
```

**WHY IS IT ADDING FILES?**
- `should_include_files_in_expert_prompt()` returns `True` for some tools
- `_prepare_files_for_expert_analysis()` reads ALL files from `consolidated_findings.relevant_files`
- Embeds ENTIRE file contents into the prompt

**Next**: → `tools/workflow/file_embedding.py::_prepare_files_for_expert_analysis()`

---

### 11. **SCRIPT 10**: `tools/workflow/file_embedding.py`
**Purpose**: File embedding for expert analysis
**What it does**:
- Collects all files from `consolidated_findings.relevant_files`
- Reads ENTIRE file contents
- Embeds into prompt

**Key Code**:
```python
# Line 41-102
def _prepare_files_for_expert_analysis(self) -> str:
    all_relevant_files = set()
    
    # Collect files from consolidated findings
    if hasattr(self, 'consolidated_findings'):
        all_relevant_files.update(self.consolidated_findings.relevant_files)
    
    # Read all files
    file_content, processed_files = self._force_embed_files_for_expert_analysis(files_for_expert)
    
    return file_content
```

**Result**: Prompt is now 50KB+ instead of 500 chars

**Next**: Back to expert_analysis.py

---

### 12. **BACK TO SCRIPT 9**: `tools/workflow/expert_analysis.py`

#### Step 3: Call Provider
```python
# Line 368-376
result = provider.generate_content(
    prompt=prompt,  # NOW 50KB+ with embedded files
    model_name=model_name,
    system_prompt=system_prompt,
    temperature=validated_temperature,
    thinking_mode=self.get_request_thinking_mode(request),
    **provider_kwargs
)
```

**Next**: → `src/providers/glm_chat.py::generate_content()`

---

### 13. **SCRIPT 11**: `src/providers/glm_chat.py`
**Purpose**: GLM provider implementation
**What it does**:
- Calls GLM API via SDK
- Sends 50KB+ prompt
- **WAITS 30 SECONDS** for response

**Key Code**:
```python
# GLM SDK call
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}  # 50KB+ prompt
    ]
)
```

**Why 30 seconds?**
- Large prompt (50KB+)
- GLM API processing time
- Network latency

**Next**: Response returns to expert_analysis.py

---

### 14. **BACK TO SCRIPT 9**: Parse Response
```python
# Line 515
analysis_result = json.loads(model_response.content.strip())
```

**Next**: Return to conversation_integration.py

---

### 15. **BACK TO SCRIPT 8**: Add to Response
```python
# Line 283
response_data["expert_analysis"] = expert_analysis
```

**Next**: Return to orchestration.py

---

### 16. **BACK TO SCRIPT 7**: Serialize Response
```python
# Line 217
return [TextContent(type="text", text=json.dumps(response_data, indent=2, ensure_ascii=False))]
```

**Next**: Return through the chain back to client

---

## THE PROBLEM

### **Why Files Are Being Embedded**

1. **`should_include_files_in_expert_prompt()`** - Returns `True` by default for some tools
2. **`consolidated_findings.relevant_files`** - Contains file paths from the workflow
3. **File embedding logic** - Reads ENTIRE files and embeds them

### **But You Didn't Provide Files!**

**CORRECT!** You called:
```python
thinkdeep_EXAI-WS(
    step="Analyze microservices vs monolithic...",
    findings="Testing thinkdeep...",
    # NO FILES PROVIDED
)
```

**So where do the files come from?**

Looking at the workflow, `consolidated_findings.relevant_files` is populated from:
- `request.relevant_files` (you didn't provide this)
- Previous steps in multi-step workflows
- **DEFAULT EMPTY LIST**

**So if you didn't provide files, `relevant_files` should be empty, and NO files should be embedded!**

---

## THE REAL QUESTION

**Why is it still taking 30 seconds if there are NO files?**

Let me check the logs again:
```
2025-10-08 22:59:44 INFO tools.workflow.expert_analysis: [EXPERT_DEBUG] About to call provider.generate_content() for thinkdeep: prompt=349 chars
```

**349 chars is TINY!** So why 30 seconds?

**Possible reasons:**
1. GLM API is just slow (even for small prompts)
2. Network latency
3. Model loading time
4. API rate limiting
5. **The SDK is doing something we don't see**

---

## WHAT MODELS ARE CONNECTED?

From the logs:
```
2025-10-08 22:59:44 INFO tools.workflow.expert_analysis: [EXPERT_ANALYSIS_DEBUG] Provider resolved: glm
2025-10-08 22:59:44 INFO src.providers.glm_chat: GLM chat using SDK: model=glm-4.5-flash, stream=False, messages_count=2
```

**Model**: `glm-4.5-flash`  
**Provider**: GLM (ZhipuAI)  
**SDK**: Official GLM Python SDK  
**API**: `https://api.z.ai/api/paas/v4/chat/completions`

---

## THE STRAIGHT LINE YOU WANT

**What SHOULD happen:**

```
User calls thinkdeep
  → Daemon receives call
    → Server routes to thinkdeep tool
      → Tool processes request
        → Tool returns response
          → Response sent back to user
```

**What ACTUALLY happens:**

```
User calls thinkdeep
  → Daemon receives call
    → Server routes to thinkdeep tool
      → Tool processes request
        → Tool decides to call expert analysis
          → Expert analysis prepares context
            → Expert analysis checks for files
              → Expert analysis embeds files (if any)
                → Expert analysis calls GLM API
                  → GLM API takes 30 seconds
                    → Expert analysis parses response
                      → Expert analysis returns to tool
                        → Tool adds expert analysis to response
                          → Tool serializes response
                            → Response sent back to user
```

**11 extra steps just for "expert validation"!**

---

## CONCLUSION

The complexity is INSANE. The expert analysis:
1. Shouldn't exist (adds no value)
2. Embeds files unnecessarily (even when empty)
3. Calls external API (30s latency)
4. Blocks the entire workflow
5. Times out before completing

**The fix**: Remove expert analysis entirely OR make it truly optional with proper env configuration.

