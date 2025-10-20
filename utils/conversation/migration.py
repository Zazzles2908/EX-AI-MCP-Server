"""
Conversation migration utilities for backward compatibility.

This module provides utilities for migrating conversations from older formats
to the current version with history stripping and version tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Current version of conversation format
CURRENT_VERSION = "1.0.0"


class ConversationTurn:
    """
    Represents a single turn in a conversation with version tracking.
    
    This class provides a structured format for conversation turns with
    metadata, version tracking, and timestamps.
    """
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a conversation turn.
        
        Args:
            role: Role of the speaker (user, assistant, system)
            content: Content of the message
            metadata: Optional metadata dictionary
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.version = CURRENT_VERSION
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.tokens = None  # Will be set by token counter
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert turn to dictionary format for storage.
        
        Returns:
            Dictionary representation of the turn
        """
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tokens": self.tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationTurn":
        """
        Create turn from dictionary format.
        
        Args:
            data: Dictionary containing turn data
            
        Returns:
            ConversationTurn instance
        """
        turn = cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            metadata=data.get("metadata", {})
        )
        turn.version = data.get("version", CURRENT_VERSION)
        turn.created_at = data.get("created_at", datetime.utcnow().isoformat())
        turn.updated_at = data.get("updated_at", turn.created_at)
        turn.tokens = data.get("tokens")
        return turn
    
    def update_content(self, new_content: str):
        """
        Update turn content and timestamp.
        
        Args:
            new_content: New content for the turn
        """
        self.content = new_content
        self.updated_at = datetime.utcnow().isoformat()
        self.tokens = None  # Reset token count


class ConversationMigrator:
    """
    Handles migration of conversations from older formats to current version.
    
    Supports migration from pre-versioned formats and future version handling.
    """
    
    def __init__(self):
        """Initialize conversation migrator."""
        self.current_version = CURRENT_VERSION
        self.migration_stats = {
            "total_migrated": 0,
            "by_version": {}
        }
    
    def migrate_turn(self, turn_data: Dict[str, Any]) -> ConversationTurn:
        """
        Migrate a turn from any previous version to the current version.
        
        Args:
            turn_data: Turn data in any format
            
        Returns:
            ConversationTurn instance in current version
        """
        version = turn_data.get("version", "0.0.0")
        
        # Track migration stats
        self.migration_stats["total_migrated"] += 1
        self.migration_stats["by_version"][version] = \
            self.migration_stats["by_version"].get(version, 0) + 1
        
        # Already current version
        if version == self.current_version:
            return ConversationTurn.from_dict(turn_data)
        
        # Handle migration from pre-versioned format
        if version == "0.0.0":
            logger.debug(f"Migrating pre-versioned turn to {self.current_version}")
            turn = ConversationTurn(
                role=turn_data.get("role", ""),
                content=turn_data.get("content", ""),
                metadata=turn_data.get("metadata", {})
            )
            # Preserve original timestamps if available
            if "created_at" in turn_data:
                turn.created_at = turn_data["created_at"]
            if "updated_at" in turn_data:
                turn.updated_at = turn_data["updated_at"]
            if "tokens" in turn_data:
                turn.tokens = turn_data["tokens"]
            return turn
        
        # Handle future versions (shouldn't happen in normal flow)
        if self._is_newer_version(version, self.current_version):
            logger.warning(
                f"Turn version {version} is newer than current {self.current_version}. "
                f"Loading as-is, but may have compatibility issues."
            )
            return ConversationTurn.from_dict(turn_data)
        
        # Handle specific version migrations
        # Example for future versions:
        # if version == "1.0.0" and self.current_version == "1.1.0":
        #     return self._migrate_from_1_0_0(turn_data)
        
        # Default: load as current version
        logger.debug(f"Migrating turn from version {version} to {self.current_version}")
        return ConversationTurn.from_dict(turn_data)
    
    def migrate_conversation(self, turns: List[Dict[str, Any]]) -> List[ConversationTurn]:
        """
        Migrate an entire conversation.
        
        Args:
            turns: List of turn dictionaries
            
        Returns:
            List of ConversationTurn instances in current version
        """
        migrated_turns = []
        for turn_data in turns:
            try:
                migrated_turn = self.migrate_turn(turn_data)
                migrated_turns.append(migrated_turn)
            except Exception as e:
                logger.error(f"Failed to migrate turn: {e}")
                # Skip problematic turns but continue migration
                continue
        
        logger.info(
            f"Migrated conversation: {len(migrated_turns)}/{len(turns)} turns successful"
        )
        
        return migrated_turns
    
    def _is_newer_version(self, version_a: str, version_b: str) -> bool:
        """
        Check if version_a is newer than version_b.
        
        Args:
            version_a: First version string (e.g., "1.2.3")
            version_b: Second version string (e.g., "1.1.0")
            
        Returns:
            True if version_a is newer than version_b
        """
        try:
            a_parts = [int(x) for x in version_a.split('.')]
            b_parts = [int(x) for x in version_b.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(a_parts), len(b_parts))
            a_parts.extend([0] * (max_len - len(a_parts)))
            b_parts.extend([0] * (max_len - len(b_parts)))
            
            for a, b in zip(a_parts, b_parts):
                if a > b:
                    return True
                if a < b:
                    return False
            
            return False
        except (ValueError, AttributeError) as e:
            logger.error(f"Error comparing versions {version_a} and {version_b}: {e}")
            return False
    
    def get_migration_stats(self) -> Dict[str, Any]:
        """
        Get migration statistics.
        
        Returns:
            Dictionary with migration statistics
        """
        return self.migration_stats.copy()
    
    def reset_stats(self):
        """Reset migration statistics."""
        self.migration_stats = {
            "total_migrated": 0,
            "by_version": {}
        }


def migrate_turn_with_history_stripping(turn_data: Dict[str, Any], 
                                        strip_history: bool = True) -> ConversationTurn:
    """
    Migrate a turn and optionally strip embedded history.
    
    This combines migration with history stripping for a complete upgrade.
    
    Args:
        turn_data: Turn data to migrate
        strip_history: If True, strip embedded history from content
        
    Returns:
        Migrated ConversationTurn with history stripped
    """
    from utils.conversation.history_detection import strip_embedded_history
    
    migrator = ConversationMigrator()
    turn = migrator.migrate_turn(turn_data)
    
    if strip_history and turn.role == "user":
        original_content = turn.content
        turn.content = strip_embedded_history(turn.content)
        
        if turn.content != original_content:
            logger.info(
                f"Stripped history during migration: "
                f"{len(original_content)} -> {len(turn.content)} chars"
            )
            # Mark in metadata that history was stripped
            turn.metadata["history_stripped"] = True
            turn.metadata["original_length"] = len(original_content)
    
    return turn


def batch_migrate_conversations(conversations: Dict[str, List[Dict[str, Any]]],
                                strip_history: bool = True) -> Dict[str, List[ConversationTurn]]:
    """
    Migrate multiple conversations in batch.
    
    Args:
        conversations: Dictionary mapping conversation IDs to turn lists
        strip_history: If True, strip embedded history during migration
        
    Returns:
        Dictionary mapping conversation IDs to migrated turn lists
    """
    migrator = ConversationMigrator()
    migrated_conversations = {}
    
    for conv_id, turns in conversations.items():
        try:
            if strip_history:
                migrated_turns = [
                    migrate_turn_with_history_stripping(turn_data)
                    for turn_data in turns
                ]
            else:
                migrated_turns = migrator.migrate_conversation(turns)
            
            migrated_conversations[conv_id] = migrated_turns
            
        except Exception as e:
            logger.error(f"Failed to migrate conversation {conv_id}: {e}")
            continue
    
    stats = migrator.get_migration_stats()
    logger.info(
        f"Batch migration complete: {len(migrated_conversations)}/{len(conversations)} "
        f"conversations migrated. Total turns: {stats['total_migrated']}"
    )
    
    return migrated_conversations


# Global migrator instance for reuse
_global_migrator = ConversationMigrator()


def quick_migrate(turn_data: Dict[str, Any]) -> ConversationTurn:
    """
    Quick migration using global migrator instance.
    
    Args:
        turn_data: Turn data to migrate
        
    Returns:
        Migrated ConversationTurn
    """
    return _global_migrator.migrate_turn(turn_data)

