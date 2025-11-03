# My Investigation - File Upload System Architecture
**Date:** 2025-11-02  
**Investigator:** Claude (Augment Agent)  
**Branch:** feat/file-upload-investigation  
**Purpose:** Comprehensive investigation before EXAI consultation

---

## Investigation Summary

I have conducted a thorough investigation of the EX-AI-MCP-Server file upload system to understand the complete architecture before consulting with EXAI. This document contains my findings and interpretation.

---

## 1. System Architecture Overview

### 1.1 Container Architecture

**Docker Setup:**
- **Container:** `exai-mcp-daemon` (image: `exai-mcp-server:latest`)
- **Base Image:** Python 3.13-slim (multi-stage build)
- **Entry Point:** `scripts/ws/run_ws_daemon.py`
- **Main Server:** `server.py` (MCP protocol server)

**Port Mapping:**
- 8079: WebSocket Daemon (MCP protocol)
- 8080: Monitoring Dashboard
- 8082: Health Check Endpoint
- 8000: Prometheus Metrics

**Volume Mounts (Critical for File Upload):**
```yaml
# Source code (hot reload)
- ./src:/app/src
- ./tools:/app/tools
- ./utils:/app/utils

# File upload support (READ-ONLY)
- c:\Project:/mnt/project:ro  # Maps Windows to Linux container
```

**Key Finding:** Files are mounted READ-ONLY from Windows host to Linux container at `/mnt/project`. This is critical for understanding file upload workflow.

### 1.2 Environment Configuration

**File:** `.env.docker` (738 lines)

**Critical Settings:**
```bash
# File Path Validation
EX_ALLOW_EXTERNAL_PATHS=true
EX_ALLOWED_EXTERNAL_PREFIXES=/app,/mnt/project

# Cross-Platform Path Mapping
EX_DRIVE_MAPPINGS=C:/app

# Test Files Directory
TEST_FILES_DIR=/mnt/project

# Kimi File Upload
KIMI_FILES_MAX_SIZE_MB=100
KIMI_FILES_UPLOAD_TIMEOUT_SECS=90
KIMI_UPLOAD_TO_SUPABASE=false  # DISABLED!

# GLM File Upload
GLM_FILE_UPLOAD_TIMEOUT_SECS=120
```

**Key Finding:** Supabase uploads are DISABLED (`KIMI_UPLOAD_TO_SUPABASE=false`). This means files are NOT being tracked in Supabase Storage.

---

## 2. Supabase Infrastructure

### 2.1 Project Details
- **Project ID:** mxaazuhlqewmkweewyaz
- **Name:** Personal AI
- **Region:** ap-southeast-2 (Sydney)
- **Status:** ACTIVE_HEALTHY
- **Database:** PostgreSQL 17.6.1.005

### 2.2 Database Tables (File-Related)

**`files` table (537 rows):**
- Tracks uploaded files and metadata
- Columns: id, storage_path, original_name, mime_type, size_bytes, file_type, sha256, provider_file_id, provider
- **Key Finding:** Has `provider_file_id` and `provider` columns for tracking platform uploads

**`provider_file_uploads` table (81 rows):**
- Tracks file uploads to AI providers (Kimi, GLM)
- Columns: id, provider, provider_file_id, sha256, filename, upload_status, supabase_file_id
- **Key Finding:** Bidirectional sync between Supabase and providers

**`file_id_mappings` table (100 rows):**
- Maps Supabase file IDs to provider-specific file IDs
- Columns: supabase_file_id, provider_file_id, provider, status, retry_count
- **Key Finding:** Retry logic exists but may not be working

**`file_metadata` table (112 rows):**
- Metadata about files for quick lookups
- Columns: file_id, user_id, filename, file_size, sha256_hash, access_count

**`file_operations` table (49 rows):**
- Tracks all file operations for audit
- Columns: operation_type (upload/download/process/delete/generate), status, metadata

### 2.3 Storage Buckets

1. **user-files** (50MB limit)
2. **generated-files** (10MB limit)
3. **results** (no limit)

### 2.4 Edge Functions

1. **gateway** - Main gateway function
2. **memory** - Memory management
3. **exai-chat** - EXAI chat handler
4. **conversation-handler** - Conversation management
5. **cache-metrics-aggregator** - Cache metrics

**Key Finding:** Gateway Edge Function exists! This is likely the entry point for external applications.

---

## 3. Provider Architecture

### 3.1 File Upload Providers

**GLM (Z.ai Platform):**
- SDK: `zai-sdk` (not `zhipuai`)
- Base URL: `https://api.z.ai/api/paas/v4`
- Implementation: `src/providers/glm_files.py`
- Timeout: 120 seconds
- Features: SDK upload with HTTP fallback

**Kimi (Moonshot Platform):**
- SDK: OpenAI-compatible SDK
- Base URL: `https://api.moonshot.ai/v1`
- Implementation: `src/providers/kimi_files.py`
- Timeout: 90 seconds
- Features: OpenAI Files API

### 3.2 Provider File Structure

**Provider Implementations:**
```
src/providers/
├── glm.py, glm_chat.py, glm_config.py, glm_files.py
├── kimi.py, kimi_chat.py, kimi_config.py, kimi_files.py
├── base.py, file_base.py
├── unified_interface.py
├── async_glm.py, async_kimi.py
└── registry.py, registry_config.py
```

**Key Finding:** Separate sync and async implementations exist. File upload uses sync providers.

---

## 4. File Upload Tools

### 4.1 Main File Upload Tool

**`tools/smart_file_query.py`** - Unified file upload and query interface
- Automatic deduplication (SHA256)
- Provider selection (Kimi/GLM/auto)
- Supabase tracking integration
- Path validation

**Key Finding:** This is the PRIMARY tool for file uploads. It's supposed to handle everything.

### 4.2 Supporting Tools

**File Upload:**
- `tools/async_file_upload_refactored.py` - Async upload logic
- `tools/file_upload_optimizer.py` - Upload optimization
- `tools/supabase_upload.py` - Supabase storage upload
- `tools/file_id_mapper.py` - File ID mapping

**File Download:**
- `tools/smart_file_download.py` - Download interface
- `tools/supabase_download.py` - Supabase storage download

**File Handling:**
- `tools/temp_file_handler.py` - Temporary file management
- `src/storage/file_handler.py` - Core file handling

**Key Finding:** Multiple file upload tools exist. This suggests fragmentation and potential conflicts.

---

## 5. Gateway Architecture

### 5.1 Entry Point

**`server.py`** (437 lines):
- MCP Server implementation
- Tool registration and discovery
- Provider configuration
- WebSocket support

**Key Finding:** Server.py is the main entry point, but it delegates to modular components.

### 5.2 Request Flow

```
External Application
    ↓
WebSocket (port 8079)
    ↓
MCP Server (server.py)
    ↓
Tool Registry (tools/registry.py)
    ↓
smart_file_query tool
    ↓
Provider (GLM/Kimi)
    ↓
Platform API
```

**Key Finding:** The gateway is the MCP server itself. External applications connect via WebSocket on port 8079.

---

## 6. SDK Documentation Research

### 6.1 Moonshot AI (Kimi) SDK

**Official Documentation:**
- Platform: https://platform.moonshot.ai/docs/api/chat
- Uses OpenAI-compatible SDK
- File Upload API: OpenAI Files API format
- Supported operations: upload, list, delete, get info

**Key Finding:** Kimi uses standard OpenAI Files API. Should be straightforward.

### 6.2 Z.ai (GLM) SDK

**Official Documentation:**
- Platform: https://open.bigmodel.cn/dev/api
- Z.ai API: https://z.ai/blog/glm-4.5
- SDK: `zhipuai` (PyPI) or `zai-sdk`
- File Upload: Custom implementation

**Key Finding:** GLM has TWO SDKs (`zhipuai` and `zai-sdk`). Current implementation uses `zai-sdk` for z.ai proxy (3x faster).

---

## 7. Critical Issues Identified

### 7.1 Configuration Issues

1. **Supabase Uploads Disabled:** `KIMI_UPLOAD_TO_SUPABASE=false`
   - Files are NOT being tracked in Supabase Storage
   - No persistent file tracking across sessions

2. **Path Mapping Confusion:**
   - Windows: `c:\Project\EX-AI-MCP-Server`
   - Container: `/app` (code) and `/mnt/project` (files)
   - Mapping: `C:/app` (but should be `C:/mnt/project`?)

3. **Multiple File Upload Tools:**
   - `smart_file_query.py` (main)
   - `async_file_upload_refactored.py` (async)
   - `file_upload_optimizer.py` (optimizer)
   - Potential conflicts and redundancy

### 7.2 Architecture Issues

1. **No Unified File Manager:**
   - Each provider implements own upload logic
   - No central orchestration
   - No file lifecycle management

2. **Missing File State Tracking:**
   - No tracking of upload status
   - No file expiration management
   - No automatic cleanup

3. **Incomplete Supabase Integration:**
   - Tables exist but not being used
   - Edge Functions exist but unclear how they're used
   - File ID mapping exists but may not be working

---

## 8. Questions for EXAI

1. **How does the gateway Edge Function work?**
   - Is it the entry point for external applications?
   - How does it route requests to the MCP server?

2. **Why are Supabase uploads disabled?**
   - What was the "service key issue" mentioned in comments?
   - How can we enable persistent file tracking?

3. **How should file uploads work end-to-end?**
   - External app → Gateway → MCP Server → Provider → Platform
   - Where does Supabase fit in?
   - How should file IDs be managed?

4. **What is the correct path mapping?**
   - Windows to Linux container
   - How should TEST_FILES_DIR work?
   - How do external applications access files?

5. **How do we clean up the architecture?**
   - Remove dead code
   - Consolidate file upload tools
   - Implement unified file manager

---

## 9. Next Steps

1. **Consult EXAI with ALL findings**
2. **Request EXAI to investigate:**
   - Moonshot SDK documentation
   - Z.ai SDK documentation
   - Gateway architecture
   - File upload workflow
3. **Get EXAI recommendations for:**
   - Complete implementation plan
   - Architecture cleanup
   - Dead code removal
4. **Create comprehensive reports:**
   - Research report
   - Error report
   - Implementation plan

---

**Status:** Investigation complete, ready for EXAI consultation


