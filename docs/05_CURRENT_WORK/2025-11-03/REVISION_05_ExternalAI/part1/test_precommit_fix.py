#!/usr/bin/env python3
"""
Test script to demonstrate the pre-commit confidence logic fix.

This test specifically verifies that the bug where confidence='certain'
caused empty responses has been fixed.
"""

import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'workflows'))

from precommit import PrecommitWorkflowTool


def test_certain_confidence_fix():
    """
    Test that demonstrates the fix for the 'certain' confidence bug.
    
    Before the fix: confidence='certain' would skip expert_analysis() causing empty responses
    After the fix: confidence='certain' still calls expert_analysis() with proper content
    """
    print("=" * 70)
    print("TESTING FIX FOR CONFIDENCE='CERTAIN' BUG")
    print("=" * 70)
    
    tool = PrecommitWorkflowTool()
    
    # Test cases covering all confidence levels
    confidence_levels = ['uncertain', 'moderate', 'certain']
    
    print("\nTesting expert analysis behavior for all confidence levels:")
    print("-" * 50)
    
    for confidence in confidence_levels:
        print(f"\n📊 Testing confidence level: '{confidence}'")
        
        # Test the critical functions
        should_skip = tool.should_skip_expert_analysis(confidence)
        should_call = tool.should_call_expert_analysis(confidence)
        
        print(f"   should_skip_expert_analysis() = {should_skip}")
        print(f"   should_call_expert_analysis() = {should_call}")
        
        # Verify the fix: should never skip, should always call
        if confidence == 'certain':
            print(f"   🔧 PREVIOUS BUG: Would have skipped analysis when confidence='certain'")
            print(f"   ✅ FIXED: Now performs expert analysis regardless of confidence")
        
        # Test actual expert analysis with sample content
        test_content = f"Sample code analysis for confidence level: {confidence}"
        result = tool.expert_analysis(test_content, confidence)
        
        print(f"   Expert analysis result: {result['status']}")
        print(f"   Content generated: {bool(result['content'])}")
        print(f"   Expert reviewed: {result['expert_reviewed']}")
        
        # Verify no empty responses
        assert result['content'], f"Content should never be empty for confidence='{confidence}'"
        assert result['expert_reviewed'], f"Expert analysis should be performed for confidence='{confidence}'"
        assert not should_skip, f"Should never skip analysis for confidence='{confidence}'"
        assert should_call, f"Should always call analysis for confidence='{confidence}'"
        
        print(f"   ✅ All assertions passed for confidence='{confidence}'")
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICATION SUMMARY")
    print("=" * 70)
    print("✅ should_skip_expert_analysis() always returns False")
    print("✅ should_call_expert_analysis() always returns True") 
    print("✅ expert_analysis() is always called regardless of confidence")
    print("✅ No empty responses generated for any confidence level")
    print("✅ Workflow integrity maintained across all confidence levels")
    print("\n🎉 BUG FIX VERIFIED: Confidence-based skipping logic successfully disabled!")


def test_workflow_integration():
    """
    Test the complete workflow integration to ensure proper expert analysis coverage.
    """
    print("\n" + "=" * 70)
    print("TESTING WORKFLOW INTEGRATION")
    print("=" * 70)
    
    tool = PrecommitWorkflowTool()
    
    # Simulate a complete pre-commit workflow with multiple steps
    workflow_steps = [
        ("lint_check", "certain", "import os; print('lint passed')"),
        ("security_scan", "moderate", "# security checks would go here"),
        ("format_validation", "uncertain", "import sys"),
        ("dependency_check", "certain", "requirements satisfied"),
        ("final_validation", "certain", "all checks complete")
    ]
    
    workflow_results = {}
    
    print("\nProcessing complete pre-commit workflow:")
    print("-" * 40)
    
    for step_name, confidence, content in workflow_steps:
        print(f"\n🔄 Step: {step_name} (confidence: {confidence})")
        
        # Process the workflow step
        result = tool.process_workflow_step(content, confidence, step_name)
        workflow_results[step_name] = result
        
        # Verify expert analysis was performed
        assert result['expert_reviewed'], f"Expert analysis should be performed for {step_name}"
        assert result['confidence_skipped'] == False, f"Should not skip confidence for {step_name}"
        assert result['content'], f"Content should not be empty for {step_name}"
        
        print(f"   ✅ Expert analysis performed: {result['expert_reviewed']}")
        print(f"   ✅ Content available: {bool(result['content'])}")
        print(f"   ✅ No skipping occurred: {not result['confidence_skipped']}")
    
    # Validate overall workflow integrity
    integrity_check = tool.validate_workflow_integrity(workflow_results)
    
    print(f"\n📋 Workflow Integrity Check: {'PASSED' if integrity_check else 'FAILED'}")
    
    assert integrity_check, "Workflow integrity should be maintained"
    
    print("\n🎯 WORKFLOW INTEGRATION TEST PASSED!")
    print("✅ All workflow steps include proper expert analysis")
    print("✅ No confidence-based skipping occurred")
    print("✅ Complete content generation maintained")


if __name__ == "__main__":
    try:
        test_certain_confidence_fix()
        test_workflow_integration()
        
        print("\n" + "=" * 70)
        print("🏆 ALL TESTS PASSED - BUG FIX SUCCESSFUL!")
        print("=" * 70)
        print("The confidence-based skipping logic has been successfully disabled.")
        print("Expert analysis is now always performed regardless of confidence level.")
        print("Empty responses caused by confidence='certain' skipping are now prevented.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)