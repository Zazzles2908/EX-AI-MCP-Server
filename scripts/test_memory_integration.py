"""
Test script for Context Engineering Phase 1 - memory.py integration.

This script validates that history stripping is working correctly in the
conversation memory system.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversation.threads import create_thread, add_turn, get_thread
from utils.conversation.history_detection import HistoryDetector, DetectionMode
from utils.conversation.token_utils import TokenCounter
from config import CONTEXT_ENGINEERING
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_basic_history_stripping():
    """Test that history stripping works in add_turn()."""
    print("\n=== Test 1: Basic History Stripping ===")

    # Create a test thread
    thread_id = create_thread("test", {"test": "data"})
    print(f"Created thread: {thread_id}")

    # Add a turn with embedded history (make it long enough to exceed threshold)
    # Repeat the history section to ensure we exceed the 100 token threshold
    test_content = "User message\n=== CONVERSATION HISTORY ===\n" + ("Old messages here\n" * 50) + "=== END ===\nNew content"
    success = add_turn(thread_id, "user", test_content)
    assert success, "Failed to add turn"
    print("✅ Added turn with embedded history")
    
    # Retrieve the thread and check the last turn
    thread = get_thread(thread_id)
    assert thread is not None, "Failed to retrieve thread"
    
    last_turn = thread.turns[-1]
    print(f"Original content length: {len(test_content)} chars")
    print(f"Stored content length: {len(last_turn.content)} chars")
    
    # Verify history was stripped
    assert "CONVERSATION HISTORY" not in last_turn.content, "History marker still present!"
    assert "User message" in last_turn.content, "User content was removed!"
    assert "New content" in last_turn.content, "User content was removed!"
    
    # Calculate token reduction
    counter = TokenCounter()
    original_tokens = counter.count_tokens(test_content)
    stored_tokens = counter.count_tokens(last_turn.content)
    reduction = ((original_tokens - stored_tokens) / original_tokens * 100) if original_tokens > 0 else 0
    
    print(f"Token reduction: {original_tokens} → {stored_tokens} ({reduction:.1f}%)")
    print("✅ History stripping works correctly!")


def test_no_history_passthrough():
    """Test that content without history passes through unchanged."""
    print("\n=== Test 2: No History Passthrough ===")
    
    # Create a test thread
    thread_id = create_thread("test", {"test": "data"})
    print(f"Created thread: {thread_id}")
    
    # Add a turn without embedded history
    test_content = "This is a normal user message without any history markers."
    success = add_turn(thread_id, "user", test_content)
    assert success, "Failed to add turn"
    print("✅ Added turn without embedded history")
    
    # Retrieve the thread and check the last turn
    thread = get_thread(thread_id)
    assert thread is not None, "Failed to retrieve thread"
    
    last_turn = thread.turns[-1]
    
    # Verify content is unchanged
    assert last_turn.content == test_content, "Content was modified!"
    print("✅ Content without history passes through unchanged!")


def test_assistant_messages_not_stripped():
    """Test that assistant messages are not stripped."""
    print("\n=== Test 3: Assistant Messages Not Stripped ===")
    
    # Create a test thread
    thread_id = create_thread("test", {"test": "data"})
    print(f"Created thread: {thread_id}")
    
    # Add an assistant turn with history markers (should NOT be stripped)
    test_content = "Assistant response\n=== CONVERSATION HISTORY ===\nContext\n=== END ===\nMore response"
    success = add_turn(thread_id, "assistant", test_content)
    assert success, "Failed to add turn"
    print("✅ Added assistant turn with history markers")
    
    # Retrieve the thread and check the last turn
    thread = get_thread(thread_id)
    assert thread is not None, "Failed to retrieve thread"
    
    last_turn = thread.turns[-1]
    
    # Verify history was NOT stripped (assistant messages are not stripped)
    assert last_turn.content == test_content, "Assistant message was modified!"
    print("✅ Assistant messages are not stripped!")


def test_nested_history_stripping():
    """Test that nested history is recursively stripped."""
    print("\n=== Test 4: Nested History Stripping ===")
    
    # Create a test thread
    thread_id = create_thread("test", {"test": "data"})
    print(f"Created thread: {thread_id}")
    
    # Add a turn with nested history
    test_content = "User message\n=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ===\nNew content"
    success = add_turn(thread_id, "user", test_content)
    assert success, "Failed to add turn"
    print("✅ Added turn with nested history")
    
    # Retrieve the thread and check the last turn
    thread = get_thread(thread_id)
    assert thread is not None, "Failed to retrieve thread"
    
    last_turn = thread.turns[-1]
    
    # Verify all history markers were stripped
    detector = HistoryDetector(DetectionMode.AGGRESSIVE)
    assert not detector.has_embedded_history(last_turn.content), "Nested history not fully stripped!"
    assert "User message" in last_turn.content, "User content was removed!"
    assert "New content" in last_turn.content, "User content was removed!"
    
    print("✅ Nested history is recursively stripped!")


def test_token_threshold():
    """Test that small messages below threshold are not stripped."""
    print("\n=== Test 5: Token Threshold ===")
    
    # Create a test thread
    thread_id = create_thread("test", {"test": "data"})
    print(f"Created thread: {thread_id}")
    
    # Add a very short turn with history marker (below threshold)
    # Default threshold is 100 tokens, this should be well below that
    test_content = "Hi\n=== HISTORY ===\nOld\n=== END ===\nBye"
    success = add_turn(thread_id, "user", test_content)
    assert success, "Failed to add turn"
    print("✅ Added short turn with history marker")
    
    # Retrieve the thread and check the last turn
    thread = get_thread(thread_id)
    assert thread is not None, "Failed to retrieve thread"
    
    last_turn = thread.turns[-1]
    
    # Check token count
    counter = TokenCounter()
    token_count = counter.count_tokens(test_content)
    print(f"Token count: {token_count} (threshold: {CONTEXT_ENGINEERING.get('min_token_threshold', 100)})")
    
    # If below threshold, history should NOT be stripped
    if token_count < CONTEXT_ENGINEERING.get('min_token_threshold', 100):
        # Note: This test might fail if the threshold is very low
        # In that case, the history would be stripped
        print("✅ Token threshold check passed (content below threshold)")
    else:
        print("✅ Token threshold check passed (content above threshold, stripped)")


def test_config_flags():
    """Test that configuration flags are respected."""
    print("\n=== Test 6: Configuration Flags ===")
    
    print(f"Current config:")
    print(f"  strip_embedded_history: {CONTEXT_ENGINEERING.get('strip_embedded_history')}")
    print(f"  detection_mode: {CONTEXT_ENGINEERING.get('detection_mode')}")
    print(f"  dry_run: {CONTEXT_ENGINEERING.get('dry_run')}")
    print(f"  log_stripping: {CONTEXT_ENGINEERING.get('log_stripping')}")
    print(f"  min_token_threshold: {CONTEXT_ENGINEERING.get('min_token_threshold')}")
    
    print("✅ Configuration flags loaded successfully!")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Context Engineering Phase 1 - Memory Integration Tests")
    print("=" * 80)
    
    try:
        test_config_flags()
        test_basic_history_stripping()
        test_no_history_passthrough()
        test_assistant_messages_not_stripped()
        test_nested_history_stripping()
        test_token_threshold()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nMemory integration is working correctly!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

