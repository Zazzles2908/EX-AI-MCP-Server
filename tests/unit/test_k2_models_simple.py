#!/usr/bin/env python3
"""
Simple test for K2 Thinking models - reads files directly
Verifies that kimi-k2-thinking and kimi-k2-thinking-turbo are configured

Date: 2025-11-10
"""

import re
from pathlib import Path


def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def test_kimi_config():
    """Test kimi_config.py for the new models"""
    print("\n" + "="*70)
    print("TEST 1: Verify kimi-k2-thinking in kimi_config.py")
    print("="*70)

    filepath = Path(__file__).parent / "src" / "providers" / "kimi_config.py"
    content = read_file(filepath)

    required_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
    all_found = True

    for model in required_models:
        if f'"{model}"' in content:
            print(f"  [PASS] Found model definition: {model}")
        else:
            print(f"  [FAIL] NOT FOUND: {model}")
            all_found = False

    # Check for extended_thinking support
    if "supports_extended_thinking=True" in content:
        print(f"\n  [PASS] Extended thinking support configured")
        thinking_count = content.count("supports_extended_thinking=True")
        print(f"  [INFO] Found {thinking_count} model(s) with extended thinking support")
    else:
        print(f"\n  [FAIL] Extended thinking support NOT found")
        all_found = False

    # Check for 262144 context window
    if "context_window=262144" in content:
        print(f"  [PASS] 256K context window (262144) configured")
    else:
        print(f"  [FAIL] 256K context window NOT configured")
        all_found = False

    return all_found


def test_model_config():
    """Test model_config.py for token limits"""
    print("\n" + "="*70)
    print("TEST 2: Verify token limits in model_config.py")
    print("="*70)

    filepath = Path(__file__).parent / "src" / "providers" / "model_config.py"
    content = read_file(filepath)

    required_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
    all_found = True

    for model in required_models:
        if f"'{model}'" in content:
            print(f"  [PASS] Found token limits: {model}")
        else:
            print(f"  [FAIL] NOT FOUND: {model}")
            all_found = False

    # Check for 262144 context in token limits
    if "'max_context_tokens': 262144" in content:
        print(f"  [PASS] Token limits have 256K context (262144)")
    else:
        print(f"  [FAIL] Token limits missing 256K context")
        all_found = False

    return all_found


def test_env_files():
    """Test .env and .env.docker for model preferences"""
    print("\n" + "="*70)
    print("TEST 3: Verify .env and .env.docker")
    print("="*70)

    env_files = [".env", ".env.docker"]
    all_found = True

    for env_file in env_files:
        filepath = Path(__file__).parent / env_file
        if not filepath.exists():
            print(f"  ⚠️  File not found: {env_file}")
            continue

        content = read_file(filepath)

        required_models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo"]
        file_ok = True

        for model in required_models:
            if model in content:
                print(f"  [PASS] {env_file:15s} - Model listed: {model}")
            else:
                print(f"  [FAIL] {env_file:15s} - NOT FOUND: {model}")
                file_ok = False
                all_found = False

        if file_ok:
            print(f"  [PASS] {env_file:15s} - All models configured")

    return all_found


def count_total_models():
    """Count total models in kimi_config.py"""
    print("\n" + "="*70)
    print("TEST 4: Count total Kimi models")
    print("="*70)

    filepath = Path(__file__).parent / "src" / "providers" / "kimi_config.py"
    content = read_file(filepath)

    # Count ModelCapabilities definitions
    model_pattern = r'"([^"]+)": ModelCapabilities\('
    matches = re.findall(model_pattern, content)

    print(f"  Total models found: {len(matches)}")
    print(f"\n  All models:")
    for model in sorted(matches):
        print(f"    - {model}")

    # Check for our new models
    if "kimi-k2-thinking" in matches:
        print(f"\n  [PASS] kimi-k2-thinking found in model list")
    else:
        print(f"\n  [FAIL] kimi-k2-thinking NOT in model list")
        return False

    if "kimi-k2-thinking-turbo" in matches:
        print(f"  [PASS] kimi-k2-thinking-turbo found in model list")
    else:
        print(f"  [FAIL] kimi-k2-thinking-turbo NOT in model list")
        return False

    return True


def verify_timestamp():
    """Verify timestamp was updated"""
    print("\n" + "="*70)
    print("TEST 5: Verify documentation timestamp")
    print("="*70)

    filepath = Path(__file__).parent / "src" / "providers" / "kimi_config.py"
    content = read_file(filepath)

    if "2025-11-10" in content:
        print(f"  [PASS] Timestamp updated to 2025-11-10")
        return True
    else:
        print(f"  [FAIL] Timestamp not updated")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("K2 THINKING MODELS VERIFICATION TEST (Simple)")
    print("="*70)

    tests = [
        ("kimi_config.py", test_kimi_config),
        ("model_config.py", test_model_config),
        (".env files", test_env_files),
        ("Model count", count_total_models),
        ("Timestamp", verify_timestamp),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[FAIL] {test_name} - Exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Final results
    print("\n" + "="*70)
    print("FINAL TEST RESULTS")
    print("="*70)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status:10s} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "="*70)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("K2 Thinking models successfully added to configuration")
        print("\nThe following models are now available:")
        print("  * kimi-k2-thinking (256K context, thinking mode)")
        print("  * kimi-k2-thinking-turbo (256K context, high-speed, thinking mode)")
        print("\nPricing (from official Moonshot AI documentation):")
        print("  * kimi-k2-thinking: $0.60 input / $2.50 output per 1M tokens")
        print("  * kimi-k2-thinking-turbo: $1.15 input / $8.00 output per 1M tokens")
    else:
        print("[WARNING] SOME TESTS FAILED")
        print("Please review the output above")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
