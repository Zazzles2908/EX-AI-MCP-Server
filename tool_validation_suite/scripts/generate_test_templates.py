"""
Generate test script templates for all remaining tools

This script generates test script templates based on tool categories,
making it easier to create the remaining 33 test scripts.
"""

import os
from pathlib import Path

# Tool definitions
CORE_TOOLS = [
    "analyze", "debug", "codereview", "refactor", "secaudit",
    "planner", "tracer", "testgen", "consensus", "thinkdeep",
    "docgen", "precommit", "challenge"
]

ADVANCED_TOOLS = [
    "listmodels", "version", "activity", "health",
    "provider_capabilities", "toolcall_log_tail", "selfcheck"
]

PROVIDER_TOOLS = [
    "kimi_upload_and_extract", "kimi_multi_file_chat",
    "kimi_intent_analysis", "kimi_capture_headers", "kimi_chat_with_tools",
    "glm_upload_file", "glm_payload_preview"
]

INTEGRATION_TESTS = [
    "conversation_id_kimi", "conversation_id_glm", "conversation_id_isolation",
    "file_upload_kimi", "file_upload_glm", "web_search_integration"
]


def generate_core_tool_template(tool_name: str) -> str:
    """Generate template for core tools (provider API calls)"""
    return f'''"""
Test suite for {tool_name.title()} tool - Provider API validation

This test suite validates the {tool_name} tool through direct provider API calls.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.response_validator import ResponseValidator


def test_{tool_name}_basic_kimi(api_client: APIClient, **kwargs):
    """Test basic {tool_name} functionality with Kimi"""
    response = api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[
            {{"role": "user", "content": "Test prompt for {tool_name}"}}
        ],
        temperature=0.0,
        tool_name="{tool_name}",
        variation="basic_functionality"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        min_length=10,
        max_length=5000
    )
    
    return {{
        "success": is_valid and score >= 70,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }}


def test_{tool_name}_basic_glm(api_client: APIClient, **kwargs):
    """Test basic {tool_name} functionality with GLM"""
    response = api_client.call_glm(
        model="glm-4.5-flash",
        messages=[
            {{"role": "user", "content": "Test prompt for {tool_name}"}}
        ],
        temperature=0.0,
        tool_name="{tool_name}",
        variation="basic_functionality"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        min_length=10,
        max_length=5000
    )
    
    return {{
        "success": is_valid and score >= 70,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }}


def test_{tool_name}_edge_cases_kimi(api_client: APIClient, **kwargs):
    """Test edge cases with Kimi"""
    response = api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[
            {{"role": "user", "content": "Edge case test for {tool_name}"}}
        ],
        temperature=0.0,
        tool_name="{tool_name}",
        variation="edge_cases"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        min_length=5,
        max_length=5000
    )
    
    return {{
        "success": is_valid and score >= 60,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }}


def test_{tool_name}_edge_cases_glm(api_client: APIClient, **kwargs):
    """Test edge cases with GLM"""
    response = api_client.call_glm(
        model="glm-4.5-flash",
        messages=[
            {{"role": "user", "content": "Edge case test for {tool_name}"}}
        ],
        temperature=0.0,
        tool_name="{tool_name}",
        variation="edge_cases"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        min_length=5,
        max_length=5000
    )
    
    return {{
        "success": is_valid and score >= 60,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }}


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("{tool_name}", "basic_functionality", "kimi", test_{tool_name}_basic_kimi),
        ("{tool_name}", "basic_functionality", "glm", test_{tool_name}_basic_glm),
        ("{tool_name}", "edge_cases", "kimi", test_{tool_name}_edge_cases_kimi),
        ("{tool_name}", "edge_cases", "glm", test_{tool_name}_edge_cases_glm),
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
    
    print(f"\\n✅ {{tool_name.title()}} tool tests complete!")
    print(f"Results saved to: {{runner.get_results_dir()}}")
'''


def generate_advanced_tool_template(tool_name: str) -> str:
    """Generate template for advanced tools (metadata, no API calls)"""
    return f'''"""
Test suite for {tool_name.title()} tool - Metadata validation

This tool returns metadata/status information without making provider API calls.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.test_runner import TestRunner


def test_{tool_name}_basic(api_client, **kwargs):
    """Test basic {tool_name} functionality"""
    # Simulate tool response
    result = {{
        "tool": "{tool_name}",
        "status": "success",
        "data": {{
            # Tool-specific data
        }}
    }}
    
    # Validate structure
    success = "tool" in result and "status" in result
    
    return {{
        "success": success,
        "result": result,
        "validation_score": 100 if success else 0
    }}


def test_{tool_name}_edge_cases(api_client, **kwargs):
    """Test edge cases"""
    results = []
    
    for i in range(3):
        result = {{
            "tool": "{tool_name}",
            "call_number": i + 1,
            "status": "success"
        }}
        results.append(result)
    
    success = len(results) == 3
    
    return {{
        "success": success,
        "calls_made": len(results),
        "validation_score": 100 if success else 0
    }}


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("{tool_name}", "basic_functionality", "none", test_{tool_name}_basic),
        ("{tool_name}", "edge_cases", "none", test_{tool_name}_edge_cases),
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
    
    print(f"\\n✅ {{tool_name.title()}} tool tests complete!")
    print(f"Results saved to: {{runner.get_results_dir()}}")
'''


def main():
    """Generate all test templates"""
    base_dir = Path(__file__).parent.parent / "tests"
    
    # Generate core tool templates
    print("Generating core tool templates...")
    for tool in CORE_TOOLS:
        filepath = base_dir / "core_tools" / f"test_{tool}.py"
        if not filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generate_core_tool_template(tool))
            print(f"  ✅ Created {filepath.name}")
        else:
            print(f"  ⏭️  Skipped {filepath.name} (already exists)")
    
    # Generate advanced tool templates
    print("\\nGenerating advanced tool templates...")
    for tool in ADVANCED_TOOLS:
        filepath = base_dir / "advanced_tools" / f"test_{tool}.py"
        if not filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generate_advanced_tool_template(tool))
            print(f"  ✅ Created {filepath.name}")
        else:
            print(f"  ⏭️  Skipped {filepath.name} (already exists)")
    
    print(f"\\n✅ Template generation complete!")
    print(f"\\nNext steps:")
    print(f"1. Review generated templates in tests/core_tools/ and tests/advanced_tools/")
    print(f"2. Customize test prompts and validation logic")
    print(f"3. Create provider tool and integration test templates manually")
    print(f"4. Run tests with: python scripts/run_all_tests.py")


if __name__ == "__main__":
    main()

