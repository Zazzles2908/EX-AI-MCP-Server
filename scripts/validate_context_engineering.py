"""
Validation script for Context Engineering Phase 1 implementation.

This script validates the core components without requiring pytest:
- History detection
- Token counting
- Migration utilities
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conversation.history_detection import (
    HistoryDetector, DetectionMode, strip_embedded_history,
    strip_history_recursive, quick_strip
)
from utils.conversation.token_utils import (
    TokenCounter, validate_token_budget, truncate_to_token_limit,
    validate_message_tokens, count_tokens
)
from utils.conversation.migration import (
    ConversationMigrator, ConversationTurn, migrate_turn_with_history_stripping,
    CURRENT_VERSION
)


def validate_history_detection():
    """Validate history detection functionality."""
    print("\n=== Validating History Detection ===")
    
    # Test 1: Conservative detection with clear markers
    detector = HistoryDetector(DetectionMode.CONSERVATIVE)
    test_text = "Hello\n=== CONVERSATION HISTORY ===\nOld message\n=== END ===\nWorld"
    markers = detector.detect_history_markers(test_text)
    assert len(markers) == 1, f"Expected 1 marker, got {len(markers)}"
    print("✅ Conservative detection with clear markers")
    
    # Test 2: No markers
    test_text = "Hello world\nNo history here"
    markers = detector.detect_history_markers(test_text)
    assert len(markers) == 0, f"Expected 0 markers, got {len(markers)}"
    print("✅ No false positives on clean text")
    
    # Test 3: Aggressive detection
    detector = HistoryDetector(DetectionMode.AGGRESSIVE)
    test_text = "Hello\n=== CHAT HISTORY ===\nOld message\n=== END ===\nWorld"
    markers = detector.detect_history_markers(test_text)
    assert len(markers) >= 1, f"Expected at least 1 marker, got {len(markers)}"
    print("✅ Aggressive detection with broader markers")
    
    # Test 4: History stripping
    test_text = "User input\n=== CONVERSATION HISTORY ===\nOld messages\n=== END ===\nNew content"
    clean = detector.strip_history(test_text)
    assert "CONVERSATION HISTORY" not in clean, "History marker still present"
    assert "User input" in clean, "User input was removed"
    assert "New content" in clean, "New content was removed"
    print("✅ History stripping preserves user content")
    
    # Test 5: Recursive stripping
    test_text = "=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ===\nNew"
    clean = strip_history_recursive(test_text)
    detector_check = HistoryDetector(DetectionMode.AGGRESSIVE)
    assert not detector_check.has_embedded_history(clean), "Nested history not fully stripped"
    print("✅ Recursive stripping removes nested history")
    
    # Test 6: Convenience functions
    test_text = "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nNew"
    clean = strip_embedded_history(test_text)
    assert "CONVERSATION HISTORY" not in clean, "Convenience function failed"
    print("✅ Convenience functions work correctly")
    
    clean = quick_strip(test_text)
    assert "CONVERSATION HISTORY" not in clean, "Quick strip failed"
    print("✅ Quick strip works correctly")
    
    print("✅ All history detection tests passed!")


def validate_token_counting():
    """Validate token counting functionality."""
    print("\n=== Validating Token Counting ===")
    
    # Test 1: Basic counting
    counter = TokenCounter()
    count = counter.count_tokens("Hello world")
    assert count > 0, f"Expected positive count, got {count}"
    print(f"✅ Basic token counting: 'Hello world' = {count} tokens")
    
    # Test 2: Empty string
    count = counter.count_tokens("")
    assert count == 0, f"Expected 0 for empty string, got {count}"
    print("✅ Empty string returns 0 tokens")
    
    # Test 3: Different models
    text = "Hello world"
    count_gpt = counter.count_tokens(text, "gpt-4")
    count_glm = counter.count_tokens(text, "glm-4.6")
    count_kimi = counter.count_tokens(text, "kimi-k2-0905-preview")
    assert all(c > 0 for c in [count_gpt, count_glm, count_kimi]), "Model-specific counting failed"
    print(f"✅ Multi-model support: GPT={count_gpt}, GLM={count_glm}, Kimi={count_kimi}")
    
    # Test 4: Message counting
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    count = counter.count_messages_tokens(messages)
    assert count > 0, f"Expected positive count for messages, got {count}"
    print(f"✅ Message token counting: {len(messages)} messages = {count} tokens")
    
    # Test 5: Token budget validation
    content = "Short message"
    history = [
        {"content": "Previous message 1", "tokens": 5},
        {"content": "Previous message 2", "tokens": 5}
    ]
    validated_content, trimmed_history = validate_token_budget(content, history, max_total=1000)
    assert validated_content == content, "Content was modified"
    assert len(trimmed_history) == len(history), "History was trimmed unnecessarily"
    print("✅ Token budget validation within limits")
    
    # Test 6: Budget trimming
    content = "Short message"
    large_history = [{"content": "Message " * 100, "tokens": 200} for _ in range(50)]
    validated_content, trimmed_history = validate_token_budget(content, large_history, max_total=1000)
    assert len(trimmed_history) < len(large_history), "History was not trimmed"
    print(f"✅ Token budget trimming: {len(large_history)} -> {len(trimmed_history)} messages")
    
    # Test 7: Circuit breaker
    try:
        content = "Very long message " * 1000
        validate_token_budget(content, [], max_total=100)
        assert False, "Circuit breaker did not trigger"
    except ValueError as e:
        assert "circuit breaker" in str(e).lower(), "Wrong error message"
        print("✅ Circuit breaker triggers for oversized content")
    
    # Test 8: Truncation
    text = "This is a long message that needs to be truncated " * 100
    truncated = truncate_to_token_limit(text, 50)
    truncated_count = counter.count_tokens(truncated)
    assert truncated_count <= 50, f"Truncated text has {truncated_count} tokens, expected <= 50"
    print(f"✅ Text truncation: {len(text)} chars -> {len(truncated)} chars ({truncated_count} tokens)")
    
    # Test 9: Message validation
    content = "Short message"
    is_valid, token_count = validate_message_tokens(content, max_tokens=1000)
    assert is_valid is True, "Valid message marked as invalid"
    print(f"✅ Message validation: {token_count} tokens (valid)")
    
    content = "Very long message " * 1000
    is_valid, token_count = validate_message_tokens(content, max_tokens=10)
    assert is_valid is False, "Invalid message marked as valid"
    print(f"✅ Message validation: {token_count} tokens (invalid)")
    
    # Test 10: Convenience function
    count = count_tokens("Hello world")
    assert count > 0, "Convenience function failed"
    print("✅ Convenience function works correctly")
    
    print("✅ All token counting tests passed!")


def validate_migration():
    """Validate migration functionality."""
    print("\n=== Validating Migration ===")
    
    # Test 1: Turn creation
    turn = ConversationTurn("user", "Hello", {"key": "value"})
    assert turn.role == "user", "Role not set correctly"
    assert turn.content == "Hello", "Content not set correctly"
    assert turn.metadata["key"] == "value", "Metadata not set correctly"
    assert turn.version == CURRENT_VERSION, "Version not set correctly"
    print("✅ Turn creation with metadata")
    
    # Test 2: Turn to dict
    turn_dict = turn.to_dict()
    assert turn_dict["role"] == "user", "Dict conversion failed for role"
    assert turn_dict["content"] == "Hello", "Dict conversion failed for content"
    assert turn_dict["version"] == CURRENT_VERSION, "Dict conversion failed for version"
    print("✅ Turn to dictionary conversion")
    
    # Test 3: Turn from dict
    turn_dict = {
        "role": "assistant",
        "content": "Hi",
        "version": "1.0.0",
        "metadata": {"key": "value"}
    }
    turn = ConversationTurn.from_dict(turn_dict)
    assert turn.role == "assistant", "From dict failed for role"
    assert turn.content == "Hi", "From dict failed for content"
    assert turn.metadata["key"] == "value", "From dict failed for metadata"
    print("✅ Turn from dictionary conversion")
    
    # Test 4: Pre-versioned migration
    migrator = ConversationMigrator()
    old_turn = {"role": "user", "content": "Hello"}
    new_turn = migrator.migrate_turn(old_turn)
    assert new_turn.version == CURRENT_VERSION, "Pre-versioned migration failed"
    assert new_turn.role == "user", "Role lost during migration"
    assert new_turn.content == "Hello", "Content lost during migration"
    print("✅ Pre-versioned turn migration")
    
    # Test 5: Current version migration
    current_turn = {
        "role": "assistant",
        "content": "Hi",
        "version": CURRENT_VERSION,
        "metadata": {"key": "value"}
    }
    new_turn = migrator.migrate_turn(current_turn)
    assert new_turn.version == CURRENT_VERSION, "Current version migration failed"
    assert new_turn.metadata["key"] == "value", "Metadata lost during migration"
    print("✅ Current version turn migration")
    
    # Test 6: Conversation migration
    turns = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "How are you?"}
    ]
    migrated = migrator.migrate_conversation(turns)
    assert len(migrated) == 3, f"Expected 3 turns, got {len(migrated)}"
    assert all(turn.version == CURRENT_VERSION for turn in migrated), "Not all turns migrated"
    print(f"✅ Conversation migration: {len(turns)} turns")
    
    # Test 7: Migration with history stripping
    turn_data = {
        "role": "user",
        "content": "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nNew message"
    }
    migrated = migrate_turn_with_history_stripping(turn_data, strip_history=True)
    assert "CONVERSATION HISTORY" not in migrated.content, "History not stripped during migration"
    assert "New message" in migrated.content, "User content lost during migration"
    assert migrated.metadata.get("history_stripped") is True, "History stripped flag not set"
    print("✅ Migration with history stripping")
    
    # Test 8: Migration stats
    stats = migrator.get_migration_stats()
    assert "total_migrated" in stats, "Stats missing total_migrated"
    assert "by_version" in stats, "Stats missing by_version"
    print(f"✅ Migration stats: {stats['total_migrated']} total migrations")
    
    print("✅ All migration tests passed!")


def validate_integration():
    """Validate integration between components."""
    print("\n=== Validating Component Integration ===")
    
    # Test 1: History stripping + token counting
    text = "=== CONVERSATION HISTORY ===\nOld messages " * 100 + "\n=== END ===\nNew message"
    clean = strip_embedded_history(text)
    
    counter = TokenCounter()
    original_tokens = counter.count_tokens(text)
    clean_tokens = counter.count_tokens(clean)
    
    assert clean_tokens < original_tokens, "Token count not reduced after stripping"
    reduction = ((original_tokens - clean_tokens) / original_tokens) * 100
    print(f"✅ History stripping reduces tokens: {original_tokens} -> {clean_tokens} ({reduction:.1f}% reduction)")
    
    # Test 2: Migration + history stripping + token counting
    turn_data = {
        "role": "user",
        "content": "=== CONVERSATION HISTORY ===\n" + ("Old message\n" * 50) + "=== END ===\nNew message"
    }
    
    migrated = migrate_turn_with_history_stripping(turn_data, strip_history=True)
    migrated_tokens = counter.count_tokens(migrated.content)
    original_tokens = counter.count_tokens(turn_data["content"])
    
    assert migrated_tokens < original_tokens, "Migration + stripping did not reduce tokens"
    reduction = ((original_tokens - migrated_tokens) / original_tokens) * 100
    print(f"✅ Migration + stripping reduces tokens: {original_tokens} -> {migrated_tokens} ({reduction:.1f}% reduction)")
    
    # Test 3: Recursive stripping prevents re-embedding
    text = "=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ===\nNew"
    clean = strip_history_recursive(text)
    
    detector = HistoryDetector(DetectionMode.AGGRESSIVE)
    assert not detector.has_embedded_history(clean), "Recursive stripping failed to remove all markers"
    print("✅ Recursive stripping prevents re-embedding")
    
    print("✅ All integration tests passed!")


def main():
    """Run all validation tests."""
    print("=" * 80)
    print("Context Engineering Phase 1 - Implementation Validation")
    print("=" * 80)
    
    try:
        validate_history_detection()
        validate_token_counting()
        validate_migration()
        validate_integration()
        
        print("\n" + "=" * 80)
        print("✅ ALL VALIDATIONS PASSED!")
        print("=" * 80)
        print("\nImplementation is ready for integration into memory.py and storage_factory.py")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

