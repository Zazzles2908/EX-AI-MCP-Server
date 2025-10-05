"""
Simple Test Runner - Execute all test scripts individually

This runner executes each test script as a separate process,
collecting results and generating a summary report.

Usage:
    python scripts/run_all_tests_simple.py [--dry-run] [--max-tests 10]

Created: 2025-10-05
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def find_all_test_scripts():
    """Find all test scripts in the tests directory."""
    test_dir = Path("tool_validation_suite/tests")
    test_scripts = []
    
    for category in ["core_tools", "advanced_tools", "provider_tools", "integration"]:
        category_dir = test_dir / category
        if category_dir.exists():
            for test_file in category_dir.glob("test_*.py"):
                test_scripts.append({
                    "path": test_file,
                    "category": category,
                    "name": test_file.stem
                })
    
    return test_scripts


def run_test_script(script_path: Path, dry_run: bool = False):
    """
    Run a single test script.
    
    Args:
        script_path: Path to test script
        dry_run: If True, don't actually run the script
    
    Returns:
        Result dictionary
    """
    if dry_run:
        return {
            "script": str(script_path),
            "status": "skipped",
            "duration": 0,
            "output": "Dry run - not executed"
        }
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per script
            cwd=Path.cwd()
        )
        
        duration = time.time() - start_time
        
        return {
            "script": str(script_path),
            "status": "passed" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "duration": duration,
            "output": result.stdout,
            "errors": result.stderr
        }
    
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "script": str(script_path),
            "status": "timeout",
            "duration": duration,
            "output": "",
            "errors": "Test script timed out after 300 seconds"
        }
    
    except Exception as e:
        duration = time.time() - start_time
        return {
            "script": str(script_path),
            "status": "error",
            "duration": duration,
            "output": "",
            "errors": str(e)
        }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run all validation tests (simple runner)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual execution")
    parser.add_argument("--max-tests", type=int, help="Maximum number of tests to run")
    parser.add_argument("--category", choices=["core_tools", "advanced_tools", "provider_tools", "integration"], help="Run only specific category")
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*60)
    print("  TOOL VALIDATION SUITE - SIMPLE TEST RUNNER")
    print("="*60)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Dry Run: {args.dry_run}")
    print("="*60 + "\n")
    
    # Find all test scripts
    print("Finding test scripts...")
    all_scripts = find_all_test_scripts()
    
    # Filter by category if specified
    if args.category:
        all_scripts = [s for s in all_scripts if s["category"] == args.category]
    
    # Limit number of tests if specified
    if args.max_tests:
        all_scripts = all_scripts[:args.max_tests]
    
    total_scripts = len(all_scripts)
    print(f"Found {total_scripts} test scripts\n")
    
    if total_scripts == 0:
        print("No test scripts found!")
        return 1
    
    # Confirm execution
    if not args.dry_run:
        print(f"⚠️  WARNING: This will execute {total_scripts} test scripts!")
        print(f"Each script may make multiple API calls.")
        print(f"Estimated time: {total_scripts * 2} - {total_scripts * 5} minutes")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return 0
    
    # Run all test scripts
    results = []
    passed = 0
    failed = 0
    errors = 0
    timeouts = 0
    
    for i, script_info in enumerate(all_scripts, 1):
        print(f"\n{'='*60}")
        print(f"Progress: {i}/{total_scripts} ({i/total_scripts*100:.1f}%)")
        print(f"Running: {script_info['name']} ({script_info['category']})")
        print(f"{'='*60}")
        
        result = run_test_script(script_info["path"], args.dry_run)
        results.append(result)
        
        # Update counters
        if result["status"] == "passed":
            passed += 1
            print(f"✅ PASSED ({result['duration']:.1f}s)")
        elif result["status"] == "failed":
            failed += 1
            print(f"❌ FAILED ({result['duration']:.1f}s)")
            if result.get("errors"):
                print(f"Error: {result['errors'][:200]}")
        elif result["status"] == "timeout":
            timeouts += 1
            print(f"⏱️  TIMEOUT ({result['duration']:.1f}s)")
        elif result["status"] == "error":
            errors += 1
            print(f"💥 ERROR ({result['duration']:.1f}s)")
            print(f"Error: {result['errors'][:200]}")
        elif result["status"] == "skipped":
            print(f"⏭️  SKIPPED (dry run)")
    
    # Print summary
    print("\n" + "="*60)
    print("  TEST EXECUTION COMPLETE")
    print("="*60)
    print(f"\nTotal Scripts: {total_scripts}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Timeouts: {timeouts}")
    
    if total_scripts > 0:
        pass_rate = (passed / total_scripts) * 100
        print(f"\nPass Rate: {pass_rate:.1f}%")
    
    # Save results
    results_file = Path("tool_validation_suite/results/latest/simple_runner_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_scripts": total_scripts,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "timeouts": timeouts,
            "pass_rate": pass_rate if total_scripts > 0 else 0,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")
    
    # Exit code based on pass rate
    if pass_rate >= 90:
        return 0
    elif pass_rate >= 70:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())

