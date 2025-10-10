"""
Conversation Memory for AI-to-AI Multi-turn Discussions

This module provides conversation persistence and context reconstruction for
stateless MCP (Model Context Protocol) environments. It enables multi-turn
conversations between Claude and Gemini by storing conversation state in memory
across independent request cycles.

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
- conversation_history: History building and formatting

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
from utils.conversation.history import build_conversation_history

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
    # History Building
    "build_conversation_history",
    # Storage
    "get_storage",
]

