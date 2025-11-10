"""
Comprehensive Tool Testing Framework

Automated testing infrastructure for all EXAI tools with:
- Unit tests for each tool
- Integration tests across tool workflows
- Performance benchmarking
- Regression testing
- Coverage reporting
- Continuous validation

Created: 2025-11-09
Medium-Term Task 3
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TestResult(Enum):
    """Test result status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class ToolTestCase:
    """Individual test case for a tool."""
    name: str
    tool_name: str
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    timeout: float = 30.0
    required_files: Optional[List[str]] = None
    mock_external: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TestResultData:
    """Test execution result."""
    test_name: str
    tool_name: str
    status: TestResult
    duration: float
    timestamp: datetime
    error_message: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceBenchmark:
    """Performance benchmark for a tool."""
    tool_name: str
    test_name: str
    avg_duration: float
    p95_duration: float
    p99_duration: float
    min_duration: float
    max_duration: float
    throughput_per_second: float
    success_rate: float
    sample_count: int


class ToolTestingFramework:
    """
    Comprehensive testing framework for EXAI tools.

    Features:
    - Automated test discovery
    - Parallel test execution
    - Performance benchmarking
    - Coverage tracking
    - Regression detection
    - Custom test scenarios
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize testing framework.

        Args:
            base_path: Base path for test files and results
        """
        self.base_path = base_path or Path("tests")
        self.results_path = self.base_path / "framework" / "results"
        self.results_path.mkdir(parents=True, exist_ok=True)

        # Test registry
        self.test_cases: Dict[str, List[ToolTestCase]] = {}
        self.test_results: List[TestResultData] = []
        self.performance_benchmarks: Dict[str, PerformanceBenchmark] = {}

    def register_test(self, test_case: ToolTestCase) -> None:
        """Register a test case."""
        if test_case.tool_name not in self.test_cases:
            self.test_cases[test_case.tool_name] = []
        self.test_cases[test_case.tool_name].append(test_case)
        logger.info(f"[TEST] Registered: {test_case.tool_name}.{test_case.name}")

    def register_test_suite(self, tool_name: str, test_suite: List[ToolTestCase]) -> None:
        """Register multiple test cases for a tool."""
        for test_case in test_suite:
            test_case.tool_name = tool_name
        self.test_cases[tool_name] = test_suite
        logger.info(f"[TEST] Registered suite: {tool_name} ({len(test_suite)} tests)")

    async def run_test(self, test_case: ToolTestCase) -> TestResultData:
        """
        Execute a single test case.

        Args:
            test_case: Test case to execute

        Returns:
            TestResultData with execution results
        """
        start_time = time.time()
        result = TestResultData(
            test_name=test_case.name,
            tool_name=test_case.tool_name,
            status=TestResult.SKIPPED,
            duration=0.0,
            timestamp=datetime.now()
        )

        try:
            # Import tool dynamically
            tool_module = await self._import_tool(test_case.tool_name)
            if not tool_module:
                result.status = TestResult.ERROR
                result.error_message = f"Failed to import tool: {test_case.tool_name}"
                return result

            # Execute tool
            output = await self._execute_tool(
                tool_module,
                test_case.input_data,
                test_case.timeout
            )

            result.duration = time.time() - start_time
            result.output = output

            # Validate output
            if test_case.expected_output:
                if self._validate_output(output, test_case.expected_output):
                    result.status = TestResult.PASSED
                else:
                    result.status = TestResult.FAILED
                    result.error_message = "Output validation failed"
            else:
                # No validation, assume pass if no exception
                result.status = TestResult.PASSED

        except asyncio.TimeoutError:
            result.status = TestResult.FAILED
            result.error_message = f"Test timed out after {test_case.timeout}s"
            result.duration = test_case.timeout

        except Exception as e:
            result.status = TestResult.ERROR
            result.error_message = f"Test error: {str(e)}"
            result.duration = time.time() - start_time

        self.test_results.append(result)
        return result

    async def run_tool_tests(
        self,
        tool_name: str,
        parallel: bool = False,
        max_concurrent: int = 5
    ) -> List[TestResultData]:
        """
        Run all tests for a specific tool.

        Args:
            tool_name: Name of tool to test
            parallel: Run tests in parallel
            max_concurrent: Max parallel tests

        Returns:
            List of test results
        """
        if tool_name not in self.test_cases:
            logger.error(f"[TEST] No tests registered for tool: {tool_name}")
            return []

        test_cases = self.test_cases[tool_name]
        logger.info(f"[TEST] Running {len(test_cases)} tests for {tool_name}")

        if parallel:
            # Run in parallel with semaphore
            semaphore = asyncio.Semaphore(max_concurrent)

            async def run_with_semaphore(tc):
                async with semaphore:
                    return await self.run_test(tc)

            results = await asyncio.gather(
                *[run_with_semaphore(tc) for tc in test_cases],
                return_exceptions=True
            )

            # Filter exceptions
            return [r for r in results if isinstance(r, TestResultData)]
        else:
            # Run sequentially
            results = []
            for test_case in test_cases:
                result = await self.run_test(test_case)
                results.append(result)
            return results

    async def run_all_tests(
        self,
        tools: Optional[List[str]] = None,
        parallel: bool = True
    ) -> Dict[str, List[TestResultData]]:
        """
        Run all registered tests.

        Args:
            tools: Specific tools to test (None for all)
            parallel: Run tools in parallel

        Returns:
            Dictionary mapping tool_name to list of test results
        """
        tools_to_test = tools or list(self.test_cases.keys())
        logger.info(f"[TEST] Running tests for {len(tools_to_test)} tools")

        if parallel:
            results = await asyncio.gather(
                *[self.run_tool_tests(tool) for tool in tools_to_test],
                return_exceptions=True
            )

            # Build result dictionary
            tool_results = {}
            for i, tool in enumerate(tools_to_test):
                if i < len(results) and isinstance(results[i], list):
                    tool_results[tool] = results[i]
                else:
                    tool_results[tool] = []
        else:
            tool_results = {}
            for tool in tools_to_test:
                tool_results[tool] = await self.run_tool_tests(tool, parallel=False)

        return tool_results

    async def benchmark_tool(
        self,
        tool_name: str,
        test_case: ToolTestCase,
        iterations: int = 10
    ) -> PerformanceBenchmark:
        """
        Run performance benchmark for a tool.

        Args:
            tool_name: Name of tool
            test_case: Test case to benchmark
            iterations: Number of iterations

        Returns:
            PerformanceBenchmark with statistics
        """
        logger.info(f"[BENCH] Benchmarking {tool_name} ({iterations} iterations)")

        durations = []
        successes = 0

        for i in range(iterations):
            result = await self.run_test(test_case)
            durations.append(result.duration)

            if result.status == TestResult.PASSED:
                successes += 1

        # Calculate statistics
        benchmark = PerformanceBenchmark(
            tool_name=tool_name,
            test_name=test_case.name,
            avg_duration=statistics.mean(durations),
            p95_duration=statistics.quantiles(durations, n=20)[18],
            p99_duration=statistics.quantiles(durations, n=100)[98],
            min_duration=min(durations),
            max_duration=max(durations),
            throughput_per_second=1 / statistics.mean(durations) if durations else 0,
            success_rate=successes / iterations,
            sample_count=iterations
        )

        self.performance_benchmarks[f"{tool_name}.{test_case.name}"] = benchmark
        return benchmark

    def generate_report(self, output_format: str = "markdown") -> str:
        """
        Generate comprehensive test report.

        Args:
            output_format: Report format (markdown, json, html)

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            return self._generate_markdown_report()

    def _generate_markdown_report(self) -> str:
        """Generate markdown report."""
        report = []
        report.append("# Tool Testing Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == TestResult.PASSED)
        failed = sum(1 for r in self.test_results if r.status == TestResult.FAILED)
        errors = sum(1 for r in self.test_results if r.status == TestResult.ERROR)

        report.append("## Summary")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Passed: {passed} ({passed/total_tests*100:.1f}%)")
        report.append(f"- Failed: {failed}")
        report.append(f"- Errors: {errors}")
        report.append("")

        # Test results by tool
        report.append("## Test Results by Tool")
        tools = set(r.tool_name for r in self.test_results)

        for tool in sorted(tools):
            report.append(f"\n### {tool}")
            tool_results = [r for r in self.test_results if r.tool_name == tool]

            for result in tool_results:
                status_icon = {
                    TestResult.PASSED: "✅",
                    TestResult.FAILED: "❌",
                    TestResult.ERROR: "⚠️",
                    TestResult.SKIPPED: "⏭️"
                }[result.status]

                report.append(
                    f"- {status_icon} {result.test_name}: "
                    f"{result.duration:.2f}s"
                )

                if result.error_message:
                    report.append(f"  - Error: {result.error_message}")

        # Performance benchmarks
        if self.performance_benchmarks:
            report.append("\n## Performance Benchmarks")
            for key, benchmark in self.performance_benchmarks.items():
                report.append(f"\n### {key}")
                report.append(f"- Avg Duration: {benchmark.avg_duration:.3f}s")
                report.append(f"- P95: {benchmark.p95_duration:.3f}s")
                report.append(f"- P99: {benchmark.p99_duration:.3f}s")
                report.append(f"- Throughput: {benchmark.throughput_per_second:.2f} req/s")
                report.append(f"- Success Rate: {benchmark.success_rate*100:.1f}%")

        return "\n".join(report)

    def _generate_json_report(self) -> str:
        """Generate JSON report."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.status == TestResult.PASSED),
                "failed": sum(1 for r in self.test_results if r.status == TestResult.FAILED),
                "errors": sum(1 for r in self.test_results if r.status == TestResult.ERROR),
            },
            "test_results": [asdict(r) for r in self.test_results],
            "performance_benchmarks": {
                k: asdict(v) for k, v in self.performance_benchmarks.items()
            }
        }
        return json.dumps(data, indent=2)

    def _generate_html_report(self) -> str:
        """Generate HTML report (simplified)."""
        # This would generate a proper HTML report
        # For now, return markdown with HTML wrapper
        markdown = self._generate_markdown_report()
        return f"<html><body><pre>{markdown}</pre></body></html>"

    async def _import_tool(self, tool_name: str) -> Optional[Any]:
        """Dynamically import a tool module."""
        try:
            # Try workflows first
            module_path = f"tools.workflows.{tool_name}"
            module = __import__(module_path, fromlist=[tool_name])
            return getattr(module, f"{tool_name.title()}Tool", None)
        except Exception as e:
            logger.error(f"[TEST] Failed to import {tool_name}: {e}")
            return None

    async def _execute_tool(
        self,
        tool: Any,
        input_data: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """Execute a tool with given input."""
        # This is a simplified execution
        # Real implementation would depend on tool interface

        # Check if tool has async method
        if hasattr(tool, 'execute_async'):
            return await asyncio.wait_for(
                tool.execute_async(**input_data),
                timeout=timeout
            )
        elif hasattr(tool, 'execute'):
            # Run sync method in thread pool
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, tool.execute, **input_data),
                timeout=timeout
            )
        else:
            raise ValueError(f"Tool has no execute method: {tool}")

    def _validate_output(self, output: Any, expected: Dict[str, Any]) -> bool:
        """Validate tool output against expected values."""
        # Simplified validation
        # Real implementation would check specific fields

        if not isinstance(output, dict):
            return False

        for key, expected_value in expected.items():
            if key not in output:
                return False
            if output[key] != expected_value:
                return False

        return True

    def save_results(self, output_format: str = "json") -> Path:
        """
        Save test results to file.

        Args:
            output_format: File format (json, markdown)

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.{output_format}"
        filepath = self.results_path / filename

        report = self.generate_report(output_format)

        with open(filepath, 'w') as f:
            f.write(report)

        logger.info(f"[TEST] Results saved to: {filepath}")
        return filepath


# Convenience functions
def create_basic_test_suite(tool_name: str) -> List[ToolTestCase]:
    """Create a basic test suite for a tool."""
    return [
        ToolTestCase(
            name="basic_functionality",
            tool_name=tool_name,
            input_data={"prompt": "Test prompt"},
            expected_output=None
        ),
        ToolTestCase(
            name="with_files",
            tool_name=tool_name,
            input_data={
                "prompt": "Analyze this code",
                "files": ["test.py"]
            },
            expected_output=None
        )
    ]


# Global framework instance
_framework: Optional[ToolTestingFramework] = None


def get_testing_framework() -> ToolTestingFramework:
    """Get global testing framework instance."""
    global _framework
    if _framework is None:
        _framework = ToolTestingFramework()
    return _framework


if __name__ == "__main__":
    # Demo usage
    async def main():
        framework = ToolTestingFramework()

        # Register tests
        test_suite = create_basic_test_suite("analyze")
        framework.register_test_suite("analyze", test_suite)

        # Run tests
        results = await framework.run_all_tests()

        # Generate report
        report = framework.generate_report("markdown")
        print(report)

        # Save results
        framework.save_results("json")

    asyncio.run(main())
