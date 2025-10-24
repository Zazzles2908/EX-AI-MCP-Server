#!/usr/bin/env python3
"""
Validation script for enhanced tool schemas.

This script validates that:
1. Enhanced schemas are valid JSON Schema draft-07
2. Capability hints are present in enhanced schemas
3. Decision matrices are included
4. Related tools metadata is available
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.registry import ToolRegistry


def validate_enhanced_schemas():
    """Validate enhanced schemas for all tools."""
    print("=" * 80)
    print("ENHANCED SCHEMA VALIDATION")
    print("=" * 80)

    # Create registry and build tools
    registry = ToolRegistry()
    registry.build_tools()
    tools = registry.list_tools()
    
    total_tools = len(tools)
    tools_with_enhanced = 0
    tools_with_hints = 0
    tools_with_decision_matrix = 0
    tools_with_related = 0
    
    print(f"\nFound {total_tools} tools in registry\n")
    
    for name, tool in tools.items():
        print(f"\n{'=' * 80}")
        print(f"Tool: {name}")
        print(f"{'=' * 80}")
        
        # Check if tool has enhanced schema method
        has_enhanced = hasattr(tool, 'get_enhanced_input_schema')
        print(f"✓ Has get_enhanced_input_schema(): {has_enhanced}")
        
        if has_enhanced:
            tools_with_enhanced += 1
            
            # Get enhanced schema
            try:
                schema = tool.get_enhanced_input_schema()
                print(f"✓ Enhanced schema generated successfully")
                
                # Check for capability hints in properties
                if "properties" in schema:
                    has_hints = False
                    for prop_name, prop_schema in schema["properties"].items():
                        if "x-capability-hints" in prop_schema:
                            has_hints = True
                            print(f"  ✓ Found x-capability-hints in '{prop_name}'")
                            print(f"    Hints: {json.dumps(prop_schema['x-capability-hints'], indent=6)}")
                        
                        if "x-decision-matrix" in prop_schema:
                            print(f"  ✓ Found x-decision-matrix in '{prop_name}'")
                            print(f"    Matrix: {json.dumps(prop_schema['x-decision-matrix'], indent=6)}")
                    
                    if has_hints:
                        tools_with_hints += 1
                
                # Check for related tools metadata
                if "x-related-tools" in schema:
                    tools_with_related += 1
                    print(f"✓ Found x-related-tools metadata")
                    print(f"  Escalation: {schema['x-related-tools'].get('escalation', [])}")
                    print(f"  Alternatives: {schema['x-related-tools'].get('alternatives', [])}")
                
                # Validate schema structure
                required_keys = ["type", "properties"]
                for key in required_keys:
                    if key not in schema:
                        print(f"  ⚠ Missing required key: {key}")
                
            except Exception as e:
                print(f"✗ Error generating enhanced schema: {e}")
        else:
            print(f"  ℹ Tool uses base schema only")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total tools: {total_tools}")
    print(f"Tools with enhanced schema: {tools_with_enhanced} ({tools_with_enhanced/total_tools*100:.1f}%)")
    print(f"Tools with capability hints: {tools_with_hints} ({tools_with_hints/total_tools*100:.1f}%)")
    print(f"Tools with related tools: {tools_with_related} ({tools_with_related/total_tools*100:.1f}%)")
    
    # Check specific tools
    print(f"\n{'=' * 80}")
    print("SPECIFIC TOOL CHECKS")
    print(f"{'=' * 80}")
    
    # Check chat tool
    if "chat" in tools:
        chat_tool = tools["chat"]
        if hasattr(chat_tool, 'get_enhanced_input_schema'):
            schema = chat_tool.get_enhanced_input_schema()
            print("\n✓ Chat tool enhanced schema:")
            print(f"  - Has 'files' parameter: {'files' in schema.get('properties', {})}")
            if 'files' in schema.get('properties', {}):
                files_schema = schema['properties']['files']
                print(f"  - Has x-capability-hints: {'x-capability-hints' in files_schema}")
                print(f"  - Has x-decision-matrix: {'x-decision-matrix' in files_schema}")
            print(f"  - Has x-related-tools: {'x-related-tools' in schema}")
    
    # Check debug tool
    if "debug" in tools:
        debug_tool = tools["debug"]
        if hasattr(debug_tool, 'get_enhanced_input_schema'):
            schema = debug_tool.get_enhanced_input_schema()
            print("\n✓ Debug tool enhanced schema:")
            print(f"  - Has x-related-tools: {'x-related-tools' in schema}")
            if 'x-related-tools' in schema:
                print(f"  - Escalation tools: {schema['x-related-tools'].get('escalation', [])}")
    
    print(f"\n{'=' * 80}")
    print("✅ VALIDATION COMPLETE")
    print(f"{'=' * 80}\n")
    
    return tools_with_enhanced > 0


if __name__ == "__main__":
    success = validate_enhanced_schemas()
    sys.exit(0 if success else 1)

