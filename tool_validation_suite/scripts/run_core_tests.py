"""
Run Core Tests - Execute tests for 15 core tools only

This script runs 180 tests (15 core tools × 12 variations) with:
- Real API calls to Kimi and GLM
- GLM Watcher observations
- Cost tracking
- Performance monitoring

Core tools tested:
- chat, analyze, debug, codereview, refactor
- secaudit, planner, tracer, testgen, consensus
- thinkdeep, docgen, precommit, challenge, status

Usage:
    python scripts/run_core_tests.py [--dry-run] [--skip-watcher]

Created: 2025-10-05
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import TestRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tool_validation_suite/results/latest/test_logs/run_core_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_test_config():
    """Load test configuration."""
    config_file = Path("tool_validation_suite/config/test_config.json")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_core_test_suite(config):
    """Build core tools test suite only."""
    test_suite = []
    
    # Core tools only
    for tool in config["tools"]["core"]:
        for variation in config["variations"]:
            test_suite.append({
                "tool_name": tool,
                "variation": variation,
                "test_func": None,
                "tool_type": "simple"
            })
    
    return test_suite


def progress_callback(current, total, test_config):
    """Progress callback for test execution."""
    percentage = (current / total) * 100
    
    print(f"\n{'='*60}")
    print(f"Progress: {current}/{total} ({percentage:.1f}%)")
    print(f"Current Test: {test_config['tool_name']}/{test_config['variation']}")
    print(f"{'='*60}\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run core tool validation tests")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual API calls")
    parser.add_argument("--skip-watcher", action="store_true", help="Skip GLM Watcher observations")
    parser.add_argument("--max-cost", type=float, default=5.0, help="Maximum total cost in USD")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set environment variables
    if args.skip_watcher:
        os.environ["ENABLE_GLM_WATCHER"] = "false"
    
    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
    
    os.environ["MAX_TOTAL_COST"] = str(args.max_cost)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    print("\n" + "="*60)
    print("  TOOL VALIDATION SUITE - CORE TESTS")
    print("="*60)
    print(f"Start Time: {datetime.utcnow().isoformat()}Z")
    print(f"Dry Run: {args.dry_run}")
    print(f"GLM Watcher: {not args.skip_watcher}")
    print(f"Max Cost: ${args.max_cost:.2f}")
    print("="*60 + "\n")
    
    # Load configuration
    logger.info("Loading test configuration...")
    config = load_test_config()
    
    # Build test suite
    logger.info("Building core test suite...")
    test_suite = build_core_test_suite(config)
    
    total_tests = len(test_suite)
    logger.info(f"Total core tests to run: {total_tests}")
    
    # Confirm execution
    if not args.dry_run:
        print(f"\n⚠️  WARNING: This will execute {total_tests} real API calls!")
        print(f"Estimated cost: $1-3 USD (max: ${args.max_cost:.2f})")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    # Initialize test runner
    logger.info("Initializing test runner...")
    runner = TestRunner()
    
    # Run test suite
    logger.info("Starting core test execution...")
    
    try:
        summary = runner.run_test_suite(
            test_suite=test_suite,
            progress_callback=progress_callback
        )
        
        # Print results
        print("\n" + "="*60)
        print("  CORE TEST EXECUTION COMPLETE")
        print("="*60)
        
        runner.print_results()
        
        # Save results
        results = runner.get_results()
        
        results_file = Path("tool_validation_suite/results/latest/core_tests_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {results_file}")
        
        # Generate reports
        from utils import ReportGenerator
        
        logger.info("Generating reports...")
        report_gen = ReportGenerator()
        report_gen.generate_all_reports(results)
        
        print(f"\n✅ Core tests complete!")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Total Cost: ${results['prompt_counter']['cost_tracking']['total_cost_usd']:.4f}")
        
        # Exit code based on pass rate
        if summary['pass_rate'] >= 90:
            sys.exit(0)
        elif summary['pass_rate'] >= 70:
            sys.exit(1)
        else:
            sys.exit(2)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        logger.warning("Test execution interrupted")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

