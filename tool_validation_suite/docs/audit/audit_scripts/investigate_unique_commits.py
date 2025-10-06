#!/usr/bin/env python3
"""
PHASE 0.2 INVESTIGATION: Detailed Analysis of Branches with Unique Commits
Examines the actual content of unique commits to determine if they're truly valuable
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

# Repository path
REPO_PATH = r"c:\Project\EX-AI-MCP-Server"

# Branches with unique commits (from Phase 0.1)
BRANCHES_TO_INVESTIGATE = [
    ("feature/p0-fallback-orchestrator-20250921", 14),
    ("chore/docs-sweep-and-layering", 13),
    ("chore/mcp-glm-websearch-toolcall-loop", 7),
    ("pr-1-review", 6),
    ("feat/phaseA-providers-shim", 5),
    ("chore/mcp-chat-qa-and-textcontent-hardening", 2),
    ("feat/docs-restore-phaseD-from-stash", 2),
    ("chore/tests-routing-continuation", 1),
    ("glm-flash-intelligent-router", 1),
    ("ci/setup-ci", 1),
]

def run_git_command(args: List[str]) -> str:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git {' '.join(args)}: {e.stderr}")
        return ""

def analyze_branch_commits(branch: str, expected_count: int) -> Dict[str, Any]:
    """Analyze unique commits in a branch"""
    # Get unique commits with details
    commits_log = run_git_command([
        "log", f"main..{branch}", 
        "--oneline", "--no-merges",
        "--format=%H|%ai|%an|%s"
    ])
    
    if not commits_log:
        return {
            "branch": branch,
            "expected_commits": expected_count,
            "actual_commits": 0,
            "commits": [],
            "analysis": "No unique commits found",
            "recommendation": "SAFE TO DELETE"
        }
    
    commits = []
    for line in commits_log.split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) == 4:
            sha, date, author, message = parts
            commits.append({
                "sha": sha[:8],
                "date": date,
                "author": author,
                "message": message
            })
    
    # Analyze commit messages for patterns
    doc_only = all("doc" in c["message"].lower() or 
                   "readme" in c["message"].lower() or
                   "comment" in c["message"].lower()
                   for c in commits)
    
    test_only = all("test" in c["message"].lower() for c in commits)
    
    cleanup_only = all(any(word in c["message"].lower() 
                          for word in ["cleanup", "remove", "delete", "prune"])
                      for c in commits)
    
    # Check if commits modify important files
    important_files = run_git_command([
        "diff", "--name-only", f"main...{branch}"
    ])
    
    has_src_changes = any(line.startswith("src/") for line in important_files.split("\n"))
    has_tool_changes = any(line.startswith("tools/") for line in important_files.split("\n"))
    has_config_changes = any(line.endswith(".json") or line.endswith(".env") 
                            for line in important_files.split("\n"))
    
    # Determine recommendation
    if doc_only:
        recommendation = "LIKELY SAFE - Documentation only"
    elif test_only:
        recommendation = "REVIEW - Test changes only"
    elif cleanup_only:
        recommendation = "LIKELY SAFE - Cleanup only"
    elif has_src_changes or has_tool_changes:
        recommendation = "REQUIRES REVIEW - Source code changes"
    elif has_config_changes:
        recommendation = "REVIEW - Configuration changes"
    else:
        recommendation = "LIKELY SAFE - No critical changes"
    
    return {
        "branch": branch,
        "expected_commits": expected_count,
        "actual_commits": len(commits),
        "commits": commits,
        "patterns": {
            "doc_only": doc_only,
            "test_only": test_only,
            "cleanup_only": cleanup_only,
            "has_src_changes": has_src_changes,
            "has_tool_changes": has_tool_changes,
            "has_config_changes": has_config_changes
        },
        "files_changed": important_files.split("\n")[:10],  # First 10 files
        "recommendation": recommendation
    }

def main():
    print("=" * 80)
    print("PHASE 0.2: Detailed Analysis of Branches with Unique Commits")
    print("=" * 80)
    print()
    
    results = []
    safe_to_delete = []
    requires_review = []
    
    for branch, expected_count in BRANCHES_TO_INVESTIGATE:
        print(f"\n{'=' * 80}")
        print(f"BRANCH: {branch}")
        print(f"Expected unique commits: {expected_count}")
        print(f"{'=' * 80}\n")
        
        result = analyze_branch_commits(branch, expected_count)
        results.append(result)
        
        print(f"Actual unique commits: {result['actual_commits']}")
        print(f"\nCommit Summary:")
        for commit in result['commits'][:5]:  # Show first 5
            print(f"  {commit['sha']} - {commit['message']}")
        if len(result['commits']) > 5:
            print(f"  ... and {len(result['commits']) - 5} more")
        
        print(f"\nPatterns:")
        print(f"  Doc only: {result['patterns']['doc_only']}")
        print(f"  Test only: {result['patterns']['test_only']}")
        print(f"  Cleanup only: {result['patterns']['cleanup_only']}")
        print(f"  Has src/ changes: {result['patterns']['has_src_changes']}")
        print(f"  Has tools/ changes: {result['patterns']['has_tool_changes']}")
        print(f"  Has config changes: {result['patterns']['has_config_changes']}")
        
        print(f"\n📋 RECOMMENDATION: {result['recommendation']}")
        
        if "SAFE" in result['recommendation']:
            safe_to_delete.append(branch)
        else:
            requires_review.append(branch)
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total branches analyzed: {len(BRANCHES_TO_INVESTIGATE)}")
    print(f"✅ Likely safe to delete: {len(safe_to_delete)}")
    print(f"⚠️  Requires manual review: {len(requires_review)}")
    print()
    
    if safe_to_delete:
        print("LIKELY SAFE TO DELETE:")
        for branch in safe_to_delete:
            result = next(r for r in results if r["branch"] == branch)
            print(f"  - {branch}")
            print(f"    Reason: {result['recommendation']}")
        print()
    
    if requires_review:
        print("REQUIRES MANUAL REVIEW:")
        for branch in requires_review:
            result = next(r for r in results if r["branch"] == branch)
            print(f"  - {branch}")
            print(f"    Reason: {result['recommendation']}")
            print(f"    Commits: {result['actual_commits']}")
        print()
    
    # Save results
    import json
    output_file = Path(__file__).parent.parent / "audit_markdown" / "UNIQUE_COMMITS_ANALYSIS.json"
    with open(output_file, "w") as f:
        json.dump({
            "total_analyzed": len(BRANCHES_TO_INVESTIGATE),
            "safe_to_delete_count": len(safe_to_delete),
            "requires_review_count": len(requires_review),
            "safe_to_delete": safe_to_delete,
            "requires_review": requires_review,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"Detailed results saved to: {output_file}")
    
    return 0 if not requires_review else 1

if __name__ == "__main__":
    sys.exit(main())

