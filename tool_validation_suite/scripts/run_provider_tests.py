"""
Run Provider Tests - Execute provider-specific tests

This script runs provider-specific tests for:
- Kimi-specific features (file upload, multi-file chat, intent analysis, etc.)
- GLM-specific features (web search, file upload, payload preview, etc.)

Usage:
    python scripts/run_provider_tests.py [--provider kimi|glm] [--dry-run]

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
        logging.FileHandler('tool_validation_suite/results/latest/test_logs/run_provider_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_test_config():
    """Load test configuration."""
    config_file = Path("tool_validation_suite/config/test_config.json")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def build_provider_test_suite(config, provider=None):
    """Build provider-specific test suite."""
    test_suite = []
    
    providers_to_test = [provider] if provider else ["kimi", "glm"]
    
    for prov in providers_to_test:
        if prov in config["tools"]["provider"]:
            for tool in config["tools"]["provider"][prov]:
                for variation in config["variations"]:
                    test_suite.append({
                        "tool_name": tool,
                        "variation": variation,
                        "test_func": None,
                        "tool_type": "provider",
                        "provider": prov
                    })
    
    return test_suite


def progress_callback(current, total, test_config):
    """Progress callback for test execution."""
    percentage = (current / total) * 100
    
    provider = test_config.get("provider", "unknown")
    
    print(f"\n{'='*60}")
    print(f"Progress: {current}/{total} ({percentage:.1f}%)")
    print(f"Provider: {provider.upper()}")
    print(f"Current Test: {test_config['tool_name']}/{test_config['variation']}")
    print(f"{'='*60}\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run provider-specific validation tests")
    parser.add_argument("--provider", choices=["kimi", "glm"], help="Test specific provider only")
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
    provider_text = args.provider.upper() if args.provider else "ALL PROVIDERS"
    
    print("\n" + "="*60)
    print(f"  TOOL VALIDATION SUITE - {provider_text} TESTS")
    print("="*60)
    print(f"Start Time: {datetime.utcnow().isoformat()}Z")
    print(f"Provider: {provider_text}")
    print(f"Dry Run: {args.dry_run}")
    print(f"GLM Watcher: {not args.skip_watcher}")
    print(f"Max Cost: ${args.max_cost:.2f}")
    print("="*60 + "\n")
    
    # Load configuration
    logger.info("Loading test configuration...")
    config = load_test_config()
    
    # Build test suite
    logger.info(f"Building provider test suite for: {provider_text}...")
    test_suite = build_provider_test_suite(config, args.provider)
    
    total_tests = len(test_suite)
    logger.info(f"Total provider tests to run: {total_tests}")
    
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
    logger.info("Starting provider test execution...")
    
    try:
        summary = runner.run_test_suite(
            test_suite=test_suite,
            progress_callback=progress_callback
        )
        
        # Print results
        print("\n" + "="*60)
        print(f"  {provider_text} TEST EXECUTION COMPLETE")
        print("="*60)
        
        runner.print_results()
        
        # Save results
        results = runner.get_results()
        
        filename = f"{args.provider}_tests_results.json" if args.provider else "provider_tests_results.json"
        results_file = Path(f"tool_validation_suite/results/latest/{filename}")
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {results_file}")
        
        # Generate reports
        from utils import ReportGenerator
        
        logger.info("Generating reports...")
        report_gen = ReportGenerator()
        report_gen.generate_all_reports(results)
        
        print(f"\n✅ Provider tests complete!")
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

