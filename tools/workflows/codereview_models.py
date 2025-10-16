"""
CodeReview Workflow Request Model

Pydantic request model for the CodeReview workflow tool with validators.
"""

from typing import Literal, Optional

from pydantic import Field, model_validator

from tools.shared.base_models import WorkflowRequest

from .codereview_config import CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS


class CodeReviewRequest(WorkflowRequest):
    """Request model for code review workflow investigation steps"""

    # Required fields for each investigation step
    step: str = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])

    # Investigation tracking fields
    findings: str = Field(..., description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )
    issues_found: list[dict] = Field(
        default_factory=list, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["issues_found"]
    )
    # confidence field inherited from WorkflowRequest with correct Literal type validation

    # Optional backtracking field
    backtrack_from_step: Optional[int] = Field(
        None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["backtrack_from_step"]
    )

    # Optional images for visual context
    images: Optional[list[str]] = Field(default=None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["images"])

    # Code review-specific fields (only used in step 1 to initialize)
    review_type: Optional[Literal["full", "security", "performance", "quick"]] = Field(
        "full", description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["review_type"]
    )
    focus_on: Optional[str] = Field(None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["focus_on"])
    standards: Optional[str] = Field(None, description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["standards"])
    severity_filter: Optional[Literal["critical", "high", "medium", "low", "all"]] = Field(
        "all", description=CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS["severity_filter"]
    )

    # Override inherited fields to exclude them from schema (except model which needs to be available)
    temperature: Optional[float] = Field(default=None, exclude=True)
    # thinking_mode field inherited from ToolRequest with correct Literal type validation
    use_websearch: Optional[bool] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_step_one_requirements(self):
        """Ensure step 1 has required relevant_files field."""
        if self.step_number == 1 and not self.relevant_files:
            raise ValueError("Step 1 requires 'relevant_files' field to specify code files or directories to review")
        return self


__all__ = ["CodeReviewRequest"]

