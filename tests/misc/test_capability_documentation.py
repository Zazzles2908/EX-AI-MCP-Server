"""
Test Capability Documentation Updates

Validates that capability documentation is accurate and complete.

Date: 2025-10-26
Purpose: Validate Task 1 completion documentation and EXAI usage patterns
"""

import os
import re
from pathlib import Path


def test_agent_capabilities_doc():
    """Test AGENT_CAPABILITIES.md for required content"""
    doc_path = Path("docs/AGENT_CAPABILITIES.md")
    
    if not doc_path.exists():
        print(f"❌ FAIL: {doc_path} not found")
        return False
    
    content = doc_path.read_text(encoding='utf-8')
    
    # Required sections
    required_sections = [
        "QUICK PATTERN REFERENCE",
        "File Handling Patterns",
        "EXAI TOOL USAGE PHILOSOPHY",
        "YOU Investigate First",
        "Confidence Level Progression",
        "Continuation ID Lifecycle Management",
        "TRANSPARENCY & VISIBILITY",
        "Deduplication Benefits",
        "COMMON ANTI-PATTERNS"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ FAIL: Missing sections in AGENT_CAPABILITIES.md:")
        for section in missing_sections:
            print(f"  - {section}")
        return False
    
    # Check for deduplication column in decision matrix
    if "| Deduplication |" not in content:
        print("❌ FAIL: Deduplication column missing from decision matrix")
        return False
    
    # Check for SHA256 mentions
    if "SHA256" not in content:
        print("❌ FAIL: SHA256 deduplication not documented")
        return False
    
    # Check for confidence levels
    confidence_levels = ["exploring", "low", "medium", "high", "very_high", "certain"]
    for level in confidence_levels:
        if f'"{level}"' not in content:
            print(f"❌ FAIL: Confidence level '{level}' not documented")
            return False
    
    # Check for continuation_id tracking pattern
    if "ConversationTracker" not in content:
        print("❌ FAIL: Continuation ID tracking pattern not documented")
        return False
    
    # Check for transparency metrics
    if "get_dedup_metrics" not in content:
        print("❌ FAIL: Deduplication metrics not documented")
        return False
    
    # Check for anti-patterns (case-insensitive)
    anti_patterns = [
        ("Investigation reversal", "investigation reversal"),
        ("Premature certainty", "confidence=\"certain\" prematurely"),
        ("Continuation ID misuse", "reusing continuation_id across different"),
        ("File deduplication circumvention", "manually checking for duplicates")
    ]

    for pattern_name, pattern_text in anti_patterns:
        if pattern_text.lower() not in content.lower():
            print(f"❌ FAIL: Anti-pattern '{pattern_name}' not documented")
            return False
    
    print("✅ PASS: AGENT_CAPABILITIES.md contains all required content")
    return True


def test_system_capabilities_doc():
    """Test SYSTEM_CAPABILITIES_OVERVIEW.md for required content"""
    doc_path = Path("docs/SYSTEM_CAPABILITIES_OVERVIEW.md")
    
    if not doc_path.exists():
        print(f"❌ FAIL: {doc_path} not found")
        return False
    
    content = doc_path.read_text(encoding='utf-8')
    
    # Required sections
    required_sections = [
        "FILE HANDLING - CRITICAL FOR TOKEN EFFICIENCY",
        "CONVERSATION CONTINUITY - MAINTAIN CONTEXT",
        "WORKFLOW TOOLS - STRUCTURED ANALYSIS",
        "YOU Investigate First",
        "COMMON PATTERNS & ANTI-PATTERNS"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ FAIL: Missing sections in SYSTEM_CAPABILITIES_OVERVIEW.md:")
        for section in missing_sections:
            print(f"  - {section}")
        return False
    
    # Check for deduplication column in decision matrix
    if "| Deduplication |" not in content:
        print("❌ FAIL: Deduplication column missing from decision matrix")
        return False
    
    # Check for SHA256 mentions
    if "SHA256" not in content:
        print("❌ FAIL: SHA256 deduplication not documented")
        return False
    
    # Check for deduplication benefits
    if "Deduplication Benefits" not in content:
        print("❌ FAIL: Deduplication benefits section missing")
        return False
    
    # Check for "YOU Investigate First" pattern
    if "YOU investigate first" not in content:
        print("❌ FAIL: 'YOU Investigate First' pattern not documented")
        return False
    
    # Check for updated anti-patterns
    if "Call workflow tools expecting them to investigate for you" not in content:
        print("❌ FAIL: Critical anti-pattern not documented")
        return False
    
    print("✅ PASS: SYSTEM_CAPABILITIES_OVERVIEW.md contains all required content")
    return True


def test_exai_usage_guide():
    """Test EXAI_USAGE_GUIDE_FOR_AGENTS_2025-10-26.md for required content"""
    doc_path = Path("docs/current/EXAI_USAGE_GUIDE_FOR_AGENTS_2025-10-26.md")
    
    if not doc_path.exists():
        print(f"❌ FAIL: {doc_path} not found")
        return False
    
    content = doc_path.read_text(encoding='utf-8')
    
    # Required sections
    required_sections = [
        "Core Consultation Patterns",
        "Continuation ID Management",
        "Model Selection Guidelines",
        "Web Search Usage",
        "Prompt Structuring Best Practices",
        "Multi-Step Workflow Pattern",
        "Common Pitfalls"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ FAIL: Missing sections in EXAI_USAGE_GUIDE:")
        for section in missing_sections:
            print(f"  - {section}")
        return False
    
    # Check for model selection
    if "glm-4.6" not in content or "glm-4.5-flash" not in content:
        print("❌ FAIL: Model selection not documented")
        return False
    
    # Check for continuation ID tracking
    if "Active Continuation IDs" not in content:
        print("❌ FAIL: Continuation ID tracking not documented")
        return False
    
    print("✅ PASS: EXAI_USAGE_GUIDE_FOR_AGENTS contains all required content")
    return True


def test_agent_file_upload_guide():
    """Test AGENT_FILE_UPLOAD_GUIDE.md for deduplication updates"""
    doc_path = Path("docs/current/AGENT_FILE_UPLOAD_GUIDE.md")
    
    if not doc_path.exists():
        print(f"❌ FAIL: {doc_path} not found")
        return False
    
    content = doc_path.read_text(encoding='utf-8')
    
    # Check for deduplication section
    if "File Deduplication (Production-Ready)" not in content:
        print("❌ FAIL: File Deduplication section missing")
        return False
    
    # Check for SHA256 mentions (case-insensitive)
    if "sha256" not in content.lower() and "deduplication" not in content.lower():
        print("❌ FAIL: SHA256 deduplication not documented")
        return False
    
    # Check for deduplication column in table
    if "| Deduplication |" not in content:
        print("❌ FAIL: Deduplication column missing from table")
        return False
    
    # Check for deduplication best practices
    if "Best Practices for Deduplication" not in content:
        print("❌ FAIL: Deduplication best practices missing")
        return False
    
    print("✅ PASS: AGENT_FILE_UPLOAD_GUIDE contains deduplication updates")
    return True


def main():
    """Run all documentation tests"""
    print("=" * 60)
    print("CAPABILITY DOCUMENTATION VALIDATION")
    print("=" * 60)
    print()
    
    tests = [
        ("AGENT_CAPABILITIES.md", test_agent_capabilities_doc),
        ("SYSTEM_CAPABILITIES_OVERVIEW.md", test_system_capabilities_doc),
        ("EXAI_USAGE_GUIDE_FOR_AGENTS", test_exai_usage_guide),
        ("AGENT_FILE_UPLOAD_GUIDE.md", test_agent_file_upload_guide)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        print("-" * 60)
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL DOCUMENTATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

