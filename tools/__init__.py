"""
Tool implementations for EXAI MCP Server
"""

from .workflows.analyze import AnalyzeTool
from .challenge import ChallengeTool
from .chat import ChatTool
from .workflows.codereview import CodeReviewTool
from .workflows.consensus import ConsensusTool
from .workflows.debug import DebugIssueTool
from .workflows.docgen import DocgenTool
from .capabilities.listmodels import ListModelsTool
from .workflows.planner import PlannerTool
from .workflows.precommit import PrecommitTool
from .workflows.refactor import RefactorTool
from .workflows.secaudit import SecauditTool
from .workflows.testgen import TestGenTool
from .workflows.thinkdeep import ThinkDeepTool
from .workflows.tracer import TracerTool
from .capabilities.version import VersionTool
from .selfcheck import SelfCheckTool
# File Management Tools (2025-11-09): Critical missing feature now exposed
from .smart_file_query import SmartFileQueryTool
from .smart_file_download import SmartFileDownloadTool

__all__ = [
    "ThinkDeepTool",
    "CodeReviewTool",
    "DebugIssueTool",
    "DocgenTool",
    "AnalyzeTool",
    "ChatTool",
    "ConsensusTool",
    "ListModelsTool",
    "PlannerTool",
    "PrecommitTool",
    "ChallengeTool",
    "RefactorTool",
    "SecauditTool",
    "TestGenTool",
    "TracerTool",
    "VersionTool",
    "SelfCheckTool",
    # File Management Tools - CRITICAL FEATURE (2025-11-09)
    "SmartFileQueryTool",
    "SmartFileDownloadTool",
]
