"""
GLM Chat Generation - Backward Compatibility Wrapper

This module provides backward compatibility for code importing from glm_chat.py.
All functionality has been refactored into focused modules:
- glm_provider.py: Core chat functions (build_payload, generate_content, chat_completions_create)
- glm_streaming_handler.py: Streaming implementations (continuation, session management)
- glm_tool_processor.py: Tool call processing (streaming with tools, text processing)

The original glm_chat.py (1,103 lines) has been split into 3 focused modules.
New code should import directly from the specific modules.

For backwards compatibility, this wrapper re-exports all public APIs.
"""

# Re-export from glm_provider.py
from src.providers.glm_provider import (
    build_payload,
    generate_content,
    chat_completions_create
)

# Re-export from glm_streaming_handler.py
from src.providers.glm_streaming_handler import (
    chat_completions_create_with_continuation,
    chat_completions_create_with_session
)

# Re-export from glm_tool_processor.py
from src.providers.glm_tool_processor import (
    _process_tool_calls_in_text,
    chat_completions_create_messages_with_session
)

# Maintain the original module docstring
__doc__ = """
GLM chat generation and streaming functionality.

PHASE 3 REFACTORING (2025-11-04):
This module has been refactored into focused components:
- glm_provider.py: Core chat functions
- glm_streaming_handler.py: Streaming implementations
- glm_tool_processor.py: Tool call processing

For new code, import directly from the specific modules.
"""

# Ensure all expected names are available for backward compatibility
__all__ = [
    # Tool processing
    '_process_tool_calls_in_text',

    # Provider core
    'build_payload',
    'generate_content',
    'chat_completions_create',

    # Streaming
    'chat_completions_create_with_continuation',
    'chat_completions_create_with_session',
    'chat_completions_create_messages_with_session',
]

# Maintain the original module structure for any code doing "from src.providers.glm_chat import X"
# All re-exported items above will be available
