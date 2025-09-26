#!/usr/bin/env python3
"""
Test runner script for EX-AI MCP Server comprehensive test suite

This script provides an easy way to run different test categories
and generate comprehensive test reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_test_environment():
    """Set up test environment variables"""
    test_env = {
        'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
        'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq',
        'AI_MANAGER_MODEL': 'glm-4.5-flash',
        'KIMI_MODEL': 'moonshot-v1-8k',
        'REQUEST_TIMEOUT': '30',
        'MAX_RETRIES': '3',
        'ENABLE_INTELLIGENT_ROUTING': 'true',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value


def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run EX-AI MCP Server tests')
    parser.add_argument('--category', choices=[
        'all', 'unit', 'integration', 'e2e', 'performance', 
        'mcp_protocol', 'routing', 'providers', 'config'
    ], default='all', help='Test category to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--fast', action='store_true', help='Skip slow tests')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_test_environment()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Base pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        pytest_cmd.extend(['-v', '--tb=long'])
    else:
        pytest_cmd.extend(['--tb=short'])
    
    if args.coverage:
        pytest_cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term-missing'])
    
    if args.fast:
        pytest_cmd.extend(['-m', 'not slow'])
    
    # Run tests based on category
    success = True
    
    if args.category == 'all':
        # Run all test categories
        test_files = [
            ('tests/test_mcp_protocol_compliance.py', 'MCP Protocol Compliance Tests'),
            ('tests/test_intelligent_routing.py', 'Intelligent Routing Tests'),
            ('tests/test_provider_integration.py', 'Provider Integration Tests'),
            ('tests/test_end_to_end_workflows.py', 'End-to-End Workflow Tests'),
            ('tests/test_configuration_environment.py', 'Configuration & Environment Tests')
        ]
        
        for test_file, description in test_files:
            if os.path.exists(test_file):
                cmd = pytest_cmd + [test_file]
                if not run_command(cmd, description):
                    success = False
            else:
                print(f"Warning: Test file {test_file} not found")
    
    elif args.category == 'mcp_protocol':
        cmd = pytest_cmd + ['tests/test_mcp_protocol_compliance.py']
        success = run_command(cmd, 'MCP Protocol Compliance Tests')
    
    elif args.category == 'routing':
        cmd = pytest_cmd + ['tests/test_intelligent_routing.py']
        success = run_command(cmd, 'Intelligent Routing Tests')
    
    elif args.category == 'providers':
        cmd = pytest_cmd + ['tests/test_provider_integration.py']
        success = run_command(cmd, 'Provider Integration Tests')
    
    elif args.category == 'e2e':
        cmd = pytest_cmd + ['tests/test_end_to_end_workflows.py']
        success = run_command(cmd, 'End-to-End Workflow Tests')
    
    elif args.category == 'config':
        cmd = pytest_cmd + ['tests/test_configuration_environment.py']
        success = run_command(cmd, 'Configuration & Environment Tests')
    
    else:
        # Run tests by marker
        cmd = pytest_cmd + ['-m', args.category]
        success = run_command(cmd, f'{args.category.title()} Tests')
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check output above for details.")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
