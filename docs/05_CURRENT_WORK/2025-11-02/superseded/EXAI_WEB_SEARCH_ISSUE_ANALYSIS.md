# EXAI Web Search Issue Analysis

**Date:** 2025-11-02  
**Issue:** Kimi Thinking Preview + Web Search + Large File Uploads = Infinite Loop  
**Status:** ROOT CAUSE IDENTIFIED  
**Diagnostic Model:** GLM-4.6 (max thinking mode)

---

## Problem Statement

When calling Kimi Thinking Preview model with:
- `use_websearch=true`
- `thinking_mode=max`
- 12 files uploaded via `files` parameter (embedded as raw content)

The model enters an infinite preparation loop:
1. Acknowledges the request
2. States "I'm ready to assist... Let me proceed with the web search..."
3. Never executes the search
4. Never provides results
5. Repeats preparation message on each follow-up

---

## Root Cause (Identified by GLM-4.6)

### Primary Cause: **Context Window Overload**

**Explanation:**
- Kimi Thinking Preview has finite context window (~128K tokens)
- Embedding 12 files as raw content consumes significant tokens
- Max thinking mode requires additional context for reasoning
- Insufficient room left for web search tool execution
- Model gets stuck in preparation loop

**Why the Loop Occurs:**
1. Model acknowledges web search request (as programmed)
2. Attempts to allocate context for both file analysis AND web search
3. Fails due to insufficient context space
4. Reverts to acknowledging the request again
5. Repeats cycle without executing either task

### Secondary Contributing Factors:

1. **Thinking Mode Conflict**
   - Max thinking mode requires additional context for reasoning
   - Further reduces available space for web search

2. **Tool Execution Priority**
   - Model may prioritize file processing over web search
   - Creates a deadlock situation

3. **Provider Limitation**
   - Kimi Thinking Preview may have specific limitations on concurrent tool usage

---

## Recommended Solutions

### Immediate Workarounds

#### Option 1: Use File Upload API (RECOMMENDED)
```python
# Upload files first (preserves context space)
file_ids = kimi_upload_files(files=["path/to/file1", "path/to/file2"])

# Then reference via file_ids
response = kimi_chat_with_files(
    prompt="Analyze these files and search for related information",
    file_ids=file_ids,
    use_websearch=True
)
```

**Benefits:**
- Files stored on Kimi platform (not embedded in context)
- Preserves context space for web search execution
- More efficient token usage

#### Option 2: Reduce File Count
- Limit to 3-4 most critical files per request
- Process in batches if needed
- Keep total embedded content under 50KB

#### Option 3: Disable Max Thinking Mode
- Use standard thinking mode or disabled
- Reserve max thinking for file-only or search-only queries
- Not both simultaneously

### Long-term Solution: Two-Stage Approach

**Stage 1: File Upload and Initial Analysis**
```python
# Upload files
file_ids = kimi_upload_files(files=all_files)

# Initial analysis without web search
analysis = kimi_chat_with_files(
    prompt="Analyze these files",
    file_ids=file_ids,
    use_websearch=False
)
```

**Stage 2: Web Search with File References**
```python
# Web search with file context
search_results = kimi_chat_with_files(
    prompt="Based on the files, search for Moonshot and Z.ai API documentation",
    file_ids=file_ids,
    use_websearch=True
)
```

---

## Best Practices for Kimi Models

### File Handling Strategy

**Small Files (<5KB total):**
```python
# Embed directly via files parameter
response = chat_EXAI(
    prompt="Analyze this code",
    files=["small_file.py"],
    use_websearch=False
)
```

**Large Files (>5KB) or Multiple Files:**
```python
# Upload first, then reference
file_ids = kimi_upload_files(files=["large_file1.py", "large_file2.py"])
response = kimi_chat_with_files(
    prompt="Analyze these files",
    file_ids=file_ids
)
```

### Context Management Guidelines

| Scenario | Embedded Content Limit | Recommendation |
|----------|----------------------|----------------|
| Web search only | N/A | Use directly |
| Files only | No limit | Use file upload API for >5KB |
| Files + web search | <50KB total | Upload files first, then search |
| Max thinking mode | <20KB total | Minimal context only |

### Model-Specific Guidelines

**Kimi Thinking Preview:**
- Best for: Deep analysis of limited context
- Avoid: Large file uploads + web search + max thinking
- Use: File upload API for multi-file analysis

**Kimi K2-0905-Preview:**
- Best for: Web search + file combinations
- Better context handling than Thinking Preview
- Faster response times

**Max Thinking Mode:**
- Use sparingly with web search
- Reserve for complex reasoning tasks
- Not suitable for large context + web search

---

## Implementation Changes Required

### Immediate Actions (Batch 9 Follow-up)

1. **Update EXAI Validation Workflow:**
   - Use file upload API instead of embedding files
   - Separate file analysis from web search
   - Document context limits in workflow tools

2. **Add Context Size Validation:**
   - Check total file size before embedding
   - Warn if >50KB with web search enabled
   - Auto-switch to file upload API if needed

3. **Update Documentation:**
   - Document file handling best practices
   - Add context management guidelines
   - Update EXAI tool descriptions

### Future Enhancements (Batch 10+)

1. **Smart File Handling:**
   - Auto-detect file size and choose strategy
   - Implement two-stage approach automatically
   - Add context usage monitoring

2. **Provider Capability Detection:**
   - Query provider for context limits
   - Adjust strategy based on model capabilities
   - Provide warnings before hitting limits

3. **Batch Processing:**
   - Split large file sets into batches
   - Process sequentially with context preservation
   - Aggregate results intelligently

---

## Lessons Learned

### What Went Wrong
1. ❌ Assumed all models handle large context + web search equally
2. ❌ Embedded 12 files as raw content without size check
3. ❌ Combined max thinking mode + web search + large files
4. ❌ No validation of total context size before request

### What Worked
1. ✅ GLM-4.6 successfully diagnosed the issue
2. ✅ Systematic investigation approach
3. ✅ Documented the problem for future reference
4. ✅ Identified clear solutions and workarounds

### Action Items
- [ ] Implement file upload API workflow for EXAI validations
- [ ] Add context size validation to chat tools
- [ ] Update EXAI tool documentation with best practices
- [ ] Create helper function for smart file handling
- [ ] Test two-stage approach with actual implementation

---

## Conclusion

The infinite loop issue with Kimi Thinking Preview + web search + large files is caused by **context window overload**. The solution is to use the file upload API instead of embedding files as raw content, which preserves context space for web search execution.

**Recommended Approach for Future EXAI Validations:**
1. Upload files via `kimi_upload_files` tool
2. Reference files via `file_ids` in chat requests
3. Use standard thinking mode (not max) with web search
4. Keep embedded content under 50KB when web search is enabled

This issue highlights the importance of understanding provider-specific limitations and implementing smart context management strategies.

---

**Next Steps:**
1. Implement file upload workflow for Batch 9 validation
2. Document findings in master checklist
3. Update EXAI validation procedures
4. Test recommended approach with actual files

