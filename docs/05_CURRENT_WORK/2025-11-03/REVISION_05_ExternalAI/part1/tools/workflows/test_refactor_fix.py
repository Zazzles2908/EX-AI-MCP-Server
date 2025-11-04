#!/usr/bin/env python3
"""Test script to verify the confidence fix in refactor.py"""

from refactor import run_refactor_analysis

def test_confidence_fix():
    """Test that expert analysis is always called regardless of confidence level"""
    print("Testing Refactor Workflow Confidence Fix")
    print("=" * 50)
    
    # Test data
    test_data = {
        "code_file": "test.py",
        "refactoring_goals": ["improve_readability"]
    }
    
    # All confidence levels to test
    confidence_levels = ["certain", "high", "medium", "low", "uncertain"]
    
    all_passed = True
    
    for confidence in confidence_levels:
        print(f"\n--- Testing confidence: {confidence} ---")
        
        result = run_refactor_analysis(test_data, confidence=confidence)
        
        # Check if expert analysis was included
        final_result = result.get('final_result', {})
        expert_included = final_result.get('expert_analysis_included', False)
        expert_data = result.get('expert_analysis')
        steps_completed = len(result.get('steps_completed', []))
        
        print(f"Expert analysis included: {expert_included}")
        print(f"Expert analysis data present: {'analysis' in expert_data if expert_data else False}")
        print(f"Steps completed: {steps_completed}")
        
        if not expert_included:
            print("❌ FAIL: expert_analysis_included flag not set!")
            all_passed = False
        elif not expert_data:
            print("❌ FAIL: Expert analysis data is missing!")
            all_passed = False
        elif 'analysis' not in expert_data:
            print("❌ FAIL: Expert analysis content is missing!")
            all_passed = False
        else:
            print("✅ PASS: Expert analysis was called successfully")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The fix ensures expert_analysis() is ALWAYS called regardless of confidence level.")
        print("The critical bug where confidence='certain' caused empty responses has been fixed.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("The fix may not be working correctly.")
    
    return all_passed

if __name__ == "__main__":
    test_confidence_fix()
