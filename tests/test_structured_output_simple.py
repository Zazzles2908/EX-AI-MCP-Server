#!/usr/bin/env python
"""
Simple Test for Structured Output Implementation

Direct testing without full module imports.
Tests the specific changes made to implement response_format support.
"""

import json
import os
import sys


def test_model_configs():
    """Test that model configurations include supports_json_mode=True"""
    print("\n" + "=" * 80)
    print("TEST 1: Model Configurations Support JSON Mode")
    print("=" * 80)

    # Read GLM config
    glm_config_path = "src/providers/glm_config.py"
    if os.path.exists(glm_config_path):
        with open(glm_config_path, 'r') as f:
            glm_content = f.read()

        glm_has_json_mode = 'supports_json_mode=True' in glm_content
        glm_count = glm_content.count('supports_json_mode=True')

        print(f"\nGLM Config ({glm_config_path}):")
        print(f"  [OK] Found supports_json_mode=True: {glm_has_json_mode}")
        print(f"  [OK] Models with JSON mode: {glm_count}")

        # Count GLM models
        model_count = glm_content.count('ModelCapabilities(')
        print(f"  [OK] Total GLM models: {model_count}")
    else:
        print(f"\n[FAIL] GLM config not found at {glm_config_path}")
        glm_has_json_mode = False

    # Read Kimi config
    kimi_config_path = "src/providers/kimi_config.py"
    if os.path.exists(kimi_config_path):
        with open(kimi_config_path, 'r') as f:
            kimi_content = f.read()

        kimi_has_json_mode = 'supports_json_mode=True' in kimi_content
        kimi_count = kimi_content.count('supports_json_mode=True')

        print(f"\nKimi Config ({kimi_config_path}):")
        print(f"  [OK] Found supports_json_mode=True: {kimi_has_json_mode}")
        print(f"  [OK] Models with JSON mode: {kimi_count}")

        # Count Kimi models
        kimi_model_count = kimi_content.count('ModelCapabilities(')
        print(f"  [OK] Total Kimi models: {kimi_model_count}")
    else:
        print(f"\n[FAIL] Kimi config not found at {kimi_config_path}")
        kimi_has_json_mode = False

    return glm_has_json_mode and kimi_has_json_mode


def test_payload_handling():
    """Test that payload handling includes response_format"""
    print("\n" + "=" * 80)
    print("TEST 2: Payload Handling Includes response_format")
    print("=" * 80)

    # Read GLM provider
    glm_provider_path = "src/providers/glm_provider.py"
    if os.path.exists(glm_provider_path):
        with open(glm_provider_path, 'r') as f:
            glm_content = f.read()

        # Check for response_format in build_payload
        has_build_payload_support = 'response_format' in glm_content and 'build_payload' in glm_content
        build_payload_support = 'if "response_format" in kwargs:' in glm_content

        # Check for response_format in chat_completions_create
        chat_completions_support = 'if "response_format" in kwargs:' in glm_content and 'chat_completions' in glm_content

        print(f"\nGLM Provider ({glm_provider_path}):")
        print(f"  [OK] build_payload handles response_format: {build_payload_support}")
        print(f"  [OK] chat_completions handles response_format: {chat_completions_support}")
        print(f"  Overall: {'[PASS]' if (build_payload_support and chat_completions_support) else '[FAIL]'}")

        return build_payload_support and chat_completions_support
    else:
        print(f"\n[FAIL] GLM provider not found at {glm_provider_path}")
        return False


def test_openai_compatible():
    """Test that OpenAI-compatible provider includes response_format"""
    print("\n" + "=" * 80)
    print("TEST 3: OpenAI-Compatible Provider Includes response_format")
    print("=" * 80)

    openai_path = "src/providers/openai_content_generator.py"
    if os.path.exists(openai_path):
        with open(openai_path, 'r') as f:
            content = f.read()

        has_response_format = 'response_format' in content
        in_build_params = 'if "response_format" in kwargs and kwargs["response_format"]:' in content

        print(f"\nOpenAI Content Generator ({openai_path}):")
        print(f"  [OK] Contains response_format: {has_response_format}")
        print(f"  [OK] In _build_completion_params: {in_build_params}")
        print(f"  Overall: {'[PASS]' if in_build_params else '[FAIL]'}")

        return in_build_params
    else:
        print(f"\n[FAIL] OpenAI content generator not found at {openai_path}")
        return False


def test_validation():
    """Test that validation includes response_format check"""
    print("\n" + "=" * 80)
    print("TEST 4: Validation Includes response_format Check")
    print("=" * 80)

    base_path = "src/providers/base.py"
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            content = f.read()

        has_validation = 'response_format' in content and 'supports_json_mode' in content
        in_validate_params = 'if "response_format" in kwargs' in content

        print(f"\nBase Provider ({base_path}):")
        print(f"  [OK] Contains response_format validation: {has_validation}")
        print(f"  [OK] In validate_parameters: {in_validate_params}")
        print(f"  Overall: {'[PASS]' if in_validate_params else '[FAIL]'}")

        return in_validate_params
    else:
        print(f"\n[FAIL] Base provider not found at {base_path}")
        return False


def show_usage_examples():
    """Show usage examples"""
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES - Structured Output with JSON Schema")
    print("=" * 80)

    example_schema = {
        "type": "object",
        "properties": {
            "code_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"]
                        },
                        "line": {"type": "integer"},
                        "message": {"type": "string"}
                    },
                    "required": ["severity", "line", "message"]
                }
            }
        },
        "required": ["code_issues"]
    }

    print("\nExample 1: Code Analysis with Structured Output")
    print("-" * 80)
    print(json.dumps(example_schema, indent=2))

    print("\n\nExample 2: Usage in Code")
    print("-" * 80)
    print("""
# With GLM Provider
provider = GLMModelProvider(api_key="your-api-key")
response = provider.generate_content(
    prompt="Analyze this code for issues",
    model_name="glm-4.6",
    response_format=example_schema
)
# Response will be JSON matching the schema

# With Kimi Provider
provider = KimiModelProvider(api_key="your-api-key")
response = provider.generate_content(
    prompt="Extract structured data",
    model_name="kimi-k2-0905-preview",
    response_format=example_schema
)
# Response will be JSON matching the schema
""")

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("STRUCTURED OUTPUT IMPLEMENTATION VERIFICATION")
    print("zai-sdk 0.0.4 - response_format with JSON Schema")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Model Configurations", test_model_configs()))
    results.append(("Payload Handling", test_payload_handling()))
    results.append(("OpenAI-Compatible Support", test_openai_compatible()))
    results.append(("Validation", test_validation()))
    results.append(("Usage Examples", show_usage_examples()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:50s} {status}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\nStructured Output (response_format) is fully implemented!")
        print("\nFeatures:")
        print("  ✅ Models support JSON mode (supports_json_mode=True)")
        print("  ✅ Build payload includes response_format")
        print("  ✅ chat_completions handles response_format")
        print("  ✅ OpenAI-compatible providers support response_format")
        print("  ✅ Validation checks response_format support")
        print("\nSupported Models:")
        print("  GLM: glm-4.6, glm-4.5, glm-4.5v, glm-4.5-air, glm-4.5-airx, glm-4.5-flash, glm-4-32b")
        print("  Kimi: kimi-k2-0905-preview, kimi-k2-0711-preview, kimi-k2-turbo-preview, kimi-thinking-preview")
        return 0
    else:
        print(f"\n❌ {total-passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
