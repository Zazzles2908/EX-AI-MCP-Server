#!/usr/bin/env python3
"""
Test Phase 3 Task 3.2: Eliminate Hardcoded Tool Lists

Validates that tool lists are now derived dynamically from TOOL_MAP
instead of being hardcoded.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_default_lean_tools():
    """Test that DEFAULT_LEAN_TOOLS is derived from TOOL_VISIBILITY."""
    from tools.registry import DEFAULT_LEAN_TOOLS, TOOL_VISIBILITY
    
    # Should contain all 'core' tools from TOOL_VISIBILITY
    expected_core_tools = {name for name, vis in TOOL_VISIBILITY.items() if vis == "core"}
    
    print("✓ Testing DEFAULT_LEAN_TOOLS derivation...")
    print(f"  Expected core tools: {sorted(expected_core_tools)}")
    print(f"  Actual DEFAULT_LEAN_TOOLS: {sorted(DEFAULT_LEAN_TOOLS)}")
    
    assert DEFAULT_LEAN_TOOLS == expected_core_tools, \
        f"DEFAULT_LEAN_TOOLS mismatch!\nExpected: {expected_core_tools}\nActual: {DEFAULT_LEAN_TOOLS}"
    
    print(f"  ✅ DEFAULT_LEAN_TOOLS correctly derived ({len(DEFAULT_LEAN_TOOLS)} tools)")
    return True


def test_essential_tools():
    """Test that ESSENTIAL_TOOLS is derived from TOOL_MAP."""
    from src.server.tools.tool_filter import ESSENTIAL_TOOLS
    from tools.registry import TOOL_MAP
    
    print("\n✓ Testing ESSENTIAL_TOOLS derivation...")
    print(f"  Total tools in TOOL_MAP: {len(TOOL_MAP)}")
    print(f"  Essential tools derived: {len(ESSENTIAL_TOOLS)}")
    print(f"  Essential tools: {sorted(ESSENTIAL_TOOLS)}")
    
    # Verify no provider-specific tools in essential
    provider_tools = [t for t in ESSENTIAL_TOOLS if t.startswith(("kimi_", "glm_"))]
    assert not provider_tools, f"Provider tools should not be essential: {provider_tools}"
    
    # Verify no diagnostic tools in essential
    diagnostic_tools = {"self-check", "provider_capabilities", "toolcall_log_tail", "health", "status", "activity"}
    found_diagnostic = ESSENTIAL_TOOLS & diagnostic_tools
    assert not found_diagnostic, f"Diagnostic tools should not be essential: {found_diagnostic}"
    
    # Verify core workflow tools are included
    core_workflows = {"chat", "analyze", "debug", "codereview", "refactor", "planner", "thinkdeep"}
    missing_core = core_workflows - ESSENTIAL_TOOLS
    assert not missing_core, f"Core workflow tools missing from essential: {missing_core}"
    
    print(f"  ✅ ESSENTIAL_TOOLS correctly derived ({len(ESSENTIAL_TOOLS)} tools)")
    print(f"  ✅ No provider-specific tools in essential")
    print(f"  ✅ No diagnostic tools in essential")
    print(f"  ✅ All core workflow tools included")
    return True


def test_tool_registry_builds():
    """Test that ToolRegistry builds successfully with dynamic lists."""
    from tools.registry import ToolRegistry
    
    print("\n✓ Testing ToolRegistry build...")
    registry = ToolRegistry()
    registry.build_tools()
    tools = registry.list_tools()
    
    print(f"  Tools loaded: {len(tools)}")
    print(f"  Tool names: {sorted(tools.keys())}")
    
    assert len(tools) > 0, "No tools loaded!"
    assert "chat" in tools, "chat tool not loaded"
    assert "analyze" in tools, "analyze tool not loaded"
    
    print(f"  ✅ ToolRegistry built successfully ({len(tools)} tools)")
    return True


def test_no_hardcoded_lists():
    """Verify that hardcoded tool lists have been eliminated."""
    import inspect
    from tools import registry
    from src.server.tools import tool_filter
    
    print("\n✓ Checking for hardcoded tool lists...")
    
    # Check registry.py source
    registry_source = inspect.getsource(registry)
    
    # DEFAULT_LEAN_TOOLS should be a set comprehension, not hardcoded
    assert "DEFAULT_LEAN_TOOLS = {" not in registry_source or \
           "for name, vis in TOOL_VISIBILITY.items()" in registry_source, \
           "DEFAULT_LEAN_TOOLS appears to be hardcoded!"
    
    # Check tool_filter.py source
    filter_source = inspect.getsource(tool_filter)
    
    # ESSENTIAL_TOOLS should be derived from function, not hardcoded
    assert "_get_essential_tools()" in filter_source, \
           "ESSENTIAL_TOOLS should be derived from _get_essential_tools()!"
    
    print("  ✅ No hardcoded tool lists found")
    print("  ✅ DEFAULT_LEAN_TOOLS uses set comprehension")
    print("  ✅ ESSENTIAL_TOOLS uses _get_essential_tools() function")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Phase 3 Task 3.2: Eliminate Hardcoded Tool Lists - Test Suite")
    print("=" * 70)
    
    tests = [
        ("DEFAULT_LEAN_TOOLS Derivation", test_default_lean_tools),
        ("ESSENTIAL_TOOLS Derivation", test_essential_tools),
        ("ToolRegistry Build", test_tool_registry_builds),
        ("No Hardcoded Lists", test_no_hardcoded_lists),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n  ❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ All tests passed! Task 3.2 implementation successful.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

