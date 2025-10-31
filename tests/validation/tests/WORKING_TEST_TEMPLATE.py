"""
WORKING TEST TEMPLATE - Correct usage of test utilities

This shows the CORRECT way to write test scripts that work with
the test validation suite utilities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.response_validator import ResponseValidator


def test_example_kimi(api_client: APIClient, **kwargs):
    """Test example with Kimi - CORRECT implementation"""
    # Call API - returns full response dictionary
    response = api_client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[
            {"role": "user", "content": "Say hello in 5 words"}
        ],
        temperature=0.0,
        tool_name="example",
        variation="basic_functionality"
    )
    
    # Response is a dictionary with structure:
    # {
    #     "choices": [{"message": {"content": "..."}}],
    #     "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    #     "_metadata": {...}
    # }
    
    # Extract the actual text content
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # Validate the response dictionary (not the content string!)
    validator = ResponseValidator()
    validation = validator.validate_response(
        response=response,
        tool_type="simple"
    )
    
    # Return test result
    return {
        "success": validation["valid"] and len(content) > 0,
        "content": content[:200],  # First 200 chars
        "validation": validation,
        "tokens": response.get("usage", {})
    }


def test_example_glm(api_client: APIClient, **kwargs):
    """Test example with GLM - CORRECT implementation"""
    # Call API
    response = api_client.call_glm(
        model="glm-4.5-flash",
        messages=[
            {"role": "user", "content": "Say hello in 5 words"}
        ],
        temperature=0.0,
        tool_name="example",
        variation="basic_functionality"
    )
    
    # Extract content
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # Validate
    validator = ResponseValidator()
    validation = validator.validate_response(
        response=response,
        tool_type="simple"
    )
    
    # Return result
    return {
        "success": validation["valid"] and len(content) > 0,
        "content": content[:200],
        "validation": validation,
        "tokens": response.get("usage", {})
    }


if __name__ == "__main__":
    # Initialize test runner
    runner = TestRunner()
    
    # Define tests to run
    tests = [
        ("example", "basic_functionality", test_example_kimi),
        ("example", "basic_functionality", test_example_glm),
    ]
    
    # Run each test
    for tool_name, variation, test_func in tests:
        result = runner.run_test(
            tool_name=tool_name,
            variation=variation,
            test_func=test_func
        )
        
        print(f"\n{'='*60}")
        print(f"Test: {tool_name}/{variation}")
        print(f"Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'passed':
            print(f"✅ PASSED")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        print(f"{'='*60}")
    
    # Generate report
    runner.generate_report()
    
    # Print summary
    runner.print_results()
    
    print(f"\n✅ Example tool tests complete!")
    print(f"Results saved to: {runner.get_results_dir()}")

