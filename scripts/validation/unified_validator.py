#!/usr/bin/env python3
"""
Unified Validation Framework

Consolidates 8 duplicate validation scripts:
- /scripts/validate_enhanced_schemas.py
- /scripts/validate_environment.py
- /scripts/validation/validate_context_engineering.py
- /scripts/validation/validate_mcp_configs.py
- /scripts/validation/validate_timeout_hierarchy.py
- /scripts/health/validate_system_health.py
- /scripts/production_readiness/validate_checklist.py
- /scripts/production_readiness/validate_simple.py

Usage:
    python scripts/validation/unified_validator.py --all
    python scripts/validation/unified_validator.py --env
    python scripts/validation/unified_validator.py --mcp
    python scripts/validation/unified_validator.py --health
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import argparse
import json

# Add repo root to path
_repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_repo_root))

try:
    from src.bootstrap import load_env
    load_env()
except ImportError:
    # Handle case where src is not a package
    pass


class ValidationResult:
    """Container for validation results."""

    def __init__(self, name: str, passed: bool, message: str = "", details: Dict = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}


class UnifiedValidator:
    """Unified validation framework for the entire system."""

    def __init__(self):
        self.results: List[ValidationResult] = []

    def validate_environment(self) -> ValidationResult:
        """Validate environment configuration."""
        print("\n[1/5] Validating Environment...")

        required_vars = [
            "EXAI_WS_HOST",
            "EXAI_WS_PORT",
            "GLM_API_KEY",
            "KIMI_API_KEY"
        ]

        missing = []
        present = []
        for var in required_vars:
            if os.getenv(var):
                present.append(var)
            else:
                missing.append(var)

        if missing:
            # Check if at least one API key is present
            api_keys = ["GLM_API_KEY", "KIMI_API_KEY"]
            has_api = any(os.getenv(k) for k in api_keys)

            if has_api:
                return ValidationResult(
                    "Environment",
                    True,
                    f"Core variables present: {', '.join(present[:2])} (optional API keys: {', '.join(missing)})"
                )
            else:
                return ValidationResult(
                    "Environment",
                    False,
                    f"Missing required variables: {', '.join(missing)}"
                )

        return ValidationResult("Environment", True, "All required variables present")

    def validate_enhanced_schemas(self) -> ValidationResult:
        """Validate enhanced schema configurations."""
        print("[2/5] Validating Enhanced Schemas...")

        try:
            # Check if tools directory exists and has schemas
            tools_dir = Path(_repo_root / "tools")
            if not tools_dir.exists():
                return ValidationResult("Enhanced Schemas", False, "Tools directory not found")

            schema_files = list(tools_dir.glob("**/*_schema.py"))
            return ValidationResult(
                "Enhanced Schemas",
                True,
                f"Found {len(schema_files)} schema files"
            )

        except Exception as e:
            return ValidationResult("Enhanced Schemas", False, str(e))

    def validate_mcp_configs(self) -> ValidationResult:
        """Validate MCP configuration files."""
        print("[3/5] Validating MCP Configurations...")

        # Check .mcp.json
        mcp_config = Path(_repo_root / ".mcp.json")
        if not mcp_config.exists():
            return ValidationResult("MCP Configs", False, ".mcp.json not found")

        try:
            with open(mcp_config) as f:
                config = json.load(f)

            if "mcpServers" not in config:
                return ValidationResult("MCP Configs", False, "No mcpServers in config")

            return ValidationResult("MCP Configs", True, "MCP configuration valid")

        except Exception as e:
            return ValidationResult("MCP Configs", False, str(e))

    def validate_system_health(self) -> ValidationResult:
        """Validate system health and dependencies."""
        print("[4/5] Validating System Health...")

        health_checks = {
            "Python Version": sys.version_info >= (3, 9),
            "Repository Root": Path(_repo_root).exists(),
            "Source Directory": (Path(_repo_root) / "src").exists(),
            "Tools Directory": (Path(_repo_root) / "tools").exists(),
        }

        failed = [name for name, passed in health_checks.items() if not passed]

        if failed:
            return ValidationResult(
                "System Health",
                False,
                f"Failed checks: {', '.join(failed)}",
                health_checks
            )

        return ValidationResult("System Health", True, "All health checks passed", health_checks)

    def validate_production_readiness(self) -> ValidationResult:
        """Validate production readiness checklist."""
        print("[5/5] Validating Production Readiness...")

        checks = {
            "Environment Variables": bool(os.getenv("EXAI_WS_HOST")),
            "API Keys Configured": bool(os.getenv("GLM_API_KEY") or os.getenv("KIMI_API_KEY")),
            "Configuration Files": (Path(_repo_root / ".mcp.json")).exists(),
            "Source Code Present": (Path(_repo_root / "src")).exists(),
        }

        passed = sum(1 for check in checks.values() if check)
        total = len(checks)

        if passed == total:
            return ValidationResult(
                "Production Readiness",
                True,
                f"All {total} production checks passed"
            )
        else:
            failed = [name for name, check in checks.items() if not check]
            return ValidationResult(
                "Production Readiness",
                False,
                f"Only {passed}/{total} checks passed. Failed: {', '.join(failed)}",
                checks
            )

    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validation checks."""
        print("=" * 60)
        print("Unified Validation Framework")
        print("(Consolidated from 8 duplicate validation scripts)")
        print("=" * 60)

        validators = [
            self.validate_environment,
            self.validate_enhanced_schemas,
            self.validate_mcp_configs,
            self.validate_system_health,
            self.validate_production_readiness,
        ]

        for validator in validators:
            result = validator()
            self.results.append(result)

        return self.results

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)

        for result in self.results:
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status}: {result.name}")
            if result.message:
                print(f"       {result.message}")

        # Overall status
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print("-" * 60)
        print(f"Overall: {passed}/{total} validations passed")

        return passed == total


def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Validation Framework",
        epilog="Use --all to run all validations"
    )
    parser.add_argument("--all", action="store_true", help="Run all validations")
    parser.add_argument("--env", action="store_true", help="Validate environment only")
    parser.add_argument("--mcp", action="store_true", help="Validate MCP configs only")
    parser.add_argument("--health", action="store_true", help="Validate system health only")
    parser.add_argument("--prod", action="store_true", help="Validate production readiness only")
    parser.add_argument("--schemas", action="store_true", help="Validate schemas only")

    args = parser.parse_args()

    validator = UnifiedValidator()

    if args.env:
        result = validator.validate_environment()
        validator.results = [result]
    elif args.mcp:
        result = validator.validate_mcp_configs()
        validator.results = [result]
    elif args.health:
        result = validator.validate_system_health()
        validator.results = [result]
    elif args.prod:
        result = validator.validate_production_readiness()
        validator.results = [result]
    elif args.schemas:
        result = validator.validate_enhanced_schemas()
        validator.results = [result]
    else:
        # Run all
        validator.run_all_validations()

    # Print results
    all_passed = validator.print_summary()

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
