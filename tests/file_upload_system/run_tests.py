"""
Test Runner for File Upload System
Executes all tests and collects detailed metrics
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.file_upload_optimizer import get_optimizer, QueryComplexity, FileSize


class TestRunner:
    """Runs comprehensive test suite and collects metrics"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {},
            "metrics": {},
        }
        self.optimizer = get_optimizer()
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("\n" + "="*80)
        print("RUNNING UNIT TESTS")
        print("="*80)
        
        test_file = Path(__file__).parent / "test_upload_comprehensive.py"
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v", "--tb=short", "--json-report", "--json-report-file=test_results.json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            output = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return output
        
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Test execution timed out after 300 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }
    
    def test_provider_selection_logic(self) -> Dict[str, Any]:
        """Test provider selection logic"""
        print("\n" + "="*80)
        print("TESTING PROVIDER SELECTION LOGIC")
        print("="*80)
        
        test_cases = [
            {
                "name": "Simple query + small file",
                "complexity": QueryComplexity.SIMPLE,
                "file_size": FileSize.SMALL,
                "expected_provider": "kimi",
            },
            {
                "name": "Moderate query + medium file",
                "complexity": QueryComplexity.MODERATE,
                "file_size": FileSize.MEDIUM,
                "expected_provider": "kimi",
            },
            {
                "name": "Complex query + small file",
                "complexity": QueryComplexity.COMPLEX,
                "file_size": FileSize.SMALL,
                "expected_provider": "glm",
            },
            {
                "name": "Complex query + large file",
                "complexity": QueryComplexity.COMPLEX,
                "file_size": FileSize.LARGE,
                "expected_provider": "glm",
            },
        ]
        
        results = []
        for test_case in test_cases:
            selected = self.optimizer.select_provider(
                test_case["complexity"],
                test_case["file_size"]
            )
            
            passed = selected == test_case["expected_provider"]
            
            result = {
                "test": test_case["name"],
                "expected": test_case["expected_provider"],
                "selected": selected,
                "passed": passed,
            }
            
            results.append(result)
            
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status}: {test_case['name']}")
            print(f"  Expected: {test_case['expected_provider']}, Got: {selected}")
        
        return {
            "test_cases": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results,
        }
    
    def test_timeout_prediction(self) -> Dict[str, Any]:
        """Test timeout prediction logic"""
        print("\n" + "="*80)
        print("TESTING TIMEOUT PREDICTION")
        print("="*80)
        
        test_cases = [
            {
                "name": "Simple query + small file",
                "complexity": QueryComplexity.SIMPLE,
                "file_size": FileSize.SMALL,
                "provider": "kimi",
                "should_timeout": False,
            },
            {
                "name": "Complex query + large file",
                "complexity": QueryComplexity.COMPLEX,
                "file_size": FileSize.LARGE,
                "provider": "kimi",
                "should_timeout": True,
            },
        ]
        
        results = []
        for test_case in test_cases:
            will_timeout = self.optimizer.will_timeout(
                test_case["complexity"],
                test_case["file_size"],
                test_case["provider"]
            )
            
            passed = will_timeout == test_case["should_timeout"]
            
            result = {
                "test": test_case["name"],
                "expected_timeout": test_case["should_timeout"],
                "predicted_timeout": will_timeout,
                "passed": passed,
            }
            
            results.append(result)
            
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status}: {test_case['name']}")
            print(f"  Expected timeout: {test_case['should_timeout']}, Got: {will_timeout}")
        
        return {
            "test_cases": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results,
        }
    
    def test_query_optimization(self) -> Dict[str, Any]:
        """Test query optimization"""
        print("\n" + "="*80)
        print("TESTING QUERY OPTIMIZATION")
        print("="*80)
        
        complex_query = "Perform a comprehensive analysis including: 1) Main themes, 2) Technical depth, 3) Potential improvements, 4) Comparison with industry standards, 5) Risk assessment."
        
        optimized = self.optimizer.optimize_query(complex_query, FileSize.LARGE)
        
        print(f"Original query length: {len(complex_query)}")
        print(f"Optimized query length: {len(optimized)}")
        print(f"Reduction: {((len(complex_query) - len(optimized)) / len(complex_query) * 100):.1f}%")
        
        return {
            "original_length": len(complex_query),
            "optimized_length": len(optimized),
            "reduction_percent": ((len(complex_query) - len(optimized)) / len(complex_query) * 100),
        }
    
    def test_prompt_engineering(self) -> Dict[str, Any]:
        """Test prompt engineering"""
        print("\n" + "="*80)
        print("TESTING PROMPT ENGINEERING")
        print("="*80)
        
        task = "Analyze the code structure and identify potential improvements"
        files = ["file1.py", "file2.py"]
        
        prompt = self.optimizer.create_analysis_prompt(task, files, "kimi")
        
        # Check for key elements
        checks = {
            "contains_task": task in prompt,
            "contains_file_list": "file1.py" in prompt and "file2.py" in prompt,
            "contains_focus_instruction": "Focus on completing the specified task" in prompt,
            "contains_no_management_instruction": "not on file management" in prompt,
        }
        
        print(f"Prompt length: {len(prompt)} characters")
        for check, result in checks.items():
            status = "[OK]" if result else "[FAIL]"
            print(f"{status} {check}")
        
        return {
            "prompt_length": len(prompt),
            "checks": checks,
            "all_passed": all(checks.values()),
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and collect results"""
        print("\n" + "="*80)
        print("FILE UPLOAD SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Started: {datetime.now().isoformat()}")
        
        start_time = time.time()
        
        # Run all test suites
        self.results["test_suites"]["unit_tests"] = self.run_unit_tests()
        self.results["test_suites"]["provider_selection"] = self.test_provider_selection_logic()
        self.results["test_suites"]["timeout_prediction"] = self.test_timeout_prediction()
        self.results["test_suites"]["query_optimization"] = self.test_query_optimization()
        self.results["test_suites"]["prompt_engineering"] = self.test_prompt_engineering()
        
        # Collect metrics
        self.results["metrics"] = self.optimizer.get_metrics_summary()
        
        # Calculate summary
        elapsed_time = time.time() - start_time
        
        self.results["summary"] = {
            "total_test_suites": len(self.results["test_suites"]),
            "elapsed_time_seconds": f"{elapsed_time:.2f}",
            "timestamp_end": datetime.now().isoformat(),
        }
        
        return self.results
    
    def save_results(self, output_file: Path) -> None:
        """Save results to JSON file"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n✓ Results saved to: {output_file}")
    
    def print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"Total test suites: {self.results['summary']['total_test_suites']}")
        print(f"Elapsed time: {self.results['summary']['elapsed_time_seconds']}s")
        
        for suite_name, suite_results in self.results["test_suites"].items():
            if isinstance(suite_results, dict) and "passed" in suite_results:
                passed = suite_results.get("passed", 0)
                failed = suite_results.get("failed", 0)
                total = passed + failed
                print(f"\n{suite_name}:")
                print(f"  Passed: {passed}/{total}")
                if failed > 0:
                    print(f"  Failed: {failed}")


def main():
    """Main entry point"""
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Save results
    output_file = Path(__file__).parent / "test_results_detailed.json"
    runner.save_results(output_file)
    
    # Print summary
    runner.print_summary()
    
    print("\n" + "="*80)
    print("[SUCCESS] TEST EXECUTION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()

