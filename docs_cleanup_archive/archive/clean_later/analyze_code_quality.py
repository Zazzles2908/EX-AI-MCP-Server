#!/usr/bin/env python3
"""Analyze code quality issues in the EX-AI MCP Server project."""

import os
import sys
import ast
import re
from pathlib import Path

def find_python_files(root_dir):
    """Find all Python files in the project."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and other build directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def analyze_file_syntax(file_path):
    """Analyze a Python file for syntax issues."""
    issues = []
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Try to decode with different encodings
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = content.decode('cp1252', errors='replace')
            except:
                issues.append(f"Cannot decode file: {file_path}")
                return issues
        
        # Check for syntax errors
        try:
            ast.parse(text, filename=file_path)
        except SyntaxError as e:
            issues.append(f"Syntax error in {file_path}:{e.lineno}: {e.msg}")
        except IndentationError as e:
            issues.append(f"Indentation error in {file_path}:{e.lineno}: {e.msg}")
        
        # Check for basic style issues
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for very long lines
            if len(line) > 120:
                issues.append(f"Line too long in {file_path}:{i}: {len(line)} characters")
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(f"Trailing whitespace in {file_path}:{i}")
            
            # Check for tabs vs spaces (basic check)
            if '\t' in line and not line.strip().startswith('#'):
                issues.append(f"Tab character found in {file_path}:{i}")
        
        # Check for missing docstrings
        if file_path.endswith('.py') and not file_path.endswith('__init__.py'):
            if 'def ' in text and '"""' not in text and "'''" not in text:
                issues.append(f"No module docstring in {file_path}")
        
        # Check for common imports that might be missing
        missing_imports = re.findall(r'(\w+)\.openai', text)
        if missing_imports and 'openai' not in text:
            issues.append(f"Missing openai import in {file_path}")
        
    except Exception as e:
        issues.append(f"Error analyzing {file_path}: {e}")
    
    return issues

def main():
    """Main analysis function."""
    print("=== EX-AI MCP Server Code Quality Analysis ===")
    
    # Analyze src/ and tools/ directories
    directories = ['src', 'tools']
    all_issues = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\nAnalyzing {directory}/ directory...")
            python_files = find_python_files(directory)
            print(f"Found {len(python_files)} Python files")
            
            for file_path in python_files:
                issues = analyze_file_syntax(file_path)
                all_issues.extend(issues)
    
    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Total issues found: {len(all_issues)}")
    
    # Group by type
    issue_types = {}
    for issue in all_issues:
        if ':' in issue:
            issue_type = issue.split(':')[0]
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
    
    print("\nIssue breakdown by type:")
    for issue_type, count in sorted(issue_types.items()):
        print(f"  {issue_type}: {count}")
    
    # Show first 20 issues
    print(f"\nFirst 20 issues:")
    for i, issue in enumerate(all_issues[:20]):
        print(f"  {i+1}. {issue}")
    
    if len(all_issues) > 20:
        print(f"  ... and {len(all_issues) - 20} more issues")
    
    # Critical issues check
    critical_issues = [issue for issue in all_issues if 'Syntax error' in issue or 'Indentation error' in issue]
    if critical_issues:
        print(f"\n⚠️  CRITICAL: {len(critical_issues)} syntax/indentation errors found!")
        for issue in critical_issues:
            print(f"  CRITICAL: {issue}")
    else:
        print("\n✅ No critical syntax errors found!")
    
    # File-specific analysis
    files_with_issues = {}
    for issue in all_issues:
        if ':' in issue and 'in' in issue:
            file_part = issue.split('in ')[1].split(':')[0] if 'in ' in issue else 'unknown'
            if file_part not in files_with_issues:
                files_with_issues[file_part] = 0
            files_with_issues[file_part] += 1
    
    print(f"\nFiles with most issues:")
    for file_path, count in sorted(files_with_issues.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {file_path}: {count} issues")
    
    return len(all_issues)

if __name__ == "__main__":
    issue_count = main()
    sys.exit(0)