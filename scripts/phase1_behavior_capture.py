"""
Phase 1: Workflow Tool Behavior Capture Script
Date: 2025-11-03
Purpose: Systematically document runtime behavior of all 12 workflow tools

This script:
1. Analyzes code structure for each tool
2. Captures schema generation patterns
3. Documents validation approaches
4. Generates structured markdown report

EXAI Consultation ID: 2dd7180e-a64a-45da-9bda-8afb1f78319a
"""

import json
import inspect
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.registry import TOOL_MAP


def analyze_tool_structure(tool_name: str) -> Dict[str, Any]:
    """Analyze a single tool's structure and behavior patterns."""
    
    try:
        # Get tool class from registry
        module_path, class_name = TOOL_MAP.get(tool_name, (None, None))
        if not module_path:
            return {"error": f"Tool {tool_name} not found in registry"}
        
        # Import the tool class
        module = __import__(module_path, fromlist=[class_name])
        tool_class = getattr(module, class_name)
        
        # Instantiate tool
        tool_instance = tool_class()
        
        # Capture key information
        analysis = {
            "tool_name": tool_name,
            "class_name": class_name,
            "module_path": module_path,
            "inheritance_chain": [c.__name__ for c in inspect.getmro(tool_class)],
            "has_expert_analysis": hasattr(tool_instance, 'should_call_expert_analysis'),
            "has_validation_method": hasattr(tool_instance, 'get_first_step_required_fields'),
            "schema": None,
            "validation_fields": None,
            "tool_specific_fields": None,
        }
        
        # Get schema
        try:
            schema = tool_instance.get_input_schema()
            analysis["schema"] = {
                "required_fields": schema.get("required", []),
                "properties": list(schema.get("properties", {}).keys()),
                "has_step_specific_validation": False,  # Will check this
            }
        except Exception as e:
            analysis["schema"] = {"error": str(e)}
        
        # Check for validation method
        if analysis["has_validation_method"]:
            try:
                validation_fields = tool_instance.get_first_step_required_fields()
                analysis["validation_fields"] = validation_fields
            except Exception as e:
                analysis["validation_fields"] = {"error": str(e)}
        
        # Get tool-specific fields
        if hasattr(tool_instance, 'get_tool_fields'):
            try:
                tool_fields = tool_instance.get_tool_fields()
                analysis["tool_specific_fields"] = list(tool_fields.keys()) if tool_fields else []
            except Exception as e:
                analysis["tool_specific_fields"] = {"error": str(e)}
        
        # Determine tool category
        if "planner" in tool_name.lower() or "tracer" in tool_name.lower():
            analysis["category"] = "structure_only"
            analysis["category_description"] = "No AI expert validation - just structures work"
        elif "consensus" in tool_name.lower():
            analysis["category"] = "multi_model"
            analysis["category_description"] = "Multi-model consultation"
        elif analysis["has_expert_analysis"]:
            analysis["category"] = "investigation_plus_validation"
            analysis["category_description"] = "Investigation + expert validation"
        else:
            analysis["category"] = "unknown"
            analysis["category_description"] = "Category unclear"
        
        return analysis
        
    except Exception as e:
        return {
            "tool_name": tool_name,
            "error": str(e),
            "error_type": type(e).__name__
        }


def generate_markdown_report(all_analyses: Dict[str, Dict[str, Any]]) -> str:
    """Generate comprehensive markdown report from analyses."""
    
    report = f"""# Phase 1: Workflow Tool Behavior Analysis
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Purpose:** Document runtime behavior of all 12 workflow tools  
**EXAI Consultation:** GLM-4.6 (ID: 2dd7180e-a64a-45da-9bda-8afb1f78319a)

---

## 🎯 EXECUTIVE SUMMARY

This report documents the actual runtime behavior of all workflow tools by analyzing:
1. Code structure and inheritance
2. Schema generation patterns
3. Validation approaches
4. Tool categorization

---

## 📊 TOOL CATEGORIZATION

"""
    
    # Group tools by category
    categories = {
        "investigation_plus_validation": [],
        "structure_only": [],
        "multi_model": [],
        "unknown": []
    }
    
    for tool_name, analysis in all_analyses.items():
        if "error" not in analysis:
            category = analysis.get("category", "unknown")
            categories[category].append(tool_name)
    
    report += f"""### Investigation + Expert Validation ({len(categories['investigation_plus_validation'])} tools)
Tools that guide investigation and call expert models for validation:
{chr(10).join(f'- `{tool}`' for tool in sorted(categories['investigation_plus_validation']))}

### Structure Only ({len(categories['structure_only'])} tools)
Tools that structure work without expert validation:
{chr(10).join(f'- `{tool}`' for tool in sorted(categories['structure_only']))}

### Multi-Model ({len(categories['multi_model'])} tools)
Tools that consult multiple models:
{chr(10).join(f'- `{tool}`' for tool in sorted(categories['multi_model']))}

---

## 🔍 DETAILED ANALYSIS

"""
    
    # Add detailed analysis for each tool
    for tool_name in sorted(all_analyses.keys()):
        analysis = all_analyses[tool_name]
        
        report += f"""### Tool: `{tool_name}`

"""
        
        if "error" in analysis:
            report += f"""**Status:** ❌ ERROR  
**Error:** {analysis['error']}  
**Error Type:** {analysis.get('error_type', 'Unknown')}

"""
            continue
        
        report += f"""**Category:** {analysis['category_description']}  
**Class:** `{analysis['class_name']}`  
**Module:** `{analysis['module_path']}`

**Inheritance Chain:**
{chr(10).join(f'- {cls}' for cls in analysis['inheritance_chain'][:5])}

**Capabilities:**
- Has Expert Analysis: {'✅' if analysis['has_expert_analysis'] else '❌'}
- Has Validation Method: {'✅' if analysis['has_validation_method'] else '❌'}

"""
        
        # Schema information
        if analysis['schema'] and 'error' not in analysis['schema']:
            schema = analysis['schema']
            report += f"""**Schema:**
- Required Fields: {', '.join(f'`{f}`' for f in schema['required_fields'][:5])}
- Total Properties: {len(schema['properties'])}

"""
        
        # Validation fields
        if analysis['validation_fields']:
            if isinstance(analysis['validation_fields'], list):
                report += f"""**Step 1 Validation Fields:**
{chr(10).join(f'- `{field}`' for field in analysis['validation_fields'])}

"""
        
        # Tool-specific fields
        if analysis['tool_specific_fields'] and isinstance(analysis['tool_specific_fields'], list):
            report += f"""**Tool-Specific Fields:**
{chr(10).join(f'- `{field}`' for field in analysis['tool_specific_fields'])}

"""
        
        report += "---\n\n"
    
    return report


def main():
    """Main execution function."""
    
    print("🔍 Phase 1: Workflow Tool Behavior Capture")
    print("=" * 60)
    
    # List of workflow tools to analyze
    workflow_tools = [
        "debug", "analyze", "codereview", "testgen", "secaudit", "refactor",
        "thinkdeep", "planner", "tracer", "consensus", "precommit", "docgen"
    ]
    
    print(f"\n📋 Analyzing {len(workflow_tools)} workflow tools...")
    
    all_analyses = {}
    
    for tool_name in workflow_tools:
        print(f"  - Analyzing {tool_name}...", end=" ")
        analysis = analyze_tool_structure(tool_name)
        all_analyses[tool_name] = analysis
        
        if "error" in analysis:
            print(f"❌ ERROR: {analysis['error']}")
        else:
            print(f"✅ {analysis['category']}")
    
    print("\n📝 Generating markdown report...")
    
    # Generate markdown report
    report = generate_markdown_report(all_analyses)
    
    # Save report
    output_dir = project_root / "docs" / "05_CURRENT_WORK" / "2025-11-03" / "REVISION_02"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "PHASE1_BEHAVIOR_ANALYSIS__2025-11-03.md"
    output_file.write_text(report, encoding="utf-8")
    
    print(f"✅ Report saved to: {output_file}")
    
    # Also save JSON for programmatic access
    json_file = output_dir / "PHASE1_BEHAVIOR_ANALYSIS__2025-11-03.json"
    json_file.write_text(json.dumps(all_analyses, indent=2), encoding="utf-8")
    
    print(f"✅ JSON data saved to: {json_file}")
    
    print("\n🎉 Phase 1 behavior capture complete!")
    print(f"\n📊 Summary:")
    print(f"  - Tools analyzed: {len(workflow_tools)}")
    print(f"  - Successful: {sum(1 for a in all_analyses.values() if 'error' not in a)}")
    print(f"  - Errors: {sum(1 for a in all_analyses.values() if 'error' in a)}")


if __name__ == "__main__":
    main()

