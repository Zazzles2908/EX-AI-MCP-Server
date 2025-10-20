"""
Comprehensive EXAI codebase analysis using Kimi.

This script:
1. Scans all EXAI-related Python files (tools/workflow/, tools/providers/, src/)
2. Uploads them to Kimi in batches
3. Analyzes design intent, architecture, and implementation patterns
4. Generates comprehensive understanding of the EXAI system
5. Implements Moonshot file hygiene best practices:
   - Batch uploads (15 files per batch)
   - Progress saving after each batch
   - Automatic file cleanup after analysis
   - Prevents platform clutter

Reference: https://platform.moonshot.ai/docs/guide/use-kimi-api-for-file-based-qa#best-practices-for-file-management
"""
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExaiCodebaseAnalyzer:
    """Analyze EXAI codebase using Kimi multi-file chat."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.docs_root = self.project_root / "docs"
        self.uploaded_files = []  # Track uploaded file IDs for cleanup
    
    def scan_exai_files(self) -> List[Path]:
        """
        Scan for all EXAI-related Python files.
        
        Returns:
            List of Path objects for Python files
        """
        logger.info("Scanning for EXAI-related Python files...")
        
        # Target directories
        target_dirs = [
            "tools/workflow",
            "tools/providers",
            "tools/shared",
            "src/providers",
            "src/config",
            "src/server"
        ]
        
        all_files = []
        
        for dir_path in target_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                logger.warning(f"Directory not found: {full_path}")
                continue
            
            # Find all Python files
            py_files = list(full_path.rglob("*.py"))
            all_files.extend(py_files)
            logger.info(f"  - {dir_path}: {len(py_files)} files")
        
        logger.info(f"\nTotal Python files found: {len(all_files)}")
        return all_files
    
    def scan_design_docs(self) -> List[Path]:
        """
        Scan for design documentation that explains EXAI intent.
        
        Returns:
            List of Path objects for markdown files
        """
        logger.info("Scanning for design documentation...")
        
        # Target documentation folders
        doc_dirs = [
            "docs/current/architecture",
            "docs/current/tools",
            "docs/guides"
        ]
        
        all_docs = []
        
        for dir_path in doc_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                logger.warning(f"Directory not found: {full_path}")
                continue
            
            # Find all markdown files
            md_files = list(full_path.rglob("*.md"))
            all_docs.extend(md_files)
            logger.info(f"  - {dir_path}: {len(md_files)} files")
        
        logger.info(f"\nTotal documentation files found: {len(all_docs)}")
        return all_docs
    
    def batch_files(self, files: List[Path], batch_size: int = 15) -> List[List[Path]]:
        """Split files into batches."""
        batches = []
        for i in range(0, len(files), batch_size):
            batches.append(files[i:i + batch_size])
        logger.info(f"Created {len(batches)} batches of up to {batch_size} files each")
        return batches
    
    def cleanup_uploaded_files(self):
        """
        Delete uploaded files from Kimi platform for hygiene.

        Best practice from Moonshot: Delete files after use to avoid clutter.
        """
        if not self.uploaded_files:
            logger.info("✅ No files to clean up (none were uploaded)")
            return

        from src.providers.kimi import KimiModelProvider
        import os

        logger.info(f"🧹 Cleaning up {len(self.uploaded_files)} uploaded files from Kimi platform...")

        try:
            # Get provider
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                logger.error("❌ KIMI_API_KEY not configured - cannot cleanup files!")
                return

            provider = KimiModelProvider(api_key=api_key)
            deleted_count = 0
            failed_count = 0

            for file_id in self.uploaded_files:
                try:
                    provider.client.files.delete(file_id)
                    deleted_count += 1
                    logger.debug(f"  ✓ Deleted file: {file_id}")
                except Exception as e:
                    failed_count += 1
                    logger.warning(f"  ✗ Failed to delete file {file_id}: {e}")

            # Report results
            if deleted_count == len(self.uploaded_files):
                logger.info(f"✅ Successfully cleaned up ALL {deleted_count} files from Kimi platform")
            elif deleted_count > 0:
                logger.warning(f"⚠️  Partial cleanup: {deleted_count}/{len(self.uploaded_files)} files deleted, {failed_count} failed")
            else:
                logger.error(f"❌ Cleanup FAILED: 0/{len(self.uploaded_files)} files deleted")

            self.uploaded_files.clear()

        except Exception as e:
            logger.error(f"❌ Failed to cleanup files: {e}")
            logger.error(f"⚠️  WARNING: {len(self.uploaded_files)} files may remain on Kimi platform!")

    def analyze_batch_with_kimi(self, batch: List[Path], batch_num: int, batch_type: str) -> Dict:
        """
        Analyze a batch of files using Kimi multi-file chat.

        Args:
            batch: List of file paths
            batch_num: Batch number
            batch_type: 'code' or 'docs'
        """
        import sys
        import os

        # Add project root to path for imports
        project_root = Path.cwd()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from tools.providers.kimi.kimi_upload import KimiUploadAndExtractTool

        logger.info(f"Analyzing {batch_type} batch {batch_num} ({len(batch)} files)...")
        
        # Prepare prompt based on batch type
        if batch_type == 'code':
            prompt = """You are analyzing the EXAI MCP Server codebase to understand its design intent and architecture.

**Context:**
- EXAI is an agentic workflow system with tools like thinkdeep, analyze, debug, consensus, etc.
- Built on top of Kimi and GLM providers
- Uses dynamic step management and confidence-driven early termination
- Implements multi-turn conversations with continuation support

**Your Task:**
Analyze the provided Python files and identify:

1. **Core Architecture Patterns**
   - How are workflows structured?
   - How do tools interact with providers?
   - What are the key abstractions?

2. **Design Intent**
   - What problems is this solving?
   - What are the key design decisions?
   - How does agentic behavior work?

3. **Implementation Patterns**
   - Common patterns across tools
   - Provider integration approach
   - Error handling and validation

4. **Dependencies & Relationships**
   - How do components depend on each other?
   - What are the key interfaces?
   - How does data flow through the system?

**Output Format (JSON):**
```json
{
  "batch_number": <number>,
  "batch_type": "code",
  "files_analyzed": <count>,
  "architecture_patterns": [
    {"pattern": "...", "description": "...", "files": ["..."]}
  ],
  "design_intent": {
    "problems_solved": ["..."],
    "key_decisions": ["..."],
    "agentic_approach": "..."
  },
  "implementation_patterns": [
    {"pattern": "...", "description": "...", "examples": ["..."]}
  ],
  "dependencies": [
    {"component": "...", "depends_on": ["..."], "purpose": "..."}
  ],
  "insights": ["..."]
}
```
"""
        else:  # docs
            prompt = """You are analyzing EXAI documentation to understand the system's design intent and architecture.

**Context:**
- EXAI is an agentic workflow system
- Documentation explains tools, architecture, and design decisions
- Need to understand the "why" behind implementation choices

**Your Task:**
Analyze the provided documentation and extract:

1. **Design Philosophy**
   - What are the core principles?
   - What problems is EXAI solving?
   - What makes it "agentic"?

2. **Tool Capabilities**
   - What does each tool do?
   - How do they work together?
   - What are the use cases?

3. **Architecture Decisions**
   - Why was it designed this way?
   - What are the key components?
   - How do they interact?

4. **User Intent & Workflows**
   - How should users interact with EXAI?
   - What are common workflows?
   - What are best practices?

**Output Format (JSON):**
```json
{
  "batch_number": <number>,
  "batch_type": "docs",
  "files_analyzed": <count>,
  "design_philosophy": {
    "core_principles": ["..."],
    "problems_solved": ["..."],
    "agentic_definition": "..."
  },
  "tool_capabilities": [
    {"tool": "...", "purpose": "...", "use_cases": ["..."]}
  ],
  "architecture_decisions": [
    {"decision": "...", "rationale": "...", "impact": "..."}
  ],
  "user_workflows": [
    {"workflow": "...", "steps": ["..."], "best_practices": ["..."]}
  ],
  "insights": ["..."]
}
```
"""
        
        # Upload files first and track file IDs for cleanup
        upload_tool = KimiUploadAndExtractTool()
        sys_msgs = upload_tool._run(files=[str(f) for f in batch])

        # Extract and track file IDs for cleanup
        for msg in sys_msgs:
            file_id = msg.get('_file_id')
            if file_id and file_id not in self.uploaded_files:
                self.uploaded_files.append(file_id)
                logger.debug(f"Tracked file ID for cleanup: {file_id}")

        logger.info(f"Uploaded {len(sys_msgs)} files, total tracked: {len(self.uploaded_files)}")

        # Now call Kimi chat with the uploaded files
        # Prepare messages: system messages from files + user prompt
        messages = [*sys_msgs, {"role": "user", "content": prompt}]

        # Get provider and call chat
        from src.providers.kimi import KimiModelProvider
        from src.providers.registry import ModelProviderRegistry

        prov = ModelProviderRegistry.get_provider_for_model("kimi-k2-0905-preview")
        if not isinstance(prov, KimiModelProvider):
            import os
            api_key = os.getenv("KIMI_API_KEY", "")
            if not api_key:
                raise RuntimeError("KIMI_API_KEY is not configured")
            prov = KimiModelProvider(api_key=api_key)

        # Call chat with timeout
        import concurrent.futures as _fut
        def _call():
            return prov.chat_completions_create(
                model="kimi-k2-0905-preview",
                messages=messages,
                temperature=0.3
            )

        timeout_s = 180.0
        try:
            with _fut.ThreadPoolExecutor(max_workers=1) as _pool:
                _future = _pool.submit(_call)
                resp = _future.result(timeout=timeout_s)
        except _fut.TimeoutError:
            raise TimeoutError(f"Kimi chat timed out after {int(timeout_s)}s")

        result = (resp or {}).get("content", "")

        # Parse JSON response
        try:
            analysis = json.loads(result)
            analysis['batch_number'] = batch_num
            analysis['batch_type'] = batch_type
            logger.info(f"✅ Batch {batch_num} analyzed successfully")
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from Kimi response: {e}")
            logger.error(f"Raw content: {result[:500]}...")
            return {
                "batch_number": batch_num,
                "batch_type": batch_type,
                "error": str(e),
                "raw_response": result[:1000]
            }
    
    def run_analysis(self):
        """Run comprehensive EXAI codebase analysis with file hygiene."""
        logger.info("=" * 80)
        logger.info("EXAI CODEBASE COMPREHENSIVE ANALYSIS")
        logger.info("=" * 80)

        try:
            # Scan files
            code_files = self.scan_exai_files()
            doc_files = self.scan_design_docs()

            # Batch files
            code_batches = self.batch_files(code_files, batch_size=15)
            doc_batches = self.batch_files(doc_files, batch_size=15)

            logger.info(f"\nTotal batches: {len(code_batches)} code + {len(doc_batches)} docs")
            logger.info("\n⚠️  File Hygiene: Files will be uploaded to Kimi and deleted after analysis")

            # Analyze code batches
            results = []

            logger.info("\n" + "=" * 80)
            logger.info("ANALYZING CODE FILES")
            logger.info("=" * 80)

            for i, batch in enumerate(code_batches, 1):
                result = self.analyze_batch_with_kimi(batch, i, 'code')
                results.append(result)

                # Save progress after each batch (single file, overwrite)
                progress_file = self.docs_root / "EXAI_ANALYSIS_PROGRESS.json"
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Progress saved: {i}/{len(code_batches)} code batches")

            # Analyze doc batches
            logger.info("\n" + "=" * 80)
            logger.info("ANALYZING DOCUMENTATION FILES")
            logger.info("=" * 80)

            for i, batch in enumerate(doc_batches, 1):
                result = self.analyze_batch_with_kimi(batch, i + len(code_batches), 'docs')
                results.append(result)

                # Save progress after each batch (single file, overwrite)
                progress_file = self.docs_root / "EXAI_ANALYSIS_PROGRESS.json"
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Progress saved: {i}/{len(doc_batches)} doc batches")

            # Save final results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.docs_root / f"EXAI_CODEBASE_ANALYSIS_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            logger.info(f"\n✅ Analysis complete! Results saved to: {output_file}")
            logger.info(f"   Analyzed {len(code_files)} code files + {len(doc_files)} docs")
            logger.info(f"   Total batches: {len(results)}")

            return output_file

        finally:
            # Always cleanup uploaded files (Moonshot best practice)
            logger.info("\n" + "=" * 80)
            logger.info("CLEANUP: Deleting uploaded files from Kimi platform")
            logger.info("=" * 80)
            self.cleanup_uploaded_files()

def main():
    """Main entry point."""
    analyzer = ExaiCodebaseAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()

