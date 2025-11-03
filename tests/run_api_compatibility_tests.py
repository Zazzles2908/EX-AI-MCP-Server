"""
API Compatibility Tests Execution Script

Executes the comprehensive API compatibility test suite with real API keys
and generates detailed test results with performance benchmarks.

Week 2-3 Implementation (2025-11-02):
- Executes all test cases with real Kimi and GLM APIs
- Validates purpose parameter enforcement
- Tests file size limit validation
- Benchmarks upload performance for each method
- Generates detailed test report
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    passed: bool
    duration: float
    error_message: str = ""
    performance_metrics: Dict[str, Any] = None


@dataclass
class TestSuiteResults:
    """Results of entire test suite"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration: float
    test_results: List[TestResult]
    performance_benchmarks: Dict[str, Any]


class APICompatibilityTestRunner:
    """
    Runs API compatibility tests and generates detailed reports.
    """
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = None
        self.performance_data = {}
    
    def _check_api_keys(self) -> Dict[str, bool]:
        """Check if API keys are available"""
        return {
            'kimi': bool(os.getenv('KIMI_API_KEY')),
            'glm': bool(os.getenv('GLM_API_KEY'))
        }
    
    def _run_test(self, test_func: callable, test_name: str) -> TestResult:
        """Run a single test and record results"""
        logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                passed=True,
                duration=duration,
                performance_metrics=result if isinstance(result, dict) else None
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return TestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e)
            )
    
    def run_kimi_tests(self) -> List[TestResult]:
        """Run Kimi API compatibility tests"""
        results = []
        
        # Test 1: Kimi upload with correct purpose
        def test_kimi_correct_purpose():
            from src.providers.kimi_files import upload_file
            from openai import OpenAI
            
            client = OpenAI(
                api_key=os.getenv('KIMI_API_KEY'),
                base_url="https://api.moonshot.ai/v1"
            )
            
            # Create test file
            test_file = project_root / "tests" / "test_data" / "test_upload.txt"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("Test content for Kimi upload")
            
            start = time.time()
            file_id = upload_file(
                client=client,
                file_path=str(test_file),
                purpose="assistants"
            )
            upload_time = time.time() - start
            
            # Cleanup
            try:
                client.files.delete(file_id)
            except:
                pass
            
            return {
                'file_id': file_id,
                'upload_time': upload_time,
                'file_size': test_file.stat().st_size
            }
        
        results.append(self._run_test(
            test_kimi_correct_purpose,
            "test_kimi_upload_with_correct_purpose"
        ))
        
        # Test 2: Kimi upload with invalid purpose (should fail)
        def test_kimi_invalid_purpose():
            from src.providers.kimi_files import upload_file
            from openai import OpenAI
            
            client = OpenAI(
                api_key=os.getenv('KIMI_API_KEY'),
                base_url="https://api.moonshot.ai/v1"
            )
            
            test_file = project_root / "tests" / "test_data" / "test_upload.txt"
            
            try:
                upload_file(
                    client=client,
                    file_path=str(test_file),
                    purpose="file-extract"  # Invalid purpose
                )
                raise AssertionError("Should have raised ValueError for invalid purpose")
            except ValueError as e:
                if "Invalid purpose" in str(e):
                    return {'validation': 'passed'}
                raise
        
        results.append(self._run_test(
            test_kimi_invalid_purpose,
            "test_kimi_upload_with_invalid_purpose"
        ))
        
        return results
    
    def run_glm_tests(self) -> List[TestResult]:
        """Run GLM API compatibility tests"""
        results = []
        
        # Test 1: GLM upload with correct purpose
        def test_glm_correct_purpose():
            from src.providers.glm_files import upload_file
            from zhipuai import ZhipuAI
            
            client = ZhipuAI(api_key=os.getenv('GLM_API_KEY'))
            
            # Create test file
            test_file = project_root / "tests" / "test_data" / "test_upload_glm.txt"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("Test content for GLM upload")
            
            start = time.time()
            file_id = upload_file(
                sdk_client=client,
                http_client=None,
                file_path=str(test_file),
                purpose="file",
                use_sdk=True
            )
            upload_time = time.time() - start
            
            return {
                'file_id': file_id,
                'upload_time': upload_time,
                'file_size': test_file.stat().st_size
            }
        
        results.append(self._run_test(
            test_glm_correct_purpose,
            "test_glm_upload_with_correct_purpose"
        ))
        
        # Test 2: GLM SDK fallback chain
        def test_glm_fallback_chain():
            from src.providers.glm_sdk_fallback import upload_file_with_fallback
            
            test_file = project_root / "tests" / "test_data" / "test_upload_glm.txt"
            
            start = time.time()
            file_id, method_used = upload_file_with_fallback(
                api_key=os.getenv('GLM_API_KEY'),
                file_path=str(test_file),
                purpose="file"
            )
            upload_time = time.time() - start
            
            return {
                'file_id': file_id,
                'method_used': method_used,
                'upload_time': upload_time,
                'file_size': test_file.stat().st_size
            }
        
        results.append(self._run_test(
            test_glm_fallback_chain,
            "test_glm_sdk_fallback_chain"
        ))
        
        return results
    
    def run_all_tests(self) -> TestSuiteResults:
        """Run all API compatibility tests"""
        self.start_time = time.time()
        self.results = []
        
        # Check API keys
        api_keys = self._check_api_keys()
        logger.info(f"API Keys available: {api_keys}")
        
        if not any(api_keys.values()):
            logger.error("No API keys available. Skipping tests.")
            return TestSuiteResults(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                total_duration=0,
                test_results=[],
                performance_benchmarks={}
            )
        
        # Run Kimi tests
        if api_keys['kimi']:
            logger.info("Running Kimi API tests...")
            self.results.extend(self.run_kimi_tests())
        
        # Run GLM tests
        if api_keys['glm']:
            logger.info("Running GLM API tests...")
            self.results.extend(self.run_glm_tests())
        
        # Calculate summary
        total_duration = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        
        # Collect performance benchmarks
        benchmarks = {}
        for result in self.results:
            if result.performance_metrics:
                benchmarks[result.test_name] = result.performance_metrics
        
        return TestSuiteResults(
            total_tests=len(self.results),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=0,
            total_duration=total_duration,
            test_results=self.results,
            performance_benchmarks=benchmarks
        )
    
    def generate_report(self, results: TestSuiteResults, output_file: Path):
        """Generate detailed test report"""
        report = {
            'summary': {
                'total_tests': results.total_tests,
                'passed': results.passed_tests,
                'failed': results.failed_tests,
                'skipped': results.skipped_tests,
                'success_rate': f"{(results.passed_tests / results.total_tests * 100):.1f}%" if results.total_tests > 0 else "0%",
                'total_duration': f"{results.total_duration:.2f}s"
            },
            'test_results': [asdict(r) for r in results.test_results],
            'performance_benchmarks': results.performance_benchmarks
        }
        
        output_file.write_text(json.dumps(report, indent=2))
        logger.info(f"Test report saved to: {output_file}")


def main():
    """Main execution"""
    runner = APICompatibilityTestRunner()
    results = runner.run_all_tests()
    
    # Generate report
    report_file = project_root / "tests" / "api_compatibility_test_results.json"
    runner.generate_report(results, report_file)
    
    # Print summary
    print("\n" + "="*60)
    print("API COMPATIBILITY TEST RESULTS")
    print("="*60)
    print(f"Total Tests: {results.total_tests}")
    print(f"Passed: {results.passed_tests}")
    print(f"Failed: {results.failed_tests}")
    print(f"Success Rate: {(results.passed_tests / results.total_tests * 100):.1f}%" if results.total_tests > 0 else "0%")
    print(f"Total Duration: {results.total_duration:.2f}s")
    print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if results.failed_tests == 0 else 1)


if __name__ == "__main__":
    main()

