"""
Report Generator - Generate comprehensive test reports

Generates:
- Markdown reports
- Coverage matrices
- Failure analysis
- Cost reports
- Feature usage reports

Created: 2025-10-05
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate comprehensive test reports.
    
    Generates:
    - Executive summary
    - Detailed test results
    - Coverage matrix
    - Failure analysis
    - Cost analysis
    - Feature usage analysis
    - Performance analysis
    """
    
    def __init__(self, results_dir: str = "./tool_validation_suite/results/latest"):
        """Initialize the report generator."""
        self.results_dir = Path(results_dir)
        self.reports_dir = self.results_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Report generator initialized")
    
    def generate_all_reports(self, results: Dict[str, Any]):
        """Generate all reports."""
        logger.info("Generating all reports...")
        
        # Generate markdown report
        self.generate_markdown_report(results)
        
        # Generate coverage matrix
        self.generate_coverage_matrix_report(results)
        
        # Generate failure analysis
        if results.get("failures"):
            self.generate_failure_analysis_report(results)
        
        # Generate cost report
        self.generate_cost_report(results)
        
        # Generate feature usage report
        self.generate_feature_usage_report(results)
        
        logger.info(f"All reports generated in {self.reports_dir}")
    
    def generate_markdown_report(self, results: Dict[str, Any]):
        """Generate comprehensive markdown report."""
        summary = results.get("summary", {})
        prompt_counter = results.get("prompt_counter", {})
        performance = results.get("performance", {})
        
        report = []
        report.append("# Tool Validation Suite - Test Report\n")
        report.append(f"**Generated:** {datetime.utcnow().isoformat()}Z\n")
        report.append("---\n\n")
        
        # Executive Summary
        report.append("## 📊 Executive Summary\n\n")
        report.append(f"- **Total Tests:** {summary.get('total_tests', 0)}\n")
        report.append(f"- **Passed:** {summary.get('passed', 0)} ({summary.get('pass_rate', 0):.1f}%)\n")
        report.append(f"- **Failed:** {summary.get('failed', 0)}\n")
        report.append(f"- **Skipped:** {summary.get('skipped', 0)}\n")
        report.append(f"- **Tools Tested:** {summary.get('total_tools', 0)}\n")
        report.append(f"- **Tools Fully Passed:** {summary.get('tools_fully_passed', 0)}\n\n")
        
        # Prompt Counter Summary
        report.append("## 🔢 Prompt Counter Summary\n\n")
        report.append(f"- **Total Prompts:** {prompt_counter.get('total_prompts', 0)}\n")
        
        prompts_by_provider = prompt_counter.get('prompts_by_provider', {})
        report.append(f"- **Kimi Prompts:** {prompts_by_provider.get('kimi', 0)}\n")
        report.append(f"- **GLM Prompts:** {prompts_by_provider.get('glm', 0)}\n")
        report.append(f"- **Watcher Prompts:** {prompts_by_provider.get('watcher', 0)}\n\n")
        
        # Feature Usage
        feature_usage = prompt_counter.get('feature_usage', {})
        report.append("### Feature Usage\n\n")
        report.append(f"- **Web Search:** {feature_usage.get('web_search', {}).get('total', 0)}\n")
        report.append(f"- **File Upload:** {feature_usage.get('file_upload', {}).get('total', 0)}\n")
        report.append(f"- **Thinking Mode:** {feature_usage.get('thinking_mode', {}).get('total', 0)}\n")
        report.append(f"- **Tool Use:** {feature_usage.get('tool_use', {}).get('total', 0)}\n\n")
        
        # Cost Summary
        cost_tracking = prompt_counter.get('cost_tracking', {})
        report.append("## 💰 Cost Summary\n\n")
        report.append(f"- **Total Cost:** ${cost_tracking.get('total_cost_usd', 0):.4f} USD\n")
        
        by_provider = cost_tracking.get('by_provider', {})
        report.append(f"- **Kimi Cost:** ${by_provider.get('kimi', 0):.4f}\n")
        report.append(f"- **GLM Cost:** ${by_provider.get('glm', 0):.4f}\n")
        report.append(f"- **Watcher Cost:** ${by_provider.get('watcher', 0):.4f}\n\n")
        
        # Performance Summary
        report.append("## ⚡ Performance Summary\n\n")
        report.append(f"- **Average Duration:** {performance.get('avg_duration_secs', 0):.2f}s\n")
        report.append(f"- **Max Duration:** {performance.get('max_duration_secs', 0):.2f}s\n")
        report.append(f"- **Min Duration:** {performance.get('min_duration_secs', 0):.2f}s\n\n")
        
        if performance.get('avg_memory_mb', 0) > 0:
            report.append(f"- **Average Memory:** {performance.get('avg_memory_mb', 0):.1f} MB\n")
            report.append(f"- **Max Memory:** {performance.get('max_memory_mb', 0):.1f} MB\n\n")
        
        # Coverage Matrix
        report.append("## 📋 Coverage Matrix\n\n")
        coverage = results.get('coverage', {})
        
        if coverage:
            report.append("| Tool | Total | Passed | Failed | Pass Rate |\n")
            report.append("|------|-------|--------|--------|----------|\n")
            
            for tool_name, tool_coverage in sorted(coverage.items()):
                total = tool_coverage.get('total', 0)
                passed = tool_coverage.get('passed', 0)
                failed = tool_coverage.get('failed', 0)
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                status_emoji = "✅" if failed == 0 else "❌"
                report.append(f"| {status_emoji} {tool_name} | {total} | {passed} | {failed} | {pass_rate:.1f}% |\n")
            
            report.append("\n")
        
        # Failure Summary
        failure_analysis = results.get('failure_analysis', {})
        if failure_analysis.get('total_failures', 0) > 0:
            report.append("## ❌ Failure Analysis\n\n")
            report.append(f"- **Total Failures:** {failure_analysis.get('total_failures', 0)}\n")
            report.append(f"- **Failure Rate:** {failure_analysis.get('failure_rate', 0):.1f}%\n\n")
            
            common_errors = failure_analysis.get('common_errors', [])
            if common_errors:
                report.append("### Most Common Errors\n\n")
                for i, error in enumerate(common_errors[:5], 1):
                    report.append(f"{i}. **{error['error']}** ({error['count']} occurrences)\n")
                report.append("\n")
            
            tools_with_failures = failure_analysis.get('tools_with_most_failures', [])
            if tools_with_failures:
                report.append("### Tools with Most Failures\n\n")
                for i, tool in enumerate(tools_with_failures[:5], 1):
                    report.append(f"{i}. **{tool['tool']}** ({tool['failures']} failures)\n")
                report.append("\n")
        
        # Save report
        report_file = self.reports_dir / "test_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("".join(report))
        
        logger.info(f"Generated markdown report: {report_file}")
    
    def generate_coverage_matrix_report(self, results: Dict[str, Any]):
        """Generate detailed coverage matrix."""
        coverage = results.get('coverage', {})
        
        report = []
        report.append("# Coverage Matrix - Detailed View\n\n")
        
        for tool_name, tool_coverage in sorted(coverage.items()):
            report.append(f"## {tool_name}\n\n")
            report.append(f"- **Total Tests:** {tool_coverage.get('total', 0)}\n")
            report.append(f"- **Passed:** {tool_coverage.get('passed', 0)}\n")
            report.append(f"- **Failed:** {tool_coverage.get('failed', 0)}\n\n")
            
            variations = tool_coverage.get('variations', {})
            if variations:
                report.append("### Variations\n\n")
                report.append("| Variation | Status |\n")
                report.append("|-----------|--------|\n")
                
                for variation, status in sorted(variations.items()):
                    emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⏭️"
                    report.append(f"| {variation} | {emoji} {status} |\n")
                
                report.append("\n")
        
        # Save report
        report_file = self.reports_dir / "coverage_matrix.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("".join(report))
        
        logger.info(f"Generated coverage matrix: {report_file}")
    
    def generate_failure_analysis_report(self, results: Dict[str, Any]):
        """Generate detailed failure analysis."""
        failures = results.get('failures', [])
        
        report = []
        report.append("# Failure Analysis - Detailed View\n\n")
        report.append(f"**Total Failures:** {len(failures)}\n\n")
        
        for i, failure in enumerate(failures, 1):
            report.append(f"## Failure #{i}: {failure['tool']}/{failure['variation']}\n\n")
            report.append(f"- **Error:** {failure.get('error', 'Unknown')}\n")
            report.append(f"- **Duration:** {failure.get('duration_secs', 0):.2f}s\n")
            report.append(f"- **Timestamp:** {failure.get('timestamp', 'Unknown')}\n\n")
            
            validation = failure.get('validation', {})
            if validation.get('errors'):
                report.append("### Validation Errors\n\n")
                for error in validation['errors']:
                    report.append(f"- {error}\n")
                report.append("\n")
        
        # Save report
        report_file = self.reports_dir / "failure_analysis.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("".join(report))
        
        logger.info(f"Generated failure analysis: {report_file}")
    
    def generate_cost_report(self, results: Dict[str, Any]):
        """Generate cost analysis report."""
        prompt_counter = results.get('prompt_counter', {})
        cost_tracking = prompt_counter.get('cost_tracking', {})
        
        report = []
        report.append("# Cost Analysis Report\n\n")
        report.append(f"**Total Cost:** ${cost_tracking.get('total_cost_usd', 0):.4f} USD\n\n")
        
        # By provider
        report.append("## Cost by Provider\n\n")
        by_provider = cost_tracking.get('by_provider', {})
        for provider, cost in sorted(by_provider.items()):
            report.append(f"- **{provider.capitalize()}:** ${cost:.4f}\n")
        report.append("\n")
        
        # By feature
        report.append("## Cost by Feature\n\n")
        by_feature = cost_tracking.get('by_feature', {})
        for feature, cost in sorted(by_feature.items()):
            report.append(f"- **{feature.replace('_', ' ').title()}:** ${cost:.4f}\n")
        report.append("\n")
        
        # Save report
        report_file = self.reports_dir / "cost_analysis.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("".join(report))
        
        logger.info(f"Generated cost report: {report_file}")
    
    def generate_feature_usage_report(self, results: Dict[str, Any]):
        """Generate feature usage report."""
        prompt_counter = results.get('prompt_counter', {})
        feature_usage = prompt_counter.get('feature_usage', {})
        
        report = []
        report.append("# Feature Usage Report\n\n")
        
        # Web Search
        web_search = feature_usage.get('web_search', {})
        report.append("## Web Search\n\n")
        report.append(f"- **Total:** {web_search.get('total', 0)}\n")
        report.append(f"- **Kimi:** {web_search.get('kimi', 0)}\n")
        report.append(f"- **GLM:** {web_search.get('glm', 0)}\n\n")
        
        # File Upload
        file_upload = feature_usage.get('file_upload', {})
        report.append("## File Upload\n\n")
        report.append(f"- **Total:** {file_upload.get('total', 0)}\n")
        report.append(f"- **Kimi:** {file_upload.get('kimi', 0)}\n")
        report.append(f"- **GLM:** {file_upload.get('glm', 0)}\n\n")
        
        # Thinking Mode
        thinking_mode = feature_usage.get('thinking_mode', {})
        report.append("## Thinking Mode\n\n")
        report.append(f"- **Total:** {thinking_mode.get('total', 0)}\n")
        report.append(f"- **Basic:** {thinking_mode.get('basic', 0)}\n")
        report.append(f"- **Deep:** {thinking_mode.get('deep', 0)}\n")
        report.append(f"- **Expert:** {thinking_mode.get('expert', 0)}\n\n")
        
        # Tool Use
        tool_use = feature_usage.get('tool_use', {})
        report.append("## Tool Use\n\n")
        report.append(f"- **Total:** {tool_use.get('total', 0)}\n")
        report.append(f"- **Kimi:** {tool_use.get('kimi', 0)}\n")
        report.append(f"- **GLM:** {tool_use.get('glm', 0)}\n\n")
        
        # Save report
        report_file = self.reports_dir / "feature_usage.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("".join(report))
        
        logger.info(f"Generated feature usage report: {report_file}")


# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    
    # Load results
    results_file = Path("tool_validation_suite/results/latest/test_results.json")
    if results_file.exists():
        with open(results_file, "r") as f:
            results = json.load(f)
        
        # Generate all reports
        generator.generate_all_reports(results)
    else:
        print("No results found")

