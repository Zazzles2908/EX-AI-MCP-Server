# File Upload Architecture & Monitoring Dashboard Improvements
**Date:** October 26, 2025  
**EXAI Consultation:** Kimi Thinking Mode with Web Search  
**Continuation ID:** c90cdeec-48bb-4d10-b075-925ebbf39c8a (18 turns remaining)

---

## Executive Summary

This document outlines comprehensive improvements to EXAI's file upload architecture and monitoring dashboard based on EXAI consultation. The goal is to enable external applications on the user's Windows host to upload files to EXAI running in Docker, while providing complete visibility into system health.

---

## PART 1: FILE UPLOAD ARCHITECTURE

### Problem Statement

**Current Issue:**
- User runs EXAI MCP Server in Docker (WSL/Linux container)
- Multiple applications on Windows host need to upload files to EXAI
- Files from external applications fail with "File not accessible in container (not mounted)"
- No clear guidance for agents on which upload method to use

**User's Environment:**
- Windows host with multiple applications (VSCode, standalone scripts, AI agents)
- Files can be anywhere on Windows filesystem (C:\, D:\, etc.)
- Docker container with limited mounted directories

### EXAI Recommendations

#### 1. Hybrid Mounting + File Proxy Service

**Recommended Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Windows Host                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ VSCode Agent │  │ Script Agent │  │ Other Apps   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │ File Proxy      │ (Port 8081)            │
│                   │ Service         │                        │
│                   └────────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTP Upload
┌────────────────────────────▼──────────────────────────────────┐
│                    Docker Container                           │
│  ┌────────────────────────────────────────────────────┐      │
│  │ EXAI MCP Server                                    │      │
│  │  ┌──────────────┐  ┌──────────────┐               │      │
│  │  │ Proxy        │  │ File Handler │               │      │
│  │  │ Endpoint     │→ │              │               │      │
│  │  └──────────────┘  └──────┬───────┘               │      │
│  │                            │                       │      │
│  │  ┌──────────────┐  ┌──────▼───────┐               │      │
│  │  │ Kimi Upload  │  │ GLM Upload   │               │      │
│  │  └──────────────┘  └──────────────┘               │      │
│  └────────────────────────────────────────────────────┘      │
│                            │                                 │
│  ┌────────────────────────▼──────────────────────────┐      │
│  │ Supabase Storage                                  │      │
│  └───────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Security: Avoids exposing entire filesystem
- ✅ Flexibility: Supports any Windows path
- ✅ Performance: Temporary files are cleaned up
- ✅ Compatibility: Works with existing file handler

**Trade-offs:**
- ⚠️ Adds network hop for file transfer
- ⚠️ Requires Windows service installation

#### 2. File Size Thresholds & Upload Method Selection

**EXAI-Recommended Thresholds:**

| File Size | Upload Method | Rationale |
|-----------|---------------|-----------|
| < 50 KB | **Embedding** (files parameter) | Direct embedding in prompt, minimal overhead |
| 0.5 MB - 10 MB | **Kimi Upload** (kimi_upload_files) | 70-80% token savings, multi-turn analysis |
| 0.5 MB - 5 MB | **GLM Upload** (glm_upload_file) | Alternative to Kimi for GLM-specific workflows |
| > 10 MB | **Supabase Storage** (direct upload) | Large file handling, persistent storage |

**Decision Flow:**
```python
def select_upload_method(file_path: str) -> str:
    """Select optimal upload method based on file size"""
    size = get_file_size(file_path)
    
    if size < 50 * 1024:  # < 50KB
        if is_text_file(file_path):
            return "embedding"
    
    if 0.5 * 1024 * 1024 <= size <= 10 * 1024 * 1024:  # 0.5MB - 10MB
        return "kimi_upload"
    
    if 0.5 * 1024 * 1024 <= size <= 5 * 1024 * 1024:  # 0.5MB - 5MB
        return "glm_upload"
    
    if size > 10 * 1024 * 1024:  # > 10MB
        return "supabase_storage"
    
    return "embedding"  # Default fallback
```

#### 3. Agent Documentation Guidelines

**File Accessibility Check:**
```python
def is_file_accessible(file_path: str) -> tuple[bool, str]:
    """
    Check if file is accessible in Docker container
    
    Returns:
        (accessible, message)
    """
    normalized = normalize_path(file_path)
    
    if normalized.startswith("http"):
        return False, "File requires proxy upload (not mounted)"
    
    if os.path.exists(normalized):
        return True, "File accessible"
    
    return False, "File not found in container"
```

**Error Handling Documentation:**
- **"File not accessible"**: Use proxy upload or mount directory
- **"Size limit exceeded"**: Choose different upload method
- **"Mount permission denied"**: Contact system administrator

---

## PART 2: MONITORING DASHBOARD IMPROVEMENTS

### Critical Missing Metrics (Priority Order)

#### Priority 1: Semaphore Status (HIGH)
**Why Critical:** Semaphore leaks caused test crashes at concurrency=5

**Metrics to Add:**
- Current semaphore values (expected vs actual)
- Semaphore leak warnings
- Per-port semaphore status (8079, 8080)
- Provider-specific semaphore status (Kimi, GLM)

**Visualization:**
```
┌─────────────────────────────────────────────────────┐
│ 🔒 Semaphore Health                                 │
├─────────────────────────────────────────────────────┤
│ Port 8079:  ████████░░ 8/10  ✅ Healthy            │
│ Port 8080:  ██████░░░░ 6/10  ✅ Healthy            │
│                                                     │
│ Kimi:       ███░░░░░░░ 3/3   ✅ At Limit           │
│ GLM:        ██░░░░░░░░ 2/2   ✅ At Limit           │
│                                                     │
│ Leaks Detected: 0                                   │
│ Last Recovery: Never                                │
└─────────────────────────────────────────────────────┘
```

#### Priority 2: WebSocket Connection Metrics (HIGH)
**Why Critical:** WebSocket keepalive ping timeouts caused test failures

**Metrics to Add:**
- Ping/pong latency (current, average, p95)
- Connection uptime
- Reconnection events count
- Timeout warnings

**Visualization:**
```
┌─────────────────────────────────────────────────────┐
│ 🌐 WebSocket Health                                 │
├─────────────────────────────────────────────────────┤
│ Port 8079:  ✅ Connected (Uptime: 2h 15m)           │
│   Ping Latency: 12ms (avg: 15ms, p95: 28ms)        │
│   Reconnections: 0                                  │
│                                                     │
│ Port 8080:  ✅ Connected (Uptime: 2h 15m)           │
│   Ping Latency: 8ms (avg: 10ms, p95: 18ms)         │
│   Reconnections: 0                                  │
└─────────────────────────────────────────────────────┘
```

#### Priority 3: Provider-Specific Metrics (MEDIUM)
**Why Important:** Need to compare GLM vs Kimi performance

**Metrics to Add:**
- Request count per provider
- Latency (mean, p50, p95, p99)
- Error count and rate
- Timeout/retry statistics
- Fallback events

**Visualization:**
```
┌─────────────────────────────────────────────────────┐
│ 🤖 Provider Performance                             │
├─────────────────────────────────────────────────────┤
│ Kimi (kimi-k2-0905-preview):                        │
│   Requests: 150 (Success: 148, Failed: 2)           │
│   Latency: 1.87ms (p95: 3.2ms, p99: 5.1ms)         │
│   Error Rate: 1.3%                                  │
│                                                     │
│ GLM (glm-4.6):                                      │
│   Requests: 75 (Success: 75, Failed: 0)             │
│   Latency: 2282ms (p95: 3500ms, p99: 4200ms)       │
│   Error Rate: 0%                                    │
│                                                     │
│ Fallback Events: 0                                  │
└─────────────────────────────────────────────────────┘
```

#### Priority 4: File Upload Metrics (MEDIUM)
**Why Important:** Track file upload usage and failures

**Metrics to Add:**
- Files uploaded (count, total size)
- Upload failures by method
- Storage usage (current, limit)
- Upload method distribution

**Visualization:**
```
┌─────────────────────────────────────────────────────┐
│ 📁 File Upload Metrics                              │
├─────────────────────────────────────────────────────┤
│ Total Uploads: 45 files (125.3 MB)                  │
│ Storage Used: 125.3 MB / 1 GB (12.5%)               │
│                                                     │
│ By Method:                                          │
│   Embedding:   15 files (0.5 MB)   ████░░░░░░      │
│   Kimi:        20 files (85.2 MB)  ████████░░      │
│   GLM:         5 files (12.1 MB)   ██░░░░░░░░      │
│   Supabase:    5 files (27.5 MB)   ███░░░░░░░      │
│                                                     │
│ Failed Uploads: 2 (4.4%)                            │
└─────────────────────────────────────────────────────┘
```

#### Priority 5: Resource Usage Monitoring (LOW)
**Why Important:** Detect resource exhaustion before crashes

**Metrics to Add:**
- Docker container memory usage
- CPU usage percentage
- Network I/O
- Disk usage

**Visualization:**
```
┌─────────────────────────────────────────────────────┐
│ 💻 Resource Usage                                   │
├─────────────────────────────────────────────────────┤
│ Memory:  ████████░░ 1.2 GB / 2 GB (60%)  ✅        │
│ CPU:     ███░░░░░░░ 30%                  ✅        │
│ Network: ↓ 2.5 MB/s  ↑ 1.2 MB/s         ✅        │
│ Disk:    ████░░░░░░ 8.5 GB / 20 GB (42%) ✅        │
└─────────────────────────────────────────────────────┘
```

---

## PART 3: IMPLEMENTATION ROADMAP

### Phase 1: File Upload Architecture (Priority: HIGH)

**Step 1.1: Update File Size Validator** ✅ READY
- File: `utils/file/size_validator.py`
- Update thresholds: 5KB → 50KB for embedding
- Add Kimi range: 0.5MB-10MB
- Add GLM range: 0.5MB-5MB
- Add Supabase threshold: >10MB
- Add `select_upload_method()` function

**Step 1.2: Create Agent Documentation** ⏳ NEXT
- File: `docs/current/AGENT_FILE_UPLOAD_GUIDE.md`
- Document file accessibility checks
- Document upload method selection
- Document error handling
- Provide code examples

**Step 1.3: File Proxy Service** ⏳ FUTURE
- Create Windows service (port 8081)
- Add Docker proxy endpoint
- Update path normalization
- Integration testing

### Phase 2: Monitoring Dashboard - Critical Metrics (Priority: HIGH)

**Step 2.1: Add Semaphore Metrics** ✅ READY
- File: `src/daemon/monitoring_endpoint.py`
- Expose semaphore values via WebSocket
- Track per-port and per-provider semaphores
- Add leak detection warnings

**Step 2.2: Add WebSocket Health Metrics** ✅ READY
- File: `src/daemon/monitoring_endpoint.py`
- Track ping/pong latency
- Monitor connection uptime
- Count reconnection events

**Step 2.3: Update Dashboard UI** ✅ READY
- File: `static/js/dashboard-core.js`
- Add semaphore health panel
- Add WebSocket health panel
- Add provider performance panel

### Phase 3: Additional Monitoring Features (Priority: MEDIUM)

**Step 3.1: File Upload Metrics** ⏳ FUTURE
- Track upload counts and sizes
- Monitor method distribution
- Track failure rates

**Step 3.2: Resource Usage Monitoring** ⏳ FUTURE
- Integrate Docker metrics API
- Display memory/CPU/network/disk
- Add historical trends

**Step 3.3: Alerting System** ⏳ FUTURE
- Implement alert checking
- Add visual indicators
- Create alert history log

---

## IMMEDIATE ACTIONS

### Action 1: Update File Size Validator

**Implementation:**
```python
# utils/file/size_validator.py

# PHASE 2.4 FIX (2025-10-26): EXAI COMPREHENSIVE FIX - Updated file size thresholds
# Based on EXAI consultation with kimi-thinking-preview
# Rationale: Optimize upload method selection for different file sizes

# File size thresholds (EXAI-recommended)
FILE_SIZE_EMBEDDING_KB = 50  # < 50KB: Use embedding (direct in prompt)
FILE_SIZE_EMBEDDING_BYTES = FILE_SIZE_EMBEDDING_KB * 1024

FILE_SIZE_KIMI_MIN_MB = 0.5  # 0.5MB-10MB: Use Kimi upload
FILE_SIZE_KIMI_MAX_MB = 10
FILE_SIZE_KIMI_MIN_BYTES = int(FILE_SIZE_KIMI_MIN_MB * 1024 * 1024)
FILE_SIZE_KIMI_MAX_BYTES = int(FILE_SIZE_KIMI_MAX_MB * 1024 * 1024)

FILE_SIZE_GLM_MIN_MB = 0.5  # 0.5MB-5MB: Use GLM upload
FILE_SIZE_GLM_MAX_MB = 5
FILE_SIZE_GLM_MIN_BYTES = int(FILE_SIZE_GLM_MIN_MB * 1024 * 1024)
FILE_SIZE_GLM_MAX_BYTES = int(FILE_SIZE_GLM_MAX_MB * 1024 * 1024)

FILE_SIZE_SUPABASE_MIN_MB = 10  # >10MB: Use Supabase storage
FILE_SIZE_SUPABASE_MIN_BYTES = int(FILE_SIZE_SUPABASE_MIN_MB * 1024 * 1024)


def select_upload_method(file_path: str) -> dict:
    """
    Select optimal upload method based on file size

    Returns:
        {
            'method': str,  # 'embedding', 'kimi_upload', 'glm_upload', 'supabase_storage'
            'reason': str,  # Explanation for selection
            'size': int,    # File size in bytes
            'size_formatted': str  # Human-readable size
        }
    """
    size = get_file_size(file_path)
    if size is None:
        return {
            'method': 'error',
            'reason': 'File not found or inaccessible',
            'size': 0,
            'size_formatted': '0 B'
        }

    size_formatted = format_file_size(size)

    # < 50KB: Use embedding
    if size < FILE_SIZE_EMBEDDING_BYTES:
        return {
            'method': 'embedding',
            'reason': f'File size ({size_formatted}) < 50KB - optimal for direct embedding',
            'size': size,
            'size_formatted': size_formatted
        }

    # 0.5MB-10MB: Use Kimi upload
    if FILE_SIZE_KIMI_MIN_BYTES <= size <= FILE_SIZE_KIMI_MAX_BYTES:
        return {
            'method': 'kimi_upload',
            'reason': f'File size ({size_formatted}) in range 0.5MB-10MB - use kimi_upload_files for 70-80% token savings',
            'size': size,
            'size_formatted': size_formatted
        }

    # 0.5MB-5MB: Use GLM upload (alternative)
    if FILE_SIZE_GLM_MIN_BYTES <= size <= FILE_SIZE_GLM_MAX_BYTES:
        return {
            'method': 'glm_upload',
            'reason': f'File size ({size_formatted}) in range 0.5MB-5MB - use glm_upload_file for GLM-specific workflows',
            'size': size,
            'size_formatted': size_formatted
        }

    # >10MB: Use Supabase storage
    if size > FILE_SIZE_SUPABASE_MIN_BYTES:
        return {
            'method': 'supabase_storage',
            'reason': f'File size ({size_formatted}) > 10MB - use Supabase storage for large files',
            'size': size,
            'size_formatted': size_formatted
        }

    # Fallback: embedding
    return {
        'method': 'embedding',
        'reason': f'File size ({size_formatted}) - using embedding as fallback',
        'size': size,
        'size_formatted': size_formatted
    }
```

---

## EXAI CONSULTATION SUMMARY

**Continuation ID:** c90cdeec-48bb-4d10-b075-925ebbf39c8a (18 turns remaining)
**Model:** kimi-thinking-preview
**Thinking Mode:** high
**Web Search:** Enabled
**Temperature:** 0.3

**Key Recommendations:**
1. ✅ **File Upload:** Hybrid mounting + proxy service for security and flexibility
2. ✅ **Size Thresholds:** 50KB embedding, 0.5-10MB Kimi, >10MB Supabase
3. ✅ **Monitoring Priority:** Semaphore status and WebSocket health are critical
4. ✅ **Alerting:** Automatic alerts for semaphore leaks (>20% over expected)
5. ✅ **Resource Monitoring:** Essential for preventing concurrency crashes

**Next Steps:**
1. Implement file size validator updates
2. Add semaphore and WebSocket metrics to dashboard
3. Create agent documentation for file uploads
4. Test with Phase 2.3 comparison test
5. Continue EXAI consultation after implementation

