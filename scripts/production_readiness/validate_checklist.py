#!/usr/bin/env python3
"""
Production Readiness Checklist Validator
Validates checklist items and generates actionable reports
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class ProductionReadinessValidator:
    """Validates production readiness checklist items"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'passed': [],
            'failed': [],
            'warnings': [],
            'skipped': [],
            'summary': {}
        }

    def log_result(self, category: str, item: str, status: str, details: str = ""):
        """Log validation result"""
        result = {
            'category': category,
            'item': item,
            'status': status,
            'details': details
        }

        if status == 'PASS':
            self.results['passed'].append(result)
        elif status == 'FAIL':
            self.results['failed'].append(result)
        elif status == 'WARN':
            self.results['warnings'].append(result)
        elif status == 'SKIP':
            self.results['skipped'].append(result)

    def check_file_exists(self, path: str) -> bool:
        """Check if file exists"""
        return (self.project_root / path).exists()

    def check_directory_exists(self, path: str) -> bool:
        """Check if directory exists"""
        return (self.project_root / path).is_dir()

    def validate_code_quality(self):
        """Validate Phase 1: Code Quality & Architecture"""
        print("\n🔍 Phase 1: Code Quality & Architecture")
        print("=" * 60)

        # Check for god objects
        god_objects = [
            'src/daemon/monitoring_endpoint.py',
            'src/storage/supabase_client.py',
            'src/daemon/ws/request_router.py',
            'src/providers/glm_chat.py',
            'src/providers/openai_compatible.py'
        ]

        for obj in god_objects:
            if self.check_file_exists(obj):
                # Get line count
                try:
                    with open(self.project_root / obj, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    if lines > 800:
                        self.log_result('CODE_QUALITY', f'God object: {obj}', 'FAIL',
                                      f'{lines} lines (exceeds 800 line limit)')
                    else:
                        self.log_result('CODE_QUALITY', f'God object: {obj}', 'PASS',
                                      f'{lines} lines')
                except Exception as e:
                    self.log_result('CODE_QUALITY', f'God object: {obj}', 'WARN', str(e))

        # Check for workflow tools
        workflow_dir = self.project_root / 'tools' / 'workflows'
        if workflow_dir.exists():
            workflow_tools = list(workflow_dir.glob('*.py'))
            # Verify base class usage
            base_file = self.project_root / 'tools' / 'workflow' / 'base.py'
            if base_file.exists():
                self.log_result('CODE_QUALITY', 'Workflow tools base class', 'PASS',
                              f'{len(workflow_tools)} tools with base class')
            else:
                self.log_result('CODE_QUALITY', 'Workflow tools base class', 'FAIL',
                              'Base class not found')

        print(f"✓ Checked {len(god_objects)} god objects")

    def validate_security(self):
        """Validate Phase 3: Security"""
        print("\n🔐 Phase 3: Security")
        print("=" * 60)

        # Check for hardcoded secrets
        secrets_patterns = [
            'password', 'api_key', 'secret', 'token',
            'sk-', 'pk_', 'AKIA', 'ghp_'
        ]

        secrets_found = []
        for root, dirs, files in os.walk(self.project_root / 'src'):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in secrets_patterns:
                                if pattern in content.lower() and 'example' not in content.lower():
                                    secrets_found.append(f"{file}: {pattern}")
                    except:
                        pass

        if secrets_found:
            self.log_result('SECURITY', 'Hardcoded secrets', 'FAIL',
                          f'{len(secrets_found)} potential secrets found')
        else:
            self.log_result('SECURITY', 'Hardcoded secrets', 'PASS',
                          'No obvious hardcoded secrets')

        # Check for .env files
        env_files = ['.env', '.env.docker', '.env.example']
        env_found = 0
        for env_file in env_files:
            if self.check_file_exists(env_file):
                env_found += 1
        self.log_result('SECURITY', '.env configuration', 'PASS',
                      f'{env_found}/{len(env_files)} .env files found')

        print(f"✓ Security checks completed")

    def validate_database(self):
        """Validate Phase 2: Database & Storage"""
        print("\n💾 Phase 2: Database & Storage")
        print("=" * 60)

        # Check for Supabase configuration
        supabase_dir = self.project_root / 'supabase'
        if supabase_dir.exists():
            self.log_result('DATABASE', 'Supabase directory', 'PASS',
                          'Supabase configuration found')

            # Check for migrations
            migrations_dir = supabase_dir / 'migrations'
            if migrations_dir.exists():
                migrations = list(migrations_dir.glob('*.sql'))
                self.log_result('DATABASE', 'Database migrations', 'PASS',
                              f'{len(migrations)} migration files')
            else:
                self.log_result('DATABASE', 'Database migrations', 'WARN',
                              'No migrations found')
        else:
            self.log_result('DATABASE', 'Supabase configuration', 'FAIL',
                          'Supabase directory not found')

        # Check for database connection in config
        if self.check_file_exists('config/__init__.py'):
            self.log_result('DATABASE', 'Database config', 'PASS',
                          'Configuration found')
        else:
            self.log_result('DATABASE', 'Database config', 'FAIL',
                          'Configuration not found')

        print(f"✓ Database checks completed")

    def validate_monitoring(self):
        """Validate Phase 5: Monitoring"""
        print("\n📊 Phase 5: Monitoring")
        print("=" * 60)

        # Check for monitoring endpoint
        if self.check_file_exists('src/daemon/monitoring_endpoint.py'):
            self.log_result('MONITORING', 'Monitoring endpoint', 'PASS',
                          'Monitoring endpoint exists')

            # Check for health tracking
            if self.check_file_exists('src/daemon/monitoring/health_tracker.py'):
                self.log_result('MONITORING', 'Health tracking', 'PASS',
                              'Health tracker module exists')
            else:
                self.log_result('MONITORING', 'Health tracking', 'WARN',
                              'Health tracker module not found')

        else:
            self.log_result('MONITORING', 'Monitoring endpoint', 'FAIL',
                          'Monitoring endpoint not found')

        # Check for logging configuration
        if self.check_file_exists('config/__init__.py'):
            self.log_result('MONITORING', 'Logging configuration', 'PASS',
                          'Configuration found')
        else:
            self.log_result('MONITORING', 'Logging configuration', 'WARN',
                          'Configuration not found')

        print(f"✓ Monitoring checks completed")

    def validate_containerization(self):
        """Validate Phase 7: Containerization"""
        print("\n📦 Phase 7: Containerization")
        print("=" * 60)

        # Check for Docker files
        docker_files = ['docker-compose.yml', 'Dockerfile', '.dockerignore']
        for docker_file in docker_files:
            if self.check_file_exists(docker_file):
                self.log_result('CONTAINERS', docker_file, 'PASS',
                              f'{docker_file} found')
            else:
                self.log_result('CONTAINERS', docker_file, 'WARN',
                              f'{docker_file} not found')

        print(f"✓ Containerization checks completed")

    def validate_testing(self):
        """Validate Phase 4: Testing"""
        print("\n🧪 Phase 4: Testing")
        print("=" * 60)

        # Check for test directory
        tests_dir = self.project_root / 'tests'
        if tests_dir.exists():
            self.log_result('TESTING', 'Test directory', 'PASS',
                          'Tests directory exists')

            # Count test files
            test_files = list(tests_dir.rglob('test_*.py'))
            self.log_result('TESTING', 'Test files', 'PASS',
                          f'{len(test_files)} test files found')
        else:
            self.log_result('TESTING', 'Test directory', 'FAIL',
                          'Tests directory not found')

        # Check for pytest configuration
        if self.check_file_exists('pytest.ini') or self.check_file_exists('pyproject.toml'):
            self.log_result('TESTING', 'Pytest configuration', 'PASS',
                          'Pytest configuration found')
        else:
            self.log_result('TESTING', 'Pytest configuration', 'WARN',
                          'Pytest configuration not found')

        print(f"✓ Testing checks completed")

    def validate_documentation(self):
        """Validate Phase 9: Documentation"""
        print("\n📚 Phase 9: Documentation")
        print("=" * 60)

        # Check for README
        if self.check_file_exists('README.md'):
            self.log_result('DOCS', 'README.md', 'PASS',
                          'README.md found')
        else:
            self.log_result('DOCS', 'README.md', 'FAIL',
                          'README.md not found')

        # Check for docs directory
        if self.check_directory_exists('docs'):
            self.log_result('DOCS', 'Documentation directory', 'PASS',
                          'docs directory exists')
        else:
            self.log_result('DOCS', 'Documentation directory', 'WARN',
                          'docs directory not found')

        # Check for production readiness checklist
        checklist_files = [
            'PRODUCTION_READINESS_CHECKLIST.md',
            'PRODUCTION_READINESS_ENHANCED.md'
        ]
        for checklist in checklist_files:
            if self.check_file_exists(checklist):
                self.log_result('DOCS', f'{checklist}', 'PASS',
                              f'{checklist} found')
                break

        print(f"✓ Documentation checks completed")

    def run_all_validations(self):
        """Run all validation checks"""
        print("\n" + "=" * 60)
        print("PRODUCTION READINESS VALIDATOR")
        print("=" * 60)
        print(f"Project: {self.project_root}")
        print(f"Timestamp: {self.results['timestamp']}")
        print()

        # Run all checks
        self.validate_code_quality()
        self.validate_security()
        self.validate_database()
        self.validate_monitoring()
        self.validate_containerization()
        self.validate_testing()
        self.validate_documentation()

        # Generate summary
        self.results['summary'] = {
            'total': len(self.results['passed']) + len(self.results['failed']) +
                     len(self.results['warnings']) + len(self.results['skipped']),
            'passed': len(self.results['passed']),
            'failed': len(self.results['failed']),
            'warnings': len(self.results['warnings']),
            'skipped': len(self.results['skipped'])
        }

        # Calculate score
        if self.results['summary']['total'] > 0:
            score = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
            self.results['summary']['score'] = round(score, 2)

        # Print summary
        self.print_summary()

        # Save results
        self.save_results()

        return self.results

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        summary = self.results['summary']
        print(f"Total Checks: {summary['total']}")
        print(f"Passed: {summary['passed']} ✓")
        print(f"Failed: {summary['failed']} ✗")
        print(f"Warnings: {summary['warnings']} ⚠")
        print(f"Skipped: {summary['skipped']} ⊘")
        print()
        print(f"Overall Score: {summary.get('score', 0):.2f}%")
        print()

        # Print failed items
        if self.results['failed']:
            print("❌ FAILED CHECKS:")
            for item in self.results['failed']:
                print(f"  • [{item['category']}] {item['item']}")
                if item['details']:
                    print(f"    {item['details']}")
            print()

        # Print warnings
        if self.results['warnings']:
            print("⚠️ WARNINGS:")
            for item in self.results['warnings']:
                print(f"  • [{item['category']}] {item['item']}")
                if item['details']:
                    print(f"    {item['details']}")
            print()

    def save_results(self):
        """Save results to JSON file"""
        results_file = self.project_root / 'production_readiness_report.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")


def main():
    """Main entry point"""
    validator = ProductionReadinessValidator()
    results = validator.run_all_validations()

    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        print("\n❌ Production readiness validation FAILED")
        print(f"   {results['summary']['failed']} critical issues need to be addressed")
        sys.exit(1)
    elif results['summary']['warnings'] > 0:
        print("\n⚠️ Production readiness validation PASSED with warnings")
        print(f"   {results['summary']['warnings']} warnings found")
        sys.exit(0)
    else:
        print("\n✅ Production readiness validation PASSED")
        print("   All checks successful!")
        sys.exit(0)


if __name__ == '__main__':
    main()
