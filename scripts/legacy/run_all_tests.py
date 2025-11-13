#!/usr/bin/env python3
"""
Master Test Runner for EX-AI MCP Server
Supports: unit, integration, e2e, coverage, parallel execution

Usage:
    python scripts/run_all_tests.py --type all
    python scripts/run_all_tests.py --coverage
    python scripts/run_all_tests.py --parallel
    python scripts/run_all_tests.py --type unit --coverage --parallel
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Optional
import time


class TestRunner:
    """Comprehensive test runner for EX-AI MCP Server"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"

    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        print(f"\n{'='*80}")
        print(f"Running: {' '.join(cmd)}")
        print(f"{'='*80}\n")

        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=False,
            text=True,
            check=check
        )

        return result

    def run_tests(
        self,
        test_type: str = "all",
        coverage: bool = False,
        parallel: bool = False,
        output_dir: Optional[str] = None,
        verbose: bool = False,
        fail_fast: bool = False
    ) -> int:
        """
        Run tests with the specified configuration

        Args:
            test_type: Type of tests to run (unit, integration, e2e, all)
            coverage: Whether to generate coverage report
            parallel: Whether to run tests in parallel
            output_dir: Directory for test reports
            verbose: Enable verbose output
            fail_fast: Stop on first failure

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        # Build base pytest command
        cmd = ["python", "-m", "pytest"]

        # Add test paths based on type
        if test_type == "all":
            cmd.append(str(self.test_dir))
        elif test_type == "unit":
            # Run only unit tests (fast tests, not integration or e2e)
            cmd.extend([
                str(self.test_dir),
                "-m", "not integration and not e2e and not slow"
            ])
        elif test_type == "integration":
            cmd.extend([
                str(self.test_dir),
                "-m", "integration"
            ])
        elif test_type == "e2e":
            cmd.extend([
                str(self.test_dir),
                "-m", "e2e"
            ])
        else:
            print(f"❌ Unknown test type: {test_type}")
            return 1

        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=" + str(self.src_dir),
                "--cov-report=term-missing:skip-covered",
                "--cov-report=html:" + str(self.project_root / "htmlcov"),
                "--cov-report=xml:" + str(self.project_root / "coverage.xml"),
            ])

        # Add parallel execution
        if parallel:
            # Auto-detect CPU count for optimal parallelization
            cpu_count = os.cpu_count() or 1
            cmd.extend(["-n", str(cpu_count)])
            print(f"Running tests in parallel (using {cpu_count} workers)")

        # Add verbose output
        if verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")

        # Add other options
        if fail_fast:
            cmd.append("-x")
        else:
            cmd.append("--tb=short")

        # Add timeout
        cmd.append("--timeout=300")

        # Run tests
        try:
            result = self.run_command(cmd, check=False)
            return result.returncode
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            return 130
        except Exception as e:
            print(f"\nError running tests: {e}")
            return 1

    def check_coverage(self, threshold: float = 80.0) -> bool:
        """Check if coverage meets the threshold"""
        print("\n" + "="*80)
        print("Checking Coverage Threshold")
        print("="*80)

        cmd = [
            "python", "-c",
            f"""
import xml.etree.ElementTree as ET
import sys

try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    # Parse coverage percentage from XML
    for elem in root.iter():
        if 'line-rate' in elem.attrib:
            coverage_pct = float(elem.attrib['line-rate']) * 100
            print(f'Coverage: {{coverage_pct:.2f}}%')
            if coverage_pct < {threshold}:
                print(f'Coverage {{coverage_pct:.2f}}% is below threshold {threshold}%')
                sys.exit(1)
            else:
                print(f'Coverage {{coverage_pct:.2f}}% meets threshold {threshold}%')
            sys.exit(0)
    print('Could not parse coverage.xml')
    sys.exit(1)
except Exception as e:
    print(f'Error checking coverage: {{e}}')
    sys.exit(1)
"""
        ]

        result = self.run_command(cmd, check=False)
        return result.returncode == 0

    def generate_report(self, output_dir: str) -> None:
        """Generate test report"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print("\n" + "="*80)
        print(f"Generating Test Report in {output_path}")
        print("="*80)

        # Generate JUnit XML report
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "--junit-xml=" + str(output_path / "test-results.xml"),
            "--cov=" + str(self.src_dir),
            "--cov-report=xml:" + str(output_path / "coverage.xml"),
        ]

        self.run_command(cmd, check=False)

        print(f"\nReport generated in {output_path}")
        print(f"   - Test results: {output_path}/test-results.xml")
        print(f"   - Coverage report: {output_path}/coverage.xml")

    def list_tests(self, test_type: str = "all") -> None:
        """List all tests without running them"""
        print("\n" + "="*80)
        print(f"Listing {test_type} tests")
        print("="*80)

        cmd = ["python", "-m", "pytest", "--collect-only", "-q"]

        if test_type != "all":
            marker = test_type
            cmd.extend(["-m", marker])

        if test_type == "unit":
            cmd = ["python", "-m", "pytest", str(self.test_dir), "--collect-only", "-q", "-m", "not integration and not e2e and not slow"]

        self.run_command(cmd, check=True)

    def show_help(self) -> None:
        """Show detailed help"""
        help_text = """
EX-AI MCP Server Test Runner
============================

This script provides a comprehensive test runner for the EX-AI MCP Server project.

Test Types:
----------
  unit        - Run unit tests only (fast tests, marked with 'unit' or no marker)
  integration - Run integration tests (marked with 'integration')
  e2e         - Run end-to-end tests (marked with 'e2e')
  all         - Run all tests (default)

Options:
--------
  --coverage         Generate coverage report
  --parallel         Run tests in parallel (auto-detects CPU count)
  --output DIR       Generate test report in DIR
  --verbose          Enable verbose output (-vv)
  --fail-fast        Stop on first failure
  --list             List tests without running them
  --check-coverage   Check if coverage meets threshold (80%)
  --help             Show this help message

Examples:
--------
  # Run all tests
  python scripts/run_all_tests.py --type all

  # Run unit tests with coverage
  python scripts/run_all_tests.py --type unit --coverage

  # Run all tests in parallel with coverage
  python scripts/run_all_tests.py --type all --parallel --coverage

  # Run tests and check coverage threshold
  python scripts/run_all_tests.py --type all --coverage --check-coverage

  # Generate test report
  python scripts/run_all_tests.py --type all --output test-reports

  # List all tests
  python scripts/run_all_tests.py --list

  # Run tests with verbose output
  python scripts/run_all_tests.py --type all --verbose

Coverage Requirements:
---------------------
  Minimum coverage: 80%
  Coverage reports: htmlcov/index.html (HTML), coverage.xml (XML)

Parallel Execution:
------------------
  Automatically detects CPU count for optimal performance
  For manual control, use: pytest -n <count>

Exit Codes:
----------
  0 - All tests passed
  1 - Some tests failed
  130 - Interrupted by user
"""
        print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="EX-AI MCP Server Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )

    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )

    parser.add_argument(
        "--output",
        help="Output directory for reports"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List tests without running them"
    )

    parser.add_argument(
        "--check-coverage",
        action="store_true",
        help="Check if coverage meets threshold"
    )

    parser.add_argument(
        "--help-detailed",
        action="store_true",
        help="Show detailed help"
    )

    args = parser.parse_args()

    # Show detailed help
    if args.help_detailed:
        TestRunner().show_help()
        return 0

    # Create test runner
    runner = TestRunner()

    # List tests
    if args.list:
        runner.list_tests(args.type)
        return 0

    print("\n" + "="*80)
    print("EX-AI MCP Server Test Runner")
    print("="*80)
    print(f"Test type: {args.type}")
    print(f"Coverage: {args.coverage}")
    print(f"Parallel: {args.parallel}")
    print(f"Verbose: {args.verbose}")
    print("="*80 + "\n")

    # Check if src directory exists
    if not runner.src_dir.exists():
        print(f"Warning: {runner.src_dir} not found. Coverage may not work correctly.")

    # Run tests
    start_time = time.time()
    exit_code = runner.run_tests(
        test_type=args.type,
        coverage=args.coverage,
        parallel=args.parallel,
        output_dir=args.output,
        verbose=args.verbose,
        fail_fast=args.fail_fast
    )
    end_time = time.time()

    print("\n" + "="*80)
    print(f"Test execution completed in {end_time - start_time:.2f} seconds")
    print("="*80)

    # Check coverage if requested
    if args.coverage and args.check_coverage:
        print("\n")
        coverage_ok = runner.check_coverage()
        if not coverage_ok:
            print("\nCoverage check failed!")
            return 1

    # Generate report if output directory specified
    if args.output:
        runner.generate_report(args.output)

    # Summary
    if exit_code == 0:
        print("\nAll tests passed!")
    else:
        print(f"\nTests failed with exit code {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
