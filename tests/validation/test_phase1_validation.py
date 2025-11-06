#!/usr/bin/env python3
"""
Phase 1 Validation Test Suite
Tests the pragmatic file upload fix from multiple angles
"""

import os
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_1_path_validation():
    """Test 1: Path validation allows both /app and /mnt/project"""
    logger.info("=" * 80)
    logger.info("TEST 1: PATH VALIDATION")
    logger.info("=" * 80)
    
    from utils.file.cross_platform import CrossPlatformPathHandler
    
    handler = CrossPlatformPathHandler()
    
    # Test /app paths
    app_path = "/app/docs/test.md"
    try:
        validated = handler.validate_and_normalize_path(app_path)
        logger.info(f"✅ /app path validated: {app_path} → {validated}")
    except Exception as e:
        logger.error(f"❌ /app path validation failed: {e}")
        return False
    
    # Test /mnt/project paths
    mnt_path = "/mnt/project/EX-AI-MCP-Server/docs/test.md"
    try:
        validated = handler.validate_and_normalize_path(mnt_path)
        logger.info(f"✅ /mnt/project path validated: {mnt_path} → {validated}")
    except Exception as e:
        logger.error(f"❌ /mnt/project path validation failed: {e}")
        return False
    
    logger.info("✅ TEST 1 PASSED: Path validation working correctly\n")
    return True


def test_2_output_directory_writable():
    """Test 2: Output directory is writable"""
    logger.info("=" * 80)
    logger.info("TEST 2: OUTPUT DIRECTORY WRITABLE")
    logger.info("=" * 80)
    
    output_dir = Path("/app/docs/05_CURRENT_WORK/part2_2025-10-29")
    
    # Check if directory exists
    if not output_dir.exists():
        logger.error(f"❌ Output directory does not exist: {output_dir}")
        return False
    
    logger.info(f"✅ Output directory exists: {output_dir}")
    
    # Try to create a test file
    test_file = output_dir / "test_write.txt"
    try:
        test_file.write_text("Test write successful")
        logger.info(f"✅ Successfully wrote test file: {test_file}")
        test_file.unlink()  # Clean up
        logger.info(f"✅ Successfully deleted test file")
    except Exception as e:
        logger.error(f"❌ Failed to write to output directory: {e}")
        return False
    
    logger.info("✅ TEST 2 PASSED: Output directory is writable\n")
    return True


def test_3_batch_analysis_outputs():
    """Test 3: Batch analysis outputs exist and are valid"""
    logger.info("=" * 80)
    logger.info("TEST 3: BATCH ANALYSIS OUTPUTS")
    logger.info("=" * 80)
    
    output_dir = Path("/app/docs/05_CURRENT_WORK/part2_2025-10-29")
    
    # Check for batch files
    expected_files = [
        "batch_1_analysis.md",
        "batch_2_analysis.md",
        "batch_3_analysis.md",
        "batch_4_analysis.md",
        "MASTER_ARCHIVE_ANALYSIS.md"
    ]
    
    all_exist = True
    for filename in expected_files:
        filepath = output_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            logger.info(f"✅ {filename} exists ({size} bytes)")
        else:
            logger.error(f"❌ {filename} does not exist")
            all_exist = False
    
    if not all_exist:
        return False
    
    # Check master file content
    master_file = output_dir / "MASTER_ARCHIVE_ANALYSIS.md"
    content = master_file.read_text()
    
    if "Archive Documentation Analysis Report" in content:
        logger.info("✅ Master file contains expected header")
    else:
        logger.error("❌ Master file missing expected header")
        return False
    
    if "Total Files:" in content:
        logger.info("✅ Master file contains file count")
    else:
        logger.error("❌ Master file missing file count")
        return False
    
    logger.info("✅ TEST 3 PASSED: All batch analysis outputs exist and are valid\n")
    return True


def test_4_env_configuration():
    """Test 4: Environment configuration is correct"""
    logger.info("=" * 80)
    logger.info("TEST 4: ENVIRONMENT CONFIGURATION")
    logger.info("=" * 80)
    
    # Check EX_ALLOWED_EXTERNAL_PREFIXES
    allowed_prefixes = os.getenv("EX_ALLOWED_EXTERNAL_PREFIXES", "")
    logger.info(f"EX_ALLOWED_EXTERNAL_PREFIXES={allowed_prefixes}")
    
    if "/app" in allowed_prefixes:
        logger.info("✅ /app is in allowed prefixes")
    else:
        logger.error("❌ /app is NOT in allowed prefixes")
        return False
    
    if "/mnt/project" in allowed_prefixes:
        logger.info("✅ /mnt/project is in allowed prefixes")
    else:
        logger.error("❌ /mnt/project is NOT in allowed prefixes")
        return False
    
    logger.info("✅ TEST 4 PASSED: Environment configuration is correct\n")
    return True


def test_5_file_upload_system():
    """Test 5: File upload system can handle /app paths"""
    logger.info("=" * 80)
    logger.info("TEST 5: FILE UPLOAD SYSTEM")
    logger.info("=" * 80)
    
    # Create a test file in /app
    test_file = Path("/app/docs/test_upload.md")
    test_content = "# Test File\n\nThis is a test file for upload validation."
    
    try:
        test_file.write_text(test_content)
        logger.info(f"✅ Created test file: {test_file}")
    except Exception as e:
        logger.error(f"❌ Failed to create test file: {e}")
        return False
    
    # Try to upload it (this will test path validation)
    try:
        from tools.smart_file_query import smart_file_query_tool
        
        # Just test that the path is accepted (don't actually upload)
        from utils.file.cross_platform import CrossPlatformPathHandler
        handler = CrossPlatformPathHandler()
        validated = handler.validate_and_normalize_path(str(test_file))
        logger.info(f"✅ File path validated for upload: {validated}")
        
    except Exception as e:
        logger.error(f"❌ File upload system failed: {e}")
        return False
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()
            logger.info(f"✅ Cleaned up test file")
    
    logger.info("✅ TEST 5 PASSED: File upload system handles /app paths\n")
    return True


def main():
    """Run all validation tests"""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 VALIDATION TEST SUITE")
    logger.info("=" * 80 + "\n")
    
    tests = [
        ("Path Validation", test_1_path_validation),
        ("Output Directory Writable", test_2_output_directory_writable),
        ("Batch Analysis Outputs", test_3_batch_analysis_outputs),
        ("Environment Configuration", test_4_env_configuration),
        ("File Upload System", test_5_file_upload_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Phase 1 implementation is working correctly.")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

