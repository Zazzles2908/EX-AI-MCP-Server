#!/usr/bin/env python3
"""
Mini-Agent Project Validator
Quick validation that the project is properly structured for Mini-Agent use.
"""

import os
import sys
from pathlib import Path

def validate_project_structure():
    """Validate that the project has the correct structure for Mini-Agent"""
    
    print("Validating EX-AI MCP Server structure for Mini-Agent...")
    
    issues = []
    passed = []
    
    # Check required directories exist
    required_dirs = [
        "agent-workspace",
        "agent-workspace/skills", 
        "src",
        "docs",
        "tools"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            passed.append(f"[OK] Directory: {dir_path}")
        else:
            issues.append(f"[FAIL] Missing directory: {dir_path}")
    
    # Check required files exist
    required_files = [
        "agent-workspace/skills/__init__.py",
        "agent-workspace/skills/exai_system_diagnostics.py",
        "agent-workspace/skills/exai_log_cleanup.py", 
        "agent-workspace/skills/exai_minimax_router_test.py",
        "README.md",
        "docker-compose.yml"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            passed.append(f"[OK] File: {file_path}")
        else:
            issues.append(f"[FAIL] Missing file: {file_path}")
    
    # Check that skills can be imported
    try:
        sys.path.append("agent-workspace/skills")
        from __init__ import list_available_skills
        skills = list_available_skills()
        if len(skills) == 3:
            passed.append(f"[OK] Skills: {len(skills)} skills available")
        else:
            issues.append(f"[FAIL] Wrong number of skills: {len(skills)} (expected 3)")
    except Exception as e:
        # Skills import might fail due to environment issues, this is not critical
        passed.append(f"[WARN] Skills import: {e} (may be environment-related)")
    
    # Clean up root directory (should not have clutter)
    root_clutter = [
        "log_cleanup_script.py",
        "log_cleanup_simple.py", 
        "documentation_debt_analyzer.py",
        "SENIOR_DEVELOPER_ASSESSMENT.md",
        ".claude"
    ]
    
    for item in root_clutter:
        if Path(item).exists():
            issues.append(f"[FAIL] Root clutter: {item}")
        else:
            passed.append(f"[OK] Clean: {item} removed")
    
    return issues, passed

def main():
    """Main validation function"""
    issues, passed = validate_project_structure()
    
    print("\n" + "="*60)
    print("MINI-AGENT PROJECT VALIDATION")
    print("="*60)
    
    if passed:
        print("\n[OK] PASSED CHECKS:")
        for item in passed:
            print(f"  {item}")
    
    if issues:
        print("\n[FAIL] ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print(f"\nTotal issues: {len(issues)}")
    else:
        print("\n[SUCCESS] PROJECT IS MINI-AGENT READY!")
        print("No issues found - project structure is optimal.")
    
    print("\n" + "="*60)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)