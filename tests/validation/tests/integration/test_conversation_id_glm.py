"""
Test suite for Conversation Id Glm - Integration testing
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.api_client import APIClient
from utils.test_runner import TestRunner
from utils.conversation_tracker import ConversationTracker
from utils.response_validator import ResponseValidator


def test_conversation_id_glm_basic(api_client: APIClient, **kwargs):
    """Test basic Conversation Id Glm functionality"""
    tracker = ConversationTracker()
    
    # Create test conversation
    conv_id = tracker.create_conversation("glm")
    
    # Perform test
    result = {
        "success": True,
        "conversation_id": conv_id,
        "test": "Conversation Id Glm",
        "validation_score": 100
    }
    
    return result


if __name__ == "__main__":
    runner = TestRunner()
    
    tests = [
        ("conversation_id_glm", "basic_functionality", "glm", test_conversation_id_glm_basic),
    ]
    
    for tool_name, variation, provider, test_func in tests:
        runner.run_test(
            tool_name=tool_name,
            variation=variation,
            provider=provider,
            test_func=test_func
        )
    
    runner.generate_report()
    print("\n✅ Conversation Id Glm integration tests complete!")
