#!/usr/bin/env python3
"""
K2 Review Script - External AI Changes
Consults K2 to comprehensively review all external AI changes.

Usage:
    python scripts/review_external_ai_changes_with_k2.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.chat import ChatTool


async def main():
    """Execute K2 review of external AI changes."""
    
    print("=" * 80)
    print("K2 REVIEW - EXTERNAL AI CHANGES")
    print("=" * 80)
    print()
    
    # Initialize chat tool
    chat_tool = ChatTool()
    
    # Prepare review request
    review_request = """Today is November 3, 2025.

I need you to comprehensively review all changes made by an external AI to the EX-AI-MCP-Server project. This is a critical code review to determine:

1. **Quality & Correctness**: Are the implementations sound and bug-free?
2. **Integration Safety**: Will these changes conflict with existing work (Day 1 Adaptive Timeout implementation on branch phase5-production-validation)?
3. **Priority Assessment**: What should be committed immediately vs deferred?
4. **Risk Analysis**: What are the potential issues or concerns?

## External AI's Work Summary:

### 1. File Registry System (NEW FEATURE)
- Complete cross-platform file registry with SQLite backend
- UUID-based tracking, metadata storage, search capabilities
- Moonshot storage integration hooks
- Thread-safe operations
- Located in: `src/file_management/registry/`

### 2. Critical Bug Fixes (WORKFLOW TOOLS)
- Fixed `tools/workflows/precommit.py` - confidence-based skipping logic causing empty responses
- Fixed `tools/workflows/thinkdeep.py` - same confidence bug
- Also fixed: `codereview.py`, `refactor.py`, `secaudit.py`, `docgen.py`, `testgen.py`
- Root cause: `should_skip_expert_analysis()` returned True when confidence='certain', skipping expert analysis

### 3. Additional File Management Features
- Audit logging system (`src/file_management/audit/`)
- Health checker (`src/file_management/health/`)
- Lifecycle sync (`src/file_management/lifecycle/`)
- Recovery manager (`src/file_management/recovery/`)

### 4. Security Analysis
- Environment configuration security audit
- Validation tool for detecting hardcoded secrets
- Implementation checklist for security hardening

## Current Project State:
- Branch: `phase5-production-validation`
- Last commit: Day 1 Adaptive Timeout implementation (committed & pushed)
- All external AI work is UNTRACKED in git

## Your Review Tasks:

1. **Analyze the bug fixes** - Are they correct? Should they be committed immediately?
2. **Evaluate the file registry system** - Is it production-ready? Does it fit the architecture?
3. **Check for conflicts** - Will this interfere with adaptive timeout work or existing systems?
4. **Prioritize integration** - What order should we integrate these changes?
5. **Identify risks** - What could go wrong? What needs testing?

Please provide:
- ✅ APPROVE or ❌ REJECT for each component
- Integration strategy (immediate commit, separate branch, defer, etc.)
- Testing requirements before integration
- Any concerns or modifications needed

I've attached the comprehensive review request document and all key implementation files for your analysis.
"""
    
    # Files to attach for review
    files_to_review = [
        # Review request document
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\K2_REVIEW_REQUEST__EXTERNAL_AI_CHANGES.md",
        
        # Summary documents
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\IMPLEMENTATION_SUMMARY.md",
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\BUG_FIX_SUMMARY.md",
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\thinkdeep_confidence_fix_summary.md",
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\FILE_REGISTRY_DOCUMENTATION.md",
        
        # Implementation files - workflow fixes
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\tools\\workflows\\precommit.py",
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\tools\\workflows\\thinkdeep.py",
        
        # Implementation files - file registry
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\src\\file_management\\registry\\file_registry.py",
        
        # Security analysis
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\environment_security_analysis.md",
        
        # Test files
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\test_precommit_fix.py",
        "c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_05_ExternalAI\\test_thinkdeep_fix.py",
    ]
    
    # Verify files exist
    print("📁 Verifying files for review...")
    missing_files = []
    for file_path in files_to_review:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"   ⚠️  Missing: {file_path}")
        else:
            print(f"   ✅ Found: {Path(file_path).name}")
    
    if missing_files:
        print()
        print(f"❌ ERROR: {len(missing_files)} files not found!")
        print("Please ensure all external AI files are in the correct location.")
        return 1
    
    print()
    print("=" * 80)
    print("CALLING K2 FOR COMPREHENSIVE REVIEW")
    print("=" * 80)
    print()
    print("Model: kimi-k2-0905-preview")
    print("Files attached: {}".format(len(files_to_review)))
    print("Web search: Disabled")
    print()
    
    # Execute K2 review
    try:
        result = await chat_tool.execute(
            prompt=review_request,
            model="kimi-k2-0905-preview",
            files=files_to_review,
            use_websearch=False,
            thinking_mode="high"
        )
        
        print("=" * 80)
        print("K2 REVIEW RESPONSE")
        print("=" * 80)
        print()
        print(result.get("response", "No response received"))
        print()
        
        # Save response to file
        output_file = project_root / "docs" / "05_CURRENT_WORK" / "2025-11-03" / "K2_REVIEW_RESPONSE__EXTERNAL_AI_CHANGES.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# K2 Review Response - External AI Changes\n\n")
            f.write(f"**Date:** 2025-11-03\n")
            f.write(f"**Model:** kimi-k2-0905-preview\n")
            f.write(f"**Files Reviewed:** {len(files_to_review)}\n\n")
            f.write("---\n\n")
            f.write(result.get("response", "No response received"))
        
        print(f"✅ Review response saved to: {output_file}")
        print()
        
        # Extract continuation_id if available
        if "continuation_id" in result:
            print(f"📝 Continuation ID: {result['continuation_id']}")
            print("   Use this ID to continue the conversation with K2")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR during K2 review: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

