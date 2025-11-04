#!/usr/bin/env python3
"""
Production Readiness Checklist Validator (Simple Version)
Validates checklist items without emoji to avoid encoding issues
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class SimpleProductionValidator:
    """Simple production readiness validator"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'passed': [],
            'failed': [],
            'warnings': [],
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

    def check_file(self, path: str) -> bool:
        """Check if file exists"""
        return (self.project_root / path).exists()

    def validate_all(self):
        """Run all validations"""
        print("\nPRODUCTION READINESS VALIDATOR")
        print("=" * 60)

        # 1. Code Quality
        print("\n[1] Code Quality & Architecture")
        god_objects = [
            'src/daemon/monitoring_endpoint.py',
            'src/storage/supabase_client.py',
            'src/daemon/ws/request_router.py',
            'src/providers/glm_chat.py'
        ]
        for obj in god_objects:
            if self.check_file(obj):
                try:
                    with open(self.project_root / obj, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    if lines > 800:
                        self.log_result('CODE', f'God object: {obj}', 'FAIL', f'{lines} lines')
                    else:
                        self.log_result('CODE', f'God object: {obj}', 'PASS', f'{lines} lines')
                except:
                    self.log_result('CODE', f'God object: {obj}', 'WARN', 'Could not read')

        # 2. Security
        print("[2] Security")
        # Check for .env files
        env_files = ['.env', '.env.docker', '.env.example']
        env_found = sum(1 for f in env_files if self.check_file(f))
        self.log_result('SECURITY', '.env files', 'PASS', f'{env_found}/{len(env_files)} found')

        # 3. Database
        print("[3] Database")
        if self.check_file('supabase'):
            self.log_result('DATABASE', 'Supabase directory', 'PASS', 'Found')
            if self.check_file('supabase/migrations'):
                migrations = list((self.project_root / 'supabase/migrations').glob('*.sql'))
                self.log_result('DATABASE', 'Migrations', 'PASS', f'{len(migrations)} files')
            else:
                self.log_result('DATABASE', 'Migrations', 'WARN', 'Not found')
        else:
            self.log_result('DATABASE', 'Supabase directory', 'FAIL', 'Not found')

        # 4. Testing
        print("[4] Testing")
        if self.check_file('tests'):
            test_files = list((self.project_root / 'tests').rglob('test_*.py'))
            self.log_result('TESTING', 'Test files', 'PASS', f'{len(test_files)} files')
        else:
            self.log_result('TESTING', 'Test directory', 'FAIL', 'Not found')

        # 5. Containerization
        print("[5] Containerization")
        docker_files = ['docker-compose.yml', 'Dockerfile']
        for f in docker_files:
            if self.check_file(f):
                self.log_result('CONTAINERS', f, 'PASS', 'Found')
            else:
                self.log_result('CONTAINERS', f, 'WARN', 'Not found')

        # 6. Documentation
        print("[6] Documentation")
        if self.check_file('README.md'):
            self.log_result('DOCS', 'README.md', 'PASS', 'Found')
        else:
            self.log_result('DOCS', 'README.md', 'FAIL', 'Not found')

        # 7. Monitoring
        print("[7] Monitoring")
        if self.check_file('src/daemon/monitoring_endpoint.py'):
            self.log_result('MONITORING', 'Monitoring endpoint', 'PASS', 'Found')
        else:
            self.log_result('MONITORING', 'Monitoring endpoint', 'FAIL', 'Not found')

        # Calculate summary
        self.results['summary'] = {
            'total': len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings']),
            'passed': len(self.results['passed']),
            'failed': len(self.results['failed']),
            'warnings': len(self.results['warnings'])
        }

        if self.results['summary']['total'] > 0:
            score = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
            self.results['summary']['score'] = round(score, 2)

        # Print results
        self.print_results()

        # Save to JSON
        results_file = self.project_root / 'validation_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {results_file}")

        return self.results

    def print_results(self):
        """Print validation results"""
        summary = self.results['summary']
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Checks: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Score: {summary.get('score', 0):.2f}%")

        if self.results['failed']:
            print("\nFAILED CHECKS:")
            for item in self.results['failed']:
                print(f"  - [{item['category']}] {item['item']}: {item['details']}")

        if self.results['warnings']:
            print("\nWARNINGS:")
            for item in self.results['warnings']:
                print(f"  - [{item['category']}] {item['item']}: {item['details']}")


def main():
    validator = SimpleProductionValidator()
    results = validator.validate_all()

    if results['summary']['failed'] > 0:
        print("\nVALIDATION FAILED - Critical issues found")
        sys.exit(1)
    else:
        print("\nVALIDATION PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
