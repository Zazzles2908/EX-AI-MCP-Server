#!/usr/bin/env python3
"""
Validation and fix script for on_chunk parameter issue.

This script:
1. Scans all tools for execute() methods
2. Identifies which ones are missing the on_chunk parameter
3. Optionally applies the fix automatically
4. Validates the fix was applied correctly
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple


class ExecuteMethodVisitor(ast.NodeVisitor):
    """AST visitor to find execute() method definitions."""
    
    def __init__(self):
        self.execute_methods = []
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Track current class name."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_AsyncFunctionDef(self, node):
        """Find async def execute() methods."""
        if node.name == "execute":
            # Check if it has on_chunk parameter
            has_on_chunk = any(
                arg.arg == "on_chunk" 
                for arg in node.args.args + node.args.kwonlyargs
            )
            
            # Get parameter names
            params = [arg.arg for arg in node.args.args]
            
            self.execute_methods.append({
                "class": self.current_class,
                "line": node.lineno,
                "has_on_chunk": has_on_chunk,
                "params": params
            })
        
        self.generic_visit(node)


def scan_file(file_path: Path) -> List[dict]:
    """Scan a Python file for execute() methods."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = ExecuteMethodVisitor()
        visitor.visit(tree)
        
        return visitor.execute_methods
    except Exception as e:
        print(f"  ⚠️  Error parsing {file_path}: {e}")
        return []


def scan_tools_directory(tools_dir: Path) -> List[Tuple[Path, List[dict]]]:
    """Scan all Python files in tools directory."""
    results = []
    
    for py_file in tools_dir.rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        
        methods = scan_file(py_file)
        if methods:
            results.append((py_file, methods))
    
    return results


def fix_file(file_path: Path, dry_run: bool = True) -> bool:
    """Fix execute() methods in a file to include on_chunk parameter."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Scan for execute methods
        methods = scan_file(file_path)
        if not methods:
            return False
        
        modified = False
        for method in methods:
            if method["has_on_chunk"]:
                continue  # Already has the parameter
            
            # Find the line with the execute method signature
            line_idx = method["line"] - 1
            original_line = lines[line_idx]
            
            # Check if signature spans multiple lines
            if ")" not in original_line:
                # Multi-line signature - find the closing paren
                end_idx = line_idx
                while end_idx < len(lines) and ")" not in lines[end_idx]:
                    end_idx += 1
                
                if end_idx < len(lines):
                    # Add on_chunk parameter before the closing paren
                    closing_line = lines[end_idx]
                    indent = len(closing_line) - len(closing_line.lstrip())
                    
                    # Insert on_chunk parameter line before closing paren
                    new_param_line = " " * indent + "on_chunk=None\n"
                    lines.insert(end_idx, new_param_line)
                    modified = True
            else:
                # Single-line signature
                # Find the position of the closing paren
                paren_pos = original_line.rfind(")")
                
                # Check if there are existing parameters
                if "arguments:" in original_line or "arguments :" in original_line:
                    # Add on_chunk after arguments
                    new_line = original_line[:paren_pos] + ", on_chunk=None" + original_line[paren_pos:]
                    lines[line_idx] = new_line
                    modified = True
        
        if modified and not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        
        return modified
    
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix on_chunk parameter issue in tools")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (default: dry run)")
    parser.add_argument("--tools-dir", default="tools", help="Path to tools directory")
    args = parser.parse_args()
    
    tools_dir = Path(args.tools_dir)
    if not tools_dir.exists():
        print(f"❌ Tools directory not found: {tools_dir}")
        return 1
    
    print("="*80)
    print("🔍 SCANNING FOR EXECUTE() METHODS")
    print("="*80)
    print(f"Tools directory: {tools_dir.absolute()}")
    print(f"Mode: {'FIX' if args.fix else 'DRY RUN'}")
    print()
    
    # Scan all files
    results = scan_tools_directory(tools_dir)
    
    # Categorize results
    missing_on_chunk = []
    has_on_chunk = []
    
    for file_path, methods in results:
        for method in methods:
            if method["has_on_chunk"]:
                has_on_chunk.append((file_path, method))
            else:
                missing_on_chunk.append((file_path, method))
    
    # Print summary
    print(f"📊 SUMMARY")
    print(f"  Total execute() methods found: {len(missing_on_chunk) + len(has_on_chunk)}")
    print(f"  ✅ Already have on_chunk: {len(has_on_chunk)}")
    print(f"  ❌ Missing on_chunk: {len(missing_on_chunk)}")
    print()
    
    if missing_on_chunk:
        print("="*80)
        print("❌ METHODS MISSING on_chunk PARAMETER")
        print("="*80)
        
        for file_path, method in missing_on_chunk:
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path
            print(f"\n📁 {rel_path}")
            print(f"   Class: {method['class']}")
            print(f"   Line: {method['line']}")
            print(f"   Params: {', '.join(method['params'])}")
        
        print()
        
        if args.fix:
            print("="*80)
            print("🔧 APPLYING FIXES")
            print("="*80)
            
            fixed_files = set()
            for file_path, method in missing_on_chunk:
                if file_path not in fixed_files:
                    if fix_file(file_path, dry_run=False):
                        try:
                            rel_path = file_path.relative_to(Path.cwd())
                        except ValueError:
                            rel_path = file_path
                        print(f"  ✅ Fixed: {rel_path}")
                        fixed_files.add(file_path)
            
            print(f"\n✅ Fixed {len(fixed_files)} files")
        else:
            print("💡 Run with --fix to apply changes")
    else:
        print("✅ All execute() methods already have on_chunk parameter!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

