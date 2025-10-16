"""
Simple Verification of Critical Fixes - 2025-10-14

This script verifies the fixes by checking the source code directly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def verify_kimi_finish_reason():
    """Verify Fix #1: Kimi finish_reason extraction"""
    print("\n" + "="*80)
    print("FIX #1: Kimi finish_reason Extraction")
    print("="*80)
    
    try:
        with open(project_root / "src/providers/kimi_chat.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for finish_reason extraction code
        if "Extract finish_reason from response" in content:
            print("✅ PASS: finish_reason extraction code exists")
            
            # Check it's added to metadata
            if '"finish_reason": finish_reason' in content:
                print("✅ PASS: finish_reason added to metadata")
                return True
            else:
                print("❌ FAIL: finish_reason not added to metadata")
                return False
        else:
            print("❌ FAIL: finish_reason extraction code not found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def verify_completeness_check():
    """Verify Fix #2: Response completeness validation"""
    print("\n" + "="*80)
    print("FIX #2: Response Completeness Validation")
    print("="*80)
    
    try:
        with open(project_root / "tools/simple/base.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for finish_reason check BEFORE content check
        if 'finish_reason in ["length", "content_filter"]' in content:
            print("✅ PASS: Completeness check exists")
            
            # Verify it comes before content check
            finish_reason_pos = content.find('finish_reason in ["length", "content_filter"]')
            content_check_pos = content.find('if getattr(model_response, "content", None):')
            
            if finish_reason_pos < content_check_pos:
                print("✅ PASS: Completeness check comes BEFORE content check")
                return True
            else:
                print("❌ FAIL: Completeness check comes AFTER content check")
                return False
        else:
            print("❌ FAIL: Completeness check not found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def verify_parameter_validation():
    """Verify Fix #3: Parameter validation"""
    print("\n" + "="*80)
    print("FIX #3: Parameter Validation")
    print("="*80)
    
    try:
        with open(project_root / "src/providers/base.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = {
            "thinking_mode validation": '"thinking_mode" in kwargs' in content,
            "tools validation": '"tools" in kwargs' in content,
            "images validation": '"images" in kwargs' in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ PASS: {check_name} exists")
            else:
                print(f"❌ FAIL: {check_name} not found")
                all_passed = False
        
        return all_passed
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def verify_structure_validation():
    """Verify Fix #4: Response structure validation"""
    print("\n" + "="*80)
    print("FIX #4: Response Structure Validation")
    print("="*80)
    
    try:
        with open(project_root / "src/providers/kimi_chat.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = {
            "choices field validation": "Invalid Kimi API response: missing 'choices' field" in content,
            "empty choices validation": "Invalid Kimi API response: empty 'choices' array" in content,
            "message field validation": "Invalid Kimi API response: choice missing 'message' field" in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✅ PASS: {check_name} exists")
            else:
                print(f"❌ FAIL: {check_name} not found")
                all_passed = False
        
        return all_passed
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def verify_timeout_coordination():
    """Verify Fix #5: Timeout coordination"""
    print("\n" + "="*80)
    print("FIX #5: Timeout Coordination")
    print("="*80)
    
    try:
        with open(project_root / "tools/workflow/conversation_integration.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for timeout from environment
        if 'os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS"' in content:
            print("✅ PASS: Timeout loaded from environment")
            
            # Check for timeout handling
            if '"analysis_timeout"' in content:
                print("✅ PASS: Timeout status handled")
                return True
            else:
                print("❌ FAIL: Timeout status not handled")
                return False
        else:
            print("❌ FAIL: Timeout not loaded from environment")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all verifications"""
    print("\n" + "="*80)
    print("CRITICAL FIXES VERIFICATION - 2025-10-14")
    print("="*80)
    
    results = {
        "Kimi finish_reason": verify_kimi_finish_reason(),
        "Completeness validation": verify_completeness_check(),
        "Parameter validation": verify_parameter_validation(),
        "Structure validation": verify_structure_validation(),
        "Timeout coordination": verify_timeout_coordination(),
    }
    
    print("\n" + "="*80)
    print("VERIFICATION RESULTS SUMMARY")
    print("="*80)
    
    for fix_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {fix_name}")
    
    total = len(results)
    passed = sum(1 for p in results.values() if p)
    
    print(f"\nTotal: {passed}/{total} fixes verified")
    
    if passed == total:
        print("\n🎉 ALL FIXES VERIFIED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} fixes not verified")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

