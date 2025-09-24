"""
Agentic engine scaffolding package.

Enhanced with GLM-4.5 Flash intelligent routing capabilities:
- RequestAnalyzer: Smart preprocessing without sending large content to GLM
- GLMFlashManager: Intelligent AI manager for routing decisions
- ProviderCapabilityRegistry: Capability-aware provider selection
- Enhanced routing strategies: capability-based, cost-optimized, performance-optimized, hybrid

Original components:
- HybridPlatformManager (Moonshot + Z.ai)
- IntelligentTaskRouter (capability/context/multimodal-aware)
- AdvancedContextManager (256K-aware context optimization)
- ResilientErrorHandler (retry/backoff/fallbacks)
- SecureInputValidator (centralized path/image validation)

All integration is gated by feature flags in config.py and is OFF by default.
"""

from .context_manager import AdvancedContextManager
from .engine import AutonomousWorkflowEngine
from .error_handler import ResilientErrorHandler
from .hybrid_platform_manager import HybridPlatformManager
from .task_router import IntelligentTaskRouter, TaskType
from .request_analyzer import RequestAnalyzer, RequestAnalysis, RequestType, ContentComplexity
from .glm_flash_manager import GLMFlashManager, RoutingStrategy, RoutingDecision, ProviderCapabilityRegistry

__all__ = [
    "AdvancedContextManager",
    "AutonomousWorkflowEngine", 
    "ResilientErrorHandler",
    "HybridPlatformManager",
    "IntelligentTaskRouter",
    "TaskType",
    "RequestAnalyzer",
    "RequestAnalysis", 
    "RequestType",
    "ContentComplexity",
    "GLMFlashManager",
    "RoutingStrategy",
    "RoutingDecision",
    "ProviderCapabilityRegistry",
]

