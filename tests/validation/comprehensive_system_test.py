#!/usr/bin/env python3
"""
Comprehensive System Test
Runs all validation tests and generates a complete report
"""

import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class TestResult:
    """Test result"""
    name: str
    status: str
    duration: float
    details: str
    success: bool

class ComprehensiveSystemTester:
    """Comprehensive system tester"""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def run_test(self, name: str, command: List[str], cwd: str = None) -> TestResult:
        """Run a single test"""
        print(f"\n🔄 Running: {name}")
        print(f"Command: {' '.join(command)}")

        start = time.time()

        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )

            duration = time.time() - start

            if result.returncode == 0:
                status = "PASSED"
                success = True
                details = f"Test completed successfully in {duration:.2f}s"
            else:
                status = "FAILED"
                success = False
                details = f"Test failed with exit code {result.returncode}"
                if result.stderr:
                    details += f"\nError: {result.stderr[:500]}"

            print(f"✅ {name}: {status} ({duration:.2f}s)")

            return TestResult(name, status, duration, details, success)

        except subprocess.TimeoutExpired:
            duration = time.time() - start
            status = "TIMEOUT"
            success = False
            details = f"Test timed out after {duration:.2f}s"
            print(f"⏱️  {name}: {status}")

            return TestResult(name, status, duration, details, success)

        except Exception as e:
            duration = time.time() - start
            status = "ERROR"
            success = False
            details = f"Test error: {str(e)}"
            print(f"❌ {name}: {status}")

            return TestResult(name, status, duration, details, success)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print(f"\n{'='*80}")
        print(f"🏆 COMPREHENSIVE SYSTEM TEST SUITE")
        print(f"{'='*80}")

        tests = [
            # MCP Protocol Tests
            ("MCP Comprehensive Test", [
                sys.executable, "tests/protocol/mcp/mcp_comprehensive_test.py"
            ]),
            ("Kimi MCP Test", [
                sys.executable, "tests/protocol/mcp/test_kimi_complete_mcp.py"
            ]),
            ("Configuration Validation", [
                sys.executable, "tests/validation/configuration_validation_test.py"
            ]),
            # Async Stability Tests
            ("Async Stability Test", [
                sys.executable, "tests/protocol/mcp_async_stability_test.py"
            ]),
            # Benchmark Tests
            ("Routing Performance Bench", [
                sys.executable, "tests/benchmarks/routing_performance_bench.py"
            ]),
        ]

        # Run all tests
        for name, command in tests:
            test_result = self.run_test(name, command)
            self.test_results.append(test_result)

        # Generate summary
        return self.generate_summary()

    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        total_time = time.time() - self.start_time

        passed = sum(1 for r in self.test_results if r.success)
        failed = sum(1 for r in self.test_results if not r.success)
        total = len(self.test_results)

        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": total_time,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "test_results": [asdict(r) for r in self.test_results],
            "critical_issues": [
                r.name for r in self.test_results
                if not r.success and "fail" in r.name.lower()
            ]
        }

        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {total_time:.2f}s")

        if summary['critical_issues']:
            print(f"\n⚠️  Critical Issues:")
            for issue in summary['critical_issues']:
                print(f"  - {issue}")

        if passed == total:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ System is ready for production")
        else:
            print(f"\n⚠️  {failed} TEST(S) FAILED")
            print(f"🔧 Review and fix issues before deploying")

        return summary

    def save_report(self, summary: Dict[str, Any], filename: str):
        """Save test report to file"""
        filepath = f"docs/reports/{filename}"

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n📄 Report saved to: {filepath}")

def main():
    """Main execution"""
    tester = ComprehensiveSystemTester()

    try:
        summary = tester.run_all_tests()
        tester.save_report(summary, "comprehensive_system_test_report.json")

        # Exit with appropriate code
        passed = summary["passed"]
        total = summary["total_tests"]
        sys.exit(0 if passed == total else 1)

    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
