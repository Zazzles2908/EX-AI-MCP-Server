#!/usr/bin/env python3
"""
Test script to verify the thinkdeep confidence logic fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools/workflows'))

from thinkdeep import run_think_deep_analysis, ConfidenceLevel

def test_confidence_fix():
    """Test that expert analysis is always called regardless of confidence level"""
    
    print("Testing Think Deep Workflow Confidence Logic Fix")
    print("=" * 50)
    
    # Test data
    test_data = {
        "problem": "test_problem",
        "requirements": "test_requirements",
        "context": "testing fix"
    }
    
    # Test with different confidence levels
    confidence_levels = ["certain", "high", "medium", "low", "uncertain"]
    
    all_tests_passed = True
    
    for confidence in confidence_levels:
        print(f"\nTesting with confidence: {confidence}")
        print("-" * 30)
        
        # Run analysis
        result = run_think_deep_analysis(test_data.copy(), confidence=confidence)
        
        # Check that workflow completed successfully
        if not result.get('workflow_complete', False):
            print(f"❌ FAILED: Workflow did not complete for confidence '{confidence}'")
            all_tests_passed = False
            continue
            
        # Check that expert analysis was included (the key fix)
        if 'expert_analysis' not in result:
            print(f"❌ FAILED: Expert analysis missing for confidence '{confidence}' - BUG NOT FIXED!")
            all_tests_passed = False
            continue
            
        # Check that expert analysis has proper content (not empty)
        expert_analysis = result['expert_analysis']
        if not expert_analysis.get('analysis') or expert_analysis.get('analysis').strip() == "":
            print(f"❌ FAILED: Expert analysis is empty for confidence '{confidence}'")
            all_tests_passed = False
            continue
            
        # Check that all steps were executed
        expected_steps = ['problem_analysis', 'solution_design', 'validation']
        executed_steps = result.get('steps_completed', [])
        if executed_steps != expected_steps:
            print(f"❌ FAILED: Not all steps executed for confidence '{confidence}'")
            all_tests_passed = False
            continue
            
        # Verify final result confirms expert analysis was included
        final_result = result.get('final_result', {})
        if not final_result.get('expert_analysis_included', False):
            print(f"❌ FAILED: Final result doesn't confirm expert analysis for confidence '{confidence}'")
            all_tests_passed = False
            continue
            
        print(f"✅ PASSED: Expert analysis included and working for confidence '{confidence}'")
        print(f"   - Expert analysis: {expert_analysis['analysis']}")
        print(f"   - Steps executed: {len(executed_steps)}/3")
        
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! The confidence logic fix is working correctly.")
        print("✅ Expert analysis is now ALWAYS called regardless of confidence level.")
        print("✅ The original bug (empty responses when confidence='certain') is FIXED.")
    else:
        print("❌ SOME TESTS FAILED! The confidence logic fix may not be working properly.")
        
    return all_tests_passed


def test_direct_should_skip_function():
    """Test the should_skip_expert_analysis function directly"""
    print("\nTesting should_skip_expert_analysis() function directly")
    print("-" * 50)
    
    from thinkdeep import WorkflowStep, ConfidenceLevel
    
    step = WorkflowStep("test", "test step")
    
    # Test that the function always returns False regardless of confidence
    test_contexts = [
        {'confidence': ConfidenceLevel.CERTAIN.value},
        {'confidence': ConfidenceLevel.HIGH.value},
        {'confidence': ConfidenceLevel.MEDIUM.value},
        {'confidence': ConfidenceLevel.LOW.value},
        {'confidence': ConfidenceLevel.UNCERTAIN.value},
        {},  # No confidence specified
        {'confidence': 'unknown_value'}
    ]
    
    all_passed = True
    
    for context in test_contexts:
        should_skip = step.should_skip_expert_analysis(context)
        confidence = context.get('confidence', 'not_set')
        
        if should_skip:
            print(f"❌ FAILED: should_skip_expert_analysis returned True for confidence '{confidence}'")
            all_passed = False
        else:
            print(f"✅ PASSED: should_skip_expert_analysis correctly returned False for confidence '{confidence}'")
    
    print("-" * 50)
    if all_passed:
        print("✅ should_skip_expert_analysis() function test PASSED!")
    else:
        print("❌ should_skip_expert_analysis() function test FAILED!")
        
    return all_passed


if __name__ == "__main__":
    print("Think Deep Workflow - Confidence Logic Fix Verification")
    print("=" * 60)
    
    # Run both tests
    test1_passed = test_confidence_fix()
    test2_passed = test_direct_should_skip_function()
    
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY:")
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The confidence logic bug fix is confirmed working.")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED! The confidence logic bug fix may not be working properly.")
        sys.exit(1)