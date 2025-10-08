"""
Unit Test Runner for EX-AI-MCP-Server

This script runs all unit tests for core provider functionality.
These tests do NOT require API keys or network access.

Usage:
    python tests/unit/run_unit_tests.py
    python tests/unit/run_unit_tests.py --verbose
    python tests/unit/run_unit_tests.py --test glm
    python tests/unit/run_unit_tests.py --test kimi
    python tests/unit/run_unit_tests.py --test timeout
"""

import sys
import subprocess
from pathlib import Path


def run_tests(test_filter=None, verbose=False):
    """
    Run unit tests with pytest.
    
    Args:
        test_filter: Optional filter for specific test file (glm, kimi, timeout)
        verbose: Whether to run in verbose mode
    """
    # Build pytest command
    cmd = ["pytest", "tests/unit/"]
    
    # Add test filter if specified
    if test_filter:
        if test_filter == "glm":
            cmd.append("tests/unit/test_glm_provider.py")
        elif test_filter == "kimi":
            cmd.append("tests/unit/test_kimi_provider.py")
        elif test_filter == "timeout":
            cmd.append("tests/unit/test_http_client_timeout.py")
        else:
            print(f"Unknown test filter: {test_filter}")
            print("Valid filters: glm, kimi, timeout")
            return 1
    
    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")
    
    # Add coverage if available
    try:
        import pytest_cov
        cmd.extend(["--cov=src/providers", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    # Run tests
    print(f"Running: {' '.join(cmd)}")
    print("=" * 80)
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run EX-AI-MCP-Server unit tests")
    parser.add_argument(
        "--test",
        choices=["glm", "kimi", "timeout"],
        help="Run specific test suite only"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    args = parser.parse_args()
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("ERROR: pytest is not installed")
        print("Install with: pip install pytest")
        return 1
    
    # Run tests
    return run_tests(test_filter=args.test, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())

