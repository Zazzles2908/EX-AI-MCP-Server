"""
SecAudit Workflow Request Model

Pydantic request model for the SecAudit workflow tool with validators.
"""

import logging
from typing import Literal, Optional

from pydantic import Field, model_validator

from tools.shared.base_models import WorkflowRequest

from .secaudit_config import SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS

logger = logging.getLogger(__name__)


class SecauditRequest(WorkflowRequest):
    """Request model for security audit workflow investigation steps"""

    # Required fields for each investigation step
    step: str = Field(..., description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["step"])
    step_number: int = Field(..., description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["step_number"])
    total_steps: int = Field(..., description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"])
    next_step_required: bool = Field(..., description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"])

    # Investigation tracking fields
    findings: str = Field(..., description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["findings"])
    files_checked: list[str] = Field(
        default_factory=list, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["files_checked"]
    )
    relevant_files: list[str] = Field(
        default_factory=list, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"]
    )
    relevant_context: list[str] = Field(
        default_factory=list, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["relevant_context"]
    )
    issues_found: list[dict] = Field(
        default_factory=list, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["issues_found"]
    )
    # confidence field inherited from WorkflowRequest with correct Literal type validation

    # Optional backtracking field
    backtrack_from_step: Optional[int] = Field(
        None, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["backtrack_from_step"]
    )

    # Optional images for visual context
    images: Optional[list[str]] = Field(default=None, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["images"])

    # Security audit-specific fields
    security_scope: Optional[str] = Field(None, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["security_scope"])
    threat_level: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        "medium", description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["threat_level"]
    )
    compliance_requirements: Optional[list[str]] = Field(
        default_factory=list, description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["compliance_requirements"]
    )
    audit_focus: Optional[Literal["owasp", "compliance", "infrastructure", "dependencies", "comprehensive"]] = Field(
        "comprehensive", description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["audit_focus"]
    )
    severity_filter: Optional[Literal["critical", "high", "medium", "low", "all"]] = Field(
        "all", description=SECAUDIT_WORKFLOW_FIELD_DESCRIPTIONS["severity_filter"]
    )

    @model_validator(mode="after")
    def validate_security_audit_request(self):
        """Validate security audit request parameters"""
        # Ensure security scope is provided for comprehensive audits
        if self.step_number == 1 and not self.security_scope:
            logger.warning("Security scope not provided for security audit - defaulting to general application")

        # Validate compliance requirements format
        if self.compliance_requirements:
            valid_compliance = {"SOC2", "PCI DSS", "HIPAA", "GDPR", "ISO 27001", "NIST", "FedRAMP", "FISMA"}
            for req in self.compliance_requirements:
                if req not in valid_compliance:
                    logger.warning(f"Unknown compliance requirement: {req}")

        return self


__all__ = ["SecauditRequest"]

