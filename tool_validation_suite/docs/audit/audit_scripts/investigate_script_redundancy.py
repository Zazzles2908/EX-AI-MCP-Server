#!/usr/bin/env python3
"""
SCRIPT REDUNDANCY INVESTIGATION: Evidence-Based Script Analysis
Compares scripts in scripts/ with validation suite to verify actual redundancy
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import difflib

# Repository path
REPO_PATH = Path(r"c:\Project\EX-AI-MCP-Server")

# Scripts proposed for deletion with their validation suite equivalents
SCRIPT_PAIRS = [
    # GLM Web Search Tests
    ("scripts/test_glm_websearch.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    ("scripts/test_glm_websearch_detailed.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    ("scripts/test_glm_all_configs.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    ("scripts/debug_glm_websearch_response.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    ("scripts/test_web_search_fix.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    ("scripts/test_websearch_fix_final.py", "tool_validation_suite/tests/provider_tools/test_glm_web_search.py"),
    
    # Kimi/Native Web Search Tests
    ("scripts/test_native_websearch.py", "tool_validation_suite/tests/integration/test_web_search_integration.py"),
    ("scripts/test_kimi_builtin_flow.py", "tool_validation_suite/tests/provider_tools/test_kimi_upload_and_extract.py"),
    ("scripts/test_websearch_rag_failure.py", "tool_validation_suite/tests/integration/test_web_search_integration.py"),
    
    # Debug/Diagnostic Scripts
    ("scripts/debug_kimi_tool_calls.py", "scripts/diagnostics/ws_probe.py"),
    ("scripts/debug_model_response.py", "scripts/diagnostics/ws_probe.py"),
    ("scripts/tmp_registry_probe.py", "scripts/diagnostics/ws_probe.py"),
    
    # Wave/Epic Test Scripts
    ("scripts/test_wave3_complete.py", "tool_validation_suite/scripts/run_all_tests_simple.py"),
    ("scripts/test_agentic_transition.py", "tool_validation_suite/scripts/run_all_tests_simple.py"),
    
    # Documentation/Cleanup Scripts
    ("scripts/validate_docs.py", None),  # No equivalent
    ("scripts/docs_cleanup/verify_kimi_cleanup.py", None),  # No equivalent
    ("scripts/delete_all_kimi_files.py", None),  # Dangerous, should delete
    
    # Validation/Probe Scripts
    ("scripts/validate_exai_ws_kimi_tools.py", "tool_validation_suite/scripts/run_all_tests_simple.py"),
    ("scripts/probe_kimi_tooluse.py", "scripts/diagnostics/ws_probe.py"),
    
    # Diagnostic Kimi Scripts
    ("scripts/diagnostics/kimi/capture_headers_run.py", "tool_validation_suite/tests/provider_tools/test_kimi_upload_and_extract.py"),
    ("scripts/diagnostics/kimi/normalize_tester.py", "tool_validation_suite/tests/provider_tools/test_kimi_upload_and_extract.py"),
    ("scripts/check_no_legacy_imports.py", None),  # One-time check, can delete
]

def file_exists(path: Path) -> bool:
    """Check if file exists"""
    return (REPO_PATH / path).exists()

def get_file_size(path: Path) -> int:
    """Get file size in bytes"""
    try:
        return (REPO_PATH / path).stat().st_size
    except:
        return 0

def get_file_lines(path: Path) -> int:
    """Count lines in file"""
    try:
        with open(REPO_PATH / path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

def search_references(script_name: str) -> List[str]:
    """Search for references to script in codebase"""
    try:
        result = subprocess.run(
            ["git", "grep", "-l", script_name],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [line for line in result.stdout.split('\n') if line and not line.startswith('scripts/')]
        return []
    except:
        return []

def compare_functionality(script_path: Path, equivalent_path: Path) -> Dict[str, Any]:
    """Compare two scripts to assess functional overlap"""
    if not file_exists(script_path):
        return {"error": "Script does not exist"}
    
    if equivalent_path is None:
        return {
            "has_equivalent": False,
            "recommendation": "DELETE - No equivalent needed"
        }
    
    if not file_exists(equivalent_path):
        return {
            "has_equivalent": False,
            "recommendation": "KEEP - Equivalent does not exist"
        }
    
    # Read both files
    try:
        with open(REPO_PATH / script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        with open(REPO_PATH / equivalent_path, 'r', encoding='utf-8') as f:
            equiv_content = f.read()
    except Exception as e:
        return {"error": f"Failed to read files: {e}"}
    
    # Compare key characteristics
    script_has_tests = "def test_" in script_content or "class Test" in script_content
    equiv_has_tests = "def test_" in equiv_content or "class Test" in equiv_content
    
    script_has_main = "if __name__" in script_content
    equiv_has_main = "if __name__" in equiv_content
    
    # Check for unique functionality
    script_functions = set([line.strip() for line in script_content.split('\n') if line.strip().startswith('def ')])
    equiv_functions = set([line.strip() for line in equiv_content.split('\n') if line.strip().startswith('def ')])
    
    unique_to_script = script_functions - equiv_functions
    
    # Similarity ratio
    similarity = difflib.SequenceMatcher(None, script_content, equiv_content).ratio()
    
    # Determine recommendation
    if similarity > 0.8:
        recommendation = "DELETE - Very similar to equivalent"
    elif equiv_has_tests and not script_has_tests:
        recommendation = "DELETE - Equivalent has better test structure"
    elif unique_to_script:
        recommendation = "REVIEW - Has unique functions"
    else:
        recommendation = "DELETE - Functionality covered by equivalent"
    
    return {
        "has_equivalent": True,
        "similarity": round(similarity * 100, 2),
        "script_has_tests": script_has_tests,
        "equiv_has_tests": equiv_has_tests,
        "unique_functions": len(unique_to_script),
        "recommendation": recommendation
    }

def analyze_script(script_path: str, equivalent_path: str) -> Dict[str, Any]:
    """Analyze a single script for redundancy"""
    script_p = Path(script_path)
    equiv_p = Path(equivalent_path) if equivalent_path else None
    
    exists = file_exists(script_p)
    if not exists:
        return {
            "script": script_path,
            "exists": False,
            "recommendation": "ALREADY DELETED"
        }
    
    size = get_file_size(script_p)
    lines = get_file_lines(script_p)
    references = search_references(script_p.name)
    comparison = compare_functionality(script_p, equiv_p)
    
    return {
        "script": script_path,
        "equivalent": equivalent_path,
        "exists": True,
        "size_bytes": size,
        "lines": lines,
        "references": references,
        "has_references": len(references) > 0,
        "comparison": comparison,
        "recommendation": comparison.get("recommendation", "REVIEW")
    }

def main():
    print("=" * 80)
    print("SCRIPT REDUNDANCY INVESTIGATION")
    print("=" * 80)
    print()
    
    results = []
    safe_to_delete = []
    requires_review = []
    already_deleted = []
    
    for script_path, equivalent_path in SCRIPT_PAIRS:
        print(f"\nAnalyzing: {script_path}")
        result = analyze_script(script_path, equivalent_path)
        results.append(result)
        
        if not result["exists"]:
            already_deleted.append(script_path)
            print(f"  ✅ ALREADY DELETED")
            continue
        
        print(f"  Size: {result['size_bytes']} bytes, {result['lines']} lines")
        print(f"  References: {len(result['references'])}")
        
        if result["has_references"]:
            print(f"  ⚠️  Found references in:")
            for ref in result['references'][:3]:
                print(f"     - {ref}")
        
        if "comparison" in result and "similarity" in result["comparison"]:
            print(f"  Similarity: {result['comparison']['similarity']}%")
        
        print(f"  📋 {result['recommendation']}")
        
        if "DELETE" in result["recommendation"] and not result["has_references"]:
            safe_to_delete.append(script_path)
        else:
            requires_review.append(script_path)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total scripts analyzed: {len(SCRIPT_PAIRS)}")
    print(f"✅ Safe to delete: {len(safe_to_delete)}")
    print(f"⚠️  Requires review: {len(requires_review)}")
    print(f"🗑️  Already deleted: {len(already_deleted)}")
    print()
    
    if safe_to_delete:
        print("SAFE TO DELETE (no references, covered by equivalent):")
        for script in safe_to_delete:
            print(f"  - {script}")
        print()
    
    if requires_review:
        print("REQUIRES REVIEW:")
        for script in requires_review:
            result = next(r for r in results if r["script"] == script)
            print(f"  - {script}")
            if result["has_references"]:
                print(f"    Reason: Has {len(result['references'])} references")
            else:
                print(f"    Reason: {result['recommendation']}")
        print()
    
    # Save results
    import json
    output_file = REPO_PATH / "tool_validation_suite/docs/audit/audit_markdown/SCRIPT_REDUNDANCY_RESULTS.json"
    with open(output_file, "w") as f:
        json.dump({
            "total_analyzed": len(SCRIPT_PAIRS),
            "safe_to_delete_count": len(safe_to_delete),
            "requires_review_count": len(requires_review),
            "already_deleted_count": len(already_deleted),
            "safe_to_delete": safe_to_delete,
            "requires_review": requires_review,
            "already_deleted": already_deleted,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"Detailed results saved to: {output_file}")
    
    return 0 if not requires_review else 1

if __name__ == "__main__":
    sys.exit(main())

