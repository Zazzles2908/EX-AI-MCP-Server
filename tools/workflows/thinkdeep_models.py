"""
ThinkDeep Workflow Request Model

Pydantic request model for the ThinkDeep workflow tool.
Defines the comprehensive investigation capabilities and parameters.
"""

from typing import Optional

from pydantic import Field

from tools.shared.base_models import WorkflowRequest


class ThinkDeepWorkflowRequest(WorkflowRequest):
    """Request model for thinkdeep workflow tool with comprehensive investigation capabilities"""

    # Core workflow parameters
    step: str = Field(description="Current work step content and findings from your overall work")
    step_number: int = Field(description="Current step number in the work sequence (starts at 1)", ge=1)
    total_steps: int = Field(description="Estimated total steps needed to complete the work", ge=1)
    next_step_required: bool = Field(description="Whether another work step is needed after this one")
    findings: str = Field(
        description="Summarize everything discovered in this step about the problem/goal. Include new insights, "
        "connections made, implications considered, alternative approaches, potential issues identified, "
        "and evidence from thinking. Be specific and avoid vague language—document what you now know "
        "and how it affects your hypothesis or understanding. IMPORTANT: If you find compelling evidence "
        "that contradicts earlier assumptions, document this clearly. In later steps, confirm or update "
        "past findings with additional reasoning."
    )

    # Investigation tracking
    files_checked: list[str] = Field(
        default_factory=list,
        description="List all files (as absolute paths) examined during the investigation so far. "
        "Include even files ruled out or found unrelated, as this tracks your exploration path.",
    )
    relevant_files: list[str] = Field(
        default_factory=list,
        description="Subset of files_checked (as full absolute paths) that contain information directly "
        "relevant to the problem or goal. Only list those directly tied to the root cause, "
        "solution, or key insights. This could include the source of the issue, documentation "
        "that explains the expected behavior, configuration files that affect the outcome, or "
        "examples that illustrate the concept being analyzed.",
    )
    relevant_context: list[str] = Field(
        default_factory=list,
        description="Key concepts, methods, or principles that are central to the thinking analysis, "
        "in the format 'concept_name' or 'ClassName.methodName'. Focus on those that drive "
        "the core insights, represent critical decision points, or define the scope of the analysis.",
    )
    hypothesis: Optional[str] = Field(
        default=None,
        description="Current theory or understanding about the problem/goal based on evidence gathered. "
        "This should be a concrete theory that can be validated or refined through further analysis. "
        "You are encouraged to revise or abandon hypotheses in later steps based on new evidence.",
    )

    # Analysis metadata
    issues_found: list[dict] = Field(
        default_factory=list,
        description="Issues identified during work with severity levels - each as a dict with "
        "'severity' (critical, high, medium, low) and 'description' fields.",
    )
    confidence: str = Field(
        default="low",
        description="Indicate your current confidence in the analysis. Use: 'exploring' (starting analysis), "
        "'low' (early thinking), 'medium' (some insights gained), 'high' (strong understanding), "
        "'very_high' (very strong understanding), 'almost_certain' (nearly complete analysis), "
        "'certain' (100% confidence - analysis is complete and conclusions are definitive with no need for external model validation). "
        "Do NOT use 'certain' unless the thinking is comprehensively complete, use 'very_high' or 'almost_certain' instead when in doubt. "
        "Using 'certain' means you have complete confidence locally and prevents external model validation.",
    )
    # thinking_mode field inherited from ToolRequest with correct Literal type validation

    # Advanced workflow features
    backtrack_from_step: Optional[int] = Field(
        default=None,
        description="If an earlier finding or hypothesis needs to be revised or discarded, "
        "specify the step number from which to start over. Use this to acknowledge analytical "
        "dead ends and correct the course.",
        ge=1,
    )

    # Expert analysis configuration - keep these fields available for configuring the final assistant model
    # in expert analysis (commented out exclude=True)
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature for creative thinking (0-1, default 0.7)",
        ge=0.0,
        le=1.0,
        # exclude=True  # Excluded from MCP schema but available for internal use
    )
    # NOTE: thinking_mode is already defined above at lines 74-80, removed duplicate definition
    use_websearch: Optional[bool] = Field(
        default=None,
        description="Enable web search for documentation, best practices, and current information. Particularly useful for: brainstorming sessions, architectural design discussions, exploring industry best practices, working with specific frameworks/technologies, researching solutions to complex problems, or when current documentation and community insights would enhance the analysis.",
        # exclude=True  # Excluded from MCP schema but available for internal use
    )

    # Context files and investigation scope
    problem_context: Optional[str] = Field(
        default=None,
        description="Provide additional context about the problem or goal. Be as expressive as possible. More information will be very helpful for the analysis.",
    )
    focus_areas: Optional[list[str]] = Field(
        default=None,
        description="Specific aspects to focus on (architecture, performance, security, etc.)",
    )


__all__ = ["ThinkDeepWorkflowRequest"]

