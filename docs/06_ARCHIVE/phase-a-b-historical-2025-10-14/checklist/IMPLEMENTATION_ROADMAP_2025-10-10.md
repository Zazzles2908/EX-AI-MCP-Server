# EXAI-MCP IMPLEMENTATION ROADMAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Timezone:** AEDT (Melbourne, Australia)  
**Status:** Ready for Implementation

---

## QUICK REFERENCE

### Documents Created
1. **ROOT_CAUSE_ANALYSIS_2025-10-10.md** - Issues 1-2 (Dynamic prompts, Date awareness)
2. **ROOT_CAUSE_ANALYSIS_PART2_2025-10-10.md** - Issues 3-5 (Routing, Embeddings, Logging)
3. **ROOT_CAUSE_INVESTIGATION_COMPLETE_2025-10-10.md** - Executive summary
4. **IMPLEMENTATION_ROADMAP_2025-10-10.md** - This file (quick start guide)

### External References
- **checklist_25-10-10.md** - Claude's observability audit (10 flags)
- **2025-10-10_terminaloutput1.md** - Server logs showing issues
- **.logs/toolcalls.jsonl** - JSONL logs with timestamp issues

---

## IMPLEMENTATION PRIORITY

### 🔴 WEEK 1: CRITICAL FIXES (14-18 hours)

#### Day 1: Quick Wins (8-10 hours)

**Morning: Issue 2 - Model Training Date Awareness** (3-4 hours)
```bash
# Step 1: Create timestamp utility
touch src/utils/timestamp_utils.py

# Step 2: Implement timestamp functions
# See ROOT_CAUSE_ANALYSIS_2025-10-10.md lines 150-200

# Step 3: Inject into prompts
# Modify tools/simple/base.py

# Step 4: Test
# Prompt: "What's today's date?"
# Expected: "2025-10-10"
```

**Afternoon: Issue 3 - Model Routing Rules** (5-6 hours)
```bash
# Step 1: Create model registry
touch src/utils/model_registry.py

# Step 2: Implement registry with aliases
# See ROOT_CAUSE_ANALYSIS_PART2_2025-10-10.md lines 50-150

# Step 3: Add validation to request handler
# Modify src/server/handlers/request_handler.py

# Step 4: Test
# Prompt with model="kimi-latest-128k"
# Expected: Resolves to "kimi-k2-0905-preview", no 404 error
```

#### Day 2-3: Major Improvement (6-8 hours)

**Issue 1 - Dynamic System Prompts**
```bash
# Step 1: Create prompt engineering module
touch src/utils/prompt_engineering.py

# Step 2: Implement intent detection
# See ROOT_CAUSE_ANALYSIS_2025-10-10.md lines 50-150

# Step 3: Update chat tool
# Modify tools/chat.py

# Step 4: Update base tool interface
# Modify tools/shared/base_tool_core.py

# Step 5: Test
# Prompt: "Review this code for bugs"
# Expected: System prompt mentions "code quality analysis"
```

#### Day 4: Testing & Validation

**Unit Tests**
```bash
# Create test files
touch tests/test_timestamp_utils.py
touch tests/test_model_registry.py
touch tests/test_prompt_engineering.py

# Run tests
pytest tests/
```

**Integration Tests**
```bash
# Test date awareness
# Test model routing
# Test dynamic prompts
```

**Manual Testing**
```bash
# Test 1: Date awareness
# Prompt: "What's today's date?"
# Expected: "2025-10-10"

# Test 2: Model routing
# Prompt: "Test" with model="kimi-latest-128k"
# Expected: No 404 error, uses kimi-k2-0905-preview

# Test 3: Dynamic prompts
# Prompt: "Review this code: def foo(): pass"
# Expected: System prompt mentions code review
```

---

### 🟡 WEEK 2: IMPORTANT ENHANCEMENTS (14-18 hours)

#### Day 1-2: Observability (4-6 hours)

**Issue 5 - Log Visibility**
```bash
# Step 1: Integrate timestamp_utils into logging
# Find current logging location
# Add human-readable timestamps

# Step 2: Add request_id correlation
# Modify request handler to generate request_id
# Add to all log entries

# Step 3: Flatten JSON structure
# Remove nested stringification
# See checklist_25-10-10.md FLAG #3

# Step 4: Test
# Check logs have AEDT timestamps
# Verify request_id in all entries
```

#### Day 3-5: Advanced Features (10-12 hours)

**Issue 4 - GLM Embeddings**
```bash
# Step 1: Create embeddings provider
touch src/providers/glm_embeddings.py

# Step 2: Create file chunker
touch src/utils/file_chunker.py

# Step 3: Integrate with file handling
# Find current file handling location
# Add chunking + embeddings fallback

# Step 4: Test
# Upload file > 1MB
# Expected: Chunked and processed via embeddings
```

---

## NEW FILES TO CREATE

### Utilities
1. **src/utils/timestamp_utils.py** (Issue 2)
   - `get_current_timestamps()` - Returns dict with unix, utc_iso, aedt_human, date_only
   - `format_date_for_prompt()` - Human-readable date for AI prompts
   - Uses pytz for Melbourne timezone

2. **src/utils/model_registry.py** (Issue 3)
   - `ModelRegistry` class with GLM and Kimi models
   - `resolve_model_name()` - Alias resolution
   - `is_valid_model()` - Validation
   - `get_provider_for_model()` - Provider lookup

3. **src/utils/prompt_engineering.py** (Issue 1)
   - `PromptEngineer` class with intent detection
   - `analyze_intent()` - Detect code_review, debugging, architecture, etc.
   - `detect_domain()` - Detect frontend, backend, devops, security
   - `generate_system_prompt()` - Dynamic prompt generation

4. **src/utils/file_chunker.py** (Issue 4)
   - `FileChunker` class for smart chunking
   - `chunk_text()` - Chunk with overlap
   - `chunk_file()` - File-based chunking

### Providers
5. **src/providers/glm_embeddings.py** (Issue 4)
   - `GLMEmbeddings` class
   - `generate_embeddings()` - Batch embedding generation
   - `cosine_similarity()` - Similarity calculation
   - `find_most_similar()` - Semantic search

---

## FILES TO MODIFY

### Core Changes
1. **tools/simple/base.py** (Issues 1, 2)
   - Line ~966-1017: `build_standard_prompt()`
   - Add: Date injection
   - Add: Pass user_prompt to get_system_prompt

2. **tools/chat.py** (Issue 1)
   - Line ~50-80: `get_system_prompt()`
   - Replace: Static prompt with dynamic generation
   - Add: Call to prompt_engineering.py

3. **src/server/handlers/request_handler.py** (Issues 2, 3)
   - Line ~73: Add request_id generation
   - Line ~96-109: Add model validation
   - Add: Timestamp metadata injection

4. **tools/shared/base_tool_core.py** (Issue 1)
   - Update: `get_system_prompt()` signature
   - Add: `user_prompt` parameter

### Provider Changes
5. **src/providers/kimi.py** (Issue 3)
   - Line ~124-145: `generate_content()`
   - Add: Model validation before API call

6. **src/providers/glm_chat.py** (Issue 3)
   - Add: Model validation before API call

### Routing Changes
7. **src/server/handlers/request_handler_model_resolution.py** (Issue 3)
   - Line ~146-206: `resolve_auto_model_legacy()`
   - Add: Use model registry for validation

---

## TESTING CHECKLIST

### Unit Tests
- [ ] `tests/test_timestamp_utils.py` - Timestamp formatting
- [ ] `tests/test_model_registry.py` - Model validation and alias resolution
- [ ] `tests/test_prompt_engineering.py` - Intent detection and prompt generation
- [ ] `tests/test_file_chunker.py` - File chunking logic
- [ ] `tests/test_glm_embeddings.py` - Embedding generation

### Integration Tests
- [ ] `tests/test_request_handler.py` - Request_id generation, timestamp injection
- [ ] `tests/test_chat_tool.py` - Dynamic prompts end-to-end
- [ ] `tests/test_model_routing.py` - Model validation and routing
- [ ] `tests/test_file_handling.py` - Large file processing

### Manual Tests
- [ ] Date awareness: "What's today's date?" → "2025-10-10"
- [ ] Model routing: model="kimi-latest-128k" → No 404 error
- [ ] Dynamic prompts: "Review this code" → Code review system prompt
- [ ] Log visibility: Check logs have AEDT timestamps and request_id
- [ ] Large files: Upload file > 1MB → Processed via embeddings

---

## VALIDATION CRITERIA

### User-Facing
- [ ] Models respond with correct current date (2025-10-10)
- [ ] System prompts adapt to user intent
- [ ] No 404 errors from invalid model names
- [ ] Large files processed (not skipped)

### Developer-Facing
- [ ] Logs have human-readable timestamps (AEDT)
- [ ] Every log entry has request_id
- [ ] Can trace complete request flow
- [ ] JSON logs parseable with single json.loads()

### System Health
- [ ] No duplicate log entries
- [ ] Token usage tracked accurately
- [ ] Sub-tool calls visible in logs
- [ ] Model routing rules enforced

---

## ROLLBACK PLAN

If any implementation causes issues:

### Issue 1: Dynamic Prompts
```bash
# Revert tools/chat.py to static prompt
git checkout HEAD -- tools/chat.py

# Remove prompt_engineering.py
rm src/utils/prompt_engineering.py
```

### Issue 2: Date Awareness
```bash
# Revert tools/simple/base.py
git checkout HEAD -- tools/simple/base.py

# Remove timestamp_utils.py
rm src/utils/timestamp_utils.py
```

### Issue 3: Model Routing
```bash
# Revert request_handler.py
git checkout HEAD -- src/server/handlers/request_handler.py

# Remove model_registry.py
rm src/utils/model_registry.py
```

---

## DEPENDENCIES

### Python Packages
```bash
# Already in requirements.txt (verify):
pip install pytz  # For timezone handling
pip install zhipuai  # For GLM embeddings
pip install numpy  # For similarity calculations
```

### Environment Variables
```bash
# Already in .env (verify):
GLM_API_KEY=your_key_here
KIMI_API_KEY=your_key_here
```

---

## SUCCESS METRICS

### Before Implementation
- ❌ Models respond with training date (April 2024)
- ❌ System prompts are generic ("senior engineering thought-partner")
- ❌ Model "kimi-latest-128k" causes 404 error
- ❌ Files > 1MB are skipped
- ❌ Logs have Unix timestamps (1757200863.3202353)

### After Implementation
- ✅ Models respond with current date (2025-10-10)
- ✅ System prompts adapt to intent (code review, debugging, etc.)
- ✅ Model "kimi-latest-128k" resolves to "kimi-k2-0905-preview"
- ✅ Files > 1MB processed via embeddings
- ✅ Logs have AEDT timestamps (2025-10-10 14:30:25 AEDT)

---

## NEXT STEPS

### Option 1: Start Implementation
```bash
# Begin with Issue 2 (quickest win)
cd c:\Project\EX-AI-MCP-Server
touch src/utils/timestamp_utils.py

# Follow ROOT_CAUSE_ANALYSIS_2025-10-10.md
# Section: Issue 2, Step 1
```

### Option 2: Review & Adjust
- Review root cause analysis documents
- Adjust priorities if needed
- Request clarifications

### Option 3: Deep Dive
- Pick one issue for detailed walkthrough
- Review exact code changes
- Validate approach

---

## CONTACT & SUPPORT

**Documentation:**
- Full analysis: `docs/checklist/ROOT_CAUSE_ANALYSIS_2025-10-10.md`
- Part 2: `docs/checklist/ROOT_CAUSE_ANALYSIS_PART2_2025-10-10.md`
- Summary: `docs/handoff-next-agent/ROOT_CAUSE_INVESTIGATION_COMPLETE_2025-10-10.md`

**External References:**
- Claude's audit: `docs/checklist/checklist_25-10-10.md`
- Terminal logs: `docs/terminal_output/2025-10-10_terminaloutput1.md`
- JSONL logs: `.logs/toolcalls.jsonl`

---

**READY TO IMPLEMENT ✅**

Choose your starting point and let's begin!

