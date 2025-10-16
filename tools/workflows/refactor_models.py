"""
Refactor Workflow Request Model

Pydantic request model for the Refactor workflow tool.
"""

from typing import Literal, Optional

from pydantic import Field

from tools.shared.base_models import WorkflowRequest

from .refactor_config import REFACTOR_FIELD_DESCRIPTIONS


class RefactorRequest(WorkflowRequest):
    """Request model for refactor workflow investigation steps"""

    # Required fields for each investigation step
    step: str = Field(..., description=REFACTOR_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=REFACTOR_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=REFACTOR_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=REFACTOR_FIELD_DESCRIPTIONS["next_step_required"])

    # Investigation tracking fields
    findings: str = Field(..., description=REFACTOR_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=REFACTOR_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=REFACTOR_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=REFACTOR_FIELD_DESCRIPTIONS["relevant_context"]
    )
    issues_found: list[dict] = Field(
        default_factory=list, description=REFACTOR_FIELD_DESCRIPTIONS["issues_found"]
    )
    # confidence field inherited from WorkflowRequest with correct Literal type validation
    # Note: refactor uses "incomplete" as default, but base class uses "low" - this may need adjustment

    # Optional backtracking field
    backtrack_from_step: Optional[int] = Field(
        None, description=REFACTOR_FIELD_DESCRIPTIONS["backtrack_from_step"]
    )

    # Optional images for visual context
    images: Optional[list[str]] = Field(default=None, description=REFACTOR_FIELD_DESCRIPTIONS["images"])

    # Refactor-specific fields
    refactor_type: Optional[Literal["codesmells", "decompose", "modernize", "organization"]] = Field(
        "codesmells", description=REFACTOR_FIELD_DESCRIPTIONS["refactor_type"]
    )
    focus_areas: Optional[list[str]] = Field(default=None, description=REFACTOR_FIELD_DESCRIPTIONS["focus_areas"])
    style_guide_examples: Optional[list[str]] = Field(
        default=None, description=REFACTOR_FIELD_DESCRIPTIONS["style_guide_examples"]
    )

    # Override inherited fields to exclude them from schema (except model which needs to be available)
    temperature: Optional[float] = Field(default=None, exclude=True)
    # thinking_mode field inherited from ToolRequest with correct Literal type validation
    use_websearch: Optional[bool] = Field(default=None, exclude=True)


__all__ = ["RefactorRequest"]

