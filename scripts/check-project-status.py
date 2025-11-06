#!/usr/bin/env python3
"""
Project Status Check Script
Checks current state of the EX-AI MCP Server project
Shows what cleanup is needed
"""

import os
import subprocess
from pathlib import Path


def check_root_files():
    """Check root directory for pollution"""
    print("=" * 60)
    print("ROOT DIRECTORY CHECK")
    print("=" * 60)

    root = Path.cwd()
    py_files = list(root.glob("*.py"))
    md_files = list(root.glob("*.md"))

    essential = {"README.md", "CONTRIBUTING.md", "LICENSE", "CHANGELOG.md", "CLAUDE.md"}
    non_essential_py = [f for f in py_files if f.name not in essential]
    non_essential_md = [f for f in md_files if f.name not in essential]

    print(f"\n❌ Non-essential .py files in root: {len(non_essential_py)}")
    for f in non_essential_py[:5]:
        print(f"   - {f.name}")
    if len(non_essential_py) > 5:
        print(f"   ... and {len(non_essential_py) - 5} more")

    print(f"\n❌ Non-essential .md files in root: {len(non_essential_md)}")
    for f in non_essential_md[:5]:
        print(f"   - {f.name}")
    if len(non_essential_md) > 5:
        print(f"   ... and {len(non_essential_md) - 5} more")

    if not non_essential_py and not non_essential_md:
        print("\n✅ Root directory is clean!")

    return len(non_essential_py) + len(non_essential_md)


def check_cache_files():
    """Check for Python cache files"""
    print("\n" + "=" * 60)
    print("CACHE FILES CHECK")
    print("=" * 60)

    cache_dirs = list(Path.cwd().rglob("__pycache__"))
    pyc_files = list(Path.cwd().rglob("*.pyc"))

    print(f"\n❌ __pycache__ directories found: {len(cache_dirs)}")
    for d in cache_dirs[:5]:
        print(f"   - {d}")
    if len(cache_dirs) > 5:
        print(f"   ... and {len(cache_dirs) - 5} more")

    print(f"\n❌ .pyc files found: {len(pyc_files)}")
    for f in pyc_files[:5]:
        print(f"   - {f}")
    if len(pyc_files) > 5:
        print(f"   ... and {len(pyc_files) - 5} more")

    if not cache_dirs and not pyc_files:
        print("\n✅ No cache files found!")

    return len(cache_dirs) + len(pyc_files)


def check_git_status():
    """Check git status"""
    print("\n" + "=" * 60)
    print("GIT STATUS CHECK")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        if not lines:
            print("\n✅ Working tree clean!")
            return 0

        print(f"\n❌ Untracked/modified files: {len(lines)}")
        for line in lines[:10]:
            print(f"   {line}")
        if len(lines) > 10:
            print(f"   ... and {len(lines) - 10} more")

        return len(lines)
    except Exception as e:
        print(f"\n⚠️  Could not check git status: {e}")
        return -1


def check_structure():
    """Check project structure"""
    print("\n" + "=" * 60)
    print("PROJECT STRUCTURE CHECK")
    print("=" * 60)

    checks = [
        ("src/ directory", Path("src").exists()),
        ("tests/ directory", Path("tests").exists()),
        ("docs/ directory", Path("docs").exists()),
        ("scripts/ directory", Path("scripts").exists()),
        ("tools/ directory", Path("tools").exists()),
    ]

    all_good = True
    for name, exists in checks:
        status = "✅" if exists else "❌"
        print(f"{status} {name}")
        if not exists:
            all_good = False

    if all_good:
        print("\n✅ Project structure looks good!")

    return 0 if all_good else 1


def check_agent_progress():
    """Check what other agents accomplished"""
    print("\n" + "=" * 60)
    print("AGENT PROGRESS CHECK")
    print("=" * 60)

    # Agent 1 (Performance)
    monitoring_exists = Path("src/daemon/monitoring").exists()
    if monitoring_exists:
        files = list(Path("src/daemon/monitoring").glob("*.py"))
        print(f"\n✅ Agent 1 (Performance):")
        print(f"   - monitoring/ directory exists with {len(files)} files")
        endpoint_size = 0
        if Path("src/daemon/monitoring_endpoint.py").exists():
            endpoint_size = Path("src/daemon/monitoring_endpoint.py").stat().st_size
            with open("src/daemon/monitoring_endpoint.py") as f:
                lines = len(f.readlines())
            print(f"   - monitoring_endpoint.py: {lines} lines (was 1467)")
    else:
        print(f"\n❌ Agent 1 (Performance): Not started")

    # Agent 2 (Error Handling)
    try:
        result = subprocess.run(
            ["grep", "-r", "raise Exception", "src/", "--include", "*.py"],
            capture_output=True,
            text=True
        )
        exceptions = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        if exceptions == 0:
            print(f"\n✅ Agent 2 (Error Handling): Complete")
        else:
            print(f"\n⚠️  Agent 2 (Error Handling): {exceptions} direct exceptions remain")
    except:
        print(f"\n⚠️  Agent 2 (Error Handling): Could not check")

    # Agent 3 (Testing)
    test_runner = Path("scripts/run_all_tests.py")
    if test_runner.exists():
        print(f"\n✅ Agent 3 (Testing):")
        print(f"   - Test runner created")
        tests_dir = Path("tests")
        if tests_dir.exists():
            test_files = list(tests_dir.rglob("test_*.py"))
            print(f"   - {len(test_files)} test files found")
    else:
        print(f"\n❌ Agent 3 (Testing): Not started")

    # Agent 4 (Architecture)
    singletons = Path("src/bootstrap/singletons.py")
    if singletons.exists():
        print(f"\n✅ Agent 4 (Architecture):")
        print(f"   - singletons.py created (in progress)")
    else:
        print(f"\n❌ Agent 4 (Architecture): Not started")


def check_imports():
    """Check if key modules can be imported"""
    print("\n" + "=" * 60)
    print("IMPORT CHECK")
    print("=" * 60)

    imports_to_check = [
        ("src.daemon.monitoring", "Agent 1's monitoring module"),
        ("src.daemon.error_handling", "Error handling framework"),
    ]

    for module, description in imports_to_check:
        try:
            __import__(module)
            print(f"\n✅ {description}")
        except Exception as e:
            print(f"\n❌ {description}: {e}")


def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("EX-AI MCP SERVER - PROJECT STATUS REPORT")
    print("=" * 60)
    print(f"Working Directory: {Path.cwd()}")

    issues = 0

    # Run all checks
    issues += check_root_files()
    issues += check_cache_files()
    issues += check_git_status()
    issues += check_structure()
    check_agent_progress()
    check_imports()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if issues == 0:
        print("\n✅ Project is CLEAN and PROFESSIONAL!")
    else:
        print(f"\n❌ Found {issues} issues that need cleanup")
        print("\n💡 Run Agent 5 to clean up:")
        print("   cat agent-prompts/agent-5-cleanup-professionalizer.md")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
