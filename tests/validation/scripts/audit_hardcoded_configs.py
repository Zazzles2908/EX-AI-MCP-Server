"""
Configuration Audit Script

Scans the entire codebase for hardcoded timeout values, configuration constants,
and other values that should be moved to environment variables.

This script helps identify technical debt and ensures all configuration is centralized.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Patterns to search for
PATTERNS = {
    "timeout": [
        r"timeout\s*=\s*(\d+)",
        r"TIMEOUT\s*=\s*(\d+)",
        r"timeout_secs\s*=\s*(\d+)",
        r"max_wait_seconds\s*=\s*(\d+)",
        r"\.timeout\((\d+)\)",
        r"asyncio\.wait_for\([^,]+,\s*timeout\s*=\s*(\d+)",
    ],
    "size_limit": [
        r"MAX_.*_SIZE\s*=\s*(\d+)",
        r"max_size\s*=\s*(\d+)",
        r"\[:(\d{3,})\]",  # String slicing like [:1000]
        r"MAX_MSG_BYTES\s*=\s*(\d+)",
    ],
    "retry": [
        r"max_retries\s*=\s*(\d+)",
        r"MAX_RETRIES\s*=\s*(\d+)",
        r"retry_count\s*=\s*(\d+)",
    ],
    "interval": [
        r"interval\s*=\s*(\d+)",
        r"INTERVAL\s*=\s*(\d+)",
        r"sleep\((\d+)\)",
        r"asyncio\.sleep\((\d+)\)",
    ],
    "port": [
        r"port\s*=\s*(\d{4,5})",
        r"PORT\s*=\s*(\d{4,5})",
    ],
}

# Directories to scan
SCAN_DIRS = [
    "src",
    "tools",
    "tool_validation_suite/utils",
    "tool_validation_suite/scripts",
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".git",
    "node_modules",
    ".venv",
    "venv",
]


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from scan."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def scan_file(file_path: Path) -> List[Dict]:
    """Scan a single file for hardcoded configurations."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        for category, patterns in PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    # Skip if it's already using os.getenv or environment variable
                    if 'os.getenv' in line_content or 'os.environ' in line_content:
                        continue
                    
                    # Skip comments
                    if line_content.startswith('#'):
                        continue
                    
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'category': category,
                        'value': match.group(1) if match.groups() else match.group(0),
                        'context': line_content,
                    })
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return findings


def scan_directory(base_dir: str) -> List[Dict]:
    """Scan a directory recursively for hardcoded configurations."""
    all_findings = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Directory not found: {base_dir}")
        return all_findings
    
    for file_path in base_path.rglob("*.py"):
        if should_exclude(file_path):
            continue
        
        findings = scan_file(file_path)
        all_findings.extend(findings)
    
    return all_findings


def generate_report(findings: List[Dict]) -> str:
    """Generate a markdown report of findings."""
    report = ["# Configuration Audit Report", ""]
    report.append(f"**Total Findings:** {len(findings)}")
    report.append("")
    
    # Group by category
    by_category = {}
    for finding in findings:
        category = finding['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(finding)
    
    for category, items in sorted(by_category.items()):
        report.append(f"## {category.upper()} ({len(items)} findings)")
        report.append("")
        
        # Group by file
        by_file = {}
        for item in items:
            file = item['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(item)
        
        for file, file_items in sorted(by_file.items()):
            report.append(f"### {file}")
            report.append("")
            
            for item in sorted(file_items, key=lambda x: x['line']):
                report.append(f"**Line {item['line']}:** `{item['context']}`")
                report.append(f"- Value: `{item['value']}`")
                report.append("")
    
    return "\n".join(report)


def generate_env_template(findings: List[Dict]) -> str:
    """Generate environment variable template from findings."""
    template = ["# Generated Environment Variable Template", ""]
    template.append("# This file contains suggested environment variables")
    template.append("# based on hardcoded values found in the codebase.")
    template.append("")
    
    # Group by category
    by_category = {}
    for finding in findings:
        category = finding['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(finding)
    
    for category, items in sorted(by_category.items()):
        template.append(f"# {category.upper()} CONFIGURATION")
        template.append("# " + "=" * 70)
        
        # Create unique variable names
        seen = set()
        for item in items:
            # Extract variable name from context
            context = item['context']
            
            # Try to extract variable name
            var_match = re.search(r'(\w+)\s*=', context)
            if var_match:
                var_name = var_match.group(1).upper()
            else:
                var_name = f"{category.upper()}_VALUE"
            
            # Make unique
            original_name = var_name
            counter = 1
            while var_name in seen:
                var_name = f"{original_name}_{counter}"
                counter += 1
            
            seen.add(var_name)
            
            template.append(f"{var_name}={item['value']}")
            template.append(f"# Source: {item['file']}:{item['line']}")
            template.append("")
        
        template.append("")
    
    return "\n".join(template)


def main():
    """Main execution function."""
    print("=" * 80)
    print("CONFIGURATION AUDIT SCRIPT")
    print("=" * 80)
    print()
    
    all_findings = []
    
    for scan_dir in SCAN_DIRS:
        print(f"Scanning {scan_dir}...")
        findings = scan_directory(scan_dir)
        all_findings.extend(findings)
        print(f"  Found {len(findings)} hardcoded values")
    
    print()
    print(f"Total findings: {len(all_findings)}")
    print()
    
    # Generate reports
    output_dir = Path("tool_validation_suite/docs/current/audits")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Markdown report
    report_path = output_dir / "configuration_audit_report.md"
    report = generate_report(all_findings)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Report saved: {report_path}")
    
    # Environment template
    template_path = output_dir / "suggested_env_variables.env"
    template = generate_env_template(all_findings)
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"✅ Template saved: {template_path}")
    
    # JSON export
    json_path = output_dir / "configuration_audit.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, indent=2)
    print(f"✅ JSON export saved: {json_path}")
    
    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review the audit report")
    print("2. Decide which values should be environment variables")
    print("3. Update .env and .env.testing files")
    print("4. Refactor code to use os.getenv()")
    print("5. Test thoroughly")


if __name__ == "__main__":
    main()

