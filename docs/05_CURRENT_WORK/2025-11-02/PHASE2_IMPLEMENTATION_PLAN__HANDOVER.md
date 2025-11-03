# PHASE 2 HIGH PRIORITY IMPLEMENTATION - HANDOVER DOCUMENT

**Document Created:** 2025-11-01  
**EXAI Consultation ID:** fa6820a0-d18b-49da-846f-ee5d5db2ae8b (19 turns remaining)  
**Status:** Ready for Implementation  
**Estimated Implementation Time:** 2-3 hours  
**Estimated Lines of Code:** ~2300 lines (1500 new, 500 modified, 300 removed)

---

## 1. CURRENT STATUS SUMMARY

### ✅ COMPLETED PHASES

#### Phase 0: SECURITY CRITICAL (COMPLETE)
- Task 0.1: Path traversal prevention ✅
- Task 0.2: Input sanitization ✅
- Task 0.3: Rate limiting ✅
- Task 0.4: Audit logging ✅

**Validation:** 4 rounds of EXAI validation completed successfully  
**Documentation:** `SECURITY_CRITICAL_IMPLEMENTATION_COMPLETE.md`

#### Phase 1: URGENT (3-Day Deadline) (COMPLETE)
- Task 0.1: Implement authentication (JWT-based, user quotas) ✅
- Task 2.1: Create unified manager (circuit breakers, SHA256 deduplication) ✅
- Task 2.2: Add file locking (distributed locking, async context manager) ✅
- Task 2.3: Standardize errors (error codes, HTTP status mapping) ✅

**Files Created:**
- `src/auth/file_upload_auth.py` (300 lines)
- `src/file_management/unified_manager.py` (530 lines)
- `src/file_management/file_lock_manager.py` (250 lines)
- `src/file_management/errors.py` (280 lines)
- `src/database/migrations/001_user_quotas.sql` (120 lines)

**Validation:** 2 rounds of EXAI validation completed successfully (CORRECT WORKFLOW)  
**Documentation:** `PHASE1_VALIDATION_COMPLETE__CORRECT_WORKFLOW.md`

### 🔄 IN PROGRESS

#### Phase 2: HIGH PRIORITY (1-Week Deadline) (IN PROGRESS)
- Task 3.1: Reduce configuration complexity 🔄
- Task 3.2: Consolidate configuration files 🔄
- Task 4.1: Add comprehensive monitoring 🔄
- Task 4.2: Implement lifecycle management 🔄
- Additional: Remove all dead code 🔄

**Current State:**
- EXAI consultation completed (fa6820a0-d18b-49da-846f-ee5d5db2ae8b)
- Comprehensive implementation plan received from EXAI
- Ready for systematic implementation

---

## 2. EXAI IMPLEMENTATION PLAN INTEGRATION

### 2.1 Configuration Consolidation (Tasks 3.1 & 3.2)

**Current Problem:**
- `.env.docker` file: 776 lines (target: <200 lines)
- Configuration scattered across multiple files
- Many non-sensitive defaults in .env file
- Duplicate configurations between modules

**EXAI's Solution:**

#### New Configuration Structure
```
config/
├── __init__.py
├── base.py              # Base configuration classes (NEW)
├── models.py            # Model configuration (from core.py)
├── operations.py        # Operations configuration (refactor existing)
├── file_management.py   # File upload configuration (NEW)
└── sensitive.py         # Only API keys and secrets (NEW)
```

#### Environment Variable Classification

**KEEP in .env.docker (sensitive data only):**
- `GLM_API_KEY` - Z.ai API key
- `KIMI_API_KEY` - Moonshot AI API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT signing secret
- Database credentials
- External service credentials

**MOVE to Python config classes (with defaults):**
- Feature flags: `INTELLIGENT_ROUTING_ENABLED`, `ROUTER_ENABLED`, `USE_ASYNC_PROVIDERS`
- Performance settings: `MAX_CONCURRENT_REQUESTS`, `RATE_LIMIT_PER_MINUTE`
- Timeouts: `REQUEST_TIMEOUT`, `DEFAULT_CONSENSUS_TIMEOUT`, `UPLOAD_TIMEOUT`
- File handling: `MAX_FILE_SIZE`, `ALLOWED_EXTENSIONS`, `ENABLE_DEDUPLICATION`
- Model configuration: `DEFAULT_MODEL`, `TEMPERATURE_*`, `DEFAULT_THINKING_MODE_THINKDEEP`
- Context engineering: `STRIP_EMBEDDED_HISTORY`, `DETECTION_MODE`, `MIN_TOKEN_THRESHOLD`

#### Master Checklist Mapping
- **Task 3.1 (Reduce configuration complexity)** → Create `config/base.py` and `config/file_management.py`
- **Task 3.2 (Consolidate configuration files)** → Refactor existing configs, reduce .env.docker to <200 lines

### 2.2 Monitoring Enhancement (Task 4.1)

**Current Problem:**
- Existing `metrics.py` (518 lines) has comprehensive Prometheus metrics
- NO file-specific metrics currently implemented
- Missing: upload_attempts, upload_bytes, upload_duration, active_uploads, deduplication_hits, circuit_breaker_trips

**EXAI's Solution:**

#### Create File-Specific Metrics Module
**Location:** `src/monitoring/file_metrics.py`

**Metrics to Add:**
- `FILE_UPLOAD_ATTEMPTS` - Counter with labels [provider, user_id]
- `FILE_UPLOAD_BYTES` - Counter with labels [provider, status]
- `FILE_UPLOAD_DURATION` - Histogram with labels [provider]
- `ACTIVE_UPLOADS` - Gauge (no labels)
- `DEDUPLICATION_HITS` - Counter (no labels)
- `CIRCUIT_BREAKER_TRIPS` - Counter with labels [provider]

#### Integration Points
1. **In `src/file_management/unified_manager.py`:**
   - Import file_metrics module
   - Add `record_upload_attempt()` at start of upload_file()
   - Add `record_upload_completion()` at end of upload_file()
   - Add `record_deduplication_hit()` when SHA256 match found
   - Add `record_circuit_breaker_trip()` when circuit breaker opens

2. **Dashboard Integration:**
   - Create Prometheus alerting rules
   - Create Grafana dashboard JSON (optional)

#### Master Checklist Mapping
- **Task 4.1 (Add comprehensive monitoring)** → Create `src/monitoring/file_metrics.py` and instrument unified_manager.py

### 2.3 Lifecycle Management (Task 4.2)

**Current Problem:**
- Existing `graceful_shutdown.py` (251 lines) handles shutdown
- NO file cleanup lifecycle management
- Files never cleaned up, orphaned files accumulate

**EXAI's Solution:**

#### Create Lifecycle Manager
**Location:** `src/file_management/lifecycle_manager.py`

**Key Features:**
- Periodic cleanup task (every 24 hours)
- Retention policy (default 30 days, configurable)
- Orphaned file detection and removal
- Integration with graceful shutdown manager

**Implementation Details:**
- Use `asyncio.create_task()` for background cleanup loop
- Query Supabase for expired files (created_at < cutoff_date)
- Delete from provider using unified_manager.delete_file()
- Mark as deleted in Supabase
- Graceful shutdown integration via shutdown handler registration

#### Integration Points
1. **In `src/monitoring/persistence/graceful_shutdown.py`:**
   - Add lifecycle manager shutdown handler registration
   - Ensure cleanup task completes before shutdown

2. **In server startup (main.py or ws_server.py):**
   - Initialize lifecycle manager after other components
   - Start cleanup task

3. **In shutdown sequence:**
   - Stop accepting new uploads
   - Wait for active uploads to complete
   - Stop lifecycle manager
   - Proceed with existing shutdown

#### Master Checklist Mapping
- **Task 4.2 (Implement lifecycle management)** → Create `src/file_management/lifecycle_manager.py` and integrate with graceful_shutdown.py

### 2.4 Dead Code Removal

**EXAI's Identified Dead Code:**

**Files to DELETE:**
- `config/timeouts.py` - Duplicate timeout configurations (consolidate into operations.py)
- `config/migration.py` - Unused migration configuration
- `config/file_handling.py` - Redundant file handling guidance

**Code to REMOVE:**
- Unused imports in `src/core/env_config.py`
- Redundant helper functions in config modules
- Duplicate validation logic in provider modules
- Unused error handling patterns

**Consolidation Required:**
- Merge timeout configurations from `timeouts.py` into `operations.py`
- Update all imports after file deletions

---

## 3. FILES TO CREATE

### 3.1 config/base.py (NEW)

**Purpose:** Base configuration classes with common utilities

**Full Code Template:**
```python
"""
Base configuration classes for EX-AI-MCP-Server
Provides common utilities for environment variable parsing
"""
from abc import ABC
from typing import Dict, Any, Optional
import os
from pathlib import Path

class BaseConfig(ABC):
    """Base configuration with common utilities"""
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Parse boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    @classmethod
    def get_int(cls, key: str, default: int) -> int:
        """Parse integer environment variable with fallback"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float) -> float:
        """Parse float environment variable with fallback"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @classmethod
    def get_str(cls, key: str, default: str = "") -> str:
        """Get string environment variable"""
        return os.getenv(key, default)
    
    @classmethod
    def get_list(cls, key: str, default: str = "", separator: str = ",") -> list:
        """Parse comma-separated list from environment variable"""
        value = os.getenv(key, default)
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]
```

**Lines:** ~50 lines
**Dependencies:** None (standard library only)

### 3.2 config/file_management.py (NEW)

**Purpose:** Configuration for file management operations

**Full Code Template:**
```python
"""
File management configuration for EX-AI-MCP-Server
Consolidates all file upload, validation, and lifecycle settings
"""
from .base import BaseConfig
from typing import List, Dict

class FileManagementConfig(BaseConfig):
    """Configuration for file management operations"""

    # File size limits (in bytes)
    MAX_FILE_SIZE: int = BaseConfig.get_int("MAX_FILE_SIZE", 100 * 1024 * 1024)  # 100MB default
    MAX_FILE_SIZE_KIMI: int = BaseConfig.get_int("MAX_FILE_SIZE_KIMI", 100 * 1024 * 1024)  # 100MB
    MAX_FILE_SIZE_GLM: int = BaseConfig.get_int("MAX_FILE_SIZE_GLM", 20 * 1024 * 1024)  # 20MB

    # Allowed file types
    ALLOWED_EXTENSIONS: List[str] = BaseConfig.get_list(
        "ALLOWED_EXTENSIONS",
        "txt,pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif,zip,py,js,ts,json,yaml,yml,md"
    )

    # Upload configuration
    UPLOAD_TIMEOUT: int = BaseConfig.get_int("UPLOAD_TIMEOUT", 300)  # 5 minutes
    MAX_CONCURRENT_UPLOADS: int = BaseConfig.get_int("MAX_CONCURRENT_UPLOADS", 5)

    # Deduplication
    ENABLE_DEDUPLICATION: bool = BaseConfig.get_bool("ENABLE_DEDUPLICATION", True)

    # Provider preferences
    PREFERRED_PROVIDER: str = BaseConfig.get_str("PREFERRED_PROVIDER", "")  # empty = auto

    # Lifecycle management
    RETENTION_DAYS: int = BaseConfig.get_int("FILE_RETENTION_DAYS", 30)
    CLEANUP_INTERVAL_HOURS: int = BaseConfig.get_int("CLEANUP_INTERVAL_HOURS", 24)

    # User quotas
    DEFAULT_USER_QUOTA_GB: int = BaseConfig.get_int("DEFAULT_USER_QUOTA_GB", 10)
    MAX_FILE_SIZE_PER_USER: int = BaseConfig.get_int("MAX_FILE_SIZE_PER_USER", 512 * 1024 * 1024)  # 512MB

    @classmethod
    def get_provider_limits(cls) -> Dict[str, int]:
        """Get file size limits by provider"""
        return {
            "kimi": cls.MAX_FILE_SIZE_KIMI,
            "glm": cls.MAX_FILE_SIZE_GLM
        }

    @classmethod
    def is_extension_allowed(cls, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename or "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in cls.ALLOWED_EXTENSIONS
```

**Lines:** ~55 lines
**Dependencies:** `config/base.py`

### 3.3 src/monitoring/file_metrics.py (NEW)

**Purpose:** File-specific Prometheus metrics

**Full Code Template:**
```python
"""
File upload metrics for EX-AI-MCP-Server
Provides Prometheus-compatible metrics for file operations
"""
import logging
from prometheus_client import Counter, Histogram, Gauge
from typing import Optional

logger = logging.getLogger(__name__)

# File upload metrics
FILE_UPLOAD_ATTEMPTS = Counter(
    'mcp_file_upload_attempts_total',
    'Total file upload attempts',
    ['provider', 'user_id']
)

FILE_UPLOAD_BYTES = Counter(
    'mcp_file_upload_bytes_total',
    'Total bytes uploaded',
    ['provider', 'status']
)

FILE_UPLOAD_DURATION = Histogram(
    'mcp_file_upload_duration_seconds',
    'File upload duration in seconds',
    ['provider'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')]
)

ACTIVE_UPLOADS = Gauge(
    'mcp_file_active_uploads',
    'Number of active file uploads'
)

DEDUPLICATION_HITS = Counter(
    'mcp_file_deduplication_hits_total',
    'Total deduplication hits (files already uploaded)'
)

CIRCUIT_BREAKER_TRIPS = Counter(
    'mcp_file_circuit_breaker_trips_total',
    'Total circuit breaker trips',
    ['provider']
)

FILE_DELETIONS = Counter(
    'mcp_file_deletions_total',
    'Total file deletions',
    ['provider', 'reason']  # reason: expired, manual, orphaned
)

# Helper functions
def record_upload_attempt(provider: str, user_id: str) -> None:
    """Record a file upload attempt"""
    try:
        FILE_UPLOAD_ATTEMPTS.labels(provider=provider, user_id=user_id).inc()
        ACTIVE_UPLOADS.inc()
        logger.debug(f"Recorded upload attempt: provider={provider}, user_id={user_id}")
    except Exception as e:
        logger.error(f"Error recording upload attempt: {e}")

def record_upload_completion(provider: str, status: str, bytes_count: int, duration: float) -> None:
    """Record a completed file upload"""
    try:
        FILE_UPLOAD_BYTES.labels(provider=provider, status=status).inc(bytes_count)
        FILE_UPLOAD_DURATION.labels(provider=provider).observe(duration)
        ACTIVE_UPLOADS.dec()
        logger.debug(f"Recorded upload completion: provider={provider}, status={status}, bytes={bytes_count}, duration={duration:.2f}s")
    except Exception as e:
        logger.error(f"Error recording upload completion: {e}")

def record_deduplication_hit() -> None:
    """Record a deduplication hit (file already exists)"""
    try:
        DEDUPLICATION_HITS.inc()
        logger.debug("Recorded deduplication hit")
    except Exception as e:
        logger.error(f"Error recording deduplication hit: {e}")

def record_circuit_breaker_trip(provider: str) -> None:
    """Record a circuit breaker trip"""
    try:
        CIRCUIT_BREAKER_TRIPS.labels(provider=provider).inc()
        logger.warning(f"Recorded circuit breaker trip: provider={provider}")
    except Exception as e:
        logger.error(f"Error recording circuit breaker trip: {e}")

def record_file_deletion(provider: str, reason: str) -> None:
    """Record a file deletion"""
    try:
        FILE_DELETIONS.labels(provider=provider, reason=reason).inc()
        logger.debug(f"Recorded file deletion: provider={provider}, reason={reason}")
    except Exception as e:
        logger.error(f"Error recording file deletion: {e}")
```

**Lines:** ~100 lines
**Dependencies:** `prometheus_client`, `src/monitoring/metrics.py` (for integration)

### 3.4 src/file_management/lifecycle_manager.py (NEW)

**Purpose:** File lifecycle management with periodic cleanup

**Full Code Template (Part 1 - Class Definition):**
```python
"""
File lifecycle manager for EX-AI-MCP-Server
Handles periodic cleanup, retention policy, and orphaned file detection
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from src.storage.supabase_manager import SupabaseManager
from src.file_management.unified_manager import UnifiedFileManager
from src.monitoring.file_metrics import record_file_deletion

logger = logging.getLogger(__name__)

class FileLifecycleManager:
    """Manages file lifecycle including cleanup and retention"""

    def __init__(
        self,
        unified_manager: UnifiedFileManager,
        supabase: SupabaseManager,
        retention_days: int = 30,
        cleanup_interval_hours: int = 24
    ):
        """
        Initialize file lifecycle manager

        Args:
            unified_manager: Unified file manager for file operations
            supabase: Supabase manager for database operations
            retention_days: Number of days to retain files (default: 30)
            cleanup_interval_hours: Hours between cleanup runs (default: 24)
        """
        self.unified_manager = unified_manager
        self.supabase = supabase
        self.retention_days = retention_days
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._is_running = False

        logger.info(
            f"FileLifecycleManager initialized: "
            f"retention={retention_days} days, "
            f"cleanup_interval={cleanup_interval_hours} hours"
        )

    async def start(self) -> None:
        """Start periodic cleanup task"""
        if self._cleanup_task is not None:
            logger.warning("Lifecycle manager already running")
            return

        self._is_running = True
        self._shutdown_event.clear()
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("File lifecycle manager started")

    async def stop(self) -> None:
        """Stop periodic cleanup task gracefully"""
        if self._cleanup_task is None:
            logger.warning("Lifecycle manager not running")
            return

        logger.info("Stopping file lifecycle manager...")
        self._is_running = False
        self._shutdown_event.set()

        try:
            await asyncio.wait_for(self._cleanup_task, timeout=30)
            logger.info("File lifecycle manager stopped gracefully")
        except asyncio.TimeoutError:
            logger.warning("Lifecycle manager stop timeout, cancelling task")
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                logger.info("Lifecycle manager task cancelled")

        self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop"""
        logger.info("Cleanup loop started")

        while self._is_running and not self._shutdown_event.is_set():
            try:
                logger.info("Starting cleanup cycle...")

                # Run cleanup tasks
                expired_count = await self._cleanup_expired_files()
                orphaned_count = await self._detect_orphaned_files()

                logger.info(
                    f"Cleanup cycle complete: "
                    f"expired={expired_count}, orphaned={orphaned_count}"
                )

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)

            # Wait for next cleanup interval or shutdown signal
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.cleanup_interval.total_seconds()
                )
                logger.info("Shutdown signal received, exiting cleanup loop")
                break
            except asyncio.TimeoutError:
                # Timeout is expected, continue to next cleanup cycle
                continue

        logger.info("Cleanup loop exited")
```

**Full Code Template (Part 2 - Cleanup Methods):**
```python
    async def _cleanup_expired_files(self) -> int:
        """
        Clean up files older than retention period

        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        deleted_count = 0

        try:
            # Query expired files from Supabase
            result = await self.supabase.client.table("file_uploads")\
                .select("file_id, provider, user_id, file_name")\
                .lt("created_at", cutoff_date.isoformat())\
                .eq("status", "active")\
                .execute()

            if not result.data:
                logger.debug("No expired files found")
                return 0

            logger.info(f"Found {len(result.data)} expired files for cleanup")

            for file_record in result.data:
                try:
                    # Delete from provider
                    success = await self.unified_manager.delete_file(
                        file_id=file_record["file_id"],
                        provider=file_record["provider"],
                        user_id=file_record["user_id"]
                    )

                    if success:
                        # Mark as deleted in Supabase
                        await self.supabase.client.table("file_uploads")\
                            .update({
                                "status": "deleted",
                                "deleted_at": datetime.utcnow().isoformat(),
                                "deletion_reason": "expired"
                            })\
                            .eq("file_id", file_record["file_id"])\
                            .execute()

                        # Record metrics
                        record_file_deletion(file_record["provider"], "expired")

                        deleted_count += 1
                        logger.info(
                            f"Deleted expired file: {file_record['file_id']} "
                            f"({file_record['file_name']})"
                        )
                    else:
                        logger.error(
                            f"Failed to delete expired file: {file_record['file_id']}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error deleting file {file_record['file_id']}: {e}",
                        exc_info=True
                    )

            return deleted_count

        except Exception as e:
            logger.error(f"Error in cleanup_expired_files: {e}", exc_info=True)
            return deleted_count

    async def _detect_orphaned_files(self) -> int:
        """
        Detect files in providers but not in Supabase (orphaned files)

        Returns:
            Number of orphaned files detected
        """
        # This is a placeholder for orphaned file detection
        # Full implementation would require provider-specific list operations
        logger.debug("Checking for orphaned files...")

        # TODO: Implement provider-specific orphaned file detection
        # - Query all files from Kimi provider
        # - Query all files from GLM provider
        # - Compare with Supabase records
        # - Delete files not in Supabase

        return 0
```

**Lines:** ~200 lines total
**Dependencies:** `src/storage/supabase_manager.py`, `src/file_management/unified_manager.py`, `src/monitoring/file_metrics.py`

---

## 4. FILES TO MODIFY

### 4.1 config/operations.py

**Changes Required:**
1. Import `BaseConfig` from `config/base.py`
2. Convert class to inherit from `BaseConfig`
3. Replace all `os.getenv()` calls with `BaseConfig.get_*()` methods
4. Add timeout configurations from `config/timeouts.py` (before deleting that file)

**Example Modification:**
```python
# BEFORE:
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

# AFTER:
from .base import BaseConfig

class OperationsConfig(BaseConfig):
    LOG_LEVEL: str = BaseConfig.get_str("LOG_LEVEL", "INFO")
    MAX_RETRIES: int = BaseConfig.get_int("MAX_RETRIES", 3)
```

### 4.2 src/core/env_config.py

**Changes Required:**
1. Import new config modules: `from config.file_management import FileManagementConfig`
2. Update `ClientConfig`, `ProviderConfig`, `SystemConfig` to use new config classes
3. Remove redundant helper functions (now in `BaseConfig`)
4. Add file management configuration access methods

**Example Modification:**
```python
# ADD:
from config.file_management import FileManagementConfig

class FileConfig:
    @staticmethod
    def get_max_file_size() -> int:
        return FileManagementConfig.MAX_FILE_SIZE

    @staticmethod
    def get_retention_days() -> int:
        return FileManagementConfig.RETENTION_DAYS
```

### 4.3 src/file_management/unified_manager.py

**Changes Required:**
1. Import `file_metrics` module at top
2. Add metrics instrumentation to `upload_file()` method
3. Add metrics instrumentation to `delete_file()` method
4. Add metrics for circuit breaker state changes
5. Add metrics for deduplication hits

**Specific Integration Points:**

**In `upload_file()` method:**
```python
# ADD at start of method:
from src.monitoring.file_metrics import (
    record_upload_attempt,
    record_upload_completion,
    record_deduplication_hit
)
import time

# At start of upload_file():
start_time = time.time()
record_upload_attempt(provider, user_id)

# When SHA256 match found (deduplication):
record_deduplication_hit()

# At end of upload_file() (success):
duration = time.time() - start_time
record_upload_completion(provider, "success", file_size, duration)

# At end of upload_file() (failure):
duration = time.time() - start_time
record_upload_completion(provider, "failure", 0, duration)
```

**In circuit breaker state change:**
```python
# ADD when circuit breaker opens:
from src.monitoring.file_metrics import record_circuit_breaker_trip

if circuit_breaker.state == CircuitBreakerState.OPEN:
    record_circuit_breaker_trip(provider)
```

### 4.4 src/monitoring/persistence/graceful_shutdown.py

**Changes Required:**
1. Add lifecycle manager shutdown handler registration
2. Ensure lifecycle manager stops before other shutdown handlers

**Specific Integration:**
```python
# ADD new helper function:
def register_lifecycle_manager_handler(lifecycle_manager) -> None:
    """Register lifecycle manager shutdown handler"""
    handler = get_shutdown_handler()

    async def lifecycle_shutdown():
        logger.info("Stopping lifecycle manager...")
        await lifecycle_manager.stop()
        logger.info("Lifecycle manager stopped")

    handler.register_shutdown_handler(lifecycle_shutdown)
```

### 4.5 .env.docker

**Changes Required:**
Reduce from 776 lines to <200 lines by removing all non-sensitive configuration.

**KEEP (Sensitive Data - ~50 lines):**
```bash
# API Keys
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Database Credentials (if separate)
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password

# External Service Credentials
# Add any other API keys or secrets here
```

**REMOVE (Move to Python configs - ~726 lines):**
- All feature flags (INTELLIGENT_ROUTING_ENABLED, etc.)
- All performance settings (MAX_CONCURRENT_REQUESTS, etc.)
- All timeout configurations
- All file handling settings
- All model configurations
- All context engineering settings
- All default values that can be in Python

**Backup Strategy:**
```bash
# Before modifying .env.docker:
cp .env.docker .env.docker.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 5. FILES TO DELETE

### 5.1 Dead Code Files

**Files to DELETE:**
1. `config/timeouts.py` - Consolidate into `config/operations.py`
2. `config/migration.py` - Unused migration configuration
3. `config/file_handling.py` - Redundant file handling guidance

**Before Deletion:**
1. Extract any useful configurations from these files
2. Merge into appropriate config modules
3. Update all imports that reference these files
4. Search codebase for any remaining references

**Import Update Pattern:**
```python
# BEFORE:
from config.timeouts import DEFAULT_TIMEOUT

# AFTER:
from config.operations import OperationsConfig
timeout = OperationsConfig.DEFAULT_TIMEOUT
```

---

## 6. IMPLEMENTATION SEQUENCE

### Step-by-Step Implementation Order

#### PHASE 1: Configuration Foundation (30 minutes)
1. **Create `config/base.py`** (NEW)
   - Copy template from Section 3.1
   - Test import: `python -c "from config.base import BaseConfig; print('OK')"`

2. **Create `config/file_management.py`** (NEW)
   - Copy template from Section 3.2
   - Test import: `python -c "from config.file_management import FileManagementConfig; print('OK')"`

3. **Refactor `config/operations.py`** (MODIFY)
   - Add `from .base import BaseConfig`
   - Convert to class inheriting from `BaseConfig`
   - Replace all `os.getenv()` with `BaseConfig.get_*()`
   - Test import: `python -c "from config.operations import OperationsConfig; print('OK')"`

4. **Update `src/core/env_config.py`** (MODIFY)
   - Import new config modules
   - Add `FileConfig` class
   - Remove redundant helper functions
   - Test import: `python -c "from src.core.env_config import FileConfig; print('OK')"`

**Testing Checkpoint 1:**
- All imports work without errors
- Configuration values load correctly
- No circular import issues

#### PHASE 2: Monitoring Enhancement (30 minutes)
5. **Create `src/monitoring/file_metrics.py`** (NEW)
   - Copy template from Section 3.3
   - Test import: `python -c "from src.monitoring.file_metrics import record_upload_attempt; print('OK')"`

6. **Instrument `src/file_management/unified_manager.py`** (MODIFY)
   - Add file_metrics imports
   - Add metrics to `upload_file()` method
   - Add metrics to `delete_file()` method
   - Add metrics to circuit breaker state changes
   - Test: Verify metrics are recorded (check Prometheus endpoint)

**Testing Checkpoint 2:**
- Metrics module imports successfully
- unified_manager.py still functions correctly
- Metrics are recorded during file operations

#### PHASE 3: Lifecycle Management (45 minutes)
7. **Create `src/file_management/lifecycle_manager.py`** (NEW)
   - Copy template from Section 3.4
   - Test import: `python -c "from src.file_management.lifecycle_manager import FileLifecycleManager; print('OK')"`

8. **Integrate with `src/monitoring/persistence/graceful_shutdown.py`** (MODIFY)
   - Add `register_lifecycle_manager_handler()` function
   - Test: Verify shutdown handler registration works

9. **Update server startup** (MODIFY `src/daemon/ws_server.py` or `main.py`)
   - Initialize lifecycle manager
   - Start cleanup task
   - Register shutdown handler
   - Test: Verify lifecycle manager starts and stops correctly

**Testing Checkpoint 3:**
- Lifecycle manager starts successfully
- Cleanup task runs in background
- Graceful shutdown works correctly

#### PHASE 4: Configuration Cleanup (30 minutes)
10. **Backup and reduce `.env.docker`** (MODIFY)
    - Create backup: `cp .env.docker .env.docker.backup.$(date +%Y%m%d_%H%M%S)`
    - Remove all non-sensitive configuration
    - Keep only API keys and secrets (~50 lines)
    - Test: Verify system still loads configuration correctly

11. **Delete dead code files** (DELETE)
    - Delete `config/timeouts.py`
    - Delete `config/migration.py`
    - Delete `config/file_handling.py`
    - Update all imports
    - Test: Verify no import errors

**Testing Checkpoint 4:**
- .env.docker reduced to <200 lines
- All configuration still loads correctly
- No import errors after file deletions

#### PHASE 5: Integration Testing (15 minutes)
12. **End-to-end testing**
    - Test file upload with metrics collection
    - Test file deletion with metrics collection
    - Test lifecycle cleanup (manually trigger)
    - Test graceful shutdown
    - Verify all metrics are recorded correctly

**Final Testing Checkpoint:**
- All components work together
- No errors in logs
- Metrics are collected correctly
- Lifecycle management works
- Graceful shutdown works

---

## 7. VALIDATION WORKFLOW (EXACT SEQUENCE)

### CRITICAL: Follow this EXACT sequence for validation

#### Step 1: Docker Rebuild
```bash
# Stop containers
docker-compose down

# Rebuild without cache
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Wait for initialization
timeout /t 10 /nobreak
```

#### Step 2: Create Completion Markdown
Create file: `docs/05_CURRENT_WORK/2025-11-02/HIGH_TASKS_IMPLEMENTATION_COMPLETE.md`

**Required Content:**
- Summary of all 5 tasks completed
- List of ALL files created (full absolute paths)
- List of ALL files modified (full absolute paths)
- List of ALL files deleted (full absolute paths)
- Implementation details and features
- **Note:** Docker logs are PENDING (will be collected after EXAI Round 1)

#### Step 3: EXAI Validation Round 1 (Initial Review)
**Upload to EXAI:**
- Completion markdown
- ALL newly created files
- ALL modified files

**EXAI Parameters:**
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b`

**Prompt:**
```
Phase 2 HIGH priority tasks implementation complete. Please review the implementation and validate that all objectives have been achieved:

1. Configuration consolidation (Tasks 3.1 & 3.2):
   - .env.docker reduced from 776 lines to <200 lines
   - New config modules created (base.py, file_management.py)
   - Existing configs refactored to use base classes

2. Comprehensive monitoring (Task 4.1):
   - file_metrics.py created with Prometheus metrics
   - unified_manager.py instrumented for metrics collection
   - Metrics: upload_attempts, upload_bytes, upload_duration, active_uploads, deduplication_hits, circuit_breaker_trips

3. Lifecycle management (Task 4.2):
   - lifecycle_manager.py created with periodic cleanup
   - Retention policy (30 days) implemented
   - Integration with graceful shutdown manager

4. Dead code removal:
   - Deleted: config/timeouts.py, config/migration.py, config/file_handling.py
   - Consolidated duplicate configurations

Please validate:
- No import errors
- All modules integrate correctly
- Configuration loads properly
- Metrics are defined correctly
- Lifecycle manager logic is sound
- No obvious bugs or issues

Docker logs will be provided in Round 2 for runtime validation.
```

#### Step 4: Collect Docker Logs
```bash
# Collect logs AFTER containers have been running
docker logs exai-mcp-daemon --tail 1000 > docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt
```

**IMPORTANT:** This OVERWRITES any existing `docker_logs_high.txt` file

#### Step 5: EXAI Validation Round 2 (Comprehensive Review)
**Upload to EXAI:**
- Completion markdown
- ALL files (created + modified)
- Docker logs (`docker_logs_high.txt`)

**EXAI Parameters:**
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b`

**Prompt:**
```
Comprehensive review of Phase 2 HIGH priority implementation with Docker logs.

Please verify:
1. Container started successfully (no import errors in logs)
2. All modules loaded correctly
3. No runtime errors
4. Configuration system working (values loaded from new config modules)
5. Metrics system initialized (Prometheus metrics registered)
6. Lifecycle manager started successfully
7. No warnings or errors in logs
8. System is stable and production-ready

If any issues are found, provide specific recommendations for fixes.
```

#### Step 6: Implement EXAI Findings (if any)
If EXAI identifies issues:
1. Implement fixes immediately
2. Rebuild Docker: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
3. Repeat validation workflow from Step 2
4. Continue until EXAI confirms all objectives achieved

#### Step 7: Update Master Checklists
Update all 3 master checklist files:

**File 1:** `COMPREHENSIVE_MASTER_CHECKLIST__FINAL.md` (Part 1)
- Mark Phase 2 tasks as COMPLETE
- Add completion timestamp
- Reference completion markdown

**File 2:** `COMPREHENSIVE_MASTER_CHECKLIST__PART2.md` (Part 2)
- Document all script changes
- Document system impact
- List all files created/modified/deleted

**File 3:** `COMPREHENSIVE_MASTER_CHECKLIST__PART3.md` (Part 3)
- Document batch details
- Add completion timestamps
- Include implementation code examples

---

## 8. RISK MITIGATION

### Configuration Consolidation Risks

**Risk 1:** Breaking existing deployments
- **Mitigation:** Maintain backward compatibility during transition
- **Rollback:** Restore `.env.docker.backup` file
- **Testing:** Test with existing .env values before cleanup

**Risk 2:** Accidentally exposing sensitive data
- **Mitigation:** Clear separation of sensitive.py, add .gitignore rules
- **Validation:** Review all config files before commit
- **Pre-commit hook:** Check for API keys in non-sensitive files

### Monitoring Enhancement Risks

**Risk 3:** Performance impact from metrics collection
- **Mitigation:** Use async metrics collection, minimal overhead
- **Monitoring:** Watch for latency increases
- **Fallback:** Disable metrics if performance degrades

**Risk 4:** Metrics storage overhead
- **Mitigation:** Configure appropriate retention periods
- **Monitoring:** Monitor Prometheus storage usage
- **Cleanup:** Implement metrics cleanup policy

### Lifecycle Management Risks

**Risk 5:** Accidentally deleting active files
- **Mitigation:** Strict status checking (only delete status="active" AND created_at < cutoff)
- **Safety:** Soft delete before actual deletion (mark as "deleted" first)
- **Validation:** Log all deletions for audit trail

**Risk 6:** Resource exhaustion during cleanup
- **Mitigation:** Rate limit cleanup operations (batch processing with delays)
- **Monitoring:** Monitor cleanup task resource usage
- **Timeout:** Enforce cleanup timeout to prevent runaway tasks

---

## 9. EXAI CONSULTATION STRATEGY

### When to Consult EXAI

**BEFORE Implementation:**
- Validate understanding of handover document
- Confirm implementation approach for each component
- Get approval for any deviations from plan

**DURING Implementation:**
- Troubleshoot any errors or issues
- Validate complex code sections
- Get second opinion on design decisions

**AFTER Implementation:**
- Validate completion (Round 1 - code review)
- Validate runtime behavior (Round 2 - with logs)
- Confirm all objectives achieved

### EXAI Consultation Parameters

**Continuation ID:** fa6820a0-d18b-49da-846f-ee5d5db2ae8b (19 turns remaining)
**Model:** glm-4.6
**Thinking Mode:** max
**Web Search:** true
**Tool:** Use `chat_EXAI-WS-VSCode1` (NOT `chat_EXAI-WS-VSCode2`)

### Sample EXAI Consultation Prompts

**Before Starting:**
```
I'm about to implement Phase 2 HIGH priority tasks based on the handover document. Here's my understanding:

1. Configuration consolidation: Create config/base.py and config/file_management.py, refactor existing configs, reduce .env.docker to <200 lines
2. Monitoring: Create src/monitoring/file_metrics.py, instrument unified_manager.py
3. Lifecycle: Create src/file_management/lifecycle_manager.py, integrate with graceful_shutdown.py
4. Dead code: Delete config/timeouts.py, config/migration.py, config/file_handling.py

Is this understanding correct? Any potential issues I should be aware of before starting?
```

**During Implementation (if stuck):**
```
I'm implementing [specific component] and encountered [specific issue]. Here's what I've tried:
- [attempt 1]
- [attempt 2]

Error message: [error]

What's the root cause and how should I fix it?
```

**After Implementation:**
```
I've completed Phase 2 implementation. Here's what was done:
- [summary of changes]

Please review the uploaded files and validate that all objectives have been achieved.
```

---

## 10. SUCCESS CRITERIA

### Phase 2 Implementation is COMPLETE when:

✅ **Configuration Consolidation:**
- [ ] `config/base.py` created and tested
- [ ] `config/file_management.py` created and tested
- [ ] `config/operations.py` refactored to use base classes
- [ ] `src/core/env_config.py` updated with new imports
- [ ] `.env.docker` reduced from 776 lines to <200 lines
- [ ] All configuration loads correctly
- [ ] No import errors

✅ **Monitoring Enhancement:**
- [ ] `src/monitoring/file_metrics.py` created with all metrics
- [ ] `src/file_management/unified_manager.py` instrumented
- [ ] Metrics recorded during file operations
- [ ] Prometheus endpoint shows new metrics
- [ ] No performance degradation

✅ **Lifecycle Management:**
- [ ] `src/file_management/lifecycle_manager.py` created
- [ ] Periodic cleanup task runs successfully
- [ ] Retention policy enforced (30 days)
- [ ] Integration with graceful shutdown works
- [ ] Cleanup metrics recorded

✅ **Dead Code Removal:**
- [ ] `config/timeouts.py` deleted
- [ ] `config/migration.py` deleted
- [ ] `config/file_handling.py` deleted
- [ ] All imports updated
- [ ] No import errors after deletion

✅ **Validation:**
- [ ] Docker rebuild successful (no errors)
- [ ] EXAI Round 1 validation passed
- [ ] Docker logs collected (1000 lines)
- [ ] EXAI Round 2 validation passed
- [ ] All 3 master checklists updated
- [ ] System production-ready

---

## 11. NEXT STEPS AFTER PHASE 2

Once Phase 2 is complete and validated:

1. **Review Phase 3 (MEDIUM priority) tasks** in master checklist
2. **Consult EXAI** for Phase 3 implementation strategy
3. **Create Phase 3 handover document** (if needed)
4. **Proceed with systematic implementation**

---

## 12. APPENDIX: QUICK REFERENCE

### File Paths (Absolute)
- Handover doc: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\PHASE2_IMPLEMENTATION_PLAN__HANDOVER.md`
- Master checklist (Part 1): `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\COMPREHENSIVE_MASTER_CHECKLIST__FINAL.md`
- Master checklist (Part 2): `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\COMPREHENSIVE_MASTER_CHECKLIST__PART2.md`
- Master checklist (Part 3): `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\COMPREHENSIVE_MASTER_CHECKLIST__PART3.md`
- Completion markdown: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\HIGH_TASKS_IMPLEMENTATION_COMPLETE.md`
- Docker logs: `c:\Project\EX-AI-MCP-Server\docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt`

### Key Commands
```bash
# Docker rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
timeout /t 10 /nobreak

# Collect logs
docker logs exai-mcp-daemon --tail 1000 > docs\05_CURRENT_WORK\2025-11-02\docker_logs_high.txt

# Backup .env.docker
cp .env.docker .env.docker.backup.$(date +%Y%m%d_%H%M%S)

# Test imports
python -c "from config.base import BaseConfig; print('OK')"
python -c "from config.file_management import FileManagementConfig; print('OK')"
python -c "from src.monitoring.file_metrics import record_upload_attempt; print('OK')"
python -c "from src.file_management.lifecycle_manager import FileLifecycleManager; print('OK')"
```

### EXAI Consultation
- Continuation ID: `fa6820a0-d18b-49da-846f-ee5d5db2ae8b`
- Turns remaining: 19
- Model: `glm-4.6`
- Thinking mode: `max`
- Web search: `true`
- Tool: `chat_EXAI-WS-VSCode1`

---

---

## 13. EXAI VALIDATION FEEDBACK & CRITICAL UPDATES

**EXAI Review Date:** 2025-11-01
**EXAI Continuation ID:** fa6820a0-d18b-49da-846f-ee5d5db2ae8b (18 turns remaining)
**Overall Assessment:** 95% complete - Excellent foundation with critical clarifications needed

### 13.1 CRITICAL: Configuration Migration Mapping Table

**EXAI Identified Gap:** Specific mapping of which environment variables move where

**SOLUTION: Complete Environment Variable Migration Map**

| Environment Variable | Current Location | New Location | Keep in .env? | Notes |
|---------------------|------------------|--------------|---------------|-------|
| `GLM_API_KEY` | .env.docker | .env.docker | ✅ YES | Sensitive - API key |
| `KIMI_API_KEY` | .env.docker | .env.docker | ✅ YES | Sensitive - API key |
| `SUPABASE_URL` | .env.docker | .env.docker | ✅ YES | Sensitive - DB URL |
| `SUPABASE_KEY` | .env.docker | .env.docker | ✅ YES | Sensitive - Service role key |
| `SUPABASE_JWT_SECRET` | .env.docker | .env.docker | ✅ YES | Sensitive - JWT signing |
| `DEFAULT_MODEL` | .env.docker | config/core.py | ❌ NO | Default: "glm-4.5-flash" |
| `INTELLIGENT_ROUTING_ENABLED` | .env.docker | config/core.py | ❌ NO | Default: True |
| `ROUTER_ENABLED` | .env.docker | config/core.py | ❌ NO | Default: True |
| `MAX_CONCURRENT_REQUESTS` | .env.docker | config/operations.py | ❌ NO | Default: 10 |
| `RATE_LIMIT_PER_MINUTE` | .env.docker | config/operations.py | ❌ NO | Default: 100 |
| `REQUEST_TIMEOUT` | .env.docker | config/operations.py | ❌ NO | Default: 30 |
| `UPLOAD_TIMEOUT` | .env.docker | config/file_management.py | ❌ NO | Default: 300 |
| `MAX_FILE_SIZE` | .env.docker | config/file_management.py | ❌ NO | Default: 100MB |
| `MAX_FILE_SIZE_KIMI` | .env.docker | config/file_management.py | ❌ NO | Default: 100MB |
| `MAX_FILE_SIZE_GLM` | .env.docker | config/file_management.py | ❌ NO | Default: 20MB |
| `ALLOWED_EXTENSIONS` | .env.docker | config/file_management.py | ❌ NO | Default: txt,pdf,doc... |
| `ENABLE_DEDUPLICATION` | .env.docker | config/file_management.py | ❌ NO | Default: True |
| `FILE_RETENTION_DAYS` | .env.docker | config/file_management.py | ❌ NO | Default: 30 |
| `CLEANUP_INTERVAL_HOURS` | .env.docker | config/file_management.py | ❌ NO | Default: 24 |
| `DEFAULT_USER_QUOTA_GB` | .env.docker | config/file_management.py | ❌ NO | Default: 10 |
| `TEMPERATURE_ANALYTICAL` | .env.docker | config/core.py | ❌ NO | Default: 0.2 |
| `TEMPERATURE_BALANCED` | .env.docker | config/core.py | ❌ NO | Default: 0.5 |
| `TEMPERATURE_CREATIVE` | .env.docker | config/core.py | ❌ NO | Default: 0.7 |

**Action Required:** Use this table to systematically migrate each variable

### 13.2 CRITICAL: Database Schema Verification

**EXAI Identified Gap:** Confirmation that file_uploads table has required columns

**REQUIRED COLUMNS for Lifecycle Manager:**
```sql
-- Verify these columns exist in file_uploads table:
file_id VARCHAR PRIMARY KEY
provider VARCHAR NOT NULL
user_id VARCHAR NOT NULL
file_name VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
status VARCHAR NOT NULL  -- Must support: 'active', 'deleted', 'uploading'
deleted_at TIMESTAMP NULL
deletion_reason VARCHAR NULL
```

**Action Required:** Before implementing lifecycle manager, verify schema:
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'file_uploads';
```

If columns are missing, create migration:
```sql
-- Add missing columns if needed
ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS deletion_reason VARCHAR(50) NULL;
```

### 13.3 CRITICAL: Code Template Fixes

**Fix 1: config/base.py - Type Hint**
```python
# BEFORE (Line 31):
def get_list(cls, key: str, default: str = "", separator: str = ",") -> list:

# AFTER:
from typing import List  # Add to imports at top

def get_list(cls, key: str, default: str = "", separator: str = ",") -> List[str]:
```

**Fix 2: src/file_management/lifecycle_manager.py - Null Check**
```python
# BEFORE (Line 150):
if not result.data:

# AFTER:
if not result or not result.data:
```

**Fix 3: src/monitoring/file_metrics.py - Add Initialization**
```python
# ADD at end of file:
def init_file_metrics() -> None:
    """
    Initialize file metrics (called during server startup)
    This ensures all metrics are registered with Prometheus
    """
    logger.info("File metrics initialized")
    logger.info(f"Registered metrics: FILE_UPLOAD_ATTEMPTS, FILE_UPLOAD_BYTES, "
                f"FILE_UPLOAD_DURATION, ACTIVE_UPLOADS, DEDUPLICATION_HITS, "
                f"CIRCUIT_BREAKER_TRIPS, FILE_DELETIONS")
```

### 13.4 CRITICAL: Race Condition Prevention

**EXAI Identified Risk:** Cleanup task might delete files being actively uploaded

**SOLUTION: Enhanced Status Checking**
```python
# In lifecycle_manager.py, _cleanup_expired_files() method:
# MODIFY the query to exclude files being uploaded:

result = await self.supabase.client.table("file_uploads")\
    .select("file_id, provider, user_id, file_name")\
    .lt("created_at", cutoff_date.isoformat())\
    .eq("status", "active")\  # Only delete 'active' files
    .neq("status", "uploading")\  # CRITICAL: Never delete uploading files
    .execute()
```

### 13.5 CRITICAL: Configuration Validation

**EXAI Identified Gap:** No validation of configuration values

**SOLUTION: Add Validation Methods**
```python
# ADD to config/base.py:
@classmethod
def validate(cls) -> bool:
    """
    Validate configuration values
    Returns True if valid, raises ValueError if invalid
    """
    # Override in subclasses to add specific validation
    return True

# ADD to config/file_management.py:
@classmethod
def validate(cls) -> bool:
    """Validate file management configuration"""
    if cls.MAX_FILE_SIZE <= 0:
        raise ValueError("MAX_FILE_SIZE must be positive")
    if cls.RETENTION_DAYS < 1:
        raise ValueError("RETENTION_DAYS must be at least 1")
    if cls.CLEANUP_INTERVAL_HOURS < 1:
        raise ValueError("CLEANUP_INTERVAL_HOURS must be at least 1")
    if cls.MAX_FILE_SIZE_KIMI > 100 * 1024 * 1024:
        logger.warning("MAX_FILE_SIZE_KIMI exceeds Kimi's 100MB limit")
    if cls.MAX_FILE_SIZE_GLM > 20 * 1024 * 1024:
        logger.warning("MAX_FILE_SIZE_GLM exceeds GLM's 20MB limit")
    return True
```

### 13.6 CRITICAL: Implementation Sequence Update

**EXAI Identified Issue:** Testing happens too late

**UPDATED IMPLEMENTATION SEQUENCE:**

#### PHASE 1: Configuration Foundation (30 minutes)
1. Create `config/base.py` → **TEST IMMEDIATELY**
2. Create `config/file_management.py` → **TEST IMMEDIATELY**
3. Refactor `config/operations.py` → **TEST IMMEDIATELY**
4. Update `src/core/env_config.py` → **TEST IMMEDIATELY**
5. **CHECKPOINT:** Run all configuration tests, verify no import errors

#### PHASE 2: Monitoring Enhancement (30 minutes)
6. Create `src/monitoring/file_metrics.py` → **TEST IMMEDIATELY**
7. Add `init_file_metrics()` to server startup → **TEST IMMEDIATELY**
8. Instrument `unified_manager.py` → **TEST WITH SAMPLE UPLOAD**
9. **CHECKPOINT:** Verify metrics appear in Prometheus endpoint

#### PHASE 3: Lifecycle Management (45 minutes)
10. Verify database schema (file_uploads table)
11. Create `src/file_management/lifecycle_manager.py` → **TEST IMMEDIATELY**
12. Integrate with graceful_shutdown.py → **TEST SHUTDOWN**
13. Update server startup → **TEST LIFECYCLE START/STOP**
14. **CHECKPOINT:** Manually trigger cleanup (dry run)

#### PHASE 4: Configuration Cleanup (30 minutes)
15. Backup .env.docker
16. Reduce .env.docker using migration table
17. **TEST:** Verify all configs still load
18. Delete dead code files
19. **CHECKPOINT:** Full system test

#### PHASE 5: Docker Validation (15 minutes)
20. Docker rebuild
21. Verify container starts without errors
22. Run end-to-end tests
23. **CHECKPOINT:** All tests pass

### 13.7 CRITICAL: Additional Validation Steps

**EXAI Identified Gaps:** Missing validation steps

**ADD THESE VALIDATION STEPS:**

**Before Docker Rebuild:**
1. **Configuration Validation Test:**
   ```python
   python -c "from config.file_management import FileManagementConfig; FileManagementConfig.validate(); print('Config valid')"
   ```

2. **Metrics Endpoint Test:**
   ```bash
   curl http://localhost:8000/metrics | grep mcp_file
   # Should show all new file metrics
   ```

3. **Lifecycle Dry Run Test:**
   ```python
   # Add to lifecycle_manager.py for testing:
   async def dry_run_cleanup(self) -> Dict[str, int]:
       """Test cleanup without actually deleting files"""
       cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
       result = await self.supabase.client.table("file_uploads")\
           .select("file_id")\
           .lt("created_at", cutoff_date.isoformat())\
           .eq("status", "active")\
           .execute()
       return {"would_delete": len(result.data) if result and result.data else 0}
   ```

4. **Error Scenario Test:**
   ```python
   # Test behavior when Supabase is unavailable
   # Temporarily set invalid SUPABASE_URL and verify graceful degradation
   ```

5. **Performance Impact Test:**
   ```python
   # Measure upload latency before and after metrics instrumentation
   # Acceptable overhead: <5ms per upload
   ```

### 13.8 CRITICAL: Orphaned File Detection

**EXAI Identified Gap:** `_detect_orphaned_files()` is incomplete

**SOLUTION: Mark as Future Enhancement**

The `_detect_orphaned_files()` method in lifecycle_manager.py is intentionally incomplete because:
1. Kimi and GLM providers don't expose file listing APIs
2. Orphaned file detection requires provider-specific implementation
3. This is a MEDIUM priority enhancement, not required for Phase 2

**Action Required:**
- Keep the placeholder method
- Add TODO comment explaining limitation
- Document as future enhancement in completion markdown

```python
async def _detect_orphaned_files(self) -> int:
    """
    Detect files in providers but not in Supabase (orphaned files)

    NOTE: This is a placeholder for future enhancement.
    Current limitation: Kimi and GLM providers don't expose file listing APIs.

    Future implementation would:
    1. Query all files from each provider
    2. Compare with Supabase records
    3. Delete files not in Supabase

    Returns:
        Number of orphaned files detected (always 0 for now)
    """
    logger.debug("Orphaned file detection not yet implemented (provider API limitation)")
    return 0
```

---

**END OF HANDOVER DOCUMENT**

**Next Agent:** Read this document thoroughly, paying special attention to Section 13 (EXAI Validation Feedback). Consult EXAI to validate your understanding, then proceed with systematic implementation following the exact sequence outlined above.


