"""
Server Scripts Comprehensive Audit Tool

Identifies underlying code issues that may be "crippling the whole system":
1. Dead code (unused functions, classes, imports)
2. Legacy references (old patterns, deprecated code)
3. Hardcoded values (should be in .env)
4. Silent failures (try/except pass, ignored errors)
5. Performance bottlenecks (blocking operations, inefficiencies)
6. Technical debt (code smells, complexity issues)

Based on best practices from automated code auditing research.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import subprocess

# ============================================================================
# CONFIGURATION
# ============================================================================

# Files to audit
TARGET_FILES = [
    "src/daemon/ws_server.py",
    "src/server.py",
    "src/providers/kimi_chat.py",
    "src/providers/glm_chat.py",
    "src/providers/openai_compatible.py",
]

# Legacy patterns to detect
LEGACY_PATTERNS = [
    (r'\bzen\b', "Legacy 'zen' reference (code never properly updated)", "high"),
    (r'\bold_config\b', "Deprecated config pattern", "medium"),
    (r'\bDEPRECATED\b', "Explicitly marked as deprecated", "high"),
    (r'# TODO.*remove', "TODO comment about removing code", "low"),
    (r'# FIXME', "FIXME comment indicating known issue", "medium"),
]

# Silent failure patterns
SILENT_FAILURE_PATTERNS = [
    (r'except.*:\s*pass', "Bare except with pass (silent failure)", "critical"),
    (r'except Exception:\s*pass', "Broad exception with pass", "critical"),
    (r'except.*:\s*continue', "Exception with continue (may hide errors)", "high"),
    (r'except.*:\s*return\s*None', "Exception returning None (may hide errors)", "medium"),
]

# Performance anti-patterns
PERFORMANCE_PATTERNS = [
    (r'time\.sleep\(', "Blocking sleep (may block event loop)", "medium"),
    (r'subprocess\.run\(', "Blocking subprocess call", "medium"),
    (r'requests\.get\(', "Blocking HTTP request (use async)", "high"),
    (r'\.join\(\)', "Thread join (blocking operation)", "medium"),
]

# Hardcoded value patterns (beyond what audit_hardcoded_configs.py finds)
HARDCODED_PATTERNS = [
    (r'https?://[^\s"\']+', "Hardcoded URL", "medium"),
    (r'sk-[a-zA-Z0-9]{48}', "Hardcoded API key (SECURITY RISK!)", "critical"),
    (r'/[a-z]+/[a-z]+/[a-z]+', "Hardcoded file path", "low"),
]

# Code smell patterns
CODE_SMELL_PATTERNS = [
    (r'def\s+\w+\([^)]{100,}\)', "Long parameter list (>100 chars)", "medium"),
    (r'if.*if.*if.*if.*if', "Deep nesting (5+ levels)", "high"),
    (r'class\s+\w+.*:\s*pass', "Empty class definition", "low"),
]


# ============================================================================
# AST-BASED ANALYSIS
# ============================================================================

class ASTAnalyzer(ast.NodeVisitor):
    """AST-based code analysis for deeper inspection."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues = []
        self.imports = set()
        self.defined_names = set()
        self.used_names = set()
        self.functions = []
        self.classes = []
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        self.functions.append({
            'name': node.name,
            'lineno': node.lineno,
            'args': len(node.args.args),
            'complexity': self._calculate_complexity(node),
        })
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.classes.append({
            'name': node.name,
            'lineno': node.lineno,
            'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
        })
        self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Detect try/except patterns."""
        for handler in node.handlers:
            # Check for bare except
            if handler.type is None:
                self.issues.append({
                    'type': 'silent_failure',
                    'severity': 'critical',
                    'line': handler.lineno,
                    'message': 'Bare except clause (catches all exceptions)',
                })
            
            # Check for empty except body
            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                self.issues.append({
                    'type': 'silent_failure',
                    'severity': 'critical',
                    'line': handler.lineno,
                    'message': 'Empty except with pass (silent failure)',
                })
        
        self.generic_visit(node)
    
    def _calculate_complexity(self, node):
        """Simple cyclomatic complexity calculation."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def get_unused_definitions(self) -> List[str]:
        """Find defined but unused names."""
        return list(self.defined_names - self.used_names)
    
    def get_high_complexity_functions(self, threshold=10) -> List[Dict]:
        """Find functions with high cyclomatic complexity."""
        return [f for f in self.functions if f['complexity'] > threshold]


# ============================================================================
# PATTERN-BASED ANALYSIS
# ============================================================================

def scan_file_for_patterns(file_path: Path, patterns: List[Tuple[str, str, str]]) -> List[Dict]:
    """Scan file for regex patterns."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for pattern, message, severity in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip()
                
                findings.append({
                    'file': str(file_path),
                    'line': line_num,
                    'severity': severity,
                    'message': message,
                    'context': line_content,
                    'pattern': pattern,
                })
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return findings


def analyze_file_with_ast(file_path: Path) -> Tuple[ASTAnalyzer, List[Dict]]:
    """Analyze file using AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        analyzer = ASTAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        return analyzer, analyzer.issues
    
    except SyntaxError as e:
        return None, [{
            'type': 'syntax_error',
            'severity': 'critical',
            'line': e.lineno,
            'message': f'Syntax error: {e.msg}',
        }]
    except Exception as e:
        return None, [{
            'type': 'analysis_error',
            'severity': 'error',
            'line': 0,
            'message': f'Analysis failed: {str(e)}',
        }]


# ============================================================================
# MAIN AUDIT RUNNER
# ============================================================================

def run_comprehensive_audit() -> Dict:
    """Run all audit checks and compile results."""
    print("=" * 80)
    print("SERVER SCRIPTS COMPREHENSIVE AUDIT")
    print("=" * 80)
    print()
    
    results = {
        'legacy_references': [],
        'silent_failures': [],
        'performance_issues': [],
        'hardcoded_values': [],
        'code_smells': [],
        'ast_issues': [],
        'high_complexity': [],
        'unused_definitions': [],
    }
    
    for file_path_str in TARGET_FILES:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"⚠ File not found: {file_path}")
            continue
        
        print(f"Auditing: {file_path}")
        
        # Pattern-based scans
        results['legacy_references'].extend(
            scan_file_for_patterns(file_path, LEGACY_PATTERNS)
        )
        results['silent_failures'].extend(
            scan_file_for_patterns(file_path, SILENT_FAILURE_PATTERNS)
        )
        results['performance_issues'].extend(
            scan_file_for_patterns(file_path, PERFORMANCE_PATTERNS)
        )
        results['hardcoded_values'].extend(
            scan_file_for_patterns(file_path, HARDCODED_PATTERNS)
        )
        results['code_smells'].extend(
            scan_file_for_patterns(file_path, CODE_SMELL_PATTERNS)
        )
        
        # AST-based analysis
        analyzer, ast_issues = analyze_file_with_ast(file_path)
        results['ast_issues'].extend([
            {**issue, 'file': str(file_path)} for issue in ast_issues
        ])
        
        if analyzer:
            # High complexity functions
            for func in analyzer.get_high_complexity_functions():
                results['high_complexity'].append({
                    'file': str(file_path),
                    'function': func['name'],
                    'line': func['lineno'],
                    'complexity': func['complexity'],
                    'severity': 'high' if func['complexity'] > 15 else 'medium',
                })
            
            # Unused definitions
            for name in analyzer.get_unused_definitions():
                results['unused_definitions'].append({
                    'file': str(file_path),
                    'name': name,
                    'severity': 'low',
                })
    
    return results


def generate_report(results: Dict) -> str:
    """Generate markdown report from audit results."""
    report = ["# Server Scripts Audit Report", ""]
    report.append(f"**Date:** 2025-10-07")
    report.append("")
    
    # Summary
    total_issues = sum(len(v) for v in results.values())
    report.append(f"**Total Issues Found:** {total_issues}")
    report.append("")
    
    # Critical issues first
    critical_count = sum(
        1 for category in results.values()
        for item in category
        if item.get('severity') == 'critical'
    )
    if critical_count > 0:
        report.append(f"## 🔴 CRITICAL ISSUES ({critical_count})")
        report.append("")
        
        for category, items in results.items():
            critical_items = [i for i in items if i.get('severity') == 'critical']
            if critical_items:
                report.append(f"### {category.replace('_', ' ').title()}")
                report.append("")
                for item in critical_items:
                    report.append(f"**{item.get('file', 'Unknown')}:{item.get('line', 0)}**")
                    report.append(f"- {item.get('message', 'No message')}")
                    if 'context' in item:
                        report.append(f"- Context: `{item['context']}`")
                    report.append("")
    
    # All issues by category
    for category, items in results.items():
        if items:
            report.append(f"## {category.replace('_', ' ').title()} ({len(items)} findings)")
            report.append("")
            
            # Group by file
            by_file = defaultdict(list)
            for item in items:
                by_file[item.get('file', 'Unknown')].append(item)
            
            for file, file_items in sorted(by_file.items()):
                report.append(f"### {file}")
                report.append("")
                
                for item in sorted(file_items, key=lambda x: x.get('line', 0)):
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🔵',
                    }.get(item.get('severity', 'low'), '⚪')
                    
                    report.append(f"{severity_emoji} **Line {item.get('line', 0)}:** {item.get('message', 'No message')}")
                    if 'context' in item:
                        report.append(f"   - `{item['context'][:100]}`")
                    if 'complexity' in item:
                        report.append(f"   - Complexity: {item['complexity']}")
                    report.append("")
    
    return "\n".join(report)


def main():
    """Main execution."""
    results = run_comprehensive_audit()
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    output_dir = Path("tool_validation_suite/docs/current/audits")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "server_scripts_audit.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"Report saved: {report_path}")
    print()
    
    # Print summary
    total_issues = sum(len(v) for v in results.values())
    critical_count = sum(
        1 for category in results.values()
        for item in category
        if item.get('severity') == 'critical'
    )
    
    print(f"Total issues: {total_issues}")
    print(f"Critical issues: {critical_count}")
    print()
    
    if critical_count > 0:
        print("⚠ CRITICAL ISSUES FOUND - Review immediately!")


if __name__ == "__main__":
    main()

