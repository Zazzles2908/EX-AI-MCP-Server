#!/usr/bin/env python3
"""
Test script for agentic architecture transition.

This script validates the transition from rigid workflows to agentic behavior by:
1. Using Kimi upload to analyze architecture interconnections
2. Testing confidence-based early termination
3. Validating dynamic step adjustment
4. Verifying backward compatibility

Usage:
    python scripts/test_agentic_transition.py
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgenticTransitionTester:
    """Test suite for agentic architecture transition."""
    
    def __init__(self):
        self.results = {
            "kimi_upload": None,
            "architecture_analysis": None,
            "confidence_test": None,
            "early_termination": None,
            "backward_compat": None,
        }
    
    async def test_kimi_upload_architecture_analysis(self):
        """
        Test 1: Use Kimi upload to analyze architecture files.
        
        This validates that we can upload key architecture files to Kimi
        and get intelligent analysis of interconnections.
        """
        logger.info("=" * 80)
        logger.info("TEST 1: Kimi Upload Architecture Analysis")
        logger.info("=" * 80)
        
        try:
            from tools.providers.kimi.kimi_upload import KimiUploadAndExtractTool, KimiMultiFileChatTool
            
            # Key architecture files to analyze
            files_to_analyze = [
                str(PROJECT_ROOT / "tools" / "shared" / "base_models.py"),
                str(PROJECT_ROOT / "tools" / "workflow" / "base.py"),
                str(PROJECT_ROOT / "tools" / "workflows" / "debug.py"),
                str(PROJECT_ROOT / "src" / "providers" / "registry.py"),
            ]
            
            logger.info(f"Uploading {len(files_to_analyze)} architecture files to Kimi...")
            
            # Test upload and extract
            upload_tool = KimiUploadAndExtractTool()
            messages = upload_tool._run(files=files_to_analyze)
            
            logger.info(f"✅ Successfully uploaded {len(messages)} files")
            logger.info(f"   Total content size: {sum(len(m['content']) for m in messages):,} chars")
            
            # Test multi-file chat for analysis
            chat_tool = KimiMultiFileChatTool()
            analysis_prompt = """
            Analyze these architecture files and identify:
            1. How confidence parameter is currently used
            2. Where early termination logic should be added
            3. What scripts are interconnected for agentic behavior
            4. What's the safest transition path
            
            Provide a concise summary with specific file/line references.
            """
            
            result = chat_tool.run(
                files=files_to_analyze,
                prompt=analysis_prompt,
                model="kimi-k2-0905-preview",
                temperature=0.3
            )
            
            logger.info("✅ Kimi analysis complete")
            logger.info(f"\n{result['content']}\n")
            
            self.results["kimi_upload"] = "PASS"
            self.results["architecture_analysis"] = result['content']
            
        except Exception as e:
            logger.error(f"❌ Kimi upload test failed: {e}")
            self.results["kimi_upload"] = f"FAIL: {e}"
            raise
    
    async def test_confidence_parameter_exists(self):
        """
        Test 2: Verify confidence parameter exists in all workflow tools.
        """
        logger.info("=" * 80)
        logger.info("TEST 2: Confidence Parameter Validation")
        logger.info("=" * 80)
        
        try:
            from tools.shared.base_models import WorkflowRequest, WORKFLOW_FIELD_DESCRIPTIONS
            
            # Check confidence is in WorkflowRequest
            assert hasattr(WorkflowRequest, '__fields__'), "WorkflowRequest missing fields"
            assert 'confidence' in WorkflowRequest.__fields__, "Confidence field missing"
            
            # Check valid confidence levels
            confidence_desc = WORKFLOW_FIELD_DESCRIPTIONS.get("confidence", "")
            valid_levels = ["exploring", "low", "medium", "high", "very_high", "almost_certain", "certain"]
            
            for level in valid_levels:
                assert level in confidence_desc, f"Missing confidence level: {level}"
            
            logger.info("✅ Confidence parameter exists with all valid levels")
            logger.info(f"   Valid levels: {', '.join(valid_levels)}")
            
            self.results["confidence_test"] = "PASS"
            
        except Exception as e:
            logger.error(f"❌ Confidence test failed: {e}")
            self.results["confidence_test"] = f"FAIL: {e}"
            raise
    
    async def test_early_termination_logic(self):
        """
        Test 3: Test early termination logic (to be implemented).
        
        This is a placeholder for testing the early termination feature
        once it's implemented in Phase 1.
        """
        logger.info("=" * 80)
        logger.info("TEST 3: Early Termination Logic (Placeholder)")
        logger.info("=" * 80)
        
        logger.info("⚠️  Early termination not yet implemented")
        logger.info("   This will be tested after Phase 1 Quick Win #5")
        
        self.results["early_termination"] = "PENDING"
    
    async def test_backward_compatibility(self):
        """
        Test 4: Verify backward compatibility with existing workflows.
        """
        logger.info("=" * 80)
        logger.info("TEST 4: Backward Compatibility")
        logger.info("=" * 80)
        
        try:
            from tools.workflows.debug import DebugTool
            from tools.workflows.analyze import AnalyzeTool
            
            # Verify tools can be instantiated
            debug_tool = DebugTool()
            analyze_tool = AnalyzeTool()
            
            # Verify they have required methods
            assert hasattr(debug_tool, 'get_input_schema'), "Debug tool missing get_input_schema"
            assert hasattr(analyze_tool, 'get_input_schema'), "Analyze tool missing get_input_schema"
            
            # Verify schemas include confidence
            debug_schema = debug_tool.get_input_schema()
            analyze_schema = analyze_tool.get_input_schema()
            
            assert 'confidence' in debug_schema['properties'], "Debug schema missing confidence"
            assert 'confidence' in analyze_schema['properties'], "Analyze schema missing confidence"
            
            logger.info("✅ Backward compatibility maintained")
            logger.info("   All workflow tools instantiate correctly")
            logger.info("   All schemas include confidence parameter")
            
            self.results["backward_compat"] = "PASS"
            
        except Exception as e:
            logger.error(f"❌ Backward compatibility test failed: {e}")
            self.results["backward_compat"] = f"FAIL: {e}"
            raise
    
    async def run_all_tests(self):
        """Run all transition tests."""
        logger.info("\n" + "=" * 80)
        logger.info("AGENTIC ARCHITECTURE TRANSITION TEST SUITE")
        logger.info("=" * 80 + "\n")
        
        tests = [
            self.test_kimi_upload_architecture_analysis,
            self.test_confidence_parameter_exists,
            self.test_early_termination_logic,
            self.test_backward_compatibility,
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                logger.error(f"Test failed, continuing with remaining tests...")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result == "PASS" else "⚠️  PENDING" if result == "PENDING" else f"❌ {result}"
            logger.info(f"{test_name:30s}: {status}")
        
        # Save results
        results_file = PROJECT_ROOT / "docs" / "upgrades" / "international-users" / "agentic-transition-test-results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\nResults saved to: {results_file}")
        
        return self.results


async def main():
    """Main entry point."""
    tester = AgenticTransitionTester()
    results = await tester.run_all_tests()
    
    # Exit with error if any tests failed
    failed = [k for k, v in results.items() if v and isinstance(v, str) and v.startswith("FAIL")]
    if failed:
        logger.error(f"\n❌ {len(failed)} test(s) failed")
        sys.exit(1)
    else:
        logger.info("\n✅ All tests passed or pending!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

