"""
Result Collector - Collect and aggregate test results

Collects:
- Test results
- Statistics
- Coverage matrix
- Failure analysis

Created: 2025-10-05
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResultCollector:
    """
    Collect and aggregate test results.
    
    Features:
    - Collect test results
    - Calculate statistics
    - Generate coverage matrix
    - Analyze failures
    - Save results to disk
    """
    
    def __init__(self, results_dir: str = "./tool_validation_suite/results/latest"):
        """Initialize the result collector."""
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Results storage
        self.results = {
            "session_start": datetime.utcnow().isoformat() + "Z",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "pass_rate": 0.0
            },
            "coverage": {},
            "failures": []
        }
        
        logger.info("Result collector initialized")
    
    def add_result(
        self,
        tool_name: str,
        variation: str,
        status: str,
        duration_secs: float,
        validation: Dict[str, Any],
        watcher_observation: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Add a test result.
        
        Args:
            tool_name: Tool name
            variation: Test variation
            status: Test status (passed/failed/skipped)
            duration_secs: Test duration
            validation: Validation result
            watcher_observation: GLM watcher observation
            performance_metrics: Performance metrics
            error: Error message if failed
        """
        result = {
            "tool": tool_name,
            "variation": variation,
            "status": status,
            "duration_secs": duration_secs,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "validation": validation,
            "watcher_observation": watcher_observation,
            "performance_metrics": performance_metrics,
            "error": error
        }
        
        self.results["tests"].append(result)
        
        # Update summary
        self.results["summary"]["total"] += 1
        
        if status == "passed":
            self.results["summary"]["passed"] += 1
        elif status == "failed":
            self.results["summary"]["failed"] += 1
            self.results["failures"].append(result)
        elif status == "skipped":
            self.results["summary"]["skipped"] += 1
        
        # Update pass rate
        total = self.results["summary"]["total"]
        passed = self.results["summary"]["passed"]
        self.results["summary"]["pass_rate"] = (passed / total * 100) if total > 0 else 0
        
        # Update coverage
        if tool_name not in self.results["coverage"]:
            self.results["coverage"][tool_name] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "variations": {}
            }
        
        self.results["coverage"][tool_name]["total"] += 1
        
        if status == "passed":
            self.results["coverage"][tool_name]["passed"] += 1
        elif status == "failed":
            self.results["coverage"][tool_name]["failed"] += 1
        
        self.results["coverage"][tool_name]["variations"][variation] = status
        
        # Save results
        self.save()
        
        logger.info(f"Added result: {tool_name}/{variation} - {status}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get results summary."""
        return {
            "session_start": self.results["session_start"],
            "total_tests": self.results["summary"]["total"],
            "passed": self.results["summary"]["passed"],
            "failed": self.results["summary"]["failed"],
            "skipped": self.results["summary"]["skipped"],
            "pass_rate": self.results["summary"]["pass_rate"],
            "total_tools": len(self.results["coverage"]),
            "tools_fully_passed": sum(1 for t in self.results["coverage"].values() if t["failed"] == 0 and t["total"] > 0),
            "tools_with_failures": sum(1 for t in self.results["coverage"].values() if t["failed"] > 0)
        }
    
    def get_coverage_matrix(self) -> Dict[str, Any]:
        """Get coverage matrix."""
        return self.results["coverage"]
    
    def get_failures(self) -> List[Dict[str, Any]]:
        """Get all failures."""
        return self.results["failures"]
    
    def get_failure_analysis(self) -> Dict[str, Any]:
        """Analyze failures."""
        if not self.results["failures"]:
            return {
                "total_failures": 0,
                "failure_rate": 0.0,
                "common_errors": [],
                "tools_with_most_failures": []
            }
        
        # Count errors
        error_counts = {}
        for failure in self.results["failures"]:
            error = failure.get("error", "Unknown error")
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Sort by count
        common_errors = sorted(
            [{"error": k, "count": v} for k, v in error_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        # Tools with most failures
        tool_failures = {}
        for failure in self.results["failures"]:
            tool = failure["tool"]
            tool_failures[tool] = tool_failures.get(tool, 0) + 1
        
        tools_with_most_failures = sorted(
            [{"tool": k, "failures": v} for k, v in tool_failures.items()],
            key=lambda x: x["failures"],
            reverse=True
        )[:10]
        
        return {
            "total_failures": len(self.results["failures"]),
            "failure_rate": (len(self.results["failures"]) / self.results["summary"]["total"] * 100) if self.results["summary"]["total"] > 0 else 0,
            "common_errors": common_errors,
            "tools_with_most_failures": tools_with_most_failures
        }
    
    def save(self):
        """Save results to disk."""
        try:
            # Save full results
            results_file = self.results_dir / "test_results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            # Save summary
            summary_file = self.results_dir / "summary.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(self.get_summary(), f, indent=2, ensure_ascii=False)
            
            # Save coverage matrix
            coverage_file = self.results_dir / "coverage_matrix.json"
            with open(coverage_file, "w", encoding="utf-8") as f:
                json.dump(self.get_coverage_matrix(), f, indent=2, ensure_ascii=False)
            
            # Save failure analysis
            if self.results["failures"]:
                failures_file = self.results_dir / "failures.json"
                with open(failures_file, "w", encoding="utf-8") as f:
                    json.dump(self.get_failure_analysis(), f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved results to {self.results_dir}")
        
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_summary(self):
        """Print summary to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("  TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"\nTotal Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ({summary['pass_rate']:.1f}%)")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        
        print(f"\nTools Tested: {summary['total_tools']}")
        print(f"Tools Fully Passed: {summary['tools_fully_passed']}")
        print(f"Tools with Failures: {summary['tools_with_failures']}")
        
        if self.results["failures"]:
            print("\n" + "-"*60)
            print("  FAILURE ANALYSIS")
            print("-"*60)
            
            analysis = self.get_failure_analysis()
            
            print(f"\nTotal Failures: {analysis['total_failures']}")
            print(f"Failure Rate: {analysis['failure_rate']:.1f}%")
            
            if analysis["common_errors"]:
                print("\nMost Common Errors:")
                for i, error in enumerate(analysis["common_errors"][:5], 1):
                    print(f"  {i}. {error['error']} ({error['count']} times)")
            
            if analysis["tools_with_most_failures"]:
                print("\nTools with Most Failures:")
                for i, tool in enumerate(analysis["tools_with_most_failures"][:5], 1):
                    print(f"  {i}. {tool['tool']} ({tool['failures']} failures)")
        
        print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    collector = ResultCollector()
    
    # Add some test results
    collector.add_result(
        tool_name="chat",
        variation="basic_functionality",
        status="passed",
        duration_secs=2.5,
        validation={"valid": True, "checks": {}}
    )
    
    collector.add_result(
        tool_name="chat",
        variation="web_search",
        status="failed",
        duration_secs=5.0,
        validation={"valid": False, "errors": ["Timeout"]},
        error="Request timeout"
    )
    
    # Print summary
    collector.print_summary()

