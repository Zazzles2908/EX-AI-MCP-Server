"""
Test Runner - Main orchestration engine for test execution

Orchestrates:
- Test execution
- Retry logic
- Timeout handling
- Progress reporting
- Result collection

Created: 2025-10-05
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .api_client import APIClient
from .conversation_tracker import ConversationTracker
from .file_uploader import FileUploader
from .glm_watcher import GLMWatcher
from .performance_monitor import PerformanceMonitor
from .prompt_counter import PromptCounter
from .response_validator import ResponseValidator
from .result_collector import ResultCollector

logger = logging.getLogger(__name__)


class TestRunner:
    """
    Main test orchestration engine.
    
    Features:
    - Execute tests with all variations
    - Handle retries and timeouts
    - Collect results
    - Monitor performance
    - Generate reports
    """
    
    def __init__(self):
        """Initialize the test runner."""
        # Configuration
        self.max_retries = int(os.getenv("MAX_RETRIES", "2"))
        self.test_timeout = int(os.getenv("TEST_TIMEOUT_SECS", "300"))
        self.retry_delay = int(os.getenv("RETRY_DELAY_SECS", "5"))
        
        # Initialize components
        self.prompt_counter = PromptCounter()
        self.api_client = APIClient(prompt_counter=self.prompt_counter)
        self.conversation_tracker = ConversationTracker()
        self.file_uploader = FileUploader()
        self.watcher = GLMWatcher()
        self.performance_monitor = PerformanceMonitor()
        self.response_validator = ResponseValidator()
        self.result_collector = ResultCollector()
        
        logger.info("Test runner initialized")
    
    def run_test(
        self,
        tool_name: str,
        variation: str,
        test_func: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a single test with retries and monitoring.
        
        Args:
            tool_name: Tool name
            variation: Test variation
            test_func: Test function to execute
            **kwargs: Additional arguments for test function
        
        Returns:
            Test result dictionary
        """
        test_id = f"{tool_name}_{variation}_{int(time.time())}"
        
        logger.info(f"Running test: {tool_name}/{variation}")
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring(test_id)
        
        # Retry loop
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                # Execute test
                result = test_func(
                    api_client=self.api_client,
                    conversation_tracker=self.conversation_tracker,
                    file_uploader=self.file_uploader,
                    **kwargs
                )
                
                # Validate response
                validation = self.response_validator.validate_response(
                    result,
                    tool_type=kwargs.get("tool_type", "simple")
                )
                
                # Get watcher observation
                watcher_observation = None
                if os.getenv("ENABLE_GLM_WATCHER", "true").lower() == "true":
                    try:
                        watcher_observation = self.watcher.observe_test(
                            tool_name=tool_name,
                            variation_name=variation,
                            test_input=kwargs.get("test_input", {}),
                            expected_behavior=kwargs.get("expected_behavior", ""),
                            actual_output=result,
                            performance_metrics=self.performance_monitor.get_metrics(test_id),
                            test_status="passed" if validation["valid"] else "failed"
                        )
                    except Exception as e:
                        logger.warning(f"Watcher observation failed: {e}")
                
                # Stop performance monitoring
                performance_metrics = self.performance_monitor.stop_monitoring(test_id)
                
                # Determine status
                status = "passed" if validation["valid"] else "failed"
                
                # Collect result
                self.result_collector.add_result(
                    tool_name=tool_name,
                    variation=variation,
                    status=status,
                    duration_secs=performance_metrics.get("duration_secs", 0),
                    validation=validation,
                    watcher_observation=watcher_observation,
                    performance_metrics=performance_metrics,
                    error=None if validation["valid"] else "; ".join(validation.get("errors", []))
                )
                
                logger.info(f"Test {status}: {tool_name}/{variation}")
                
                return {
                    "tool": tool_name,
                    "variation": variation,
                    "status": status,
                    "result": result,
                    "validation": validation,
                    "watcher_observation": watcher_observation,
                    "performance_metrics": performance_metrics
                }
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Test failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    # Final failure
                    performance_metrics = self.performance_monitor.stop_monitoring(test_id)
                    
                    self.result_collector.add_result(
                        tool_name=tool_name,
                        variation=variation,
                        status="failed",
                        duration_secs=performance_metrics.get("duration_secs", 0),
                        validation={"valid": False, "errors": [last_error]},
                        watcher_observation=None,
                        performance_metrics=performance_metrics,
                        error=last_error
                    )
                    
                    return {
                        "tool": tool_name,
                        "variation": variation,
                        "status": "failed",
                        "error": last_error,
                        "performance_metrics": performance_metrics
                    }
    
    def run_test_suite(
        self,
        test_suite: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run a suite of tests.
        
        Args:
            test_suite: List of test configurations
            progress_callback: Optional callback for progress updates
        
        Returns:
            Suite results
        """
        total_tests = len(test_suite)
        logger.info(f"Running test suite: {total_tests} tests")
        
        for i, test_config in enumerate(test_suite, 1):
            # Progress update
            if progress_callback:
                progress_callback(i, total_tests, test_config)
            else:
                logger.info(f"Progress: {i}/{total_tests} ({i/total_tests*100:.1f}%)")
            
            # Run test
            self.run_test(**test_config)
        
        # Get final results
        summary = self.result_collector.get_summary()
        
        logger.info(f"Test suite complete: {summary['passed']}/{summary['total_tests']} passed ({summary['pass_rate']:.1f}%)")
        
        return summary
    
    def get_results(self) -> Dict[str, Any]:
        """Get all results."""
        return {
            "summary": self.result_collector.get_summary(),
            "coverage": self.result_collector.get_coverage_matrix(),
            "failures": self.result_collector.get_failures(),
            "failure_analysis": self.result_collector.get_failure_analysis(),
            "prompt_counter": self.prompt_counter.get_summary(),
            "performance": self.performance_monitor.get_summary()
        }
    
    def print_results(self):
        """Print results to console."""
        self.result_collector.print_summary()
        self.prompt_counter.print_summary()

        perf_summary = self.performance_monitor.get_summary()

        print("\n" + "="*60)
        print("  PERFORMANCE SUMMARY")
        print("="*60)
        print(f"\nAverage Duration: {perf_summary['avg_duration_secs']:.2f}s")
        print(f"Max Duration: {perf_summary['max_duration_secs']:.2f}s")
        print(f"Min Duration: {perf_summary['min_duration_secs']:.2f}s")

        if perf_summary.get("avg_memory_mb", 0) > 0:
            print(f"\nAverage Memory: {perf_summary['avg_memory_mb']:.1f} MB")
            print(f"Max Memory: {perf_summary['max_memory_mb']:.1f} MB")

        if perf_summary.get("avg_cpu_percent", 0) > 0:
            print(f"\nAverage CPU: {perf_summary['avg_cpu_percent']:.1f}%")
            print(f"Max CPU: {perf_summary['max_cpu_percent']:.1f}%")

        if perf_summary.get("total_alerts", 0) > 0:
            print(f"\nTotal Alerts: {perf_summary['total_alerts']}")

        print("\n" + "="*60 + "\n")

    def get_results_dir(self) -> Path:
        """Get the results directory path."""
        results_dir = Path(os.getenv("TEST_RESULTS_DIR", "./tool_validation_suite/results/latest"))
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir

    def generate_report(self):
        """Generate and save test report."""
        from .report_generator import ReportGenerator

        results = self.get_results()
        results_dir = self.get_results_dir()

        # Save JSON results
        results_file = results_dir / "test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {results_file}")

        # Generate reports using ReportGenerator
        try:
            report_gen = ReportGenerator()
            report_gen.generate_all_reports(results)
            logger.info("Reports generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")

        return results_file


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    runner = TestRunner()
    
    # Example test function
    def test_chat_basic(api_client, **kwargs):
        return api_client.call_kimi(
            model="kimi-k2-0905-preview",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            tool_name="chat",
            variation="basic_functionality"
        )
    
    # Run single test
    result = runner.run_test(
        tool_name="chat",
        variation="basic_functionality",
        test_func=test_chat_basic,
        tool_type="simple",
        test_input={"message": "Hello, how are you?"},
        expected_behavior="Friendly greeting response"
    )
    
    # Print results
    runner.print_results()

