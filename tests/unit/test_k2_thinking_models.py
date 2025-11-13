#!/usr/bin/env python3
"""
Test script for K2 Thinking models verification
Verifies that kimi-k2-thinking and kimi-k2-thinking-turbo are properly configured

Date: 2025-11-10
Purpose: Validate official K2 thinking model additions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from providers.kimi_config import SUPPORTED_MODELS
from providers.model_config import get_model_token_limits
from providers.base import ProviderType


def test_k2_thinking_models_exist():
    """Test that both K2 thinking models exist in SUPPORTED_MODELS"""
    print("\n" + "="*70)
    print("TEST 1: Verify K2 Thinking Models Exist")
    print("="*70)

    required_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
    results = {}

    for model_name in required_models:
        if model_name in SUPPORTED_MODELS:
            results[model_name] = "✅ PASS"
            print(f"  ✅ {model_name:30s} - Found in SUPPORTED_MODELS")
        else:
            results[model_name] = "❌ FAIL"
            print(f"  ❌ {model_name:30s} - NOT FOUND in SUPPORTED_MODELS")

    return all(results.values())


def test_model_capabilities():
    """Test that models have correct capabilities"""
    print("\n" + "="*70)
    print("TEST 2: Verify Model Capabilities")
    print("="*70)

    test_cases = {
        "kimi-k2-thinking": {
            "context_window": 262144,
            "supports_extended_thinking": True,
            "supports_images": True,
            "supports_function_calling": True,
        },
        "kimi-k2-thinking-turbo": {
            "context_window": 262144,
            "supports_extended_thinking": True,
            "supports_images": True,
            "supports_function_calling": True,
        }
    }

    all_passed = True

    for model_name, expected_caps in test_cases.items():
        print(f"\n  Testing: {model_name}")
        model = SUPPORTED_MODELS.get(model_name)

        if not model:
            print(f"    ❌ Model not found")
            all_passed = False
            continue

        # Check each capability
        for cap_name, expected_value in expected_caps.items():
            actual_value = getattr(model, cap_name, None)
            if actual_value == expected_value:
                print(f"    ✅ {cap_name:30s} = {actual_value}")
            else:
                print(f"    ❌ {cap_name:30s} = {actual_value} (expected {expected_value})")
                all_passed = False

    return all_passed


def test_token_limits():
    """Test that token limits are correctly configured"""
    print("\n" + "="*70)
    print("TEST 3: Verify Token Limits")
    print("="*70)

    test_cases = {
        "kimi-k2-thinking": {
            "max_context_tokens": 262144,
            "provider": "kimi"
        },
        "kimi-k2-thinking-turbo": {
            "max_context_tokens": 262144,
            "provider": "kimi"
        }
    }

    all_passed = True

    for model_name, expected_limits in test_cases.items():
        print(f"\n  Testing: {model_name}")
        limits = get_model_token_limits(model_name)

        for limit_name, expected_value in expected_limits.items():
            actual_value = limits.get(limit_name)
            if actual_value == expected_value:
                print(f"    ✅ {limit_name:30s} = {actual_value}")
            else:
                print(f"    ❌ {limit_name:30s} = {actual_value} (expected {expected_value})")
                all_passed = False

    return all_passed


def test_provider_type():
    """Test that models are correctly tagged as KIMI provider"""
    print("\n" + "="*70)
    print("TEST 4: Verify Provider Type")
    print("="*70)

    required_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
    all_passed = True

    for model_name in required_models:
        model = SUPPORTED_MODELS.get(model_name)

        if not model:
            print(f"  ❌ {model_name:30s} - Model not found")
            all_passed = False
            continue

        if model.provider == ProviderType.KIMI:
            print(f"  ✅ {model_name:30s} - ProviderType.KIMI")
        else:
            print(f"  ❌ {model_name:30s} - Wrong provider: {model.provider}")
            all_passed = False

    return all_passed


def test_model_count():
    """Test that we now have all expected models"""
    print("\n" + "="*70)
    print("TEST 5: Verify Total Model Count")
    print("="*70)

    # Count all Kimi models
    kimi_models = [name for name, model in SUPPORTED_MODELS.items()
                   if model.provider == ProviderType.KIMI]

    print(f"  Total Kimi models configured: {len(kimi_models)}")
    print(f"\n  All Kimi models:")
    for model in sorted(kimi_models):
        print(f"    - {model}")

    # Expected minimum (original 14 + 2 new ones = 16)
    expected_min = 16
    if len(kimi_models) >= expected_min:
        print(f"\n  ✅ Have {len(kimi_models)} models (minimum expected: {expected_min})")
        return True
    else:
        print(f"\n  ❌ Only {len(kimi_models)} models (expected at least: {expected_min})")
        return False


def test_aliases():
    """Test that models have proper aliases"""
    print("\n" + "="*70)
    print("TEST 6: Verify Model Aliases")
    print("="*70)

    test_cases = {
        "kimi-k2-thinking": ["kimi-k2-thinking", "kimi-thinking-k2"],
        "kimi-k2-thinking-turbo": ["kimi-k2-thinking-turbo", "kimi-thinking-k2-turbo"]
    }

    all_passed = True

    for model_name, expected_aliases in test_cases.items():
        model = SUPPORTED_MODELS.get(model_name)

        if not model:
            print(f"  ❌ {model_name:30s} - Model not found")
            all_passed = False
            continue

        if model.aliases == expected_aliases:
            print(f"  ✅ {model_name:30s} - Aliases: {model.aliases}")
        else:
            print(f"  ❌ {model_name:30s} - Wrong aliases: {model.aliases}")
            print(f"     Expected: {expected_aliases}")
            all_passed = False

    return all_passed


def print_summary():
    """Print comprehensive model information"""
    print("\n" + "="*70)
    print("K2 THINKING MODELS SUMMARY")
    print("="*70)

    models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]

    for model_name in models:
        if model_name in SUPPORTED_MODELS:
            model = SUPPORTED_MODELS[model_name]
            limits = get_model_token_limits(model_name)

            print(f"\n  Model: {model_name}")
            print(f"  Description: {model.description}")
            print(f"  Context Window: {model.context_window:,} tokens")
            print(f"  Max Output: {model.max_output_tokens:,} tokens")
            print(f"  Supports Vision: {model.supports_images}")
            print(f"  Supports Thinking: {model.supports_extended_thinking}")
            print(f"  Supports Function Calling: {model.supports_function_calling}")
            print(f"  Token Limit Provider: {limits.get('provider')}")
            print(f"  Aliases: {model.aliases or 'None'}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("K2 THINKING MODELS VERIFICATION TEST")
    print("Date: 2025-11-10")
    print("="*70)

    tests = [
        ("Models Exist", test_k2_thinking_models_exist),
        ("Model Capabilities", test_model_capabilities),
        ("Token Limits", test_token_limits),
        ("Provider Type", test_provider_type),
        ("Model Count", test_model_count),
        ("Model Aliases", test_aliases),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} - Exception: {e}")
            results[test_name] = False
            import traceback
            traceback.print_exc()

    # Print summary
    print_summary()

    # Final results
    print("\n" + "="*70)
    print("FINAL TEST RESULTS")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:10s} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! K2 Thinking models are properly configured.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the output above.")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
