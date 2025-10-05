"""
Conversation Tracker - Manage conversation IDs across platforms

Tracks conversation IDs for multi-turn testing with platform isolation.

Key Features:
- Platform-specific conversation IDs (Kimi vs GLM)
- Conversation ID isolation (cannot cross platforms)
- Conversation caching with TTL
- Automatic cleanup of expired conversations

Created: 2025-10-05
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConversationTracker:
    """
    Track conversation IDs for multi-turn testing.
    
    Ensures:
    - Kimi conversation IDs only work with Kimi
    - GLM conversation IDs only work with GLM
    - Conversations expire after TTL
    - Automatic cleanup
    """
    
    def __init__(self):
        """Initialize the conversation tracker."""
        self.cache_enabled = os.getenv("CACHE_CONVERSATION_IDS", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CONVERSATION_CACHE_TTL", "3600"))  # 1 hour
        
        self.kimi_cache_dir = Path(os.getenv("KIMI_CONVERSATION_CACHE_DIR", "./tool_validation_suite/cache/kimi"))
        self.glm_cache_dir = Path(os.getenv("GLM_CONVERSATION_CACHE_DIR", "./tool_validation_suite/cache/glm"))
        
        # Create cache directories
        self.kimi_cache_dir.mkdir(parents=True, exist_ok=True)
        self.glm_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.conversations = {
            "kimi": {},
            "glm": {}
        }
        
        # Load existing conversations
        self._load_conversations()
        
        logger.info("Conversation tracker initialized")
    
    def create_conversation(self, provider: str) -> str:
        """
        Create a new conversation ID.
        
        Args:
            provider: Provider name (kimi or glm)
        
        Returns:
            Conversation ID string
        """
        if provider not in ["kimi", "glm"]:
            raise ValueError(f"Invalid provider: {provider}")
        
        # Generate conversation ID with provider prefix
        conv_id = f"{provider}_conv_{uuid.uuid4().hex[:16]}"
        
        # Create conversation record
        conversation = {
            "conversation_id": conv_id,
            "provider": provider,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "expires_at": (datetime.utcnow() + timedelta(seconds=self.cache_ttl)).isoformat() + "Z",
            "messages": [],
            "metadata": {}
        }
        
        # Store in memory
        self.conversations[provider][conv_id] = conversation
        
        # Save to disk
        if self.cache_enabled:
            self._save_conversation(provider, conv_id, conversation)
        
        logger.info(f"Created conversation: {conv_id}")
        
        return conv_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation dictionary or None if not found/expired
        """
        # Determine provider from ID
        provider = self._get_provider_from_id(conversation_id)
        
        if not provider:
            logger.warning(f"Invalid conversation ID format: {conversation_id}")
            return None
        
        # Check in-memory cache
        conversation = self.conversations[provider].get(conversation_id)
        
        if not conversation:
            # Try loading from disk
            conversation = self._load_conversation(provider, conversation_id)
        
        if not conversation:
            return None
        
        # Check if expired
        if self._is_expired(conversation):
            logger.info(f"Conversation expired: {conversation_id}")
            self.remove_conversation(conversation_id)
            return None
        
        return conversation
    
    def add_message(self, conversation_id: str, role: str, content: str) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant)
            content: Message content
        
        Returns:
            True if successful, False otherwise
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            logger.warning(f"Conversation not found: {conversation_id}")
            return False
        
        # Add message
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        conversation["messages"].append(message)
        
        # Update in memory
        provider = conversation["provider"]
        self.conversations[provider][conversation_id] = conversation
        
        # Save to disk
        if self.cache_enabled:
            self._save_conversation(provider, conversation_id, conversation)
        
        return True
    
    def is_valid_for_provider(self, conversation_id: str, provider: str) -> bool:
        """
        Check if conversation ID is valid for the given provider.
        
        Args:
            conversation_id: Conversation ID
            provider: Provider name (kimi or glm)
        
        Returns:
            True if valid, False otherwise
        """
        # Check ID format
        expected_prefix = f"{provider}_conv_"
        
        if not conversation_id.startswith(expected_prefix):
            logger.warning(f"Conversation ID {conversation_id} not valid for provider {provider}")
            return False
        
        # Check if conversation exists and not expired
        conversation = self.get_conversation(conversation_id)
        
        return conversation is not None
    
    def remove_conversation(self, conversation_id: str):
        """Remove a conversation."""
        provider = self._get_provider_from_id(conversation_id)
        
        if provider and conversation_id in self.conversations[provider]:
            del self.conversations[provider][conversation_id]
            
            # Remove from disk
            if self.cache_enabled:
                cache_dir = self.kimi_cache_dir if provider == "kimi" else self.glm_cache_dir
                cache_file = cache_dir / f"{conversation_id}.json"
                
                if cache_file.exists():
                    cache_file.unlink()
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired conversations.
        
        Returns:
            Number of conversations cleaned up
        """
        cleaned = 0
        
        for provider in ["kimi", "glm"]:
            expired_ids = []
            
            for conv_id, conversation in self.conversations[provider].items():
                if self._is_expired(conversation):
                    expired_ids.append(conv_id)
            
            for conv_id in expired_ids:
                self.remove_conversation(conv_id)
                cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired conversations")
        
        return cleaned
    
    def _get_provider_from_id(self, conversation_id: str) -> Optional[str]:
        """Extract provider from conversation ID."""
        if conversation_id.startswith("kimi_conv_"):
            return "kimi"
        elif conversation_id.startswith("glm_conv_"):
            return "glm"
        else:
            return None
    
    def _is_expired(self, conversation: Dict[str, Any]) -> bool:
        """Check if conversation is expired."""
        expires_at = datetime.fromisoformat(conversation["expires_at"].replace("Z", "+00:00"))
        return datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at
    
    def _save_conversation(self, provider: str, conversation_id: str, conversation: Dict[str, Any]):
        """Save conversation to disk."""
        try:
            cache_dir = self.kimi_cache_dir if provider == "kimi" else self.glm_cache_dir
            cache_file = cache_dir / f"{conversation_id}.json"
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved conversation: {cache_file}")
        
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    def _load_conversation(self, provider: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation from disk."""
        try:
            cache_dir = self.kimi_cache_dir if provider == "kimi" else self.glm_cache_dir
            cache_file = cache_dir / f"{conversation_id}.json"
            
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    conversation = json.load(f)
                
                # Store in memory
                self.conversations[provider][conversation_id] = conversation
                
                return conversation
        
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
        
        return None
    
    def _load_conversations(self):
        """Load all conversations from disk."""
        for provider in ["kimi", "glm"]:
            cache_dir = self.kimi_cache_dir if provider == "kimi" else self.glm_cache_dir
            
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        conversation = json.load(f)
                    
                    conv_id = conversation["conversation_id"]
                    
                    # Only load if not expired
                    if not self._is_expired(conversation):
                        self.conversations[provider][conv_id] = conversation
                    else:
                        # Remove expired file
                        cache_file.unlink()
                
                except Exception as e:
                    logger.error(f"Failed to load conversation from {cache_file}: {e}")


# Example usage
if __name__ == "__main__":
    tracker = ConversationTracker()
    
    # Create Kimi conversation
    kimi_conv_id = tracker.create_conversation("kimi")
    print(f"Created Kimi conversation: {kimi_conv_id}")
    
    # Add messages
    tracker.add_message(kimi_conv_id, "user", "Hello")
    tracker.add_message(kimi_conv_id, "assistant", "Hi there!")
    
    # Verify it's valid for Kimi
    print(f"Valid for Kimi: {tracker.is_valid_for_provider(kimi_conv_id, 'kimi')}")
    print(f"Valid for GLM: {tracker.is_valid_for_provider(kimi_conv_id, 'glm')}")
    
    # Create GLM conversation
    glm_conv_id = tracker.create_conversation("glm")
    print(f"Created GLM conversation: {glm_conv_id}")
    
    # Verify isolation
    print(f"Valid for GLM: {tracker.is_valid_for_provider(glm_conv_id, 'glm')}")
    print(f"Valid for Kimi: {tracker.is_valid_for_provider(glm_conv_id, 'kimi')}")

