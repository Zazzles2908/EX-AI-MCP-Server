"""
Analyze Workflow Request Model

Pydantic request model for the Analyze workflow tool with validators.
"""

from typing import Literal, Optional

from pydantic import Field, model_validator

from tools.shared.base_models import WorkflowRequest

from .analyze_config import ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS


class AnalyzeWorkflowRequest(WorkflowRequest):
    """Request model for analyze workflow investigation steps"""

    # Required fields for each investigation step
    step: str = Field(..., description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])

    # Investigation tracking fields
    findings: str = Field(..., description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )

    # Issues found during analysis (structured with severity)
    issues_found: list[dict] = Field(
        default_factory=list,
        description="Issues or concerns identified during analysis, each with severity level (critical, high, medium, low)",
    )

    # Optional backtracking field
    backtrack_from_step: Optional[int] = Field(
        None, description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["backtrack_from_step"]
    )

    # Optional images for visual context
    images: Optional[list[str]] = Field(default=None, description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["images"])

    # Analyze-specific fields (only used in step 1 to initialize)
    # Note: Use relevant_files field instead of files for consistency across workflow tools
    analysis_type: Optional[Literal["architecture", "performance", "security", "quality", "general"]] = Field(
        "general", description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["analysis_type"]
    )
    output_format: Optional[Literal["summary", "detailed", "actionable"]] = Field(
        "detailed", description=ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS["output_format"]
    )

    # Keep thinking_mode and use_websearch from original analyze tool
    # temperature is inherited from WorkflowRequest

    @model_validator(mode="after")
    def validate_step_one_requirements(self):
        """Ensure step 1 has required relevant_files, but allow relaxations.

        Relaxation cases:
        - If continuation_id is present (continuing prior analysis), allow empty relevant_files
        - If env ANALYZE_ALLOW_DEFAULT_ROOT is true, allow defaulting to repo root ('.')
        """
        if self.step_number == 1:
            if not self.relevant_files:
                import os
                # Allow continuation-based step 1 (some clients reset numbering)
                cont_id = getattr(self, "continuation_id", None)
                allow_root = os.getenv("ANALYZE_ALLOW_DEFAULT_ROOT", "true").strip().lower() == "true"
                if cont_id or allow_root:
                    # Try a git-aware default: changed/recent files if git is available
                    try:
                        import subprocess, shlex
                        cmd = "git -c core.quotepath=false status --porcelain"
                        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
                        changed = []
                        if proc.returncode == 0:
                            for line in proc.stdout.splitlines():
                                parts = line.strip().split()
                                if parts:
                                    path = parts[-1]
                                    # Skip deletes and untracked directories noise
                                    if path and not path.endswith("/"):
                                        changed.append(path)
                        if changed:
                            # Cap to a reasonable default set
                            self.relevant_files = changed[:50]
                        else:
                            self.relevant_files = ["."]
                    except Exception:
                        self.relevant_files = ["."]


                else:
                    raise ValueError("Step 1 requires 'relevant_files' (or set ANALYZE_ALLOW_DEFAULT_ROOT=true)")
        return self
    
    @model_validator(mode="after")
    def normalize_analysis_type(self):
        # Map synonyms to valid literals; default to 'general'
        syn = (self.analysis_type or "").strip().lower()
        mapping = {
            "comprehensive": "general",
            "full": "general",
            "all": "general",
        }
        if syn in mapping:
            self.analysis_type = mapping[syn]
        elif syn not in {"architecture", "performance", "security", "quality", "general", ""}:
            self.analysis_type = "general"
        return self


__all__ = ["AnalyzeWorkflowRequest"]

