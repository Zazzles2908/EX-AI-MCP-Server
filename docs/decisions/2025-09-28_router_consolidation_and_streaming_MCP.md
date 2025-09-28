# EXAI-WS MCP Raw Output: Router Consolidation & Streaming Plan (2025-09-28)

Below is the unedited raw content returned by EXAI-WS MCP chat tool (glm-4.5-flash), captured for traceability.

---

=== BEGIN RAW MCP OUTPUT ===

# Analysis: MCP Server Architecture Consolidation & Streaming Implementation

## Router Consolidation Recommendation

After analyzing both components, I recommend **consolidating onto the registry** and removing `intelligent_router.py`. Here's why:

### Current Architecture Analysis
- `intelligent_router.py`: Handles task-based routing (web search→GLM, file processing→Kimi), fallback, retries, JSONL logging
- `src/providers/registry.py`: Implements sophisticated provider selection with priority, cost-aware ordering, category-based fallback chains, telemetry, health checks, and `call_with_fallback`

### Consolidation Arguments
1. **Functional Overlap**: The registry already handles fallback logic and provider selection
2. **Single Source of Truth**: Eliminates routing logic duplication
3. **Sophistication**: The registry has more advanced features (cost optimization, health checks, telemetry)
4. **Maintainability**: Reduces complexity and potential inconsistencies

### Action Plan for Consolidation
1. **Extract Unique Value**: Before removal, identify any unique routing logic in `intelligent_router.py` that should be preserved
2. **Integrate Task Routing**: If task-based routing is valuable, implement it as a higher-level component that uses the registry
3. **Preserve Logging**: Migrate JSONL logging to the registry if it provides unique observability value

## GLM Streaming Implementation Plan

### Minimal, Robust Implementation Strategy

1. **Provider-Level Streaming Support**
   ```python
   # In src/providers/glm_provider.py
   async def stream_chat(self, messages, **kwargs):
       """Stream chat responses via SSE"""
       url = f"{self.base_url}/chat/completions"
       headers = self._get_headers()
       payload = self._build_payload(messages, **kwargs)
       
       async for chunk in utils.http_client.stream_sse(url, headers, payload):
           yield self._process_stream_chunk(chunk)
   ```

2. **Dual Implementation Path**
   - **Primary**: SSE implementation using existing `utils.http_client.stream_sse`
   - **Fallback**: Zhipu SDK if available and provides streaming support

3. **Backward Compatibility Layer**
   ```python
   # In src/providers/registry.py
   async def call_with_fallback(self, messages, hints=None, stream=False, **kwargs):
       if stream:
           return await self._stream_with_fallback(messages, hints, **kwargs)
       return await self._non_stream_with_fallback(messages, hints, **kwargs)
   ```

### Implementation Steps

1. **Add Streaming Flag to Tool Interface**
   ```python
   # In SimpleTool.execute()
   async def execute(self, stream=False, **kwargs):
       if stream:
           return await self._execute_stream(**kwargs)
       return await self._execute(**kwargs)
   ```

2. **Implement Streaming Path**
   - Create streaming version of GLM provider
   - Use SSE helper with proper error handling
   - Ensure backpressure handling for streaming responses

3. **Maintain Non-Streaming Path**
   - Keep existing implementation unchanged
   - Default behavior remains non-streaming

4. **Error Handling Consistency**
   - Implement similar error handling for both paths
   - Ensure graceful fallback from streaming to non-streaming

## Actionable Recommendations

### For Router Consolidation
- [ ] Audit `intelligent_router.py` for unique routing logic not in registry
- [ ] If unique value exists, extract and integrate into registry
- [ ] Remove `intelligent_router.py` after consolidation
- [ ] Update all references to use registry's `call_with_fallback`

### For Streaming Implementation
- [ ] Implement GLM streaming provider using SSE helper
- [ ] Add streaming parameter to provider interface with default False
- [ ] Create streaming version of SimpleTool.execute()
- [ ] Add comprehensive error handling for streaming path
- [ ] Implement circuit breaker for streaming requests
- [ ] Add observability for streaming vs non-streaming paths

### For Backward Compatibility
- [ ] Maintain existing non-streaming behavior as default
- [ ] Ensure all existing tools continue to work without modification
- [ ] Add feature flag for streaming capability
- [ ] Implement graceful degradation when streaming fails

=== END RAW MCP OUTPUT ===

Meta: Model=glm-4.5-flash; temperature=0.1; thinking_mode=low; websearch=false

