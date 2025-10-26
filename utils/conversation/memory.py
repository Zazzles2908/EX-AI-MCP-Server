"""
Conversation Memory for AI-to-AI Multi-turn Discussions

This module provides conversation persistence and context reconstruction for
stateless MCP (Model Context Protocol) environments. It enables multi-turn
conversations between Claude and Gemini by storing conversation state in memory
across independent request cycles.

CONTEXT ENGINEERING (Phase 1):
This module implements defense-in-depth history stripping to prevent recursive
embedding of conversation history that causes token explosion (4.6M tokens bug).
History stripping is applied at storage time before turns are persisted.

CRITICAL ARCHITECTURAL REQUIREMENT:
This conversation memory system is designed for PERSISTENT MCP SERVER PROCESSES.
It uses in-memory storage that persists only within a single Python process.

⚠️  IMPORTANT: This system will NOT work correctly if MCP tool calls are made
    as separate subprocess invocations (each subprocess starts with empty memory).

    WORKING SCENARIO: Claude Desktop with persistent MCP server process
    FAILING SCENARIO: Simulator tests calling server.py as individual subprocesses

    Root cause of test failures: Each subprocess call loses the conversation
    state from previous calls because memory is process-specific, not shared
    across subprocess boundaries.

ARCHITECTURE OVERVIEW:
The MCP protocol is inherently stateless - each tool request is independent
with no memory of previous interactions. This module bridges that gap by:

1. Creating persistent conversation threads with unique UUIDs
2. Storing complete conversation context (turns, files, metadata) in memory
3. Reconstructing conversation history when tools are called with continuation_id
4. Supporting cross-tool continuation - seamlessly switch between different tools
   while maintaining full conversation context and file references

CROSS-TOOL CONTINUATION:
A conversation started with one tool (e.g., 'analyze') can be continued with
any other tool (e.g., 'codereview', 'debug', 'chat') using the same continuation_id.
The second tool will have access to:
- All previous conversation turns and responses
- File context from previous tools (preserved in conversation history)
- Original thread metadata and timing information
- Accumulated knowledge from the entire conversation

Key Features:
- UUID-based conversation thread identification with security validation
- Turn-by-turn conversation history storage with tool attribution
- Cross-tool continuation support - switch tools while preserving context
- File context preservation - files shared in earlier turns remain accessible
- NEWEST-FIRST FILE PRIORITIZATION - when the same file appears in multiple turns,
  references from newer turns take precedence over older ones. This ensures the
  most recent file context is preserved when token limits require exclusions.
- Automatic turn limiting (20 turns max) to prevent runaway conversations
- Context reconstruction for stateless request continuity
- In-memory persistence with automatic expiration (3 hour TTL)
- Thread-safe operations for concurrent access
- Graceful degradation when storage is unavailable

DUAL PRIORITIZATION STRATEGY (Files & Conversations):
The conversation memory system implements sophisticated prioritization for both files and
conversation turns, using a consistent "newest-first" approach during collection but
presenting information in the optimal format for LLM consumption:

FILE PRIORITIZATION (Newest-First Throughout):
1. When collecting files across conversation turns, the system walks BACKWARDS through
   turns (newest to oldest) and builds a unique file list
2. If the same file path appears in multiple turns, only the reference from the
   NEWEST turn is kept in the final list
3. This "newest-first" ordering is preserved throughout the entire pipeline:
   - get_conversation_file_list() establishes the order
   - build_conversation_history() maintains it during token budgeting
   - When token limits are hit, OLDER files are excluded first
4. This strategy works across conversation chains - files from newer turns in ANY
   thread take precedence over files from older turns in ANY thread

CONVERSATION TURN PRIORITIZATION (Newest-First Collection, Chronological Presentation):
1. COLLECTION PHASE: Processes turns newest-to-oldest to prioritize recent context
   - When token budget is tight, OLDER turns are excluded first
   - Ensures most contextually relevant recent exchanges are preserved
2. PRESENTATION PHASE: Reverses collected turns to chronological order (oldest-first)
   - LLM sees natural conversation flow: "Turn 1 → Turn 2 → Turn 3..."
   - Maintains proper sequential understanding while preserving recency prioritization

This dual approach ensures optimal context preservation (newest-first) with natural
conversation flow (chronological) for maximum LLM comprehension and relevance.

USAGE EXAMPLE:
1. Tool A creates thread: create_thread("analyze", request_data) → returns UUID
2. Tool A adds response: add_turn(UUID, "assistant", response, files=[...], tool_name="analyze")
3. Tool B continues thread: get_thread(UUID) → retrieves full context
4. Tool B sees conversation history via build_conversation_history()
5. Tool B adds its response: add_turn(UUID, "assistant", response, tool_name="codereview")

DUAL STRATEGY EXAMPLE:
Conversation has 5 turns, token budget allows only 3 turns:

Collection Phase (Newest-First Priority):
- Evaluates: Turn 5 → Turn 4 → Turn 3 → Turn 2 → Turn 1
- Includes: Turn 5, Turn 4, Turn 3 (newest 3 fit in budget)
- Excludes: Turn 2, Turn 1 (oldest, dropped due to token limits)

Presentation Phase (Chronological Order):
- LLM sees: "--- Turn 3 (Claude) ---", "--- Turn 4 (Gemini) ---", "--- Turn 5 (Claude) ---"
- Natural conversation flow maintained despite prioritizing recent context

This enables true AI-to-AI collaboration across the entire tool ecosystem with optimal
context preservation and natural conversation understanding.

MODULE ORGANIZATION:
This module has been refactored into focused sub-modules for maintainability:
- conversation_models: Data structures and configuration
- conversation_threads: Thread lifecycle management

BUG FIX #14 (2025-10-20): Removed legacy text-based history building
- DELETED: conversation_history module (build_conversation_history)
- Modern approach: Use message arrays via storage_factory.get_messages_array()
- SDK providers (Kimi/GLM) receive native message format, not text strings

All public APIs are re-exported from this module for backward compatibility.
"""

# Re-export all public APIs from sub-modules for backward compatibility
from utils.conversation.models import (
    CONVERSATION_TIMEOUT_SECONDS,
    MAX_CONVERSATION_TURNS,
    ConversationTurn,
    ThreadContext,
    get_storage,
)
from utils.conversation.threads import (
    add_turn,
    create_thread,
    get_conversation_file_list,
    get_conversation_image_list,
    get_thread,
    get_thread_chain,
)

# Context Engineering imports
from utils.conversation.history_detection import HistoryDetector, DetectionMode
from utils.conversation.token_utils import TokenCounter
from config import CONTEXT_ENGINEERING
import logging

logger = logging.getLogger(__name__)

__all__ = [
    # Models
    "ConversationTurn",
    "ThreadContext",
    # Constants
    "MAX_CONVERSATION_TURNS",
    "CONVERSATION_TIMEOUT_SECONDS",
    # Thread Management
    "create_thread",
    "get_thread",
    "add_turn",
    "get_thread_chain",
    # File/Image Collection
    "get_conversation_file_list",
    "get_conversation_image_list",
    # Storage
    "get_storage",
    # Class-based interface for storage factory
    "InMemoryConversation",
]


# ================================================================================
# Class-based Interface for Storage Factory
# ================================================================================


class InMemoryConversation:
    """
    Class-based wrapper for in-memory conversation storage.

    This class provides a unified interface for the storage factory pattern,
    using DIRECT Redis storage access to avoid circular dependencies.

    CRITICAL: This class MUST NOT call functions from threads.py to avoid
    infinite loops when used with the storage factory pattern.

    The storage factory calls this class, which would call threads.py,
    which would call the storage factory again → infinite loop!

    Instead, this class uses direct Redis storage access via get_storage().
    """

    def __init__(self):
        """Initialize in-memory conversation storage with context engineering"""
        # Get direct access to Redis storage backend
        self.storage = get_storage()

        # Initialize context engineering components
        self.config = CONTEXT_ENGINEERING
        self.strip_history = self.config.get("strip_embedded_history", True)

        # Initialize history detector with configured mode
        detection_mode = self.config.get("detection_mode", "conservative")
        mode = DetectionMode.AGGRESSIVE if detection_mode == "aggressive" else DetectionMode.CONSERVATIVE
        self.history_detector = HistoryDetector(mode)

        # Initialize token counter for logging
        self.token_counter = TokenCounter()

    def get_thread(self, continuation_id: str):
        """
        Get thread context by continuation ID using DIRECT Redis storage.

        CRITICAL: Does NOT call threads.py to avoid circular dependency!

        Args:
            continuation_id: Unique conversation identifier

        Returns:
            ThreadContext or None
        """
        # Use direct Redis storage access (not threads.py!)
        thread_data = self.storage.get(continuation_id)
        if not thread_data:
            return None

        # Convert to ThreadContext
        return ThreadContext(**thread_data)

    def add_turn(
        self,
        continuation_id: str,
        role: str,
        content: str,
        files=None,
        images=None,
        metadata=None,
        tool_name=None
    ) -> bool:
        """
        Add a turn to the conversation using DIRECT Redis storage.

        Implements Context Engineering Phase 1: Defense-in-depth history stripping
        to prevent recursive embedding of conversation history.

        CRITICAL: Does NOT call threads.py to avoid circular dependency!

        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata dict
            tool_name: Optional tool name

        Returns:
            True if successful, False otherwise
        """
        from datetime import datetime, timezone

        # Get thread using direct storage (not threads.py!)
        thread_data = self.storage.get(continuation_id)
        if not thread_data:
            return False

        context = ThreadContext(**thread_data)

        # Check turn limit
        if len(context.turns) >= MAX_CONVERSATION_TURNS:
            return False

        # Apply context engineering: Strip embedded history BEFORE storage
        original_content = content
        if self.strip_history and role == "user":
            content = self._strip_embedded_history(content)

            # Log stripping if content changed
            if content != original_content and self.config.get("log_stripping", True):
                tokens_before = self.token_counter.count_tokens(original_content)
                tokens_after = self.token_counter.count_tokens(content)
                reduction = ((tokens_before - tokens_after) / tokens_before * 100) if tokens_before > 0 else 0
                logger.info(
                    f"History stripped from turn: {tokens_before} → {tokens_after} tokens "
                    f"({reduction:.1f}% reduction)"
                )

            # In dry run mode, don't actually save the stripped content
            if self.config.get("dry_run", False):
                logger.info(f"DRY RUN: Would have stripped history from turn")
                content = original_content  # Restore original for dry run

        # Create new turn
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            files=files,
            images=images,
            tool_name=tool_name,
            model_metadata=metadata,
        )

        context.turns.append(turn)
        context.last_updated_at = datetime.now(timezone.utc).isoformat()

        # Save back to Redis using direct storage
        key = f"thread:{continuation_id}"
        self.storage.setex(key, CONVERSATION_TIMEOUT_SECONDS, context.model_dump_json())
        return True

    def _strip_embedded_history(self, content: str) -> str:
        """
        Strip embedded history from content using defense-in-depth approach.

        This method implements Context Engineering Phase 1 to prevent recursive
        embedding of conversation history that causes token explosion.

        Args:
            content: Content to strip history from

        Returns:
            Content with history sections removed
        """
        if not content:
            return content

        # Check token threshold - only strip if content exceeds minimum
        min_threshold = self.config.get("min_token_threshold", 100)
        token_count = self.token_counter.count_tokens(content)
        if token_count < min_threshold:
            return content

        try:
            # Detect history sections
            sections = self.history_detector.extract_history_sections(content)
            if not sections:
                return content

            # Remove history sections
            clean_parts = []
            last_end = 0

            for start, end in sections:
                # Add content before this history section
                clean_parts.append(content[last_end:start])
                last_end = end

            # Add remaining content after last history section
            clean_parts.append(content[last_end:])

            clean_content = "".join(clean_parts)

            # Recursively check for nested history
            # This ensures we get all levels of embedded history
            if self.history_detector.has_embedded_history(clean_content):
                return self._strip_embedded_history(clean_content)

            return clean_content

        except Exception as e:
            logger.error(f"History stripping failed: {e}")
            # Return original content if stripping fails (graceful degradation)
            return content

    # BUG FIX #14 (2025-10-20): DELETED build_conversation_history
    # Legacy text-based history building is no longer used.
    # Modern approach: Use get_messages_array() for SDK-native message format.

