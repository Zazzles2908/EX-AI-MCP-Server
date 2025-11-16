#!/usr/bin/env python3
"""Quick analysis of critical code quality issues."""

import os
import ast

def check_syntax_errors(directory):
    """Check for syntax errors in Python files."""
    issues = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Try to parse the file
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        issues.append(f"SYNTAX ERROR: {file_path}:{e.lineno}: {e.msg}")
                    except Exception as e:
                        issues.append(f"PARSE ERROR: {file_path}: {e}")
                
                except Exception as e:
                    issues.append(f"READ ERROR: {file_path}: {e}")
    
    return issues

def check_imports():
    """Check if main modules can be imported."""
    issues = []
    test_imports = [
        'src.providers.registry_core',
        'src.providers.kimi',
        'src.providers.glm',
        'tools.registry',
        'src.server'
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            issues.append(f"IMPORT OK: {module}")
        except Exception as e:
            issues.append(f"IMPORT FAIL: {module} - {e}")
    
    return issues

def check_file_sizes():
    """Check for very large files."""
    large_files = []
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if len(lines) > 500:
                            large_files.append(f"{file_path}: {len(lines)} lines")
                except:
                    pass
    
    return large_files

def main():
    print("=== Critical Code Quality Analysis ===")
    
    print("\\n1. Checking for syntax errors...")
    syntax_issues = check_syntax_errors('src') + check_syntax_errors('tools')
    print(f"Found {len(syntax_issues)} syntax issues:")
    for issue in syntax_issues[:20]:
        print(f"  {issue}")
    
    print("\\n2. Checking imports...")
    import_issues = check_imports()
    for issue in import_issues:
        print(f"  {issue}")
    
    print("\\n3. Checking file sizes...")
    large_files = check_file_sizes()
    print(f"Found {len(large_files)} very large files:")
    for file_info in large_files:
        print(f"  {file_info}")
    
    critical_issues = [i for i in syntax_issues if i.startswith('SYNTAX ERROR')]
    total_issues = len(critical_issues) + len([i for i in import_issues if i.startswith('IMPORT FAIL')])
    
    print(f"\\n=== SUMMARY ===")
    print(f"Total critical issues: {total_issues}")
    print(f"Syntax errors: {len(critical_issues)}")
    print(f"Failed imports: {len([i for i in import_issues if i.startswith('IMPORT FAIL')])}")
    print(f"Large files: {len(large_files)}")
    
    if critical_issues:
        print("\\nCRITICAL: Syntax errors must be fixed before Phase 5!")
        for issue in critical_issues:
            print(f"  CRITICAL: {issue}")
    else:
        print("\\nSUCCESS: No syntax errors found")
    
    return total_issues

if __name__ == "__main__":
    main()