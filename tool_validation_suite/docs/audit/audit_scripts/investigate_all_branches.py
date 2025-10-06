#!/usr/bin/env python3
"""
PHASE 0 INVESTIGATION: Comprehensive Branch Analysis
Uses gh-mcp tools to investigate ALL branches before deletion
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

# Repository path
REPO_PATH = r"c:\Project\EX-AI-MCP-Server"

# Branches proposed for deletion
PROPOSED_DELETIONS = [
    "feature/cleanup-and-reorganization",
    "feature/exai-mcp-roadmap-implementation",
    "feature/phase-a-context-registry-fixes",
    "feature/p0-fallback-orchestrator-20250921",
    "feat/phaseA-providers-shim",
    "feat/phaseB-import-blocker-and-docs-cleanup",
    "feat/phaseB-router-unification",
    "feat/phaseD-pr1-modelrouter-observability",
    "chore/docs-sweep-and-layering",
    "chore/manager-ui-reorg-docs",
    "chore/massive-cleanup-20250928",
    "chore/mcp-chat-qa-and-textcontent-hardening",
    "chore/mcp-glm-websearch-toolcall-loop",
    "chore/registry-switch-and-docfix",
    "chore/tests-routing-continuation",
    "snapshot/all-local-changes-20250927",
    "stage1-cleanup-complete",
    "integration/pr3-pr4-combined-20250926",
    "pr-1-review",
    "glm-flash-intelligent-router",
    "feat/phaseF-shim-removal",
    "feat/docs-restore-phaseD-from-stash",
    "ci/setup-ci",
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

def compare_branch_with_main(branch: str) -> Dict[str, Any]:
    """Compare a branch with main using git commands"""
    # Get commits ahead
    ahead = run_git_command(["rev-list", "--count", f"main..{branch}"])
    
    # Get commits behind
    behind = run_git_command(["rev-list", "--count", f"{branch}..main"])
    
    # Get unique commits (not in main)
    unique_commits = run_git_command(["log", f"main..{branch}", "--oneline", "--no-merges"])
    
    # Get last commit date
    last_commit_date = run_git_command(["log", branch, "-1", "--format=%ci"])
    
    # Get last commit message
    last_commit_msg = run_git_command(["log", branch, "-1", "--format=%s"])
    
    # Check if merged
    merged_branches = run_git_command(["branch", "--merged", "main"])
    is_merged = branch in merged_branches
    
    return {
        "branch": branch,
        "ahead": int(ahead) if ahead else 0,
        "behind": int(behind) if behind else 0,
        "unique_commits": unique_commits.split("\n") if unique_commits else [],
        "unique_commit_count": len(unique_commits.split("\n")) if unique_commits else 0,
        "last_commit_date": last_commit_date,
        "last_commit_msg": last_commit_msg,
        "is_merged": is_merged,
        "safe_to_delete": (int(ahead) if ahead else 0) == 0 or is_merged
    }

def main():
    print("=" * 80)
    print("PHASE 0 INVESTIGATION: Comprehensive Branch Analysis")
    print("=" * 80)
    print()
    
    # Fetch latest from remote
    print("Fetching latest from remote...")
    run_git_command(["fetch", "origin"])
    print("✅ Fetch complete\n")
    
    results = []
    safe_to_delete = []
    requires_review = []
    
    print(f"Analyzing {len(PROPOSED_DELETIONS)} branches...\n")
    
    for branch in PROPOSED_DELETIONS:
        print(f"Analyzing: {branch}")
        result = compare_branch_with_main(branch)
        results.append(result)
        
        if result["safe_to_delete"]:
            safe_to_delete.append(branch)
            print(f"  ✅ SAFE TO DELETE - {result['ahead']} ahead, {result['behind']} behind")
        else:
            requires_review.append(branch)
            print(f"  ⚠️  REQUIRES REVIEW - {result['ahead']} unique commits")
            print(f"     Last commit: {result['last_commit_msg']}")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total branches analyzed: {len(PROPOSED_DELETIONS)}")
    print(f"✅ Safe to delete: {len(safe_to_delete)}")
    print(f"⚠️  Requires review: {len(requires_review)}")
    print()
    
    if safe_to_delete:
        print("SAFE TO DELETE:")
        for branch in safe_to_delete:
            print(f"  - {branch}")
        print()
    
    if requires_review:
        print("REQUIRES REVIEW (has unique commits):")
        for branch in requires_review:
            result = next(r for r in results if r["branch"] == branch)
            print(f"  - {branch}")
            print(f"    Unique commits: {result['unique_commit_count']}")
            print(f"    Last: {result['last_commit_msg']}")
            print()
    
    # Save detailed results
    output_file = Path(__file__).parent.parent / "audit_markdown" / "BRANCH_INVESTIGATION_RESULTS.json"
    with open(output_file, "w") as f:
        json.dump({
            "total_analyzed": len(PROPOSED_DELETIONS),
            "safe_to_delete_count": len(safe_to_delete),
            "requires_review_count": len(requires_review),
            "safe_to_delete": safe_to_delete,
            "requires_review": requires_review,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"Detailed results saved to: {output_file}")
    print()
    
    # Exit code
    if requires_review:
        print("⚠️  WARNING: Some branches require manual review before deletion")
        return 1
    else:
        print("✅ All branches are safe to delete")
        return 0

if __name__ == "__main__":
    sys.exit(main())

