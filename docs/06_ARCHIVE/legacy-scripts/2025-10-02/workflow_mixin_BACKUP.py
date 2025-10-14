"""
Workflow Mixin for Zen MCP Tools

This module provides a sophisticated workflow-based pattern that enables tools to
perform multi-step work with structured findings and expert analysis.

Key Components:
- BaseWorkflowMixin: Abstract base class providing comprehensive workflow functionality
  - Composed from specialized mixins for separation of concerns:
    * RequestAccessorMixin: Request field extraction and validation
    * ConversationIntegrationMixin: Thread management and turn storage
    * FileEmbeddingMixin: Context-aware file handling and token budgeting
    * ExpertAnalysisMixin: External model integration with fallback
    * OrchestrationMixin: Main workflow execution engine

The workflow pattern enables tools like debug, precommit, and codereview to perform
systematic multi-step work with pause/resume capabilities, context-aware file embedding,
and seamless integration with external AI models for expert analysis.

Features:
- Multi-step workflow orchestration with pause/resume
- Context-aware file embedding optimization
- Expert analysis integration with token budgeting
- Conversation memory and threading support
- Proper inheritance-based architecture (no hasattr/getattr)
- Comprehensive type annotations for IDE support
- Modular design with ~400-700 line modules (AI context-friendly)
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

# Import specialized mixins
from tools.workflow.request_accessors import RequestAccessorMixin
from tools.workflow.conversation_integration import ConversationIntegrationMixin
from tools.workflow.file_embedding import FileEmbeddingMixin
from tools.workflow.expert_analysis import ExpertAnalysisMixin
from tools.workflow.orchestration import OrchestrationMixin

from tools.shared.base_models import ConsolidatedFindings

logger = logging.getLogger(__name__)


class BaseWorkflowMixin(
    RequestAccessorMixin,
    ConversationIntegrationMixin,
    FileEmbeddingMixin,
    ExpertAnalysisMixin,
    OrchestrationMixin,
    ABC
):
    """
    Abstract base class providing guided workflow functionality for tools.

    This class implements a sophisticated workflow pattern where Claude performs
    systematic local work before calling external models for expert analysis.
    Tools can inherit from this class to gain comprehensive workflow capabilities.

    Architecture:
    - Composed from specialized mixins for separation of concerns
    - Uses proper inheritance patterns instead of hasattr/getattr
    - Provides hook methods with default implementations
    - Requires abstract methods to be implemented by subclasses
    - Fully type-annotated for excellent IDE support
    - Modular design: 5 mixins × ~400 lines each = maintainable codebase

    Mixin Composition:
    1. RequestAccessorMixin: Request field extraction and validation (~416 lines)
    2. ConversationIntegrationMixin: Thread management and turn storage (~300 lines)
    3. FileEmbeddingMixin: Context-aware file handling and token budgeting (~401 lines)
    4. ExpertAnalysisMixin: External model integration with fallback (~423 lines)
    5. OrchestrationMixin: Main workflow execution engine (~703 lines)

    Context-Aware File Embedding:
    - Intermediate steps: Only reference file names (saves Claude's context)
    - Final steps: Embed full file content for expert analysis
    - Integrates with existing token budgeting infrastructure

    Requirements:
    This class expects to be used with BaseTool and requires implementation of:
    - get_model_provider(model_name)
    - _resolve_model_context(arguments, request)
    - get_system_prompt()
    - get_default_temperature()
    - _prepare_file_content_for_prompt()
    - validate_file_paths(request)
    """

    def __init__(self) -> None:
        super().__init__()
        self.work_history: list[dict[str, Any]] = []
        self.consolidated_findings: ConsolidatedFindings = ConsolidatedFindings()
        self.initial_request: Optional[str] = None

    # ================================================================================
    # Abstract Methods - Required Implementation by BaseTool or Subclasses
    # ================================================================================

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this tool. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def get_workflow_request_model(self) -> type:
        """Return the request model class for this workflow tool."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this tool. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def get_language_instruction(self) -> str:
        """Return the language instruction for localization. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def get_default_temperature(self) -> float:
        """Return the default temperature for this tool. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def get_model_provider(self, model_name: str) -> Any:
        """Get model provider for the given model. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def _resolve_model_context(self, arguments: dict[str, Any], request: Any) -> tuple[str, Any]:
        """Resolve model context from arguments. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def _prepare_file_content_for_prompt(
        self,
        request_files: list[str],
        continuation_id: Optional[str],
        context_description: str = "New files",
        max_tokens: Optional[int] = None,
        reserve_tokens: int = 1_000,
        remaining_budget: Optional[int] = None,
        arguments: Optional[dict[str, Any]] = None,
        model_context: Optional[Any] = None,
    ) -> tuple[str, list[str]]:
        """Prepare file content for prompts. Usually provided by BaseTool."""
        pass

    # ================================================================================
    # Abstract Methods - Tool-Specific Implementation Required
    # ================================================================================

    @abstractmethod
    def get_work_steps(self, request: Any) -> list[str]:
        """Define tool-specific work steps and criteria"""
        pass

    @abstractmethod
    def get_required_actions(self, step_number: int, confidence: str, findings: str, total_steps: int) -> list[str]:
        """Define required actions for each work phase.

        Args:
            step_number: Current step (1-based)
            confidence: Current confidence level (exploring, low, medium, high, certain)
            findings: Current findings text
            total_steps: Total estimated steps for this work

        Returns:
            List of specific actions Claude should take before calling tool again
        """
        pass

    # ================================================================================
    # Additional Abstract Methods - Tool-Specific Implementation
    # ================================================================================

    @abstractmethod
    def validate_and_correct_temperature(self, temperature: float, model_context: Any) -> tuple[float, list[str]]:
        """Validate temperature against model constraints. Usually provided by BaseTool."""
        pass

    @abstractmethod
    def validate_file_paths(self, request) -> Optional[str]:
        """Validate file paths for security. Usually provided by BaseTool."""
        pass

    # ================================================================================
    # Hook Methods - Default Implementations with Override Capability
    # ================================================================================
    # Note: Most hook methods are now provided by the mixins.
    # Tools can override these methods to customize behavior.

    # The following methods are provided by ExpertAnalysisMixin with default implementations:
    # - get_expert_analysis_instruction()
    # - should_call_expert_analysis(consolidated_findings, request)
    # - prepare_expert_analysis_context(consolidated_findings)
    # - requires_expert_analysis()
    # - should_include_files_in_expert_prompt()
    # - should_embed_system_prompt()
    # - get_expert_thinking_mode()
    # - get_expert_timeout_secs(request)
    # - get_expert_heartbeat_interval_secs(request)

    # The following methods are provided by FileEmbeddingMixin with default implementations:
    # - wants_line_numbers_by_default()
    # - _add_files_to_expert_context(expert_context, file_content)

    # The following methods are provided by RequestAccessorMixin with default implementations:
    # - get_completion_status()
    # - get_final_analysis_from_request(request)
    # - get_confidence_level(request)
    # - get_completion_message()
    # - get_skip_reason()
    # - get_skip_expert_analysis_status()
    # - get_expert_analysis_guidance()
    # - customize_workflow_response(response_data, request)

    # The following methods are provided by OrchestrationMixin with default implementations:
    # - should_skip_expert_analysis(request, consolidated_findings)
    # - handle_completion_without_expert_analysis(request, consolidated_findings)
    # - prepare_step_data(request)
    # - build_base_response(request, continuation_id)

    # ================================================================================
    # Main Entry Point
    # ================================================================================
    # The execute_workflow method is provided by OrchestrationMixin.
    # Tools should call this method to execute the workflow.

    # All implementation details are now in the specialized mixins:
    # - request_accessors.py: Request field extraction (~416 lines)
    # - conversation_integration.py: Thread management (~300 lines)
    # - file_embedding.py: File handling (~401 lines)
    # - expert_analysis.py: External model integration (~423 lines)
    # - orchestration.py: Main workflow engine (~703 lines)

    # This design keeps each module under 750 lines for AI context compatibility
    # while maintaining full functionality through composition.
