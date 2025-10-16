"""
Tracer Workflow Request Model

Pydantic request model for the Tracer workflow tool with validators.
"""

from typing import Literal, Optional

from pydantic import Field, field_validator

from tools.shared.base_models import WorkflowRequest

from .tracer_config import TRACER_WORKFLOW_FIELD_DESCRIPTIONS


class TracerRequest(WorkflowRequest):
    """Request model for tracer workflow investigation steps"""

    # Required fields for each investigation step
    step: str = Field(..., description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])

    # Investigation tracking fields
    findings: str = Field(..., description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )
    # confidence field inherited from WorkflowRequest with correct Literal type validation
    # Note: tracer uses "exploring" as default, but base class uses "low" - this may need adjustment

    # Tracer-specific fields (used in step 1 to initialize)
    trace_mode: Optional[Literal["precision", "dependencies", "ask"]] = Field(
        "ask", description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["trace_mode"]
    )
    target_description: Optional[str] = Field(
        None, description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["target_description"]
    )
    images: Optional[list[str]] = Field(default=None, description=TRACER_WORKFLOW_FIELD_DESCRIPTIONS["images"])

    # Exclude fields not relevant to tracing workflow
    issues_found: list[dict] = Field(default_factory=list, exclude=True, description="Tracing doesn't track issues")
    hypothesis: Optional[str] = Field(default=None, exclude=True, description="Tracing doesn't use hypothesis")
    backtrack_from_step: Optional[int] = Field(
        default=None, exclude=True, description="Tracing doesn't use backtracking"
    )

    # Exclude other non-tracing fields
    temperature: Optional[float] = Field(default=None, exclude=True)
    # thinking_mode field inherited from ToolRequest with correct Literal type validation
    use_websearch: Optional[bool] = Field(default=None, exclude=True)
    use_assistant_model: Optional[bool] = Field(default=False, exclude=True, description="Tracing is self-contained")

    @field_validator("step_number")
    @classmethod
    def validate_step_number(cls, v):
        if v < 1:
            raise ValueError("step_number must be at least 1")
        return v

    @field_validator("total_steps")
    @classmethod
    def validate_total_steps(cls, v):
        if v < 1:
            raise ValueError("total_steps must be at least 1")
        return v


__all__ = ["TracerRequest"]

