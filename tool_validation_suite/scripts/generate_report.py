"""
Generate Report - Create comprehensive validation reports

This script generates reports from test results:
- Markdown summary report
- Coverage matrix report
- Failure analysis report
- Cost breakdown report
- Feature usage report
- GLM Watcher insights report

Usage:
    python scripts/generate_report.py [--results-file path] [--format markdown|json|html]

Created: 2025-10-05
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_results(results_file):
    """Load test results from file."""
    if not results_file.exists():
        logger.error(f"Results file not found: {results_file}")
        return None
    
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load results: {e}")
        return None


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Generate validation reports")
    parser.add_argument(
        "--results-file",
        type=Path,
        default=Path("tool_validation_suite/results/latest/final_results.json"),
        help="Path to results JSON file"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html", "all"],
        default="all",
        help="Report format"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tool_validation_suite/results/latest/reports"),
        help="Output directory for reports"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    print("\n" + "="*60)
    print("  REPORT GENERATOR")
    print("="*60)
    print(f"Results File: {args.results_file}")
    print(f"Format: {args.format}")
    print(f"Output Dir: {args.output_dir}")
    print("="*60 + "\n")
    
    # Load results
    logger.info(f"Loading results from: {args.results_file}")
    results = load_results(args.results_file)
    
    if not results:
        print("❌ Failed to load results")
        sys.exit(1)
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize report generator
    logger.info("Initializing report generator...")
    report_gen = ReportGenerator()
    
    try:
        # Generate reports based on format
        if args.format in ["markdown", "all"]:
            logger.info("Generating markdown reports...")
            
            # Summary report
            summary_file = args.output_dir / "summary_report.md"
            summary_md = report_gen.generate_summary_report(results)
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary_md)
            print(f"✅ Summary report: {summary_file}")
            
            # Coverage matrix
            coverage_file = args.output_dir / "coverage_matrix.md"
            coverage_md = report_gen.generate_coverage_matrix(results)
            with open(coverage_file, "w", encoding="utf-8") as f:
                f.write(coverage_md)
            print(f"✅ Coverage matrix: {coverage_file}")
            
            # Failure analysis
            failure_file = args.output_dir / "failure_analysis.md"
            failure_md = report_gen.generate_failure_analysis(results)
            with open(failure_file, "w", encoding="utf-8") as f:
                f.write(failure_md)
            print(f"✅ Failure analysis: {failure_file}")
            
            # Cost breakdown
            cost_file = args.output_dir / "cost_breakdown.md"
            cost_md = report_gen.generate_cost_report(results)
            with open(cost_file, "w", encoding="utf-8") as f:
                f.write(cost_md)
            print(f"✅ Cost breakdown: {cost_file}")
            
            # Feature usage
            feature_file = args.output_dir / "feature_usage.md"
            feature_md = report_gen.generate_feature_usage_report(results)
            with open(feature_file, "w", encoding="utf-8") as f:
                f.write(feature_md)
            print(f"✅ Feature usage: {feature_file}")
        
        if args.format in ["json", "all"]:
            logger.info("Generating JSON reports...")
            
            # Full results JSON
            json_file = args.output_dir / "full_results.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Full results JSON: {json_file}")
            
            # Statistics JSON
            stats_file = args.output_dir / "statistics.json"
            stats = {
                "summary": results.get("summary", {}),
                "prompt_counter": results.get("prompt_counter", {}),
                "performance": results.get("performance", {})
            }
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"✅ Statistics JSON: {stats_file}")
        
        if args.format in ["html", "all"]:
            logger.info("HTML reports not yet implemented")
            print("⚠️  HTML reports: Not yet implemented")
        
        # Print summary
        print("\n" + "="*60)
        print("  REPORT GENERATION COMPLETE")
        print("="*60)
        
        summary = results.get("summary", {})
        print(f"\nTests Run: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Pass Rate: {summary.get('pass_rate', 0):.1f}%")
        
        prompt_counter = results.get("prompt_counter", {})
        cost_tracking = prompt_counter.get("cost_tracking", {})
        print(f"\nTotal Cost: ${cost_tracking.get('total_cost_usd', 0):.4f}")
        
        print(f"\n✅ All reports generated successfully!")
        print(f"Reports available in: {args.output_dir}")
        
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"\n❌ Report generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

