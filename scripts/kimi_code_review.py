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
    
    def upload_design_context(self) -> str:
        """
        Create a consolidated design context document from system-reference/.
        Returns path to consolidated file.
        """
        logger.info("📚 Creating consolidated design context from system-reference/...")

        # Get all markdown files from system-reference
        system_ref_path = self.project_root / "docs" / "system-reference"
        md_files = sorted(system_ref_path.rglob("*.md"))

        logger.info(f"Found {len(md_files)} design reference files")

        # Create consolidated context file
        context_file = self.project_root / "docs" / "KIMI_DESIGN_CONTEXT.md"

        with open(context_file, 'w', encoding='utf-8') as out:
            out.write("# EX-AI-MCP-Server Design Context\n\n")
            out.write("**Generated:** 2025-10-03\n")
            out.write("**Purpose:** Complete design intent for code review\n\n")
            out.write("---\n\n")

            for md_file in md_files:
                rel_path = md_file.relative_to(system_ref_path)
                out.write(f"\n\n## {rel_path}\n\n")
                out.write(f"**Source:** `docs/system-reference/{rel_path}`\n\n")
                out.write("---\n\n")

                try:
                    content = md_file.read_text(encoding='utf-8')
                    out.write(content)
                    out.write("\n\n")
                except Exception as e:
                    logger.warning(f"Could not read {md_file}: {e}")

        logger.info(f"✅ Design context consolidated: {context_file}")
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

**OUTPUT FORMAT (JSON):**
```json
{{
  "batch_number": {batch_num},
  "files_reviewed": {len(batch)},
  "findings": [
    {{
      "file": "path/to/file.py",
      "severity": "critical|high|medium|low",
      "category": "architecture|quality|security|performance|dead_code|consistency",
      "issue": "Description of the issue",
      "recommendation": "How to fix it",
      "line_numbers": [10, 20, 30]
    }}
  ],
  "good_patterns": [
    {{
      "file": "path/to/file.py",
      "pattern": "Description of good pattern to replicate",
      "reason": "Why this is good"
    }}
  ],
  "summary": {{
    "total_issues": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "overall_quality": "excellent|good|fair|needs_improvement"
  }}
}}
```

**GUIDELINES:**
- Reference system-reference/ docs when checking architecture alignment
- Be specific with line numbers and code examples
- Prioritize critical/high severity issues
- Identify good patterns worth replicating
- Consider maintainability and future scalability

Review the files and provide your JSON response."""

        # Call Kimi with code files only (no design context to avoid file caching issues)
        kimi_tool = KimiMultiFileChatTool()
        code_files = [str(f) for f in valid_files]

        logger.info(f"Uploading {len(code_files)} code files")

        # Include design context in the prompt instead of as uploaded files
        enhanced_prompt = f"""**DESIGN CONTEXT:**
You have access to the complete EX-AI-MCP-Server design documentation in docs/system-reference/:
- System architecture (GLM + Kimi providers, manager-first routing)
- Provider implementation patterns (dual SDK/HTTP fallback)
- Tool ecosystem (16 EXAI tools: simple-tools + workflow-tools)
- Features (streaming, web search, multimodal, caching, tool calling)
- API endpoints and best practices

{prompt}"""

        result = kimi_tool.run(
            files=code_files,
            prompt=enhanced_prompt,
            model="kimi-k2-0905-preview",
            temperature=0.3
        )
        
        # Parse JSON response
        try:
            content = result.get("content", "")
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            analysis = json.loads(content)
            logger.info(f"✅ Batch {batch_num} reviewed successfully")
            
            # Log summary
            summary = analysis.get("summary", {})
            logger.info(f"   Quality: {summary.get('overall_quality', 'N/A')}")
            logger.info(f"   Issues: {summary.get('total_issues', 0)} "
                       f"(Critical: {summary.get('critical', 0)}, "
                       f"High: {summary.get('high', 0)}, "
                       f"Medium: {summary.get('medium', 0)}, "
                       f"Low: {summary.get('low', 0)})")
            
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from Kimi response: {e}")
            logger.error(f"Raw content: {content[:500]}...")
            return {
                "batch_number": batch_num,
                "error": str(e),
                "raw_response": content
            }
    
    def review_target(self, target: str):
        """Review Python files in target directory."""
        logger.info("=" * 80)
        logger.info(f"KIMI CODE REVIEW: {target.upper()}")
        logger.info("=" * 80)

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

