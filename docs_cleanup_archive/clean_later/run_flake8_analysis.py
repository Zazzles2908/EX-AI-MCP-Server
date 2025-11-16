#!/usr/bin/env python3
"""Run flake8 and analyze the output."""

import subprocess
import sys
import os

def run_flake8():
    """Run flake8 and return the results."""
    try:
        # Run flake8
        result = subprocess.run([
            sys.executable, '-m', 'flake8', 
            'src/', 'tools/',
            '--max-line-length=120',
            '--format=%(path)s:%(row)d: %(code)s %(text)s'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print("Flake8 return code:", result.returncode)
        print("\\nSTDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\\nSTDERR:")
            print(result.stderr)
        
        # Parse the output to categorize issues
        if result.stdout:
            issues = result.stdout.strip().split('\\n')
            issues = [issue for issue in issues if issue.strip()]
            
            print(f"\\n=== FLAKE8 RESULTS ===")
            print(f"Total issues found: {len(issues)}")
            
            # Categorize issues
            issue_counts = {}
            file_issues = {}
            
            for issue in issues:
                if ':' in issue:
                    parts = issue.split(':', 3)
                    if len(parts) >= 4:
                        file_path = parts[0]
                        line_num = parts[1]
                        code = parts[2].strip()
                        message = parts[3].strip()
                        
                        # Count by error code
                        issue_counts[code] = issue_counts.get(code, 0) + 1
                        
                        # Count by file
                        if file_path not in file_issues:
                            file_issues[file_path] = 0
                        file_issues[file_path] += 1
            
            print("\\nIssue breakdown by error code:")
            for code, count in sorted(issue_counts.items()):
                print(f"  {code}: {count}")
            
            print("\\nTop files with most issues:")
            for file_path, count in sorted(file_issues.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {file_path}: {count}")
            
            print("\\nSample issues:")
            for issue in issues[:20]:
                print(f"  {issue}")
            
            if len(issues) > 20:
                print(f"  ... and {len(issues) - 20} more issues")
            
            return len(issues)
        
        return 0
        
    except Exception as e:
        print(f"Error running flake8: {e}")
        return -1

if __name__ == "__main__":
    issue_count = run_flake8()
    print(f"\\n=== FINAL RESULT ===")
    if issue_count > 0:
        print(f"Found {issue_count} linting issues that should be addressed before Phase 5")
    elif issue_count == 0:
        print("No linting issues found!")
    else:
        print("Could not run linting analysis")