#!/usr/bin/env python
"""
Test script to validate fixes for Critical Issues #7-10.

This script tests:
- Issue #7: Progress reporting (no misleading ETA)
- Issue #8: File embedding bloat (max file count limit)
- Issue #9: File inclusion terminology (clarified logging)
- Issue #10: Model auto-upgrade (configurable via env var)

Usage:
    python scripts/testing/test_critical_issues_7_to_10.py
"""

import os
import sys
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root

# Load environment variables
load_env()


def test_issue_7_progress_reporting():
    """Test Issue #7: Progress reporting should not show misleading ETA."""
    print("\n" + "=" * 70)
    print("TEST ISSUE #7: Progress Reporting (No Misleading ETA)")
    print("=" * 70)
    
    # Read the fixed code
    expert_analysis_file = get_repo_root() / "tools" / "workflow" / "expert_analysis.py"
    with open(expert_analysis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that misleading progress calculation is removed
    if "progress_pct = min(100, int((elapsed / timeout_secs) * 100))" in content:
        print("❌ FAILED: Old misleading progress calculation still present")
        return False
    
    # Check that new progress message exists
    if 'f"Elapsed: {elapsed:.1f}s"' in content:
        print("✅ PASSED: New progress reporting without misleading ETA found")
        return True
    else:
        print("❌ FAILED: New progress reporting not found")
        return False


def test_issue_8_file_count_limit():
    """Test Issue #8: File embedding should respect max file count limit."""
    print("\n" + "=" * 70)
    print("TEST ISSUE #8: File Embedding Bloat (Max File Count Limit)")
    print("=" * 70)
    
    # Read the fixed code
    file_embedding_file = get_repo_root() / "tools" / "workflow" / "file_embedding.py"
    with open(file_embedding_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that max file count limit is implemented
    if 'EXPERT_ANALYSIS_MAX_FILE_COUNT' not in content:
        print("❌ FAILED: EXPERT_ANALYSIS_MAX_FILE_COUNT not found in code")
        return False
    
    if 'if len(filtered_files) >= max_file_count:' not in content:
        print("❌ FAILED: File count limit check not found")
        return False
    
    # Check .env.example has the configuration
    env_example_file = get_repo_root() / ".env.example"
    with open(env_example_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if 'EXPERT_ANALYSIS_MAX_FILE_COUNT=' not in env_content:
        print("❌ FAILED: EXPERT_ANALYSIS_MAX_FILE_COUNT not in .env.example")
        return False
    
    print("✅ PASSED: File count limit implemented and documented")
    return True


def test_issue_9_file_inclusion_terminology():
    """Test Issue #9: File inclusion terminology should be clarified."""
    print("\n" + "=" * 70)
    print("TEST ISSUE #9: File Inclusion Terminology (Clarified Logging)")
    print("=" * 70)
    
    # Read the fixed code
    expert_analysis_file = get_repo_root() / "tools" / "workflow" / "expert_analysis.py"
    with open(expert_analysis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that clarified terminology exists
    if "Full file content embedding" not in content:
        print("❌ FAILED: Clarified terminology not found in code")
        return False
    
    if "File paths/names are still included in context" not in content:
        print("❌ FAILED: Clarification about paths/names not found")
        return False
    
    # Check .env.example has clarified documentation
    env_example_file = get_repo_root() / ".env.example"
    with open(env_example_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if "File paths/names are ALWAYS included" not in env_content:
        print("❌ FAILED: Clarification not in .env.example")
        return False
    
    print("✅ PASSED: File inclusion terminology clarified in code and docs")
    return True


def test_issue_10_model_auto_upgrade():
    """Test Issue #10: Model auto-upgrade should be configurable."""
    print("\n" + "=" * 70)
    print("TEST ISSUE #10: Model Auto-Upgrade (Configurable)")
    print("=" * 70)
    
    # Read the fixed code
    expert_analysis_file = get_repo_root() / "tools" / "workflow" / "expert_analysis.py"
    with open(expert_analysis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that auto-upgrade is configurable
    if 'EXPERT_ANALYSIS_AUTO_UPGRADE' not in content:
        print("❌ FAILED: EXPERT_ANALYSIS_AUTO_UPGRADE not found in code")
        return False
    
    if 'auto_upgrade_enabled' not in content:
        print("❌ FAILED: auto_upgrade_enabled variable not found")
        return False
    
    # Check that warning message exists
    if "Auto-upgrading" not in content or "This may affect cost/performance" not in content:
        print("❌ FAILED: Warning message about auto-upgrade not found")
        return False
    
    # Check .env.example has the configuration
    env_example_file = get_repo_root() / ".env.example"
    with open(env_example_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    if 'EXPERT_ANALYSIS_AUTO_UPGRADE=' not in env_content:
        print("❌ FAILED: EXPERT_ANALYSIS_AUTO_UPGRADE not in .env.example")
        return False
    
    print("✅ PASSED: Model auto-upgrade is configurable and documented")
    return True


def main():
    """Run all critical issues tests."""
    print("=" * 70)
    print("CRITICAL ISSUES #7-10 VALIDATION TEST SUITE")
    print("=" * 70)
    print(f"\nRepository root: {get_repo_root()}")
    print()
    
    results = []
    
    # Test Issue #7
    results.append(test_issue_7_progress_reporting())
    
    # Test Issue #8
    results.append(test_issue_8_file_count_limit())
    
    # Test Issue #9
    results.append(test_issue_9_file_inclusion_terminology())
    
    # Test Issue #10
    results.append(test_issue_10_model_auto_upgrade())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        print("\nAll critical issues #7-10 have been successfully fixed:")
        print("  ✅ Issue #7: Progress reporting (no misleading ETA)")
        print("  ✅ Issue #8: File embedding bloat (max file count limit)")
        print("  ✅ Issue #9: File inclusion terminology (clarified)")
        print("  ✅ Issue #10: Model auto-upgrade (configurable)")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

