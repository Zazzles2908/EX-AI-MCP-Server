#!/usr/bin/env python3
"""
Timeout Hierarchy Validation Script

This script validates that timeout values in .env follow the correct hierarchy:
- Tool timeout (base value)
- Daemon timeout = 1.5x tool timeout
- Shim timeout = 2.0x tool timeout  
- Client timeout = 2.5x tool timeout

The hierarchy ensures that each layer has enough time to complete before the
next layer times out, preventing cascading timeout failures.

Usage:
    python scripts/validate_timeout_hierarchy.py
    python scripts/validate_timeout_hierarchy.py --env-file .env.testing
    python scripts/validate_timeout_hierarchy.py --fix  # Auto-fix violations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import TimeoutConfig


class TimeoutValidator:
    """Validates timeout hierarchy configuration."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize validator with environment file."""
        self.env_file = env_file
        self.env_path = project_root / env_file
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
        # Load environment variables
        if self.env_path.exists():
            load_dotenv(self.env_path)
        else:
            print(f"⚠️  Warning: {env_file} not found, using defaults")
    
    def get_timeout_value(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get timeout value from environment or default."""
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                self.issues.append(f"❌ {key}={value} is not a valid integer")
                return None
        return default
    
    def validate_hierarchy(self) -> bool:
        """
        Validate timeout hierarchy.
        
        Returns:
            True if hierarchy is valid, False otherwise
        """
        print("="*60)
        print("TIMEOUT HIERARCHY VALIDATION")
        print("="*60)
        print(f"Environment file: {self.env_file}")
        print()
        
        # Get configurable timeouts
        workflow_timeout = self.get_timeout_value("WORKFLOW_TOOL_TIMEOUT_SECS", 300)
        simple_timeout = self.get_timeout_value("SIMPLE_TOOL_TIMEOUT_SECS", 60)
        expert_timeout = self.get_timeout_value("EXPERT_ANALYSIS_TIMEOUT_SECS", 180)
        
        # Get auto-calculated timeouts from TimeoutConfig
        daemon_timeout = TimeoutConfig.get_daemon_timeout()
        shim_timeout = TimeoutConfig.get_shim_timeout()
        client_timeout = TimeoutConfig.get_client_timeout()
        
        print("📊 CURRENT TIMEOUT VALUES")
        print("-"*60)
        print(f"Configurable Timeouts (from .env):")
        print(f"  WORKFLOW_TOOL_TIMEOUT_SECS:      {workflow_timeout}s")
        print(f"  SIMPLE_TOOL_TIMEOUT_SECS:        {simple_timeout}s")
        print(f"  EXPERT_ANALYSIS_TIMEOUT_SECS:    {expert_timeout}s")
        print()
        print(f"Auto-Calculated Timeouts (from config.py):")
        print(f"  Daemon timeout:  {daemon_timeout}s  (1.5x workflow = {workflow_timeout * 1.5}s)")
        print(f"  Shim timeout:    {shim_timeout}s  (2.0x workflow = {workflow_timeout * 2.0}s)")
        print(f"  Client timeout:  {client_timeout}s  (2.5x workflow = {workflow_timeout * 2.5}s)")
        print()
        
        # Validate hierarchy
        print("✅ HIERARCHY VALIDATION")
        print("-"*60)
        
        valid = True
        
        # Check tool timeout hierarchy
        if simple_timeout >= workflow_timeout:
            self.issues.append(
                f"❌ SIMPLE_TOOL_TIMEOUT_SECS ({simple_timeout}s) should be < "
                f"WORKFLOW_TOOL_TIMEOUT_SECS ({workflow_timeout}s)"
            )
            valid = False
        else:
            print(f"✅ Simple timeout ({simple_timeout}s) < Workflow timeout ({workflow_timeout}s)")
        
        if expert_timeout >= workflow_timeout:
            self.warnings.append(
                f"⚠️  EXPERT_ANALYSIS_TIMEOUT_SECS ({expert_timeout}s) >= "
                f"WORKFLOW_TOOL_TIMEOUT_SECS ({workflow_timeout}s) - may cause timeouts"
            )
        else:
            print(f"✅ Expert timeout ({expert_timeout}s) < Workflow timeout ({workflow_timeout}s)")
        
        # Check infrastructure timeout hierarchy
        expected_daemon = workflow_timeout * 1.5
        expected_shim = workflow_timeout * 2.0
        expected_client = workflow_timeout * 2.5
        
        if daemon_timeout == expected_daemon:
            print(f"✅ Daemon timeout ({daemon_timeout}s) = 1.5x workflow ({expected_daemon}s)")
        else:
            self.issues.append(
                f"❌ Daemon timeout ({daemon_timeout}s) != 1.5x workflow ({expected_daemon}s)"
            )
            valid = False
        
        if shim_timeout == expected_shim:
            print(f"✅ Shim timeout ({shim_timeout}s) = 2.0x workflow ({expected_shim}s)")
        else:
            self.issues.append(
                f"❌ Shim timeout ({shim_timeout}s) != 2.0x workflow ({expected_shim}s)"
            )
            valid = False
        
        if client_timeout == expected_client:
            print(f"✅ Client timeout ({client_timeout}s) = 2.5x workflow ({expected_client}s)")
        else:
            self.issues.append(
                f"❌ Client timeout ({client_timeout}s) != 2.5x workflow ({expected_client}s)"
            )
            valid = False
        
        # Check overall hierarchy
        if not (workflow_timeout < daemon_timeout < shim_timeout < client_timeout):
            self.issues.append(
                f"❌ Timeout hierarchy violated: "
                f"workflow ({workflow_timeout}s) < daemon ({daemon_timeout}s) < "
                f"shim ({shim_timeout}s) < client ({client_timeout}s)"
            )
            valid = False
        else:
            print(f"✅ Overall hierarchy: {workflow_timeout}s < {daemon_timeout}s < {shim_timeout}s < {client_timeout}s")
        
        print()
        
        # Print issues and warnings
        if self.issues:
            print("❌ ISSUES FOUND")
            print("-"*60)
            for issue in self.issues:
                print(issue)
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS")
            print("-"*60)
            for warning in self.warnings:
                print(warning)
            print()
        
        # Print summary
        print("="*60)
        if valid and not self.warnings:
            print("✅ VALIDATION PASSED - All timeouts correctly configured")
        elif valid and self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
        else:
            print("❌ VALIDATION FAILED - Please fix timeout configuration")
        print("="*60)
        print()
        
        return valid
    
    def print_recommendations(self):
        """Print recommendations for fixing timeout issues."""
        if not self.issues and not self.warnings:
            return
        
        print("💡 RECOMMENDATIONS")
        print("-"*60)
        print()
        print("The timeout hierarchy should follow this pattern:")
        print()
        print("  SIMPLE_TOOL_TIMEOUT_SECS < WORKFLOW_TOOL_TIMEOUT_SECS")
        print("  EXPERT_ANALYSIS_TIMEOUT_SECS < WORKFLOW_TOOL_TIMEOUT_SECS")
        print()
        print("  Daemon timeout  = 1.5x WORKFLOW_TOOL_TIMEOUT_SECS (auto-calculated)")
        print("  Shim timeout    = 2.0x WORKFLOW_TOOL_TIMEOUT_SECS (auto-calculated)")
        print("  Client timeout  = 2.5x WORKFLOW_TOOL_TIMEOUT_SECS (auto-calculated)")
        print()
        print("Example configuration in .env:")
        print()
        print("  WORKFLOW_TOOL_TIMEOUT_SECS=300")
        print("  SIMPLE_TOOL_TIMEOUT_SECS=60")
        print("  EXPERT_ANALYSIS_TIMEOUT_SECS=180")
        print()
        print("This will result in:")
        print("  - Daemon timeout:  450s (1.5x 300)")
        print("  - Shim timeout:    600s (2.0x 300)")
        print("  - Client timeout:  750s (2.5x 300)")
        print()
        print("For more information, see:")
        print("  tool_validation_suite/docs/current/guides/TIMEOUT_CONFIGURATION_GUIDE.md")
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate timeout hierarchy configuration"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Environment file to validate (default: .env)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix timeout violations (not yet implemented)"
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = TimeoutValidator(args.env_file)
    
    # Validate hierarchy
    valid = validator.validate_hierarchy()
    
    # Print recommendations if issues found
    if not valid or validator.warnings:
        validator.print_recommendations()
    
    # Exit with appropriate code
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()

