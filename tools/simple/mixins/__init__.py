"""
Mixins for SimpleTool functionality.

This package contains mixins that provide specific functionality to SimpleTool:
- WebSearchMixin: Web search instruction generation and guidance
- ToolCallMixin: Tool call detection and execution
- StreamingMixin: Streaming support configuration
- ContinuationMixin: Conversation continuation and caching

These mixins are composed into SimpleTool to provide a clean separation of concerns
while maintaining backward compatibility.
"""

from tools.simple.mixins.web_search_mixin import WebSearchMixin
from tools.simple.mixins.tool_call_mixin import ToolCallMixin
from tools.simple.mixins.streaming_mixin import StreamingMixin
from tools.simple.mixins.continuation_mixin import ContinuationMixin

__all__ = [
    "WebSearchMixin",
    "ToolCallMixin",
    "StreamingMixin",
    "ContinuationMixin",
]

