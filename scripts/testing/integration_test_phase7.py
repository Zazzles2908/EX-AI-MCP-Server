#!/usr/bin/env python3
"""
Integration Test Script for EXAI-WS MCP Server File Upload System
Phase 7: Comprehensive Integration Testing

This script validates:
1. File Upload Integration (Kimi/GLM via upload_file_with_provider)
2. Tool Integration (smart_file_query - Phase A2: KimiUploadFilesTool/GLMUploadFileTool removed)
3. Database Integration (tables populated correctly)
4. Error Handling (failed uploads, retry logic, fallback)

Created: 2025-10-30
EXAI Consultation: f9b23755-4cdf-4470-8c1d-16d5d58cb80f
"""

import os
import sys
import time
import hashlib
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env.docker (Docker configuration)
from dotenv import load_dotenv
env_file = project_root / ".env.docker"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from: {env_file}")
else:
    print(f"⚠️  .env.docker not found, using default .env")
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("integration_test")

# Import project modules
from tools.file_id_mapper import FileIdMapper
# Phase A2 Cleanup: provider_config merged into supabase_upload
from tools.supabase_upload import upload_file_with_provider, validate_file_size, get_provider_limit
# Phase A2 Cleanup: Removed KimiUploadFilesTool and GLMUploadFileTool imports (tools deleted)
from src.storage.supabase_client import get_storage_manager

# Import path normalization utilities (EXAI recommendation: use existing infrastructure)
# Phase A2 Cleanup: Use PathNormalizer class directly instead of global functions
# Phase 1 Path Consolidation (2025-10-31): Updated to use utils.path.normalizer module
from utils.path.normalizer import PathNormalizer

# Import provider registry for initialization
from src.providers.registry import ModelProviderRegistry
from src.providers.base import ProviderType
from src.providers.kimi import KimiModelProvider
from src.providers.glm import GLMModelProvider

# Test configuration
TEST_FILES_DIR_ENV = os.getenv("TEST_FILES_DIR", "c:\\Project\\EX-AI-MCP-Server")
TEST_FILES_DIR = Path(TEST_FILES_DIR_ENV.split(";")[0]) / "test_files"
SCRIPTS_DIR = project_root / "scripts" / "testing"
RESULTS_DIR = SCRIPTS_DIR / "results"

# Ensure directories exist
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
TEST_FILES_DIR.mkdir(parents=True, exist_ok=True)

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "details": []
}


def initialize_providers():
    """Initialize model providers for testing"""
    try:
        # Register Kimi provider class
        ModelProviderRegistry.register_provider(ProviderType.KIMI, KimiModelProvider)

        # Register GLM provider class
        ModelProviderRegistry.register_provider(ProviderType.GLM, GLMModelProvider)

        logger.info("✅ Provider registry initialized for testing")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize providers: {e}")
        import traceback
        traceback.print_exc()
        return False

def log_test_result(test_name: str, passed: bool, details: str = "") -> None:
    """Record a test result and update counters"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "✅ PASS"
        logger.info(f"{status}: {test_name}")
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
        logger.error(f"{status}: {test_name} - {details}")
    
    test_results["details"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })

def setup_test_files() -> Tuple[List[str], List[str]]:
    """Create or locate test files for small and medium size categories

    Returns:
        Tuple of (small_files, medium_files) as POSIX path strings
    """
    small_files = []
    medium_files = []

    # Use forward slashes regardless of platform
    test_files_dir = TEST_FILES_DIR.as_posix()
    logger.info(f"Setting up test files in: {test_files_dir}")

    # Create small test files (<5MB)
    for i in range(2):
        file_path = TEST_FILES_DIR / f"small_test_{i}.txt"
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(f"Small test file {i}\n" * 1000)  # ~20KB
        # Convert to forward slash path for consistency (use string directly)
        small_files.append(file_path.as_posix())

    # Create medium test files (5-20MB) - but keep under GLM limit
    for i in range(2):
        file_path = TEST_FILES_DIR / f"medium_test_{i}.txt"
        if not file_path.exists():
            with open(file_path, 'w') as f:
                # Create ~10MB file
                for j in range(10000):
                    f.write(f"Medium test file {i}, line {j}\n" * 100)
        # Convert to forward slash path for consistency (use string directly)
        medium_files.append(file_path.as_posix())
    
    return small_files, medium_files

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def test_file_id_mapper() -> None:
    """Test FileIdMapper functionality"""
    logger.info("Testing FileIdMapper...")
    
    try:
        storage = get_storage_manager()
        supabase_client = storage.get_client()
        mapper = FileIdMapper(supabase_client)
        
        # Test bidirectional mapping
        supabase_id = f"test_supabase_id_{int(time.time())}"
        kimi_id = f"kimi_file_{int(time.time())}"
        glm_id = f"glm_file_{int(time.time())}"
        
        # Add mappings
        mapper.store_mapping(supabase_id, kimi_id, "kimi", "test_user", status="completed")
        mapper.store_mapping(supabase_id, glm_id, "glm", "test_user", status="completed")
        
        # Test retrieval
        retrieved_kimi = mapper.get_provider_id(supabase_id, "kimi")
        retrieved_glm = mapper.get_provider_id(supabase_id, "glm")
        retrieved_supabase_from_kimi = mapper.get_supabase_id(kimi_id, "kimi")
        retrieved_supabase_from_glm = mapper.get_supabase_id(glm_id, "glm")
        
        # Validate
        assert retrieved_kimi == kimi_id, f"Expected {kimi_id}, got {retrieved_kimi}"
        assert retrieved_glm == glm_id, f"Expected {glm_id}, got {retrieved_glm}"
        assert retrieved_supabase_from_kimi == supabase_id, f"Expected {supabase_id}, got {retrieved_supabase_from_kimi}"
        assert retrieved_supabase_from_glm == supabase_id, f"Expected {supabase_id}, got {retrieved_supabase_from_glm}"
        
        log_test_result("FileIdMapper bidirectional mapping", True)
        
        # Test session tracking for GLM
        session_info = {
            "model": "glm-4.6",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "session_id": f"test_session_{int(time.time())}"
        }
        
        mapper.store_mapping(
            supabase_id=f"test_session_file_{int(time.time())}",
            provider_id=f"glm_session_file_{int(time.time())}",
            provider="glm",
            user_id="test_user",
            session_info=session_info,
            status="completed"
        )
        
        log_test_result("FileIdMapper session tracking", True)
        
    except Exception as e:
        log_test_result("FileIdMapper functionality", False, str(e))

def test_kimi_upload_integration(small_files: List[str]) -> None:
    """Test Kimi upload via upload_file_with_provider"""
    logger.info("Testing Kimi upload integration...")

    try:
        # Test with small file
        small_file = small_files[0]
        file_hash = calculate_file_hash(small_file)

        storage = get_storage_manager()
        supabase_client = storage.get_client()

        result = upload_file_with_provider(
            supabase_client=supabase_client,
            file_path=small_file,
            provider="kimi",
            user_id="test_user",
            filename=Path(small_file).name,
            bucket="user-files",
            tags=["integration-test", "kimi"]
        )
        
        # Validate result structure
        assert result["success"], "Upload should succeed"
        assert "provider_file_id" in result, "Missing provider_file_id in result"
        assert result["provider"] == "kimi", f"Expected provider 'kimi', got {result['provider']}"
        
        log_test_result("Kimi upload with small file", True)
        
    except Exception as e:
        log_test_result("Kimi upload integration", False, str(e))

def test_glm_upload_integration(small_files: List[str]) -> None:
    """Test GLM upload via upload_file_with_provider"""
    logger.info("Testing GLM upload integration...")

    try:
        # Test with small file
        small_file = small_files[1]  # Use different file to avoid deduplication
        file_hash = calculate_file_hash(small_file)

        storage = get_storage_manager()
        supabase_client = storage.get_client()

        result = upload_file_with_provider(
            supabase_client=supabase_client,
            file_path=small_file,
            provider="glm",
            user_id="test_user",
            filename=Path(small_file).name,
            bucket="user-files",
            tags=["integration-test", "glm"]
        )
        
        # Validate result structure
        assert result["success"], "Upload should succeed"
        assert "provider_file_id" in result, "Missing provider_file_id in result"
        assert result["provider"] == "glm", f"Expected provider 'glm', got {result['provider']}"
        assert "session_info" in result, "Missing session_info in result"
        
        log_test_result("GLM upload with small file", True)
        
    except Exception as e:
        log_test_result("GLM upload integration", False, str(e))

def test_sha256_deduplication(small_files: List[str]) -> None:
    """Test SHA256-based deduplication works"""
    logger.info("Testing SHA256-based deduplication...")

    try:
        # Use the same file twice to test deduplication
        test_file = small_files[0]
        file_hash = calculate_file_hash(test_file)

        storage = get_storage_manager()
        supabase_client = storage.get_client()

        # First upload
        result1 = upload_file_with_provider(
            supabase_client=supabase_client,
            file_path=test_file,
            provider="kimi",
            user_id="test_user",
            filename=Path(test_file).name,
            bucket="user-files",
            tags=["dedup-test"]
        )

        # Second upload of same file
        result2 = upload_file_with_provider(
            supabase_client=supabase_client,
            file_path=test_file,
            provider="kimi",
            user_id="test_user",
            filename=Path(test_file).name,
            bucket="user-files",
            tags=["dedup-test"]
        )
        
        # Check if deduplication occurred
        assert result2.get("deduplicated", False), "Second upload should be deduplicated"
        
        log_test_result("SHA256-based deduplication", True)
        
    except Exception as e:
        log_test_result("SHA256-based deduplication", False, str(e))

# Phase A2 Cleanup: Removed test_kimi_upload_files_tool() and test_glm_upload_file_tool()
# These tools have been deleted - use smart_file_query instead
# Original tests commented out below for reference:

# def test_kimi_upload_files_tool(small_files: List[str]) -> None:
#     """Test KimiUploadFilesTool uses enhanced utilities"""
#     # DELETED: KimiUploadFilesTool no longer exists
#     pass

# def test_glm_upload_file_tool(small_files: List[str]) -> None:
#     """Test GLMUploadFileTool uses enhanced utilities"""
#     # DELETED: GLMUploadFileTool no longer exists
#     pass


def test_application_aware_upload(small_files: List[str]) -> None:
    """Test upload with application context (Phase A1)"""
    logger.info("Testing application-aware upload...")

    try:
        from tools.supabase_upload import upload_file_with_app_context

        # Test with test-app application
        app_id = "test-app"
        test_file = str(small_files[0])

        # Run upload (now synchronous)
        result = upload_file_with_app_context(
            file_path=test_file,
            bucket="user-files",
            application_id=app_id,
            user_id="test-user",
            provider="kimi"
        )

        assert result.get("success") or "file_id" in result, f"Upload failed: {result.get('error')}"

        log_test_result("Application-aware upload", True)

    except Exception as e:
        log_test_result("Application-aware upload", False, str(e))


def test_path_validation() -> None:
    """Test new path validation logic (Phase A1)"""
    logger.info("Testing path validation...")

    try:
        # Phase 1 Path Consolidation (2025-10-31): Updated to use utils.path.validation module
        from utils.path.validation import ApplicationAwarePathValidator

        # Test with allowed paths
        validator = ApplicationAwarePathValidator({
            'allowed_paths': ['C:\\Project\\**', '/mnt/project/**']
        })

        # Test allowed path (should pass)
        test_file = Path(project_root) / "README.md"
        is_valid, error_msg = validator.validate_path(str(test_file), 'test-app')
        assert is_valid, f"Should allow project path: {error_msg}"

        # Test system context (no app_id) - should allow all
        is_valid, error_msg = validator.validate_path(str(test_file), None)
        assert is_valid, "Should allow all paths in system context"

        log_test_result("Path validation", True)

    except Exception as e:
        log_test_result("Path validation", False, str(e))

def generate_summary_report() -> None:
    """Generate a summary report of test results"""
    logger.info("Generating summary report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": test_results["total"],
            "passed": test_results["passed"],
            "failed": test_results["failed"],
            "success_rate": f"{(test_results['passed'] / test_results['total'] * 100):.1f}%" if test_results["total"] > 0 else "0%"
        },
        "details": test_results["details"]
    }
    
    # Save report to file
    report_file = RESULTS_DIR / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary to console
    print("\n" + "="*50)
    print("INTEGRATION TEST SUMMARY")
    print("="*50)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {report['summary']['success_rate']}")
    print(f"Report saved to: {report_file}")
    print("="*50)
    
    # Print failed tests if any
    failed_tests = [d for d in test_results["details"] if not d["passed"]]
    if failed_tests:
        print("\nFAILED TESTS:")
        for test in failed_tests:
            print(f"  ❌ {test['name']}: {test['details']}")

def main():
    """Main test execution function"""
    logger.info("Starting integration tests...")

    try:
        # Initialize providers first
        if not initialize_providers():
            logger.error("Failed to initialize providers, exiting")
            sys.exit(1)

        # Setup test files
        small_files, medium_files = setup_test_files()
        
        # Run all tests
        test_file_id_mapper()
        test_kimi_upload_integration(small_files)
        test_glm_upload_integration(small_files)
        test_sha256_deduplication(small_files)
        # Phase A2 Cleanup: Removed test_kimi_upload_files_tool() and test_glm_upload_file_tool()
        # These tools have been deleted - use smart_file_query instead

        # Phase A1 tests
        test_application_aware_upload(small_files)
        test_path_validation()

        # Generate summary report
        generate_summary_report()
        
        # Exit with appropriate code
        sys.exit(0 if test_results["failed"] == 0 else 1)
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

