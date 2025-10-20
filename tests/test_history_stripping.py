"""
Comprehensive tests for history stripping functionality.

Tests cover:
- History detection (conservative and aggressive modes)
- Token counting and validation
- Conversation migration
- No recursive embedding guarantee
"""

import pytest
from utils.conversation.history_detection import (
    HistoryDetector, DetectionMode, strip_embedded_history,
    detect_and_log_history, strip_history_recursive, quick_strip
)
from utils.conversation.token_utils import (
    TokenCounter, validate_token_budget, truncate_to_token_limit,
    validate_message_tokens, count_tokens
)
from utils.conversation.migration import (
    ConversationTurn, ConversationMigrator, migrate_turn_with_history_stripping,
    batch_migrate_conversations, quick_migrate, CURRENT_VERSION
)


class TestHistoryDetection:
    """Tests for history detection functionality."""
    
    def test_conservative_detection_clear_markers(self):
        """Test conservative detection with clear markers."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        # Test with clear marker
        text = "Hello\n=== CONVERSATION HISTORY ===\nOld message\n=== END ===\nWorld"
        markers = detector.detect_history_markers(text)
        assert len(markers) == 1
        assert markers[0][0] == text.find("=== CONVERSATION HISTORY ===")
    
    def test_conservative_detection_no_markers(self):
        """Test conservative detection with no markers."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        text = "Hello world\nNo history here"
        markers = detector.detect_history_markers(text)
        assert len(markers) == 0
    
    def test_aggressive_detection_broader_markers(self):
        """Test aggressive detection with less common markers."""
        detector = HistoryDetector(DetectionMode.AGGRESSIVE)
        
        text = "Hello\n=== CHAT HISTORY ===\nOld message\n=== END ===\nWorld"
        markers = detector.detect_history_markers(text)
        assert len(markers) >= 1
    
    def test_multiple_markers(self):
        """Test detection of multiple markers."""
        detector = HistoryDetector(DetectionMode.AGGRESSIVE)
        
        text = "=== PREVIOUS ===\nOld\n=== CONVERSATION HISTORY ===\nOlder\n=== END ==="
        markers = detector.detect_history_markers(text)
        assert len(markers) >= 2
    
    def test_nested_markers(self):
        """Test detection of nested markers."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        text = "=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ==="
        sections = detector.extract_history_sections(text)
        assert len(sections) >= 1
    
    def test_strip_history_basic(self):
        """Test basic history stripping."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        text = "User input\n=== CONVERSATION HISTORY ===\nOld messages\n=== END ===\nNew content"
        clean = detector.strip_history(text)
        
        # Should remove history section
        assert "CONVERSATION HISTORY" not in clean
        assert "User input" in clean
        assert "New content" in clean
    
    def test_strip_history_preserve_user_content(self):
        """Test that user content after history is preserved."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        text = "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nImportant user message"
        clean = detector.strip_history(text, preserve_user_content=True)
        
        assert "Important user message" in clean
        assert "CONVERSATION HISTORY" not in clean
    
    def test_has_embedded_history(self):
        """Test detection of embedded history."""
        detector = HistoryDetector(DetectionMode.CONSERVATIVE)
        
        text_with_history = "=== CONVERSATION HISTORY ===\nOld"
        text_without_history = "Just a normal message"
        
        assert detector.has_embedded_history(text_with_history) is True
        assert detector.has_embedded_history(text_without_history) is False
    
    def test_strip_embedded_history_convenience(self):
        """Test convenience function for stripping history."""
        text = "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nNew"
        clean = strip_embedded_history(text)
        
        assert "CONVERSATION HISTORY" not in clean
        assert "New" in clean
    
    def test_recursive_stripping(self):
        """Test recursive stripping of nested history."""
        # Create deeply nested history
        text = "=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ===\nNew"
        clean = strip_history_recursive(text)
        
        # Should remove all history markers
        detector = HistoryDetector(DetectionMode.AGGRESSIVE)
        assert not detector.has_embedded_history(clean)
    
    def test_quick_strip(self):
        """Test quick strip convenience function."""
        text = "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nNew"
        clean = quick_strip(text)
        
        assert "CONVERSATION HISTORY" not in clean


class TestTokenCounting:
    """Tests for token counting functionality."""
    
    def test_basic_token_counting(self):
        """Test basic token counting."""
        counter = TokenCounter()
        
        text = "Hello world"
        count = counter.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)
    
    def test_empty_string_tokens(self):
        """Test token counting with empty string."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0
    
    def test_different_models(self):
        """Test token counting with different models."""
        counter = TokenCounter()
        
        text = "Hello world"
        count_gpt = counter.count_tokens(text, "gpt-4")
        count_glm = counter.count_tokens(text, "glm-4.6")
        count_kimi = counter.count_tokens(text, "kimi-k2-0905-preview")
        
        # All should return positive counts
        assert count_gpt > 0
        assert count_glm > 0
        assert count_kimi > 0
    
    def test_message_token_counting_dict_format(self):
        """Test token counting with message dict format."""
        counter = TokenCounter()
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        count = counter.count_messages_tokens(messages)
        assert count > 0
    
    def test_message_token_counting_string_format(self):
        """Test token counting with string format."""
        counter = TokenCounter()
        
        messages = ["Hello", "Hi there"]
        count = counter.count_messages_tokens(messages)
        assert count > 0
    
    def test_validate_token_budget_within_limit(self):
        """Test token budget validation when within limit."""
        content = "Short message"
        history = [
            {"content": "Previous message 1", "tokens": 5},
            {"content": "Previous message 2", "tokens": 5}
        ]
        
        validated_content, trimmed_history = validate_token_budget(
            content, history, max_total=1000
        )
        
        assert validated_content == content
        assert len(trimmed_history) == len(history)
    
    def test_validate_token_budget_exceeds_limit(self):
        """Test token budget validation when history exceeds limit."""
        content = "Short message"
        # Create large history
        history = [
            {"content": "Message " * 100, "tokens": 200}
            for _ in range(50)
        ]
        
        validated_content, trimmed_history = validate_token_budget(
            content, history, max_total=1000
        )
        
        assert validated_content == content
        assert len(trimmed_history) < len(history)
    
    def test_validate_token_budget_circuit_breaker(self):
        """Test circuit breaker when content alone exceeds budget."""
        content = "Very long message " * 1000
        history = []
        
        with pytest.raises(ValueError, match="circuit breaker"):
            validate_token_budget(content, history, max_total=100)
    
    def test_truncate_to_token_limit(self):
        """Test text truncation to token limit."""
        text = "This is a long message that needs to be truncated " * 100
        max_tokens = 50
        
        truncated = truncate_to_token_limit(text, max_tokens)
        
        counter = TokenCounter()
        assert counter.count_tokens(truncated) <= max_tokens
        assert len(truncated) < len(text)
    
    def test_validate_message_tokens_valid(self):
        """Test message token validation for valid message."""
        content = "Short message"
        is_valid, token_count = validate_message_tokens(content, max_tokens=1000)
        
        assert is_valid is True
        assert token_count > 0
    
    def test_validate_message_tokens_invalid(self):
        """Test message token validation for oversized message."""
        content = "Very long message " * 1000
        is_valid, token_count = validate_message_tokens(content, max_tokens=10)
        
        assert is_valid is False
        assert token_count > 10
    
    def test_count_tokens_convenience(self):
        """Test convenience function for counting tokens."""
        text = "Hello world"
        count = count_tokens(text)
        assert count > 0


class TestMigration:
    """Tests for conversation migration functionality."""
    
    def test_turn_creation(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn("user", "Hello", {"key": "value"})
        
        assert turn.role == "user"
        assert turn.content == "Hello"
        assert turn.metadata["key"] == "value"
        assert turn.version == CURRENT_VERSION
    
    def test_turn_to_dict(self):
        """Test converting turn to dictionary."""
        turn = ConversationTurn("user", "Hello")
        turn_dict = turn.to_dict()
        
        assert turn_dict["role"] == "user"
        assert turn_dict["content"] == "Hello"
        assert turn_dict["version"] == CURRENT_VERSION
    
    def test_turn_from_dict(self):
        """Test creating turn from dictionary."""
        turn_dict = {
            "role": "assistant",
            "content": "Hi",
            "version": "1.0.0",
            "metadata": {"key": "value"}
        }
        turn = ConversationTurn.from_dict(turn_dict)
        
        assert turn.role == "assistant"
        assert turn.content == "Hi"
        assert turn.metadata["key"] == "value"
    
    def test_migrate_pre_versioned_turn(self):
        """Test migrating pre-versioned turn."""
        migrator = ConversationMigrator()
        
        old_turn = {"role": "user", "content": "Hello"}
        new_turn = migrator.migrate_turn(old_turn)
        
        assert new_turn.version == CURRENT_VERSION
        assert new_turn.role == "user"
        assert new_turn.content == "Hello"
    
    def test_migrate_current_version_turn(self):
        """Test migrating turn that's already current version."""
        migrator = ConversationMigrator()
        
        current_turn = {
            "role": "assistant",
            "content": "Hi",
            "version": CURRENT_VERSION,
            "metadata": {"key": "value"}
        }
        new_turn = migrator.migrate_turn(current_turn)
        
        assert new_turn.version == CURRENT_VERSION
        assert new_turn.metadata["key"] == "value"
    
    def test_migrate_conversation(self):
        """Test migrating entire conversation."""
        migrator = ConversationMigrator()
        
        turns = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        migrated = migrator.migrate_conversation(turns)
        
        assert len(migrated) == 3
        assert all(turn.version == CURRENT_VERSION for turn in migrated)
    
    def test_migrate_with_history_stripping(self):
        """Test migration with history stripping."""
        turn_data = {
            "role": "user",
            "content": "=== CONVERSATION HISTORY ===\nOld\n=== END ===\nNew message"
        }
        
        migrated = migrate_turn_with_history_stripping(turn_data, strip_history=True)
        
        assert "CONVERSATION HISTORY" not in migrated.content
        assert "New message" in migrated.content
        assert migrated.metadata.get("history_stripped") is True


class TestNoRecursiveEmbedding:
    """Tests to ensure no recursive embedding occurs."""
    
    def test_history_stripping_prevents_recursion(self):
        """Test that stripping prevents recursive embedding."""
        detector = HistoryDetector(DetectionMode.AGGRESSIVE)
        
        # Create nested history
        text = "=== CONVERSATION HISTORY ===\n=== PREVIOUS MESSAGES ===\nOld\n=== END ===\n=== END ===\nNew"
        
        # Strip recursively
        clean = strip_history_recursive(text)
        
        # Verify no history markers remain
        markers = detector.detect_history_markers(clean)
        assert len(markers) == 0
    
    def test_multiple_strip_iterations(self):
        """Test that multiple stripping iterations work correctly."""
        # Create deeply nested history
        text = "=== CONVERSATION HISTORY ===\n" * 5 + "Content"
        
        clean = strip_history_recursive(text, max_iterations=10)
        
        # Should have no markers left
        detector = HistoryDetector(DetectionMode.AGGRESSIVE)
        assert not detector.has_embedded_history(clean)

