# Known Issues & Investigation Roadmap
**Date:** 2025-10-21  
**Phase:** Next Investigation Priority  
**Related Docs:** NEXT_PHASE_SUPABASE_INTEGRATION_2025-10-21.md

---

## Executive Summary

This document catalogs known issues and operational challenges within the EX-AI-MCP-Server system that require investigation and resolution. These issues impact reliability, performance, and user experience.

---

## Critical Issues

### 1. Truncated EXAI Responses

**Severity:** HIGH  
**Impact:** Incomplete analysis, missing recommendations, poor user experience  
**Frequency:** Intermittent

**Description:**
EXAI tools sometimes return truncated responses, cutting off mid-sentence or missing entire sections of analysis.

**Potential Root Causes:**
1. **Token Limit Exceeded:** Response exceeds model's max output tokens
2. **Streaming Buffer Issues:** Streaming responses not fully captured
3. **Timeout Issues:** Response generation times out before completion
4. **Provider-Specific Limits:** Different providers have different output limits
5. **Network Issues:** Connection drops during response streaming

**Investigation Steps:**
```python
# Test script to reproduce truncation
async def test_truncation():
    # Test with different models
    for model in ['glm-4.6', 'kimi-k2-0905-preview']:
        # Test with different prompt sizes
        for prompt_size in [1000, 5000, 10000, 20000]:
            response = await exai_tool.execute({
                'model': model,
                'prompt': generate_test_prompt(prompt_size),
                'max_tokens': None  # Let model decide
            })
            
            # Check for truncation indicators
            is_truncated = check_truncation(response)
            log_result(model, prompt_size, is_truncated)
```

**Proposed Solutions:**
1. Implement max_tokens parameter with provider-specific limits
2. Add truncation detection and automatic retry with continuation
3. Implement chunked response handling for large outputs
4. Add response validation to detect incomplete responses
5. Log truncation events to Supabase for analysis

**Priority:** P0 (Critical)

---

### 2. File Handling Issues

**Severity:** MEDIUM  
**Impact:** File uploads fail, orphaned files, storage quota waste  
**Frequency:** Occasional

**Description:**
Issues with file uploads, downloads, and synchronization between Moonshot and Supabase.

**Known Problems:**
1. **Orphaned Files:** Files uploaded to Moonshot but not tracked in Supabase
2. **Failed Uploads:** Large files fail to upload without clear error messages
3. **Cleanup Issues:** No automatic cleanup of old/unused files
4. **Path Issues:** Absolute path requirements not always met
5. **Encoding Issues:** Non-ASCII filenames cause problems

**Investigation Steps:**
```python
# File handling test suite
async def test_file_handling():
    test_cases = [
        {'size': 1_000, 'name': 'small.txt'},
        {'size': 1_000_000, 'name': 'medium.pdf'},
        {'size': 10_000_000, 'name': 'large.zip'},
        {'size': 100, 'name': '中文文件.txt'},  # Non-ASCII
        {'size': 500, 'name': 'file with spaces.doc'}
    ]
    
    for test in test_cases:
        # Test upload
        file_id = await upload_test_file(test)
        
        # Verify Supabase sync
        metadata = await get_file_metadata(file_id)
        assert metadata is not None
        
        # Test download
        content = await download_file(file_id)
        assert len(content) == test['size']
        
        # Test cleanup
        await delete_file(file_id)
        assert not await file_exists(file_id)
```

**Proposed Solutions:**
1. Implement bidirectional file sync (Moonshot ↔ Supabase)
2. Add file size validation before upload
3. Implement automatic cleanup of files older than 30 days
4. Add retry logic for failed uploads
5. Normalize filenames to handle encoding issues

**Priority:** P1 (High)

---

### 3. Native Web Browsing Issues

**Severity:** MEDIUM  
**Impact:** Web search fails, incomplete results, timeout errors  
**Frequency:** Intermittent

**Description:**
Native web browsing with models (GLM web search, Kimi web mode) experiences reliability issues.

**Known Problems:**
1. **Timeout Errors:** Web searches timeout without results
2. **Empty Results:** Search returns no results even for valid queries
3. **Overhead Issues:** Web search adds latency even when not used
4. **Rate Limiting:** Provider rate limits on web search requests
5. **Quality Issues:** Search results not always relevant

**Investigation Steps:**
```python
# Web search reliability test
async def test_web_search():
    test_queries = [
        "Python async programming best practices",
        "Supabase row level security tutorial",
        "GLM-4 model capabilities",
        "非常具体的中文搜索查询"  # Chinese query
    ]
    
    for query in test_queries:
        for provider in ['glm', 'kimi']:
            start_time = time.time()
            
            try:
                results = await web_search(query, provider)
                latency = time.time() - start_time
                
                log_search_result(
                    query=query,
                    provider=provider,
                    success=True,
                    result_count=len(results),
                    latency=latency
                )
            except Exception as e:
                log_search_error(query, provider, str(e))
```

**Proposed Solutions:**
1. Set `use_websearch=False` as default for workflow tools
2. Enable web search only for analyze and thinkdeep tools
3. Implement timeout handling with graceful degradation
4. Add caching for common search queries
5. Implement fallback to alternative search providers

**Priority:** P1 (High)

---

### 4. Concurrent Request Hanging

**Severity:** HIGH  
**Impact:** System becomes unresponsive, blocks all users  
**Frequency:** Frequent under load

**Description:**
When multiple applications/users make concurrent EXAI requests, the system hangs or blocks subsequent requests.

**Known Problems:**
1. **Request Blocking:** One stuck request blocks all others
2. **No Timeout:** Requests wait indefinitely for stuck operations
3. **Resource Exhaustion:** Concurrent requests exhaust connection pool
4. **Model Selection Issues:** 'auto' model selection causes extended hangs
5. **No Parallelization:** Single-session architecture limits concurrency

**Investigation Steps:**
```python
# Concurrency stress test
async def test_concurrent_requests():
    num_concurrent = 10
    
    async def make_request(request_id):
        start = time.time()
        try:
            result = await exai_tool.execute({
                'prompt': f'Test request {request_id}',
                'model': 'auto'
            })
            latency = time.time() - start
            return {'id': request_id, 'success': True, 'latency': latency}
        except Exception as e:
            return {'id': request_id, 'success': False, 'error': str(e)}
    
    # Launch concurrent requests
    tasks = [make_request(i) for i in range(num_concurrent)]
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    success_rate = sum(1 for r in results if r['success']) / len(results)
    avg_latency = sum(r.get('latency', 0) for r in results) / len(results)
    
    print(f"Success Rate: {success_rate:.2%}")
    print(f"Average Latency: {avg_latency:.2f}s")
```

**Proposed Solutions:**
1. Implement multi-session parallel architecture (from ARCHITECTURAL_UPGRADE_REQUEST_2025-10-19)
2. Add request timeout with configurable limits
3. Implement connection pooling with max concurrent limit
4. Avoid 'auto' model selection (use explicit model names)
5. Add request queuing with priority levels

**Priority:** P0 (Critical)

---

### 5. Conversation ID Issues

**Severity:** MEDIUM  
**Impact:** Lost conversation context, duplicate conversations  
**Frequency:** Occasional

**Description:**
Conversation IDs (continuation_id) not properly managed, leading to context loss or duplication.

**Known Problems:**
1. **ID Collision:** Same continuation_id used for different conversations
2. **Lost Context:** Continuation_id not found in storage
3. **Expiration Issues:** Conversations expire too quickly
4. **No Cleanup:** Old conversations not cleaned up
5. **Cross-Tool Issues:** Continuation_id not working across different tools

**Investigation Steps:**
```python
# Conversation ID lifecycle test
async def test_conversation_lifecycle():
    # Create conversation
    continuation_id = await create_conversation('debug', 'Test conversation')
    
    # Verify storage
    stored = await get_conversation(continuation_id)
    assert stored is not None
    
    # Update conversation
    await update_conversation(continuation_id, new_messages=[...])
    
    # Verify update
    updated = await get_conversation(continuation_id)
    assert len(updated['messages']) > len(stored['messages'])
    
    # Test expiration
    await set_expiration(continuation_id, hours=24)
    
    # Test cleanup
    await cleanup_expired_conversations()
    
    # Verify active conversation still exists
    active = await get_conversation(continuation_id)
    assert active is not None
```

**Proposed Solutions:**
1. Implement UUID-based continuation_id generation
2. Store conversations in Supabase with proper indexing
3. Set reasonable expiration (7 days default)
4. Implement automatic cleanup of expired conversations
5. Add continuation_id validation and error handling

**Priority:** P1 (High)

---

## Additional Known Issues

### 6. Docker Container Restart Requirements

**Severity:** LOW  
**Impact:** Downtime during updates, lost in-memory state  
**Frequency:** Every code change

**Description:**
Container must be rebuilt/restarted for code changes, causing downtime.

**Solution:** Mount source directories during development (already implemented per memories)

---

### 7. Timeout Hardcoding

**Severity:** MEDIUM  
**Impact:** Inflexible timeout management, difficult to tune  
**Frequency:** N/A (architectural issue)

**Description:**
Timeouts hardcoded in scripts instead of centralized configuration.

**Solution:** Centralized timeout management in .env (per user requirements)

---

### 8. Environment Configuration Complexity

**Severity:** LOW  
**Impact:** Configuration errors, inconsistent behavior  
**Frequency:** During setup

**Description:**
Multiple .env files (.env, .env.docker, .env.example) cause confusion.

**Solution:** Standardize on .env.docker with .env.example matching (per user preference)

---

## Investigation Priority Matrix

| Issue | Severity | Impact | Frequency | Priority | Estimated Effort |
|-------|----------|--------|-----------|----------|------------------|
| Truncated Responses | HIGH | HIGH | Intermittent | P0 | 2-3 days |
| Concurrent Hanging | HIGH | HIGH | Frequent | P0 | 1 week |
| File Handling | MEDIUM | MEDIUM | Occasional | P1 | 3-4 days |
| Web Browsing | MEDIUM | MEDIUM | Intermittent | P1 | 2-3 days |
| Conversation IDs | MEDIUM | MEDIUM | Occasional | P1 | 2-3 days |
| Docker Restarts | LOW | LOW | Every change | P2 | Already solved |
| Timeout Hardcoding | MEDIUM | LOW | N/A | P2 | 1-2 days |
| Env Configuration | LOW | LOW | Setup only | P3 | 1 day |

---

## Recommended Investigation Order

### Phase 1: Critical Stability (Week 1-2)
1. **Concurrent Request Hanging** - Blocks all users, highest impact
2. **Truncated EXAI Responses** - Core functionality broken

### Phase 2: Core Functionality (Week 3-4)
3. **File Handling Issues** - Data integrity concerns
4. **Conversation ID Issues** - Context management critical
5. **Web Browsing Issues** - Feature reliability

### Phase 3: Quality of Life (Week 5-6)
6. **Timeout Hardcoding** - Architectural improvement
7. **Environment Configuration** - Developer experience

---

## Success Metrics

**Stability:**
- 99.9% uptime for concurrent requests
- <1% truncated response rate
- Zero orphaned files

**Performance:**
- <500ms average response time
- <5s p99 response time
- 100+ concurrent requests supported

**Reliability:**
- 99% conversation ID retrieval success
- 95% web search success rate
- <0.1% file upload failure rate

---

**Next Document:** MASTER_CHECKLIST_FOR_NEXT_AGENT_2025-10-21.md

