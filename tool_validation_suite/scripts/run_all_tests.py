"""
Run All Tests - Execute complete test suite

This script runs all 360 tests (30 tools × 12 variations) with:
- Real API calls to Kimi and GLM
- GLM Watcher observations
- Cost tracking
- Performance monitoring
- Comprehensive reporting

Usage:
    python scripts/run_all_tests.py [--dry-run] [--skip-watcher] [--max-cost 10.0]

Created: 2025-10-05
"""

import argparse
import importlib.util
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
        logging.FileHandler('tool_validation_suite/results/latest/test_logs/run_all_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_test_config():
    """Load test configuration."""
    config_file = Path("tool_validation_suite/config/test_config.json")

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_test_function(tool_name: str, tool_type: str):
    """
    Dynamically load test function from test script.

    Args:
        tool_name: Name of the tool
        tool_type: Type of tool (core, advanced, provider, integration)

    Returns:
        Test function or None if not found
    """
    # Determine test file path
    if tool_type == "core":
        test_dir = "core_tools"
    elif tool_type == "advanced":
        test_dir = "advanced_tools"
    elif tool_type == "provider":
        test_dir = "provider_tools"
    elif tool_type == "integration":
        test_dir = "integration"
    else:
        test_dir = "core_tools"  # Default

    test_file = Path(f"tool_validation_suite/tests/{test_dir}/test_{tool_name}.py")

    if not test_file.exists():
        logger.warning(f"Test file not found: {test_file}")
        return None

    try:
        # Load module dynamically
        spec = importlib.util.spec_from_file_location(f"test_{tool_name}", test_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for test function (try multiple naming patterns)
            function_names = [
                f"test_{tool_name}_basic",
                f"test_{tool_name}",
                "test_basic",
                "run_tests"
            ]

            for func_name in function_names:
                if hasattr(module, func_name):
                    return getattr(module, func_name)

            logger.warning(f"No test function found in {test_file}")
            return None

    except Exception as e:
        logger.error(f"Failed to load test function from {test_file}: {e}")
        return None


def build_test_suite(config):
    """Build complete test suite with dynamically loaded test functions."""
    test_suite = []

    # Core tools
    logger.info("Loading core tool tests...")
    for tool in config["tools"]["core"]:
        test_func = load_test_function(tool, "core")
        if test_func:
            # Only add one test per tool (the test function handles all variations internally)
            test_suite.append({
                "tool_name": tool,
                "variation": "all",  # Test script handles all variations
                "test_func": test_func,
                "tool_type": "core"
            })
        else:
            logger.warning(f"Skipping core tool {tool} - no test function found")

    # Advanced tools
    logger.info("Loading advanced tool tests...")
    for tool in config["tools"]["advanced"]:
        test_func = load_test_function(tool, "advanced")
        if test_func:
            test_suite.append({
                "tool_name": tool,
                "variation": "all",
                "test_func": test_func,
                "tool_type": "advanced"
            })
        else:
            logger.warning(f"Skipping advanced tool {tool} - no test function found")

    # Provider tools
    logger.info("Loading provider tool tests...")
    for provider, tools in config["tools"]["provider"].items():
        for tool in tools:
            test_func = load_test_function(tool, "provider")
            if test_func:
                test_suite.append({
                    "tool_name": tool,
                    "variation": "all",
                    "test_func": test_func,
                    "tool_type": "provider",
                    "provider": provider
                })
            else:
                logger.warning(f"Skipping provider tool {tool} - no test function found")

    logger.info(f"Loaded {len(test_suite)} test scripts")
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
    parser = argparse.ArgumentParser(description="Run all validation tests")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual API calls")
    parser.add_argument("--skip-watcher", action="store_true", help="Skip GLM Watcher observations")
    parser.add_argument("--max-cost", type=float, default=10.0, help="Maximum total cost in USD")
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
    print("  TOOL VALIDATION SUITE - FULL TEST RUN")
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
    logger.info("Building test suite...")
    test_suite = build_test_suite(config)
    
    total_tests = len(test_suite)
    logger.info(f"Total tests to run: {total_tests}")
    
    # Confirm execution
    if not args.dry_run:
        print(f"\n⚠️  WARNING: This will execute {total_tests} real API calls!")
        print(f"Estimated cost: $2-5 USD (max: ${args.max_cost:.2f})")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    # Initialize test runner
    logger.info("Initializing test runner...")
    runner = TestRunner()
    
    # Run test suite
    logger.info("Starting test execution...")
    
    try:
        summary = runner.run_test_suite(
            test_suite=test_suite,
            progress_callback=progress_callback
        )
        
        # Print results
        print("\n" + "="*60)
        print("  TEST EXECUTION COMPLETE")
        print("="*60)
        
        runner.print_results()
        
        # Save final results
        results = runner.get_results()
        
        results_file = Path("tool_validation_suite/results/latest/final_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {results_file}")
        
        # Generate reports
        from utils import ReportGenerator
        
        logger.info("Generating reports...")
        report_gen = ReportGenerator()
        report_gen.generate_all_reports(results)
        
        print(f"\n✅ All tests complete!")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Total Cost: ${results['prompt_counter']['cost_tracking']['total_cost_usd']:.4f}")
        print(f"\nReports available in: tool_validation_suite/results/latest/reports/")
        
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

