#!/usr/bin/env python3
"""
Batch Analysis of Archive Documentation

Uploads all markdown files from archive/ directory to Kimi and performs
comprehensive batch analysis to identify completed work, remaining tasks,
and content issues.

EXAI Consultation: d2134189-41c9-4e97-821c-409a06aac5a7
Strategy: Upload all files, analyze in batches of 8, aggregate results
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
# FIX (2025-10-30): Detect environment and use correct project root
print(f"DEBUG: Checking /mnt/project/EX-AI-MCP-Server exists: {os.path.exists('/mnt/project/EX-AI-MCP-Server')}")
print(f"DEBUG: Checking /mnt/project exists: {os.path.exists('/mnt/project')}")
print(f"DEBUG: __file__ = {__file__}")

if os.path.exists('/mnt/project/EX-AI-MCP-Server'):
    # Running in Docker - files are at /mnt/project/EX-AI-MCP-Server
    project_root = Path('/mnt/project/EX-AI-MCP-Server')
    sys.path.insert(0, '/app')  # Python modules are at /app
    print(f"DEBUG: Using Docker path: {project_root}")
else:
    # Running on Windows host - use script location
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    print(f"DEBUG: Using Windows path: {project_root}")

from tools.smart_file_query import SmartFileQueryTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArchiveBatchAnalyzer:
    """Batch analyzer for archive documentation using smart_file_query"""

    def __init__(self, archive_dir: str, batch_size: int = 8):
        self.archive_dir = Path(archive_dir)
        self.batch_size = batch_size
        self.smart_query_tool = SmartFileQueryTool()

        # Results storage
        self.batch_results: List[Dict[str, Any]] = []
        self.markdown_files: List[Path] = []
        
    def collect_markdown_files(self) -> List[Path]:
        """Collect all markdown files from archive directory"""
        logger.info(f"Collecting markdown files from {self.archive_dir}")

        if not self.archive_dir.exists():
            raise FileNotFoundError(f"Archive directory not found: {self.archive_dir}")

        # Collect files as Path objects (smart_file_query handles path conversion)
        markdown_files = sorted(self.archive_dir.glob("*.md"))

        logger.info(f"Found {len(markdown_files)} markdown files")
        self.markdown_files = markdown_files
        return markdown_files
    
    def create_batches(self) -> List[List[Path]]:
        """Split files into batches"""
        batches = [
            self.markdown_files[i:i + self.batch_size]
            for i in range(0, len(self.markdown_files), self.batch_size)
        ]
        logger.info(f"Created {len(batches)} batches of up to {self.batch_size} files each")
        return batches
    
    async def analyze_batch(self, batch_num: int, batch_files: List[Path]) -> Dict[str, Any]:
        """Analyze a single batch of files using smart_file_query"""
        logger.info(f"Analyzing batch {batch_num} ({len(batch_files)} files)...")

        # Get filenames for logging
        filenames = [f.name for f in batch_files]

        # Create comprehensive analysis prompt
        prompt = f"""Analyze these {len(batch_files)} markdown files from the archive and provide a structured report:

**FILES IN THIS BATCH:**
{chr(10).join(f'- {fname}' for fname in filenames)}

**COMPLETED WORK:**
List each completed item with:
- Brief description
- Evidence (file name, section)
- Confidence level (High/Medium/Low)

**REMAINING WORK:**
Identify gaps and missing elements:
- What's explicitly mentioned as TODO/incomplete
- What's implied but not implemented
- Dependencies that aren't addressed

**CONTENT ISSUES:**
- Duplicates/redundant content (cross-reference files)
- Unverified claims or missing evidence
- Inconsistencies between files

**RECOMMENDATIONS:**
Priority actions needed to complete the work

Format as markdown with clear sections."""

        try:
            # Analyze each file individually and aggregate
            # (smart_file_query works with one file at a time)
            file_analyses = []

            for file_path in batch_files:
                logger.info(f"  Analyzing {file_path.name}...")

                # Use absolute path - smart_file_query now handles universal path conversion
                abs_path = str(file_path.absolute())

                result = await self.smart_query_tool._run_async(
                    file_path=abs_path,
                    question=f"Summarize this document focusing on: completed work, remaining work, and any issues or unverified claims.",
                    provider="kimi",
                    model="kimi-k2-0905-preview"
                )
                file_analyses.append(f"### {file_path.name}\n\n{result}")

            # Combine all analyses
            combined_analysis = "\n\n---\n\n".join(file_analyses)

            logger.info(f"✅ Batch {batch_num} analysis complete")

            return {
                "batch_num": batch_num,
                "file_count": len(batch_files),
                "files": filenames,
                "analysis": combined_analysis,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Batch {batch_num} analysis failed: {e}")
            return {
                "batch_num": batch_num,
                "file_count": len(batch_files),
                "files": filenames,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def save_batch_result(self, batch_result: Dict[str, Any], output_dir: Path):
        """Save individual batch result"""
        batch_num = batch_result['batch_num']

        # Use /app/docs for writable location (not /mnt/project which is read-only)
        if Path("/app/docs").exists():
            output_dir = Path("/app/docs/05_CURRENT_WORK/part2_2025-10-29")
            output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"batch_{batch_num}_analysis.md"
        
        content = f"""# Batch {batch_num} Analysis

**Files Analyzed:** {batch_result['file_count']}
**Timestamp:** {batch_result['timestamp']}

## Files in Batch
{chr(10).join(f'- {fname}' for fname in batch_result['files'])}

---

## Analysis Results

{batch_result.get('analysis', batch_result.get('error', 'No results'))}
"""
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"💾 Saved batch {batch_num} results to {output_file}")
    
    def aggregate_results(self, output_dir: Path):
        """Aggregate all batch results into master document"""
        logger.info("Aggregating results into master document...")

        # Use /app/docs for writable location (not /mnt/project which is read-only)
        if Path("/app/docs").exists():
            output_dir = Path("/app/docs/05_CURRENT_WORK/part2_2025-10-29")
            output_dir.mkdir(parents=True, exist_ok=True)

        master_file = output_dir / "MASTER_ARCHIVE_ANALYSIS.md"

        # Count successful vs failed batches
        successful = sum(1 for r in self.batch_results if 'analysis' in r)
        failed = len(self.batch_results) - successful

        content = f"""# Archive Documentation Analysis Report

**Generated:** {datetime.utcnow().isoformat()}
**Total Files:** {len(self.markdown_files)}
**Total Batches:** {len(self.batch_results)}
**Successful Batches:** {successful}
**Failed Batches:** {failed}

---

## Executive Summary

This report analyzes {len(self.markdown_files)} markdown files from the archive directory to identify:
- Completed work with evidence
- Remaining work and gaps
- Content issues (duplicates, unverified claims, inconsistencies)
- Priority recommendations

---

"""
        
        # Add each batch analysis
        for batch_result in self.batch_results:
            batch_num = batch_result['batch_num']
            content += f"""## Batch {batch_num} Analysis

**Files:** {batch_result['file_count']}
**Status:** {'✅ Success' if 'analysis' in batch_result else '❌ Failed'}

### Files in Batch
{chr(10).join(f'- {fname}' for fname in batch_result['files'])}

### Analysis
{batch_result.get('analysis', f"ERROR: {batch_result.get('error', 'Unknown error')}")}

---

"""
        
        # Add file inventory
        content += f"""## Appendix: File Inventory

**Total Files:** {len(self.markdown_files)}

{chr(10).join(f'{i+1}. {f.name}' for i, f in enumerate(sorted(self.markdown_files)))}

---

## Analysis Methodology

- **Tool:** smart_file_query (automatic deduplication + provider selection)
- **Batch Size:** {self.batch_size} files per batch
- **Model:** kimi-k2-0905-preview
- **Provider:** Kimi (Moonshot)
- **EXAI Consultation:** d2134189-41c9-4e97-821c-409a06aac5a7
"""
        
        master_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Master document saved to {master_file}")


async def main():
    """Main execution"""
    # Configuration
    logger.info(f"DEBUG: project_root = {project_root}")
    logger.info(f"DEBUG: __file__ = {__file__}")
    logger.info(f"DEBUG: /mnt/project exists = {os.path.exists('/mnt/project')}")

    archive_dir = project_root / "docs" / "05_CURRENT_WORK" / "part2_2025-10-29" / "archive"
    output_dir = project_root / "docs" / "05_CURRENT_WORK" / "part2_2025-10-29"
    batch_size = 8

    logger.info("=" * 80)
    logger.info("BATCH ARCHIVE ANALYSIS")
    logger.info("=" * 80)

    # Create analyzer
    analyzer = ArchiveBatchAnalyzer(archive_dir, batch_size)

    # Step 1: Collect files
    markdown_files = analyzer.collect_markdown_files()

    # Step 2: Create batches
    batches = analyzer.create_batches()

    # Step 3: Analyze each batch
    for i, batch in enumerate(batches, 1):
        batch_result = await analyzer.analyze_batch(i, batch)
        analyzer.batch_results.append(batch_result)
        analyzer.save_batch_result(batch_result, output_dir)

    # Step 4: Aggregate results
    analyzer.aggregate_results(output_dir)

    logger.info("=" * 80)
    logger.info("✅ BATCH ANALYSIS COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

