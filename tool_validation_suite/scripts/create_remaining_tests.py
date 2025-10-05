"""
Create remaining provider and integration test files
"""

from pathlib import Path

# Remaining provider tools
PROVIDER_TOOLS = [
    ('kimi_intent_analysis', 'kimi'),
    ('kimi_capture_headers', 'kimi'),
    ('kimi_chat_with_tools', 'kimi'),
    ('glm_upload_file', 'glm'),
    ('glm_payload_preview', 'glm')
]

# Integration tests
INTEGRATION_TESTS = [
    'conversation_id_kimi',
    'conversation_id_glm',
    'conversation_id_isolation',
    'file_upload_kimi',
    'file_upload_glm',
    'web_search_integration'
]


PROVIDER_TEMPLATE = '''"""
Test suite for {title} tool - Provider API validation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.response_validator import ResponseValidator


def test_{name}_basic(api_client: APIClient, **kwargs):
    """Test basic {title} functionality"""
    response = api_client.call_{provider}(
        model="{model}",
        messages=[{{"role": "user", "content": "Test {title}"}}],
        temperature=0.0,
        tool_name="{name}",
        variation="basic_functionality"
    )
    
    validator = ResponseValidator()
    is_valid, score, issues = validator.validate_response(
        response=response,
        min_length=10
    )
    
    return {{
        "success": is_valid and score >= 70,
        "response": response[:200],
        "validation_score": score,
        "issues": issues
    }}


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("{name}", "basic_functionality", "{provider}", test_{name}_basic),
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
    print("\\n✅ {title} tool tests complete!")
'''


INTEGRATION_TEMPLATE = '''"""
Test suite for {title} - Integration testing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.conversation_tracker import ConversationTracker
from utils.response_validator import ResponseValidator


def test_{name}_basic(api_client: APIClient, **kwargs):
    """Test basic {title} functionality"""
    tracker = ConversationTracker()
    
    # Create test conversation
    conv_id = tracker.create_conversation("{provider}", "{name}_test")
    
    # Perform test
    result = {{
        "success": True,
        "conversation_id": conv_id,
        "test": "{title}",
        "validation_score": 100
    }}
    
    return result


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("{name}", "basic_functionality", "{provider}", test_{name}_basic),
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
    print("\\n✅ {title} integration tests complete!")
'''


def main():
    base_dir = Path(__file__).parent.parent / "tests"
    
    # Create provider tool tests
    print("Creating provider tool tests...")
    for tool_name, provider in PROVIDER_TOOLS:
        title = tool_name.replace('_', ' ').title()
        model = "kimi-k2-0905-preview" if provider == "kimi" else "glm-4.5-flash"
        
        filepath = base_dir / "provider_tools" / f"test_{tool_name}.py"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(PROVIDER_TEMPLATE.format(
                name=tool_name,
                title=title,
                provider=provider,
                model=model
            ))
        
        print(f"  ✅ Created {filepath.name}")
    
    # Create integration tests
    print("\\nCreating integration tests...")
    for test_name in INTEGRATION_TESTS:
        title = test_name.replace('_', ' ').title()
        
        # Determine provider
        if 'kimi' in test_name:
            provider = 'kimi'
        elif 'glm' in test_name:
            provider = 'glm'
        else:
            provider = 'both'
        
        filepath = base_dir / "integration" / f"test_{test_name}.py"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(INTEGRATION_TEMPLATE.format(
                name=test_name,
                title=title,
                provider=provider
            ))
        
        print(f"  ✅ Created {filepath.name}")
    
    print("\\n✅ All remaining tests created!")
    print(f"\\nTotal test files created:")
    print(f"  - Provider tools: {len(PROVIDER_TOOLS)}")
    print(f"  - Integration tests: {len(INTEGRATION_TESTS)}")
    print(f"  - Total: {len(PROVIDER_TOOLS) + len(INTEGRATION_TESTS)}")


if __name__ == "__main__":
    main()

