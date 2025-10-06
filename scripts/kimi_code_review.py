#!/usr/bin/env python3
"""
Kimi-Powered Python Code Review Script

Uses Kimi API to review all Python scripts that run the EX-AI-MCP-Server project.
Uploads system-reference/ docs as context for design intent, then analyzes Python code.

Usage:
    python scripts/kimi_code_review.py --target src
    python scripts/kimi_code_review.py --target tools
    python scripts/kimi_code_review.py --target all
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Disable file cache to avoid 404 errors from stale file IDs
os.environ["FILECACHE_ENABLED"] = "false"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KimiCodeReviewer:
    """Review Python code using Kimi API with system-reference as design intent context."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.batch_size = 5  # Reduced from 10 to avoid file upload limits
        self.results = []
        self.design_context_file = None
        self.cache_id = None  # Track cache across batches for 84-96% cost savings

    def cleanup_kimi_files(self) -> None:
        """
        Delete all previously uploaded files from Kimi platform.

        This ensures fresh file content is reviewed instead of cached versions.
        Kimi platform caches uploaded files by file_id, so we must delete old
        files before uploading new ones to ensure the latest code is reviewed.

        Reference: https://platform.moonshot.ai/docs/guide/use-kimi-api-for-file-based-qa#best-practices-for-file-management
        """
        logger.info("🧹 Cleaning up old files from Kimi platform...")

        try:
            from src.providers.kimi import KimiModelProvider
            from src.providers.registry import ModelProviderRegistry

            # Get Kimi provider
            provider = ModelProviderRegistry.get_provider("KIMI")
            if not provider:
                logger.warning("⚠️  Kimi provider not available, skipping cleanup")
                return

            # Get the SDK client
            client = provider._get_client()

            # List all files
            try:
                response = client.files.list()
                files = response.data if hasattr(response, 'data') else []
            except AttributeError:
                # Handle different SDK versions
                files = response if isinstance(response, list) else []

            if not files:
                logger.info("✅ No files to clean up")
                return

            logger.info(f"📋 Found {len(files)} file(s) to delete")

            # Delete each file
            deleted_count = 0
            failed_count = 0

            for file in files:
                try:
                    file_id = file.id if hasattr(file, 'id') else file.get('id')
                    file_name = file.filename if hasattr(file, 'filename') else file.get('filename', 'unknown')

                    if file_id:
                        client.files.delete(file_id)
                        deleted_count += 1
                        logger.info(f"  ✓ Deleted: {file_name} ({file_id[:12]}...)")
                    else:
                        logger.warning(f"  ⚠️  Skipping file with no ID: {file_name}")
                        failed_count += 1

                except Exception as e:
                    failed_count += 1
                    logger.warning(f"  ✗ Failed to delete file: {e}")

            logger.info(f"✅ Cleanup complete: {deleted_count} deleted, {failed_count} failed")

        except ImportError as e:
            logger.warning(f"⚠️  Could not import Kimi provider: {e}")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            logger.warning("⚠️  Continuing with review despite cleanup failure...")

    def upload_design_context(self) -> str:
        """
        Upload consolidated design context file to Kimi and return file path.
        Initializes cache_id for Moonshot context caching (75% cost savings on cached input).

        Cost Optimization:
        - Cache Miss: $0.60/M tokens
        - Cache Hit: $0.15/M tokens (75% savings)
        - With 35k design context: ~$0.021 first batch, ~$0.005 subsequent batches
        """
        logger.info("📚 Uploading consolidated design context to Kimi...")

        # Use existing consolidated file
        context_file = self.project_root / "docs" / "KIMI_DESIGN_CONTEXT.md"

        if not context_file.exists():
            logger.error(f"Design context file not found: {context_file}")
            raise FileNotFoundError(f"Design context file not found: {context_file}")

        # Generate cache ID for this review session (Moonshot context caching)
        import time
        self.cache_id = f"design_context_{int(time.time())}"

        logger.info(f"✅ Design context file ready: {context_file}")
        logger.info(f"   File size: {context_file.stat().st_size / 1024:.2f} KB")
        logger.info(f"   Contains: All 36 system-reference/ markdown files")
        logger.info(f"🔑 Cache ID: {self.cache_id} (enables 75% cost savings on cached input)")

        return str(context_file)
    
    def scan_python_files(self, target_dir: str) -> List[Path]:
        """Scan target directory for Python files."""
        target_path = self.project_root / target_dir
        if not target_path.exists():
            logger.warning(f"Target directory does not exist: {target_path}")
            return []
        
        py_files = list(target_path.rglob("*.py"))
        # Exclude __pycache__ and test files
        py_files = [f for f in py_files if "__pycache__" not in str(f) and "test_" not in f.name]
        
        logger.info(f"Found {len(py_files)} Python files in {target_dir}")
        return py_files
    
    def batch_files(self, files: List[Path]) -> List[List[Path]]:
        """Split files into batches of batch_size."""
        batches = []
        for i in range(0, len(files), self.batch_size):
            batches.append(files[i:i + self.batch_size])
        logger.info(f"Created {len(batches)} batches of up to {self.batch_size} files each")
        return batches

    def _parse_markdown_review(self, content: str, batch_num: int, files_count: int) -> Dict:
        """Parse markdown review response into structured JSON."""
        import re

        result = {
            "batch_number": batch_num,
            "files_reviewed": files_count,
            "findings": [],
            "good_patterns": [],
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overall_quality": "unknown"
            }
        }

        # Extract findings
        findings_section = re.search(r'## Findings\s+(.*?)(?=## |$)', content, re.DOTALL)
        if findings_section:
            findings_text = findings_section.group(1)
            # Match each finding (### SEVERITY: Title)
            for finding_match in re.finditer(r'### (\w+):\s*(.+?)\n\*\*File:\*\*\s*(.+?)\n\*\*Lines:\*\*\s*(.+?)\n\*\*Category:\*\*\s*(\w+)\s*\n\*\*Issue:\*\*\s*(.+?)\n\*\*Recommendation:\*\*\s*(.+?)(?=\n###|\n##|$)', findings_text, re.DOTALL):
                severity = finding_match.group(1).lower()
                file = finding_match.group(3).strip()
                lines_str = finding_match.group(4).strip()
                category = finding_match.group(5).strip()
                issue = finding_match.group(6).strip()
                recommendation = finding_match.group(7).strip()

                # Parse line numbers
                line_numbers = [int(x.strip()) for x in lines_str.split(',') if x.strip().isdigit()]

                result["findings"].append({
                    "file": file,
                    "severity": severity,
                    "category": category,
                    "issue": issue,
                    "recommendation": recommendation,
                    "line_numbers": line_numbers
                })

                # Update summary counts
                result["summary"]["total_issues"] += 1
                if severity in result["summary"]:
                    result["summary"][severity] += 1

        # Extract good patterns
        patterns_section = re.search(r'## Good Patterns\s+(.*?)(?=## |$)', content, re.DOTALL)
        if patterns_section:
            patterns_text = patterns_section.group(1)
            for pattern_match in re.finditer(r'### (.+?)\n\*\*File:\*\*\s*(.+?)\n\*\*Reason:\*\*\s*(.+?)(?=\n###|\n##|$)', patterns_text, re.DOTALL):
                result["good_patterns"].append({
                    "pattern": pattern_match.group(1).strip(),
                    "file": pattern_match.group(2).strip(),
                    "reason": pattern_match.group(3).strip()
                })

        # Extract summary
        summary_section = re.search(r'## Summary\s+(.*?)$', content, re.DOTALL)
        if summary_section:
            summary_text = summary_section.group(1)
            # Parse summary lines
            total_match = re.search(r'Total issues:\s*(\d+)', summary_text, re.IGNORECASE)
            if total_match:
                result["summary"]["total_issues"] = int(total_match.group(1))

            for severity in ["critical", "high", "medium", "low"]:
                severity_match = re.search(rf'{severity}:\s*(\d+)', summary_text, re.IGNORECASE)
                if severity_match:
                    result["summary"][severity] = int(severity_match.group(1))

            quality_match = re.search(r'Overall quality:\s*(\w+)', summary_text, re.IGNORECASE)
            if quality_match:
                result["summary"]["overall_quality"] = quality_match.group(1).lower()

        return result
    
    def review_batch_with_kimi(self, batch: List[Path], batch_num: int) -> Dict:
        """
        Review a batch of Python files using Kimi with design context.
        """
        from tools.providers.kimi.kimi_upload import KimiMultiFileChatTool

        logger.info(f"🔍 Reviewing batch {batch_num} ({len(batch)} files)...")

        # Validate files
        valid_files = []
        for f in batch:
            if f.exists() and f.stat().st_size > 0:
                valid_files.append(f)
            else:
                logger.warning(f"Skipping invalid file: {f}")

        if not valid_files:
            logger.warning(f"Batch {batch_num} has no valid files, skipping")
            return {
                "batch_number": batch_num,
                "files_reviewed": 0,
                "error": "No valid files in batch"
            }

        # Prepare structured prompt
        prompt = f"""You are a senior Python code reviewer analyzing the EX-AI-MCP-Server codebase.

**IMPORTANT:** Please respond ONLY in English. All findings, recommendations, and explanations must be in English.

**DESIGN CONTEXT:**
You have access to the complete system-reference/ documentation which describes:
- System architecture (GLM + Kimi providers, manager-first routing)
- Provider implementation patterns (dual SDK/HTTP fallback)
- Tool ecosystem (16 EXAI tools: simple-tools + workflow-tools)
- Features (streaming, web search, multimodal, caching, tool calling)
- API endpoints and best practices

**YOUR TASK:**
Review these {len(batch)} Python files for:

1. **Architecture Alignment** - Does code match system-reference design?
2. **Code Quality** - Clean, maintainable, well-documented?
3. **Best Practices** - Following Python/async/error handling best practices?
4. **Security** - Any security concerns (API keys, input validation)?
5. **Performance** - Any obvious performance issues?
6. **Dead Code** - Unused imports, functions, or legacy code?
7. **Consistency** - Consistent with other files in the project?

**OUTPUT FORMAT (MARKDOWN):**

Use this exact markdown structure:

```markdown
# Batch {batch_num} Code Review

## Files Reviewed
- file1.py
- file2.py
- file3.py

## Findings

### CRITICAL: Issue title
**File:** path/to/file.py
**Lines:** 10, 20, 30
**Category:** security
**Issue:** Detailed description of the issue
**Recommendation:** How to fix it

### HIGH: Another issue
**File:** path/to/file.py
**Lines:** 45
**Category:** architecture
**Issue:** Description
**Recommendation:** Fix recommendation

## Good Patterns

### Pattern name
**File:** path/to/file.py
**Reason:** Why this is good and worth replicating

## Summary
- Total issues: 7
- Critical: 0
- High: 2
- Medium: 3
- Low: 2
- Overall quality: good
```

**GUIDELINES:**
- Reference system-reference/ docs when checking architecture alignment
- Be specific with line numbers and code examples
- Prioritize critical/high severity issues
- Identify good patterns worth replicating
- Consider maintainability and future scalability
- Use markdown code blocks for code examples (they won't break the format)

Review the files and provide your markdown response."""

        # Call Kimi with design context file + code files
        kimi_tool = KimiMultiFileChatTool()
        all_files = [self.design_context_file] + [str(f) for f in valid_files]

        # Model selection: kimi-k2-0905-preview is optimal for code review
        # - 256K context window (largest available)
        # - $0.60/M input (cache miss), $0.15/M input (cache hit), $2.50/M output
        # - Enhanced agentic coding capabilities
        # - 75% cost savings on cached input vs cache miss
        review_model = os.getenv("KIMI_REVIEW_MODEL", "kimi-k2-0905-preview")

        logger.info(f"Uploading {len(all_files)} files (1 design context + {len(valid_files)} code files)")
        logger.info(f"🤖 Using model: {review_model} (256K context, $0.15/M cached input)")

        result = kimi_tool.run(
            files=all_files,
            prompt=prompt,
            model=review_model,
            temperature=0.3,
            cache_id=self.cache_id,  # Reuse cache across batches (75% cost savings)
            reset_cache_ttl=True,    # Keep cache alive for subsequent batches
        )
        
        # Parse markdown response
        try:
            content = result.get("content", "")

            # Save raw response for debugging (ALWAYS save to see what Kimi returns)
            debug_file = self.project_root / "docs" / f"KIMI_RAW_BATCH_{batch_num}.md"
            debug_file.write_text(content, encoding='utf-8')
            logger.info(f"📝 Raw response saved to: {debug_file}")

            # Parse markdown to extract structured data
            analysis = self._parse_markdown_review(content, batch_num, len(valid_files))

            logger.info(f"✅ Batch {batch_num} reviewed successfully")

            # Log summary
            summary = analysis.get("summary", {})
            logger.info(f"   Quality: {summary.get('overall_quality', 'N/A')}")
            logger.info(f"   Issues: {summary.get('total_issues', 0)} "
                       f"(Critical: {summary.get('critical', 0)}, "
                       f"High: {summary.get('high', 0)}, "
                       f"Medium: {summary.get('medium', 0)}, "
                       f"Low: {summary.get('low', 0)})")
            logger.info(f"   Findings extracted: {len(analysis.get('findings', []))}")

            return analysis
        except Exception as e:
            logger.error(f"❌ Failed to parse markdown from Kimi response: {e}")

            # Save raw response to file for manual review
            error_file = self.project_root / "docs" / f"KIMI_ERROR_BATCH_{batch_num}.txt"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Batch {batch_num} - Markdown Parse Error\n")
                f.write(f"Error: {e}\n")
                f.write(f"=" * 80 + "\n\n")
                f.write(content)

            logger.warning(f"⚠️  Raw response saved to: {error_file}")
            logger.warning(f"⚠️  Batch {batch_num} will be marked as error, continuing with next batch...")

            return {
                "batch_number": batch_num,
                "files_reviewed": len(valid_files),
                "error": f"Markdown parse error: {str(e)}",
                "error_file": str(error_file),
                "raw_response_preview": content[:500] + "..." if len(content) > 500 else content
            }
    
    def review_target(self, target: str):
        """Review Python files in target directory."""
        logger.info("=" * 80)
        logger.info(f"KIMI CODE REVIEW: {target.upper()}")
        logger.info("=" * 80)

        # Clean up old files from Kimi platform FIRST
        # This ensures fresh file content is reviewed instead of cached versions
        self.cleanup_kimi_files()

        # Create consolidated design context first
        self.design_context_file = self.upload_design_context()
        
        # Scan Python files
        files = self.scan_python_files(target)
        if not files:
            logger.warning(f"No Python files found in {target}")
            return []
        
        batches = self.batch_files(files)
        
        results = []
        for i, batch in enumerate(batches, 1):
            result = self.review_batch_with_kimi(batch, i)
            results.append(result)
        
        # Save results
        output_file = self.project_root / "docs" / f"KIMI_CODE_REVIEW_{target.replace('/', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Review complete! Results saved to: {output_file}")
        logger.info(f"   Reviewed {len(files)} files in {len(batches)} batches")
        
        # Print summary
        total_issues = sum(r.get("summary", {}).get("total_issues", 0) for r in results)
        critical = sum(r.get("summary", {}).get("critical", 0) for r in results)
        high = sum(r.get("summary", {}).get("high", 0) for r in results)
        
        logger.info(f"\n📊 OVERALL SUMMARY:")
        logger.info(f"   Total Issues: {total_issues}")
        logger.info(f"   Critical: {critical}")
        logger.info(f"   High: {high}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Review Python code using Kimi API")
    parser.add_argument("--target", type=str, required=True,
                        help="Target to review: src, tools, scripts, or all")
    args = parser.parse_args()
    
    reviewer = KimiCodeReviewer(PROJECT_ROOT)
    
    if args.target == "all":
        # Review all major directories
        for target in ["src", "tools", "scripts"]:
            reviewer.review_target(target)
    else:
        reviewer.review_target(args.target)


if __name__ == "__main__":
    main()

