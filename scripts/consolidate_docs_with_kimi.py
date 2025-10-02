#!/usr/bin/env python3
"""
Kimi-Powered Documentation Consolidation Script

Uses Kimi API with best practices to consolidate 300+ markdown files:
- Batch processing (10-15 files per call)
- Structured prompts with role/context
- Priority order (current → upgrades → architecture → archive)
- Quality assurance with human review

Usage:
    python scripts/consolidate_docs_with_kimi.py --phase 1
    python scripts/consolidate_docs_with_kimi.py --phase 2
    python scripts/consolidate_docs_with_kimi.py --phase 3
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KimiDocsConsolidator:
    """Consolidate documentation using Kimi API with best practices."""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.batch_size = 15  # Kimi best practice: 10-15 files per call
        self.results = []
    
    def scan_docs(self, target_dir: str) -> List[Path]:
        """Scan target directory for markdown files."""
        target_path = self.docs_root / target_dir
        if not target_path.exists():
            logger.warning(f"Target directory does not exist: {target_path}")
            return []
        
        md_files = list(target_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files in {target_dir}")
        return md_files
    
    def batch_files(self, files: List[Path]) -> List[List[Path]]:
        """Split files into batches of batch_size."""
        batches = []
        for i in range(0, len(files), self.batch_size):
            batches.append(files[i:i + self.batch_size])
        logger.info(f"Created {len(batches)} batches of up to {self.batch_size} files each")
        return batches
    
    def analyze_batch_with_kimi(self, batch: List[Path], batch_num: int) -> Dict:
        """
        Analyze a batch of files using Kimi multi-file chat.
        
        Uses best practices:
        - Role setting: "You are a documentation architect"
        - Context setting: Project type, design intent
        - Structured output: JSON with consolidation actions
        """
        from tools.providers.kimi.kimi_upload import KimiMultiFileChatTool
        
        logger.info(f"Analyzing batch {batch_num} ({len(batch)} files)...")
        
        # Prepare structured prompt
        prompt = f"""You are a documentation architect analyzing EX-AI-MCP-Server documentation.

**PROJECT CONTEXT:**
- Type: MCP server for AI model integration (GLM + Kimi providers)
- Design Intent: Clean, concise, aligned with current architecture
- Current State: 300+ markdown files with duplication and superseded content

**YOUR TASK:**
Analyze these {len(batch)} documentation files and identify:

1. **Superseded Content** - Files that are outdated or replaced
2. **Duplicate Content** - Files covering the same topic
3. **Consolidation Opportunities** - Related files that should be merged
4. **Alignment Issues** - Content not matching current design intent

**OUTPUT FORMAT (JSON):**
```json
{{
  "batch_number": {batch_num},
  "files_analyzed": {len(batch)},
  "superseded": [
    {{"file": "path/to/file.md", "reason": "Replaced by X", "action": "delete"}}
  ],
  "duplicates": [
    {{"files": ["file1.md", "file2.md"], "reason": "Same topic", "action": "merge into file1.md"}}
  ],
  "consolidation": [
    {{"files": ["a.md", "b.md", "c.md"], "target": "consolidated.md", "reason": "Related content"}}
  ],
  "alignment_issues": [
    {{"file": "file.md", "issue": "References old architecture", "action": "update or delete"}}
  ],
  "keep_as_is": ["file.md"],
  "confidence": "high|medium|low"
}}
```

**GUIDELINES:**
- Be conservative - when in doubt, mark for human review
- Prioritize clarity and conciseness
- Align with current architecture (GLM + Kimi, manager-first routing)
- Flag anything referencing superseded designs

Analyze the files and provide your JSON response."""

        # Call Kimi
        kimi_tool = KimiMultiFileChatTool()
        result = kimi_tool.run(
            files=[str(f) for f in batch],
            prompt=prompt,
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
            logger.info(f"✅ Batch {batch_num} analyzed successfully")
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from Kimi response: {e}")
            logger.error(f"Raw content: {content[:500]}...")
            return {
                "batch_number": batch_num,
                "error": str(e),
                "raw_response": content
            }
    
    def phase1_quick_win(self):
        """Phase 1: Quick Win - Consolidate docs/upgrades/international-users/"""
        logger.info("=" * 80)
        logger.info("PHASE 1: QUICK WIN - International Users Docs")
        logger.info("=" * 80)
        
        files = self.scan_docs("upgrades/international-users")
        batches = self.batch_files(files)
        
        results = []
        for i, batch in enumerate(batches, 1):
            result = self.analyze_batch_with_kimi(batch, i)
            results.append(result)
        
        # Save results
        output_file = self.docs_root / "upgrades" / "international-users" / "CONSOLIDATION_ANALYSIS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Phase 1 complete! Results saved to: {output_file}")
        logger.info(f"   Analyzed {len(files)} files in {len(batches)} batches")
        
        return results
    
    def phase2_architecture_cleanup(self):
        """Phase 2: Architecture Cleanup - Merge docs/architecture/ and docs/current/architecture/"""
        logger.info("=" * 80)
        logger.info("PHASE 2: ARCHITECTURE CLEANUP")
        logger.info("=" * 80)
        
        # Scan both directories
        arch_files = self.scan_docs("architecture")
        current_arch_files = self.scan_docs("current/architecture")
        
        all_files = arch_files + current_arch_files
        batches = self.batch_files(all_files)
        
        results = []
        for i, batch in enumerate(batches, 1):
            result = self.analyze_batch_with_kimi(batch, i)
            results.append(result)
        
        # Save results
        output_file = self.docs_root / "ARCHITECTURE_CONSOLIDATION_ANALYSIS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Phase 2 complete! Results saved to: {output_file}")
        logger.info(f"   Analyzed {len(all_files)} files in {len(batches)} batches")
        
        return results
    
    def phase3_archive_cleanup(self):
        """Phase 3: Archive Cleanup - Verify docs/archive/superseded/ can be deleted"""
        logger.info("=" * 80)
        logger.info("PHASE 3: ARCHIVE CLEANUP")
        logger.info("=" * 80)
        
        files = self.scan_docs("archive/superseded")
        batches = self.batch_files(files)
        
        results = []
        for i, batch in enumerate(batches, 1):
            result = self.analyze_batch_with_kimi(batch, i)
            results.append(result)
        
        # Save results
        output_file = self.docs_root / "archive" / "ARCHIVE_CLEANUP_ANALYSIS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Phase 3 complete! Results saved to: {output_file}")
        logger.info(f"   Analyzed {len(files)} files in {len(batches)} batches")
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Consolidate documentation using Kimi API")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True,
                        help="Phase to run: 1=Quick Win, 2=Architecture, 3=Archive")
    args = parser.parse_args()
    
    docs_root = PROJECT_ROOT / "docs"
    consolidator = KimiDocsConsolidator(docs_root)
    
    if args.phase == 1:
        consolidator.phase1_quick_win()
    elif args.phase == 2:
        consolidator.phase2_architecture_cleanup()
    elif args.phase == 3:
        consolidator.phase3_archive_cleanup()


if __name__ == "__main__":
    main()

