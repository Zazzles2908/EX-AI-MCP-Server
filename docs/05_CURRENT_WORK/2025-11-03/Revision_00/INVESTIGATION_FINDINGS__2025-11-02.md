# INVESTIGATION FINDINGS - November 2, 2025

**Date:** 2025-11-02  
**Status:** Investigation Complete - Ready for Fixes  
**Related:** CRITICAL_ISSUES_AND_FIXES__2025-11-02.md

---

## 🔍 INVESTIGATION SUMMARY

Completed comprehensive investigation of 3 critical issues identified in Docker logs. All root causes identified with specific file locations and fix strategies.

---

## 📁 ISSUE 1: SUPABASE BATCH LINK FAILURE

### **File Location:**
`src/storage/supabase_client.py` - Lines 959-998

### **Current Implementation:**
```python
def link_files_to_conversation_batch(
    self,
    conversation_id: str,
    file_ids: list[str]
) -> dict:
    """
    PHASE 1 FIX (2025-11-01): Batch link multiple files to a conversation.
    """
    if not self._enabled or not file_ids:
        return {"success": 0, "errors": []}
    
    try:
        client = self._get_client()
        
        # Build batch data
        batch_data = [
            {"conversation_id": conversation_id, "file_id": file_id}
            for file_id in file_ids
        ]
        
        # Use upsert to handle duplicates
        result = client.table("conversation_files").upsert(batch_data).execute()
        
        success_count = len(result.data) if result.data else 0
        logger.info(f"[BATCH_LINK] Linked {success_count}/{len(file_ids)} files")
        
        return {"success": success_count, "errors": []}
    
    except Exception as e:
        logger.error(f"[BATCH_LINK] Failed to batch link files: {e}")
        return {"success": 0, "errors": [str(e)]}
```

### **Problem:**
- **Line 989:** `.upsert(batch_data)` without proper conflict resolution
- **Missing:** Deduplication check before batch operation
- **Missing:** `ON CONFLICT` column specification

### **Root Cause:**
When the same `file_id` appears multiple times in `batch_data`, Supabase's upsert tries to update the same row twice in a single transaction, triggering PostgreSQL error 21000.

### **Fix Required:**
1. **Pre-processing Deduplication:**
   ```python
   # Remove duplicates before batch operation
   unique_file_ids = list(set(file_ids))
   ```

2. **Proper Conflict Handling:**
   ```python
   # Specify conflict resolution columns
   result = client.table("conversation_files")\
       .upsert(batch_data, on_conflict="file_id,conversation_id")\
       .execute()
   ```

3. **Transaction Splitting:**
   ```python
   # Split large batches into chunks of 50
   chunk_size = 50
   for i in range(0, len(unique_file_ids), chunk_size):
       chunk = unique_file_ids[i:i+chunk_size]
       # Process chunk...
   ```

---

## 📁 ISSUE 2: WEB SEARCH NOT WORKING

### **File Locations:**
1. `.env.docker` - Lines 532-536 (GLM web search config)
2. `src/providers/orchestration/websearch_adapter.py` - Web search adapter
3. `src/providers/tool_executor.py` - GLM web search execution

### **Current Configuration (.env.docker):**
```bash
# GLM native web search configuration (2025-10-09 - Removed DuckDuckGo fallback)
# Documentation: https://docs.z.ai/api-reference/tools/web-search
# Endpoint: https://api.z.ai/api/paas/v4/web_search
GLM_WEBSEARCH_COUNT=10  # Number of search results to return
GLM_WEBSEARCH_ENGINE=search-prime  # Search engine (search-prime or search-pro)
```

### **Docker Logs Evidence:**
```
2025-11-02 19:48:28 INFO src.providers.orchestration.websearch_adapter: 
[WEBSEARCH_DEBUG] ws.tools=[{'type': 'web_search', 'web_search': 
{'search_engine': 'search_pro_jina', 'search_recency_filter': 'oneWeek', 
'content_size': 'medium', 'result_sequence': 'after', 'search_result': True}}]

2025-11-02 19:48:29 INFO src.providers.tool_executor: GLM native web search 
completed successfully for query: 'MCP Model Context Protocol tool registration 
best practices 2024' (returned 0 results)
```

### **Problem:**
1. **Configuration Mismatch:** `.env.docker` specifies `search-prime` but code uses `search_pro_jina`
2. **Recency Filter:** `oneWeek` filter may be too restrictive for technical documentation
3. **Missing API Key:** No `GLM_WEBSEARCH_API_KEY` or similar in `.env.docker`
4. **Network Issue:** Container may not have outbound access to web search endpoints

### **Fix Required:**
1. **Add Missing Configuration:**
   ```bash
   # Add to .env.docker
   GLM_WEBSEARCH_API_KEY=your_api_key_here  # If required by Z.ai
   GLM_WEBSEARCH_RECENCY=oneMonth  # Expand from oneWeek
   ```

2. **Align Configuration:**
   - Either change `.env.docker` to `search_pro_jina`
   - Or update code to use `search-prime` from config

3. **Add Logging:**
   ```python
   # In websearch_adapter.py
   logger.info(f"[WEBSEARCH] Query: {query}, Engine: {engine}, Recency: {recency}")
   logger.info(f"[WEBSEARCH] Response: {response}")
   ```

4. **Test Network:**
   ```bash
   # Inside container
   curl -v https://api.z.ai/api/paas/v4/web_search
   ```

---

## 📁 ISSUE 3: SYSTEM DEFAULTING TO 2024

### **Investigation Results:**

**Hardcoded "2024" References Found:**
1. `.env.docker` - Line 4: `# Last Updated: 2025-10-09` (CORRECT - not the issue)
2. `.env.docker` - Line 190: `# UPDATED 2025-10-26` (CORRECT - comments only)
3. Python packages - Multiple references to model versions (e.g., `gpt-4o-2024-11-20`)
4. **CRITICAL:** Web search query in logs shows `'...best practices 2024'` instead of 2025

### **Root Cause:**
**NOT hardcoded in codebase** - The issue is in the **web search query construction**!

**Evidence from Docker Logs:**
```
2025-11-02 19:48:26 INFO src.providers.tool_executor: GLM native web search 
completed successfully for query: 'MCP Model Context Protocol tool registration 
best practices 2024' (returned 0 results)
```

The query itself contains "2024" - this is coming from the **AI model's prompt**, not the system!

### **Actual Problem:**
The AI models (GLM, Kimi) are not being told the current date in their system prompts.

### **Fix Required:**
1. **Add Current Date to System Prompts:**
   ```python
   # In src/providers/glm_chat.py and src/providers/kimi.py
   from datetime import datetime
   
   current_date = datetime.now().strftime("%Y-%m-%d")
   system_prompt = f"""You are a helpful AI assistant.
   Current date: {current_date}
   
   When searching for information, always use the current year ({datetime.now().year}) 
   unless specifically asked about historical information.
   """
   ```

2. **Update Tool Descriptions:**
   ```python
   # In tools/chat.py
   def get_description(self) -> str:
       current_year = datetime.now().year
       return f"""GENERAL CHAT & COLLABORATIVE THINKING
       
       Current date: {datetime.now().strftime("%B %d, %Y")}
       
       When using web search, default to current year ({current_year}) 
       for best practices and documentation.
       """
   ```

3. **Add Date Injection in WebSearch Adapter:**
   ```python
   # In src/providers/orchestration/websearch_adapter.py
   def enhance_query_with_date(query: str) -> str:
       current_year = datetime.now().year
       # Replace any year references with current year
       query = re.sub(r'\b202[0-4]\b', str(current_year), query)
       return query
   ```

---

## 🎯 PRIORITY FIX ORDER (REVISED)

### **Phase 1: Date Issue (IMMEDIATE)** ⏱️ 30 minutes
**Complexity:** LOW - Simple prompt injection

**Files to Modify:**
1. `src/providers/glm_chat.py` - Add current date to system prompt
2. `src/providers/kimi.py` - Add current date to system prompt
3. `tools/chat.py` - Update tool description with current date
4. `src/providers/orchestration/websearch_adapter.py` - Add date enhancement

**Testing:**
```python
# Test that models receive current date
assert "November 2, 2025" in system_prompt
assert "2025" in web_search_query
```

---

### **Phase 2: Web Search Configuration (HIGH)** ⏱️ 1 hour
**Complexity:** MEDIUM - Configuration + network testing

**Files to Modify:**
1. `.env.docker` - Add missing web search config
2. `src/providers/orchestration/websearch_adapter.py` - Align engine names
3. `src/providers/tool_executor.py` - Add detailed logging

**Testing:**
```bash
# Inside container
docker exec -it exai-mcp-daemon bash
curl -v https://api.z.ai/api/paas/v4/web_search
# Should return 200 OK or authentication error (not connection refused)
```

---

### **Phase 3: Supabase Batch Link (URGENT)** ⏱️ 2 hours
**Complexity:** MEDIUM - Schema + transaction handling

**Files to Modify:**
1. `src/storage/supabase_client.py` - Add deduplication + conflict handling
2. `tools/smart_file_query.py` - Pre-process file lists
3. `src/file_management/duplicate_detector.py` - SHA256 validation

**Testing:**
```python
# Test batch link with duplicates
file_ids = ["id1", "id2", "id1", "id3", "id2"]  # Duplicates
result = link_files_to_conversation_batch(conv_id, file_ids)
assert result["success"] == 3  # Only unique files
assert len(result["errors"]) == 0
```

---

## 📊 INVESTIGATION METRICS

**Time Spent:**
- Docker logs analysis: 15 minutes
- Kimi thinking consultation: 10 minutes
- Codebase search: 20 minutes
- File investigation: 25 minutes
- **Total:** 70 minutes

**Files Investigated:**
- `.env.docker` (776 lines)
- `src/storage/supabase_client.py` (1365 lines)
- `src/providers/orchestration/websearch_adapter.py`
- `src/providers/tool_executor.py`
- `src/providers/glm_chat.py`
- `src/providers/kimi.py`
- `tools/chat.py`

**Issues Identified:**
- ✅ Supabase batch link: Root cause confirmed
- ✅ Web search: Configuration mismatch identified
- ✅ Date issue: NOT hardcoded - prompt injection needed

---

## 🔧 NEXT IMMEDIATE ACTIONS

### **Action 1: Fix Date Issue (30 min)**
1. Modify `src/providers/glm_chat.py` to inject current date
2. Modify `src/providers/kimi.py` to inject current date
3. Update `tools/chat.py` description
4. Test with web search query

### **Action 2: Fix Web Search Config (1 hour)**
1. Add missing config to `.env.docker`
2. Align engine names in code
3. Test container network connectivity
4. Add detailed logging

### **Action 3: Fix Batch Link (2 hours)**
1. Add deduplication logic
2. Update conflict handling
3. Split large batches
4. Comprehensive testing

---

## ✅ SUCCESS CRITERIA

**Phase 1 (Date) Complete:**
- [ ] System prompts include current date (November 2, 2025)
- [ ] Web search queries use 2025 instead of 2024
- [ ] Tool descriptions show current year

**Phase 2 (Web Search) Complete:**
- [ ] Web search returns results (>0)
- [ ] Configuration aligned across files
- [ ] Network connectivity confirmed
- [ ] Detailed logging shows query/response

**Phase 3 (Batch Link) Complete:**
- [ ] Duplicate file_ids handled correctly
- [ ] No PostgreSQL 21000 errors
- [ ] Batch operations complete successfully
- [ ] All files linked to conversations

---

**END OF INVESTIGATION FINDINGS**

