# EXAI-MCP ROOT CAUSE ANALYSIS & IMPLEMENTATION PLAN (PART 2)
**Date:** 2025-10-10 (10th October 2025)  
**Continuation of:** ROOT_CAUSE_ANALYSIS_2025-10-10.md

---

## ISSUE 3: MODEL ROUTING RULES NOT WORKING

### Problem Statement
External AI (Claude) requested `kimi-latest-128k` but the system selected it despite:
1. Model doesn't exist in Kimi API (404 error in terminal output line 404)
2. Routing rules should have prevented this selection
3. Fallback chain activated but shouldn't have been needed

**Evidence from Terminal Output:**
```
Line 403: HTTP Request: POST https://api.moonshot.ai/v1/chat/completions "HTTP/1.1 404 Not Found"
Line 404: ERROR ... kimi-latest-128k error ... 'Not found the model kimi-latest-128k or Permission denied'
Line 405: WARNING ... Explicit model call failed; entering fallback chain
Line 407: INFO ... Using fallback chain for category FAST_RESPONSE
Line 408: INFO ... chat.completions.create payload ... "model": "kimi-k2-0905-preview"
```

### Root Cause Location

**File:** `src/server/handlers/request_handler_model_resolution.py`  
**Lines:** ~68-206 (_route_auto_model and resolve_auto_model_legacy)

**Problem 1: Model Name Validation Missing**
```python
# Current code (simplified):
async def SERVER_HANDLE_CALL_TOOL(name: str, arguments: dict, req_id=None):
    model_name = arguments.get("model", "auto")
    
    # NO VALIDATION HERE - accepts any string!
    if model_name != "auto":
        # Directly uses user-provided model name
        result = await provider.chat(model=model_name, ...)
```

**Problem 2: Model Alias Resolution Missing**
```python
# User requests: "kimi-latest-128k"
# System should map to: "kimi-k2-0905-preview" (actual model name)
# But NO alias resolution exists!
```

**Problem 3: Routing Rules Only Apply to "auto"**
```python
# Routing rules in request_handler_model_resolution.py
# ONLY activate when model="auto"
# If user specifies explicit model, routing is BYPASSED
```

### Script Interconnection Analysis

**Call Chain:**
```
User specifies model="kimi-latest-128k"
  → src/server/handlers/request_handler.py (SERVER_HANDLE_CALL_TOOL)
    → Line 96: model_name = arguments.get("model", "auto")
    → Line 107-109: if model_name == "auto": resolve_auto_model()
    → ELSE: Use model_name directly (NO VALIDATION!)
      → src/providers/kimi.py (generate_content)
        → OpenAI client.chat.completions.create(model="kimi-latest-128k")
          → Moonshot API returns 404 (model doesn't exist)
            → Fallback chain activates (tools/chat.py line ~200)
              → Eventually uses kimi-k2-0905-preview
```

**Key Insight:** Routing rules are NEVER consulted when user provides explicit model name.

### Implementation Strategy

**Option A: Validate All Model Names (RECOMMENDED)**
- Create model registry with valid names + aliases
- Validate ALL model names (auto or explicit)
- Resolve aliases to actual model names
- Reject invalid models early

**Option B: Force Routing for All Requests**
- Ignore user-specified models
- Always use routing rules
- **Problem:** Breaks user control

**Decision:** Use Option A - validate and resolve, but respect user choice

### Detailed Implementation Plan

#### Step 1: Create Model Registry

**File:** `src/utils/model_registry.py` (NEW)

```python
"""
Centralized model registry with validation and alias resolution.
Maintains list of valid models and their aliases.
"""

from typing import Dict, List, Optional

class ModelRegistry:
    """Registry of valid models and their aliases."""
    
    # GLM Models (ZhipuAI)
    GLM_MODELS = {
        "glm-4.6": ["glm-4.6"],
        "glm-4.5": ["glm-4.5"],
        "glm-4.5-flash": ["glm-4.5-flash", "glm-flash"],
        "glm-4.5-air": ["glm-4.5-air", "glm-air"],
        "glm-4.5v": ["glm-4.5v"],
    }
    
    # Kimi Models (Moonshot)
    KIMI_MODELS = {
        "kimi-k2-0905-preview": [
            "kimi-k2-0905-preview",
            "kimi-latest",  # Alias
            "kimi-latest-128k",  # Alias (user's requested name)
            "kimi-k2",
        ],
        "kimi-k2-turbo-preview": [
            "kimi-k2-turbo-preview",
            "kimi-turbo",
        ],
        "moonshot-v1-8k": ["moonshot-v1-8k"],
        "moonshot-v1-32k": ["moonshot-v1-32k"],
        "moonshot-v1-128k": ["moonshot-v1-128k"],
        "kimi-thinking-preview": [
            "kimi-thinking-preview",
            "kimi-thinking",
        ],
    }
    
    def __init__(self):
        """Initialize model registry."""
        # Build reverse lookup: alias -> canonical name
        self._alias_map = {}
        
        for canonical, aliases in {**self.GLM_MODELS, **self.KIMI_MODELS}.items():
            for alias in aliases:
                self._alias_map[alias.lower()] = canonical
    
    def resolve_model_name(self, model_name: str) -> Optional[str]:
        """
        Resolve model name or alias to canonical model name.
        
        Args:
            model_name: User-provided model name or alias
        
        Returns:
            Canonical model name, or None if invalid
        """
        if not model_name or model_name == "auto":
            return None  # Let routing handle it
        
        # Normalize to lowercase for lookup
        normalized = model_name.lower().strip()
        
        # Check if it's a known alias
        canonical = self._alias_map.get(normalized)
        
        if canonical:
            return canonical
        
        # Not found
        return None
    
    def is_valid_model(self, model_name: str) -> bool:
        """Check if model name is valid (canonical or alias)."""
        return self.resolve_model_name(model_name) is not None
    
    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get provider name for a model."""
        canonical = self.resolve_model_name(model_name)
        
        if not canonical:
            return None
        
        if canonical in self.GLM_MODELS:
            return "glm"
        elif canonical in self.KIMI_MODELS:
            return "kimi"
        
        return None
    
    def list_all_models(self) -> Dict[str, List[str]]:
        """List all models with their aliases."""
        return {**self.GLM_MODELS, **self.KIMI_MODELS}


# Singleton instance
_model_registry = None

def get_model_registry() -> ModelRegistry:
    """Get or create singleton ModelRegistry instance."""
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry
```

#### Step 2: Add Model Validation to Request Handler

**File:** `src/server/handlers/request_handler.py`  
**Lines:** ~96-109 (model resolution logic)

```python
from src.utils.model_registry import get_model_registry

async def SERVER_HANDLE_CALL_TOOL(name: str, arguments: dict, req_id=None):
    """Main entry point for tool execution with model validation."""
    
    # ... (request_id generation, timestamp injection)
    
    # Get model registry
    registry = get_model_registry()
    
    # Get user-requested model
    requested_model = arguments.get("model", "auto")
    
    # Resolve model name (handles aliases)
    if requested_model != "auto":
        canonical_model = registry.resolve_model_name(requested_model)
        
        if canonical_model is None:
            # Invalid model name
            logger.warning(
                f"Invalid model name '{requested_model}' requested. "
                f"Falling back to auto routing."
            )
            # Force auto routing
            arguments["model"] = "auto"
            arguments["_original_model_request"] = requested_model
        else:
            # Valid model - use canonical name
            logger.info(
                f"Resolved model alias '{requested_model}' -> '{canonical_model}'"
            )
            arguments["model"] = canonical_model
            arguments["_original_model_request"] = requested_model
    
    # Now proceed with tool execution
    # Model name is either "auto" or a VALID canonical name
    tool_obj = get_tool(name)
    result = await execute_tool_with_context(tool_obj, arguments, req_id)
    
    return result
```

#### Step 3: Update Model Resolution Logic

**File:** `src/server/handlers/request_handler_model_resolution.py`  
**Lines:** ~146-206 (resolve_auto_model_legacy)

```python
from src.utils.model_registry import get_model_registry

def resolve_auto_model_legacy(
    tool_name: str,
    arguments: dict,
    step_number: int = 1,
    total_steps: int = 1
) -> str:
    """
    Resolve 'auto' model to specific model based on routing rules.
    Now also validates explicit model names.
    """
    
    # Get model registry
    registry = get_model_registry()
    
    # Get requested model
    requested_model = arguments.get("model", "auto")
    
    # If explicit model provided, validate it
    if requested_model != "auto":
        canonical = registry.resolve_model_name(requested_model)
        
        if canonical is None:
            logger.warning(
                f"Invalid model '{requested_model}' for tool '{tool_name}'. "
                f"Using routing rules instead."
            )
            # Fall through to routing logic
        else:
            # Valid explicit model - use it
            logger.info(f"Using explicit model: {canonical}")
            return canonical
    
    # Auto routing logic (existing code)
    # ... (lines 68-91: step-aware routing)
    
    # Default fallback
    return GLM_SPEED_MODEL  # glm-4.5-flash
```

#### Step 4: Add Model Validation to Providers

**File:** `src/providers/kimi.py`  
**Lines:** ~124-145 (generate_content method)

```python
from src.utils.model_registry import get_model_registry

async def generate_content(
    self,
    prompt: str,
    system_prompt: str = "",
    model_name: str = "kimi-k2-0905-preview",
    **kwargs
) -> tuple:
    """Generate content with model validation."""
    
    # Validate model name
    registry = get_model_registry()
    canonical_model = registry.resolve_model_name(model_name)
    
    if canonical_model is None:
        raise ValueError(
            f"Invalid Kimi model name: '{model_name}'. "
            f"Valid models: {list(registry.KIMI_MODELS.keys())}"
        )
    
    # Verify it's actually a Kimi model
    provider = registry.get_provider_for_model(canonical_model)
    if provider != "kimi":
        raise ValueError(
            f"Model '{canonical_model}' is not a Kimi model (provider: {provider})"
        )
    
    # Use canonical model name
    logger.info(f"Kimi provider using validated model: {canonical_model}")
    
    # Proceed with API call using canonical name
    # ... (existing code)
```

**File:** `src/providers/glm_chat.py`  
**Similar validation logic**

### Downstream Impact Analysis

**Files That Will Change:**
1. `src/utils/model_registry.py` - NEW (centralized registry)
2. `src/server/handlers/request_handler.py` - Modified (add validation)
3. `src/server/handlers/request_handler_model_resolution.py` - Modified (use registry)
4. `src/providers/kimi.py` - Modified (validate before API call)
5. `src/providers/glm_chat.py` - Modified (validate before API call)

**Files That Benefit:**
- ALL tools get automatic model validation
- ALL provider calls use canonical names
- Logs show both requested and resolved model names

**Breaking Changes:** None (invalid models fall back to auto routing)

### Testing Requirements

**Test 1: Model Alias Resolution**
```python
# Test file: tests/test_model_registry.py
from src.utils.model_registry import get_model_registry

def test_kimi_alias_resolution():
    registry = get_model_registry()
    
    # Test valid alias
    canonical = registry.resolve_model_name("kimi-latest-128k")
    assert canonical == "kimi-k2-0905-preview"
    
    # Test canonical name
    canonical = registry.resolve_model_name("kimi-k2-0905-preview")
    assert canonical == "kimi-k2-0905-preview"
    
    # Test invalid name
    canonical = registry.resolve_model_name("invalid-model")
    assert canonical is None
```

**Test 2: Request Handler Validation**
```python
async def test_invalid_model_fallback():
    arguments = {
        "prompt": "test",
        "model": "kimi-latest-128k"  # Alias
    }
    
    await SERVER_HANDLE_CALL_TOOL("chat", arguments)
    
    # Should resolve to canonical name
    assert arguments["model"] == "kimi-k2-0905-preview"
    assert arguments["_original_model_request"] == "kimi-latest-128k"
```

**Test 3: Provider Validation**
```bash
# Manual test via chat tool
# Prompt: "Test" with model="kimi-latest-128k"
# Expected: Logs show "Resolved model alias 'kimi-latest-128k' -> 'kimi-k2-0905-preview'"
# Expected: NO 404 error
# Expected: Successful response

# Prompt: "Test" with model="invalid-model-name"
# Expected: Logs show "Invalid model name 'invalid-model-name' requested. Falling back to auto routing."
# Expected: Uses glm-4.5-flash (default)
# Expected: Successful response
```

### Implementation Checklist

- [ ] Create `src/utils/model_registry.py` with ModelRegistry class
- [ ] Add all GLM models and aliases to registry
- [ ] Add all Kimi models and aliases to registry
- [ ] Implement resolve_model_name method
- [ ] Implement is_valid_model method
- [ ] Implement get_provider_for_model method
- [ ] Update `src/server/handlers/request_handler.py` - add validation
- [ ] Update `src/server/handlers/request_handler_model_resolution.py` - use registry
- [ ] Update `src/providers/kimi.py` - validate before API call
- [ ] Update `src/providers/glm_chat.py` - validate before API call
- [ ] Write unit tests for model registry
- [ ] Write integration tests for request handler
- [ ] Write integration tests for providers
- [ ] Manual testing with valid aliases
- [ ] Manual testing with invalid model names
- [ ] Update documentation with valid model names and aliases

**Estimated Effort:** 5-6 hours  
**Risk Level:** MEDIUM (touches critical routing logic)  
**Priority:** HIGH (prevents API errors and wasted tokens)

---

## ISSUE 4: FILE SIZE LIMITS & MISSING GLM EMBEDDINGS

### Problem Statement
From terminal output (lines not shown in excerpt), server is skipping files due to size limits. GLM embeddings not implemented, causing system to wait in limbo when files are needed.

**Evidence:**
- User memory: "GLM embeddings should be implemented for robustness"
- User memory: "GLM embeddings not implemented, causing file handling issues"
- Terminal output shows file upload errors for certain file types

### Root Cause Location

**File:** `src/providers/glm_embeddings.py` (DOES NOT EXIST)  
**File:** `tools/shared/file_handling.py` (hypothetical - need to find actual location)

**Problem 1: No GLM Embeddings Implementation**
```python
# Expected file: src/providers/glm_embeddings.py
# Status: DOES NOT EXIST
# Impact: Cannot process large files via embeddings
```

**Problem 2: File Size Validation Too Strict**
```python
# Somewhere in file handling code:
MAX_FILE_SIZE = 1_000_000  # 1MB (too small?)
if file_size > MAX_FILE_SIZE:
    logger.warning(f"Skipping file {file_path} - exceeds size limit")
    return None  # File is skipped, no alternative processing
```

**Problem 3: No Chunking Strategy**
```python
# Current: Upload entire file or skip it
# Needed: Chunk large files and process in parts
```

### Script Interconnection Analysis

**Call Chain (File Upload):**
```
User provides files parameter
  → tools/chat.py (execute)
    → tools/simple/base.py (build_standard_prompt)
      → File handling logic (LOCATION UNKNOWN - need to find)
        → Size validation
          → IF too large: Skip file (NO FALLBACK!)
          → IF acceptable: Upload to Kimi
            → src/providers/kimi.py (file upload)
```

**Missing Chain (Embeddings):**
```
Large file detected
  → Should: Chunk file
    → Should: Generate embeddings via GLM
      → Should: Store in vector database
        → Should: Retrieve relevant chunks for context
  → Currently: Just skip the file
```

### Implementation Strategy

**Phase 1: Implement GLM Embeddings (NEW SCRIPT)**
- Create `src/providers/glm_embeddings.py`
- Implement text chunking
- Implement embedding generation
- Implement similarity search

**Phase 2: Create File Chunking Service (NEW SCRIPT)**
- Create `src/utils/file_chunker.py`
- Implement smart chunking (respect code boundaries)
- Implement chunk metadata tracking

**Phase 3: Integrate with File Handling**
- Modify file handling to use chunking for large files
- Add fallback: embeddings when file too large for direct upload

**Decision:** Create NEW specialized scripts, don't bloat existing code

### Detailed Implementation Plan

#### Step 1: Implement GLM Embeddings Provider

**File:** `src/providers/glm_embeddings.py` (NEW)

```python
"""
GLM embeddings provider for text vectorization.
Uses ZhipuAI embedding models for semantic search.
"""

from typing import List, Dict, Optional
import numpy as np
from zhipuai import ZhipuAI
import os

class GLMEmbeddings:
    """GLM embeddings provider."""
    
    EMBEDDING_MODEL = "embedding-3"  # GLM embedding model
    EMBEDDING_DIMENSION = 2048  # Dimension of embedding vectors
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GLM embeddings provider."""
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("GLM_API_KEY not found in environment")
        
        self.client = ZhipuAI(api_key=self.api_key)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of texts.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors (each is list of floats)
        """
        if not texts:
            return []
        
        # Call GLM embeddings API
        response = self.client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=texts
        )
        
        # Extract embeddings
        embeddings = [item.embedding for item in response.data]
        
        return embeddings
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar embeddings to query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
        
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for idx, candidate in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate)
            similarities.append((idx, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]


# Singleton instance
_glm_embeddings = None

def get_glm_embeddings() -> GLMEmbeddings:
    """Get or create singleton GLMEmbeddings instance."""
    global _glm_embeddings
    if _glm_embeddings is None:
        _glm_embeddings = GLMEmbeddings()
    return _glm_embeddings
```

#### Step 2: Implement File Chunking Service

**File:** `src/utils/file_chunker.py` (NEW)

```python
"""
File chunking service for processing large files.
Implements smart chunking that respects code boundaries.
"""

from typing import List, Dict
import os

class FileChunker:
    """Smart file chunking service."""
    
    DEFAULT_CHUNK_SIZE = 4000  # characters per chunk
    OVERLAP_SIZE = 200  # overlap between chunks for context
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap_size: int = OVERLAP_SIZE
    ):
        """Initialize file chunker."""
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of chunk dictionaries with 'text', 'index', 'metadata'
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not the last chunk, try to break at newline
            if end < len(text):
                # Look for newline within last 10% of chunk
                search_start = end - int(self.chunk_size * 0.1)
                newline_pos = text.rfind('\n', search_start, end)
                
                if newline_pos != -1:
                    end = newline_pos + 1
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # Create chunk dictionary
            chunk = {
                "text": chunk_text,
                "index": chunk_index,
                "start_pos": start,
                "end_pos": end,
                "metadata": metadata or {}
            }
            
            chunks.append(chunk)
            
            # Move to next chunk (with overlap)
            start = end - self.overlap_size
            chunk_index += 1
        
        return chunks
    
    def chunk_file(self, file_path: str) -> List[Dict]:
        """
        Chunk a file into segments.
        
        Args:
            file_path: Path to file to chunk
        
        Returns:
            List of chunk dictionaries
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create metadata
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": len(text)
        }
        
        # Chunk text
        return self.chunk_text(text, metadata)


# Singleton instance
_file_chunker = None

def get_file_chunker() -> FileChunker:
    """Get or create singleton FileChunker instance."""
    global _file_chunker
    if _file_chunker is None:
        _file_chunker = FileChunker()
    return _file_chunker
```

*[Implementation continues with integration steps...]*

### Implementation Checklist

- [ ] Create `src/providers/glm_embeddings.py` with GLMEmbeddings class
- [ ] Add zhipuai embeddings API support
- [ ] Implement generate_embeddings method
- [ ] Implement similarity search methods
- [ ] Create `src/utils/file_chunker.py` with FileChunker class
- [ ] Implement smart chunking with overlap
- [ ] Implement code-aware chunking (respect function boundaries)
- [ ] Find current file handling location in codebase
- [ ] Integrate chunking + embeddings as fallback for large files
- [ ] Add proper error handling and user feedback
- [ ] Write unit tests for embeddings
- [ ] Write unit tests for chunking
- [ ] Write integration tests for large file handling
- [ ] Manual testing with files > 1MB
- [ ] Document embeddings usage in docs/

**Estimated Effort:** 10-12 hours  
**Risk Level:** HIGH (new functionality, complex integration)  
**Priority:** MEDIUM (improves robustness but not blocking)

---

## ISSUE 5: LOG VISIBILITY & SUPABASE INTEGRATION

### Problem Statement
Current JSONL logs are difficult to interpret. Supabase integration planned but not implemented. Raw logs lack proper timestamps and structured data.

**Evidence from Logs:**
```jsonl
{"provider": "kimi", "tool_name": "file_upload_extract", "start_ts": 1757200863.3202353, ...}
```

**Problems:**
1. Unix timestamps (1757200863.3202353) are not human-readable
2. No timezone information
3. No request correlation (request_id is missing in these logs)
4. Nested JSON stringification (from Claude's audit)

### Root Cause Location

**File:** `.logs/toolcalls.jsonl`  
**File:** `src/utils/logging.py` (hypothetical - need to find actual location)

**Problem:** Log entries use Unix timestamps without human-readable dates

### Implementation Strategy

**Phase 1: Improve Current Logs (QUICK WIN)**
- Add human-readable timestamps
- Add request_id to all log entries
- Flatten JSON structure

**Phase 2: Plan Supabase Integration (FUTURE)**
- Design database schema
- Create migration plan
- Implement async logging to Supabase

**Decision:** Focus on Phase 1 first (quick improvements), plan Phase 2 for later

### Detailed Implementation Plan

*[See Claude's checklist_25-10-10.md for detailed logging improvements]*

**Key Changes:**
1. Add AEDT timestamps to all log entries
2. Add request_id correlation
3. Flatten nested JSON
4. Add structured metadata

### Implementation Checklist

- [ ] Find current logging implementation location
- [ ] Add timestamp_utils integration to logging
- [ ] Add request_id to all log entries
- [ ] Flatten JSON structure (remove nested stringification)
- [ ] Add human-readable timestamps (AEDT)
- [ ] Create log analysis scripts
- [ ] Write log parsing utilities
- [ ] Plan Supabase schema design
- [ ] Document logging format in docs/
- [ ] Create log rotation policy

**Estimated Effort:** 4-6 hours (Phase 1 only)  
**Risk Level:** LOW (improvements to existing system)  
**Priority:** MEDIUM (improves debugging but not blocking)

---

## SUMMARY & NEXT STEPS

### Priority Order

1. **ISSUE 2: Model Training Date Awareness** (3-4 hours, LOW risk, HIGH priority)
2. **ISSUE 1: Dynamic System Prompts** (6-8 hours, MEDIUM risk, HIGH priority)
3. **ISSUE 3: Model Routing Rules** (5-6 hours, MEDIUM risk, HIGH priority)
4. **ISSUE 5: Log Visibility** (4-6 hours, LOW risk, MEDIUM priority)
5. **ISSUE 4: GLM Embeddings** (10-12 hours, HIGH risk, MEDIUM priority)

### Total Estimated Effort
- **Phase 1 (Critical):** 14-18 hours (Issues 1, 2, 3)
- **Phase 2 (Important):** 14-18 hours (Issues 4, 5)
- **Total:** 28-36 hours

### Recommended Approach

**Week 1: Critical Fixes**
- Day 1-2: Issue 2 (Date awareness) + Issue 3 (Model routing)
- Day 3-4: Issue 1 (Dynamic prompts)
- Day 5: Testing and validation

**Week 2: Important Improvements**
- Day 1-2: Issue 5 (Log improvements)
- Day 3-5: Issue 4 (GLM embeddings)

### Success Criteria

- [ ] Models respond with correct current date (2025-10-10)
- [ ] System prompts adapt to user intent
- [ ] Model aliases resolve correctly (no 404 errors)
- [ ] Logs are human-readable with proper timestamps
- [ ] Large files are processed via embeddings

---

**END OF ROOT CAUSE ANALYSIS**

