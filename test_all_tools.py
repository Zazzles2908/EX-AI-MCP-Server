#!/usr/bin/env python3
"""
Comprehensive MCP Tools Test Suite
Tests all major MCP tools systematically to ensure functionality.
"""

import sys
import os
import traceback
from typing import Dict, List, Any

def test_import_tools(tool_category: str, tool_files: List[str]) -> Dict[str, Any]:
    """Test importing tools from a category."""
    results = {
        "category": tool_category,
        "total": len(tool_files),
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    for tool_file in tool_files:
        try:
            # Determine module path
            if "/" in tool_file:
                module_path = tool_file.replace("/", ".").replace(".py", "")
            else:
                module_path = tool_file.replace(".py", "")
            
            full_module = f"tools.{module_path}"
            
            # Try to import
            __import__(full_module)
            print(f"  OK {tool_file}")
            results["passed"] += 1
            
        except Exception as e:
            error_msg = f"{tool_file}: {str(e)}"
            print(f"  FAIL {tool_file}: {e}")
            results["errors"].append(error_msg)
            results["failed"] += 1
    
    return results

def run_comprehensive_tests():
    """Run comprehensive tests on all MCP tools."""
    
    print("=" * 80)
    print("EX-AI MCP SERVER - COMPREHENSIVE TOOL TESTING")
    print("=" * 80)
    
    # Test 1: Provider Registry (already tested)
    print("\n[1] PROVIDER REGISTRY TEST")
    print("-" * 40)
    try:
        from src.providers import ModelProviderRegistry
        from src.providers.kimi import KimiProvider
        from src.providers.glm import GLMModelProvider
        print("SUCCESS: Provider registry imports OK")
        print("SUCCESS: KimiProvider class imported OK")
        print("SUCCESS: GLMProvider class imported OK")
    except Exception as e:
        print(f"ERROR: Provider registry failed: {e}")
        return False
    
    # Test 2: Core Tools
    print("\n[2] CORE TOOLS TEST")
    print("-" * 40)
    core_tools = [
        "activity",
        "challenge", 
        "chat",
        "file_id_mapper",
        "file_upload_optimizer",
        "mini_agent_validator",
        "models",
        "registry",
        "selfcheck",
        "smart_file_download",
        "smart_file_query",
        "supabase_download",
        "supabase_upload",
        "temp_file_handler",
        "version"
    ]
    core_results = test_import_tools("Core", core_tools)
    
    # Test 3: Workflow Tools (the 5 main ones)
    print("\n[3] WORKFLOW TOOLS TEST")
    print("-" * 40)
    workflow_tools = [
        "workflows/analyze",
        "workflows/codereview", 
        "workflows/debug",
        "workflows/docgen",
        "workflows/refactor"
    ]
    workflow_results = test_import_tools("Workflow", workflow_tools)
    
    # Test 4: Additional Workflow Tools
    print("\n[4] ADDITIONAL WORKFLOW TOOLS TEST")
    print("-" * 40)
    additional_workflow = [
        "workflows/consensus",
        "workflows/precommit",
        "workflows/secaudit", 
        "workflows/testgen",
        "workflows/thinkdeep",
        "workflows/planner",
        "workflows/tracer"
    ]
    additional_results = test_import_tools("Additional Workflow", additional_workflow)
    
    # Test 5: Provider-Specific Tools
    print("\n[5] PROVIDER-SPECIFIC TOOLS TEST")
    print("-" * 40)
    provider_tools = [
        "providers/glm/glm_files_cleanup",
        "providers/glm/glm_payload_preview", 
        "providers/glm/glm_web_search",
        "providers/kimi/kimi_capture_headers",
        "providers/kimi/kimi_files",
        "providers/kimi/kimi_files_cleanup",
        "providers/kimi/kimi_intent",
        "providers/kimi/kimi_tools_chat"
    ]
    provider_results = test_import_tools("Provider", provider_tools)
    
    # Test 6: Shared/Base Classes
    print("\n[6] SHARED/BASE CLASSES TEST")
    print("-" * 40)
    shared_tools = [
        "shared/base_models",
        "shared/base_tool",
        "shared/base_tool_core",
        "shared/base_tool_file_handling",
        "shared/base_tool_model_management",
        "shared/base_tool_response",
        "shared/error_envelope",
        "shared/schema_builders",
        "shared/schema_enhancer"
    ]
    shared_results = test_import_tools("Shared", shared_tools)
    
    # Test 7: Simple Tools
    print("\n[7] SIMPLE TOOLS TEST")
    print("-" * 40)
    simple_tools = [
        "simple/base",
        "simple/simple_tool_execution",
        "simple/simple_tool_helpers",
        "simple/test_echo"
    ]
    simple_results = test_import_tools("Simple", simple_tools)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_results = [
        ("Core", core_results),
        ("Workflow", workflow_results),
        ("Additional Workflow", additional_results),
        ("Provider", provider_results),
        ("Shared", shared_results),
        ("Simple", simple_results)
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category, results in all_results:
        total = results["total"]
        passed = results["passed"]
        failed = results["failed"]
        total_passed += passed
        total_failed += failed
        
        print(f"{category:25} {passed:3}/{total:3} passed ({failed:3} failed)")
        
        if results["errors"]:
            print(f"  Errors in {category}:")
            for error in results["errors"][:5]:  # Show first 5 errors
                print(f"    - {error}")
            if len(results["errors"]) > 5:
                print(f"    ... and {len(results["errors"]) - 5} more")
    
    print("\n" + "=" * 80)
    overall_total = total_passed + total_failed
    print(f"OVERALL: {total_passed}/{overall_total} tests passed ({total_failed} failed)")
    
    success_rate = (total_passed / overall_total * 100) if overall_total > 0 else 0
    print(f"SUCCESS RATE: {success_rate:.1f}%")
    
    if total_failed == 0:
        print("\nALL TESTS PASSED!")
        return True
    else:
        print(f"\n{total_failed} tests failed")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)