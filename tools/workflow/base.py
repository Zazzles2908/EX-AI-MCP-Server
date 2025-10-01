"""
Base class for workflow MCP tools.

Workflow tools follow a multi-step pattern:
1. Claude calls tool with work step data
2. Tool tracks findings and progress
3. Tool forces Claude to pause and investigate between steps
4. Once work is complete, tool calls external AI model for expert analysis
5. Tool returns structured response combining investigation + expert analysis

They combine BaseTool's capabilities with BaseWorkflowMixin's workflow functionality
and use SchemaBuilder for consistent schema generation.
"""

from abc import abstractmethod
from typing import Any, Optional

# Added: safe timeout/logging support for workflow execution
import asyncio
import json
import logging
import os

from tools.shared.base_models import WorkflowRequest
from tools.shared.base_tool import BaseTool

from .schema_builders import WorkflowSchemaBuilder
from .workflow_mixin import BaseWorkflowMixin

logger = logging.getLogger(__name__)


class WorkflowTool(BaseTool, BaseWorkflowMixin):
    """
    Base class for workflow (multi-step) tools.

    Workflow tools perform systematic multi-step work with expert analysis.
    They benefit from:
    - Automatic workflow orchestration from BaseWorkflowMixin
    - Automatic schema generation using SchemaBuilder
    - Inherited conversation handling and file processing from BaseTool
    - Progress tracking with ConsolidatedFindings
    - Expert analysis integration

    To create a workflow tool:
    1. Inherit from WorkflowTool
    2. Tool name is automatically provided by get_name() method
    3. Implement get_required_actions() for step guidance
    4. Implement should_call_expert_analysis() for completion criteria
    5. Implement prepare_expert_analysis_context() for expert prompts
    6. Optionally implement get_tool_fields() for additional fields
    7. Optionally override workflow behavior methods

    Example:
        class DebugTool(WorkflowTool):
            # get_name() is inherited from BaseTool

            def get_tool_fields(self) -> Dict[str, Dict[str, Any]]:
                return {
                    "hypothesis": {
                        "type": "string",
                        "description": "Current theory about the issue",
                    }
                }

            def get_required_actions(
                self, step_number: int, confidence: str, findings: str, total_steps: int
            ) -> List[str]:
                return ["Examine relevant code files", "Trace execution flow", "Check error logs"]

            def should_call_expert_analysis(self, consolidated_findings) -> bool:
                return len(consolidated_findings.relevant_files) > 0
    """

    # ================================================================================
    # Agentic Enhancement Configuration
    # ================================================================================

    # Configurable sufficiency thresholds (can be overridden per tool)
    MINIMUM_FINDINGS_LENGTH = 100  # Minimum characters in findings for sufficiency
    MINIMUM_RELEVANT_FILES = 0  # Minimum relevant files for sufficiency

    def __init__(self):
        """Initialize WorkflowTool with proper multiple inheritance."""
        BaseTool.__init__(self)
        BaseWorkflowMixin.__init__(self)
        # Initialize step adjustment history for transparency
        self.step_adjustment_history = []

    # ================================================================================
    # Agentic Enhancement Methods
    # ================================================================================

    def get_minimum_steps_for_tool(self) -> int:
        """
        Get minimum number of steps required before early termination is allowed.

        Override in subclasses to set tool-specific minimums.
        Default: 2 steps (prevents premature termination)
        """
        return 2

    def assess_information_sufficiency(self, request) -> dict:
        """
        Assess whether sufficient information has been gathered to achieve the goal.

        This is a key agentic capability - tools can self-assess their progress.

        Args:
            request: Current workflow request

        Returns:
            {
                "sufficient": bool,  # Has enough information been gathered?
                "confidence": str,  # Current confidence level
                "missing_information": list[str],  # What's still needed (if insufficient)
                "rationale": str  # Explanation of assessment
            }
        """
        # Get current state
        confidence = self.get_request_confidence(request)
        findings = getattr(request, 'findings', '')
        files_checked = len(getattr(request, 'files_checked', []))
        relevant_files = len(getattr(request, 'relevant_files', []))

        # Default sufficiency logic (tools can override)
        sufficient = (
            confidence in ["certain", "very_high", "almost_certain"] and
            len(findings) > self.MINIMUM_FINDINGS_LENGTH and  # Substantial findings documented
            relevant_files > self.MINIMUM_RELEVANT_FILES  # At least some relevant files identified
        )

        missing = []
        if not sufficient:
            if len(findings) < self.MINIMUM_FINDINGS_LENGTH:
                missing.append(f"More detailed findings needed (minimum {self.MINIMUM_FINDINGS_LENGTH} characters)")
            if relevant_files <= self.MINIMUM_RELEVANT_FILES:
                missing.append("No relevant files identified yet")
            if confidence in ["exploring", "low"]:
                missing.append("Confidence too low - more investigation needed")

        return {
            "sufficient": sufficient,
            "confidence": confidence,
            "missing_information": missing,
            "rationale": f"Confidence: {confidence}, Files checked: {files_checked}, Relevant: {relevant_files}, Findings length: {len(findings)}"
        }

    def should_terminate_early(self, request) -> tuple[bool, str]:
        """
        Determine if workflow can terminate early based on goal achievement.

        This enables agentic early termination when goals are achieved with high confidence.

        Args:
            request: Current workflow request

        Returns:
            (should_terminate, rationale)
        """
        # Check minimum steps requirement
        min_steps = self.get_minimum_steps_for_tool()
        if request.step_number < min_steps:
            return False, f"Minimum {min_steps} steps required for {self.get_name()}"

        # Get information sufficiency assessment
        assessment = self.assess_information_sufficiency(request)
        confidence = assessment["confidence"]
        sufficient = assessment["sufficient"]

        # Early termination criteria
        if confidence == "certain" and sufficient:
            return True, f"Goal achieved with certainty at step {request.step_number}/{request.total_steps}"

        # Allow termination at final step with very_high confidence
        if confidence == "very_high" and sufficient and request.step_number >= (request.total_steps - 1):
            return True, f"Very high confidence and sufficient information at step {request.step_number}/{request.total_steps}"

        return False, "Continue investigation"

    def request_additional_steps(self, request, reason: str, additional_steps: int = 1) -> int:
        """
        Request additional investigation steps mid-workflow.

        This enables agentic step adjustment when unexpected complexity is discovered.

        Args:
            request: Current workflow request
            reason: Clear explanation for why more steps are needed
            additional_steps: How many additional steps to add (default: 1)

        Returns:
            New total_steps count

        Raises:
            ValueError: If additional_steps is not positive
        """
        # Validate input
        if additional_steps <= 0:
            raise ValueError(
                f"additional_steps must be positive, got {additional_steps}. "
                f"Use a positive integer to add steps to the workflow."
            )

        old_total = request.total_steps
        new_total = old_total + additional_steps

        logger.info(
            f"{self.get_name()}: Requesting {additional_steps} additional steps "
            f"({old_total} → {new_total}). Reason: {reason}"
        )

        # Update request
        request.total_steps = new_total

        # Store rationale for transparency
        self.step_adjustment_history.append({
            "step_number": request.step_number,
            "old_total": old_total,
            "new_total": new_total,
            "reason": reason
        })

        return new_total

    # ================================================================================
    # Tool Configuration Methods
    # ================================================================================

    def get_tool_fields(self) -> dict[str, dict[str, Any]]:
        """
        Return tool-specific field definitions beyond the standard workflow fields.

        Workflow tools automatically get all standard workflow fields:
        - step, step_number, total_steps, next_step_required
        - findings, files_checked, relevant_files, relevant_context
        - issues_found, confidence, hypothesis, backtrack_from_step
        - plus common fields (model, temperature, etc.)

        Override this method to add additional tool-specific fields.

        Returns:
            Dict mapping field names to JSON schema objects

        Example:
            return {
                "severity_filter": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Minimum severity level to report",
                }
            }
        """
        return {}

    def get_required_fields(self) -> list[str]:
        """
        Return additional required fields beyond the standard workflow requirements.

        Workflow tools automatically require:
        - step, step_number, total_steps, next_step_required, findings
        - model (if in auto mode)

        Override this to add additional required fields.

        Returns:
            List of additional required field names
        """
        return []

    def get_annotations(self) -> Optional[dict[str, Any]]:
        """
        Return tool annotations. Workflow tools are read-only by default.

        All workflow tools perform analysis and investigation without modifying
        the environment. They may call external AI models for expert analysis,
        but they don't write files or make system changes.

        Override this method if your workflow tool needs different annotations.

        Returns:
            Dictionary with readOnlyHint set to True
        """
        return {"readOnlyHint": True}

    def get_input_schema(self) -> dict[str, Any]:
        """
        Generate the complete input schema using SchemaBuilder.

        This method automatically combines:
        - Standard workflow fields (step, findings, etc.)
        - Common fields (temperature, thinking_mode, etc.)
        - Model field with proper auto-mode handling
        - Tool-specific fields from get_tool_fields()
        - Required fields from get_required_fields()

        Returns:
            Complete JSON schema for the workflow tool
        """
        return WorkflowSchemaBuilder.build_schema(
            tool_specific_fields=self.get_tool_fields(),
            required_fields=self.get_required_fields(),
            model_field_schema=self.get_model_field_schema(),
            auto_mode=self.is_effective_auto_mode(),
            tool_name=self.get_name(),
        )


    def get_first_step_required_fields(self) -> list[str]:
        """
        Declare which fields are required at step 1 for this workflow tool.
        Default assumes file-oriented workflows and requires 'relevant_files'.
        Override in subclasses (e.g., Consensus) when different.
        """
        return ["relevant_files"]

    def get_descriptor(self) -> dict[str, Any]:
        """Return workflow-specific descriptor with step semantics (MVP)."""
        desc = super().get_descriptor()
        # Mark as workflow tool
        desc.update(
            {
                "category": "workflow",
                "type": "workflow",
                "supports_workflow": True,
                "supports_pause": True,
                "step_budget_hint": 2,
            }
        )

        # Infer first-step requirements from request model if available
        try:
            # Allow subclasses to override which fields are required in step 1
            first_step_required_fields: list[str] = list(self.get_first_step_required_fields() or [])
        except Exception:
            first_step_required_fields = []

        # Planning hints for common workflow fields
        planning_hints = {
            "common_workflow_fields": [
                "step",
                "step_number",
                "total_steps",
                "next_step_required",
                "findings",
            ]
        }

        desc["step_semantics"] = {
            "first_step_required_fields": first_step_required_fields,
            "final_step_flags": ["next_step_required=false"],
        }
        # Surface which fields are required at step 1 for orchestrators
        desc.setdefault("annotations", {})["first_step_required_fields"] = first_step_required_fields
        desc["planning_hints"] = planning_hints
        return desc

    def get_workflow_request_model(self):
        """
        Return the workflow request model class.

        Workflow tools use WorkflowRequest by default, which includes
        all the standard workflow fields. Override this if your tool
        needs a custom request model.
        """
        return WorkflowRequest

    # Implement the abstract method from BaseWorkflowMixin
    def get_work_steps(self, request) -> list[str]:
        """
        Default implementation - workflow tools typically don't need predefined steps.

        The workflow is driven by Claude's investigation process rather than
        predefined steps. Override this if your tool needs specific step guidance.
        """
        return []

    # Default implementations for common workflow patterns

    def get_standard_required_actions(self, step_number: int, confidence: str, base_actions: list[str]) -> list[str]:
        """
        Helper method to generate standard required actions based on confidence and step.

        This provides common patterns that most workflow tools can use:
        - Early steps: broad exploration
        - Low confidence: deeper investigation
        - Medium/high confidence: verification and confirmation

        Args:
            step_number: Current step number
            confidence: Current confidence level
            base_actions: Tool-specific base actions

        Returns:
            List of required actions appropriate for the current state
        """
        if step_number == 1:
            # Initial investigation
            return [
                "Search for code related to the reported issue or symptoms",
                "Examine relevant files and understand the current implementation",
                "Understand the project structure and locate relevant modules",
                "Identify how the affected functionality is supposed to work",
            ]
        elif confidence in ["exploring", "low"]:
            # Need deeper investigation
            return base_actions + [
                "Trace method calls and data flow through the system",
                "Check for edge cases, boundary conditions, and assumptions in the code",
                "Look for related configuration, dependencies, or external factors",
            ]
        elif confidence in ["medium", "high"]:
            # Close to solution - need confirmation
            return base_actions + [
                "Examine the exact code sections where you believe the issue occurs",
                "Trace the execution path that leads to the failure",
                "Verify your hypothesis with concrete code evidence",
                "Check for any similar patterns elsewhere in the codebase",
            ]
        else:
            # General continued investigation
            return base_actions + [
                "Continue examining the code paths identified in your hypothesis",
                "Gather more evidence using appropriate investigation tools",
                "Test edge cases and boundary conditions",
                "Look for patterns that confirm or refute your theory",
            ]

    def should_call_expert_analysis_default(self, consolidated_findings) -> bool:
        """
        Default implementation for expert analysis decision.

        This provides a reasonable default that most workflow tools can use:
        - Call expert analysis if we have relevant files or significant findings
        - Skip if confidence is "certain" (handled by the workflow mixin)

        Override this for tool-specific logic.

        Args:
            consolidated_findings: The consolidated findings from all work steps

        Returns:
            True if expert analysis should be called
        """
        # Call expert analysis if we have relevant files or substantial findings
        return (
            len(consolidated_findings.relevant_files) > 0
            or len(consolidated_findings.findings) >= 2
            or len(consolidated_findings.issues_found) > 0
        )

    def prepare_standard_expert_context(
        self, consolidated_findings, initial_description: str, context_sections: dict[str, str] = None
    ) -> str:
        """
        Helper method to prepare standard expert analysis context.

        This provides a common structure that most workflow tools can use,
        with the ability to add tool-specific sections.

        Args:
            consolidated_findings: The consolidated findings from all work steps
            initial_description: Description of the initial request/issue
            context_sections: Optional additional sections to include

        Returns:
            Formatted context string for expert analysis
        """
        context_parts = [f"=== ISSUE DESCRIPTION ===\n{initial_description}\n=== END DESCRIPTION ==="]

        # Add work progression
        if consolidated_findings.findings:
            findings_text = "\n".join(consolidated_findings.findings)
            context_parts.append(f"\n=== INVESTIGATION FINDINGS ===\n{findings_text}\n=== END FINDINGS ===")

        # Add relevant methods if available
        if consolidated_findings.relevant_context:
            methods_text = "\n".join(f"- {method}" for method in consolidated_findings.relevant_context)
            context_parts.append(f"\n=== RELEVANT METHODS/FUNCTIONS ===\n{methods_text}\n=== END METHODS ===")

        # Add hypothesis evolution if available
        if consolidated_findings.hypotheses:
            hypotheses_text = "\n".join(
                f"Step {h['step']} ({h['confidence']} confidence): {h['hypothesis']}"
                for h in consolidated_findings.hypotheses
            )
            context_parts.append(f"\n=== HYPOTHESIS EVOLUTION ===\n{hypotheses_text}\n=== END HYPOTHESES ===")

        # Add issues found if available
        if consolidated_findings.issues_found:
            issues_text = "\n".join(
                f"[{issue.get('severity', 'unknown').upper()}] {issue.get('description', 'No description')}"
                for issue in consolidated_findings.issues_found
            )
            context_parts.append(f"\n=== ISSUES IDENTIFIED ===\n{issues_text}\n=== END ISSUES ===")

        # Add tool-specific sections
        if context_sections:
            for section_title, section_content in context_sections.items():
                context_parts.append(
                    f"\n=== {section_title.upper()} ===\n{section_content}\n=== END {section_title.upper()} ==="
                )

        return "\n".join(context_parts)

    def handle_completion_without_expert_analysis(
        self, request, consolidated_findings, initial_description: str = None
    ) -> dict[str, Any]:
        """
        Generic handler for completion when expert analysis is not needed.

        This provides a standard response format for when the tool determines
        that external expert analysis is not required. All workflow tools
        can use this generic implementation or override for custom behavior.

        Args:
            request: The workflow request object
            consolidated_findings: The consolidated findings from all work steps
            initial_description: Optional initial description (defaults to request.step)

        Returns:
            Dictionary with completion response data
        """
        # Prepare work summary using inheritance hook
        work_summary = self.prepare_work_summary()

        return {
            "status": self.get_completion_status(),
            self.get_completion_data_key(): {
                "initial_request": initial_description or request.step,
                "steps_taken": len(consolidated_findings.findings),
                "files_examined": list(consolidated_findings.files_checked),
                "relevant_files": list(consolidated_findings.relevant_files),
                "relevant_context": list(consolidated_findings.relevant_context),
                "work_summary": work_summary,
                "final_analysis": self.get_final_analysis_from_request(request),
                "confidence_level": self.get_confidence_level(request),
            },
            "next_steps": self.get_completion_message(),
            "skip_expert_analysis": True,
            "expert_analysis": {
                "status": self.get_skip_expert_analysis_status(),
                "reason": self.get_skip_reason(),
            },
        }

    # Inheritance hooks for customization

    def prepare_work_summary(self) -> str:
        """
        Prepare a summary of the work performed. Override for custom summaries.
        Default implementation provides a basic summary.
        """
        try:
            return self._prepare_work_summary()
        except AttributeError:
            try:
                return f"Completed {len(self.work_history)} work steps"
            except AttributeError:
                return "Completed 0 work steps"

    def get_completion_status(self) -> str:
        """Get the status to use when completing without expert analysis."""
        return "high_confidence_completion"

    def get_completion_data_key(self) -> str:
        """Get the key name for completion data in the response."""
        return f"complete_{self.get_name()}"

    def get_final_analysis_from_request(self, request) -> Optional[str]:
        """Extract final analysis from request. Override for tool-specific extraction."""
        try:
            return request.hypothesis
        except AttributeError:
            return None

    def get_confidence_level(self, request) -> str:
        """Get confidence level from request. Override for tool-specific logic."""
        try:
            return request.confidence or "high"
        except AttributeError:
            return "high"

    def get_completion_message(self) -> str:
        """Get completion message. Override for tool-specific messaging."""
        return (
            f"{self.get_name().capitalize()} complete with high confidence. You have identified the exact "
            "analysis and solution. MANDATORY: Present the user with the results "
            "and proceed with implementing the solution without requiring further "
            "consultation. Focus on the precise, actionable steps needed."
        )

    def get_skip_reason(self) -> str:
        """Get reason for skipping expert analysis. Override for tool-specific reasons."""
        return f"{self.get_name()} completed with sufficient confidence"

    def get_skip_expert_analysis_status(self) -> str:
        """Get status for skipped expert analysis. Override for tool-specific status."""
        return "skipped_by_tool_design"

    def is_continuation_workflow(self, request) -> bool:
        """
        Check if this is a continuation workflow that should skip multi-step investigation.

        When continuation_id is provided, the workflow typically continues from a previous
        conversation and should go directly to expert analysis rather than starting a new
        multi-step investigation.

        Args:
            request: The workflow request object

        Returns:
            True if this is a continuation that should skip multi-step workflow
        """
        continuation_id = self.get_request_continuation_id(request)
        return bool(continuation_id)

    # Abstract methods that must be implemented by specific workflow tools
    # (These are inherited from BaseWorkflowMixin and must be implemented)

    @abstractmethod
    def get_required_actions(self, step_number: int, confidence: str, findings: str, total_steps: int) -> list[str]:
        """Define required actions for each work phase."""
        pass

    @abstractmethod
    def should_call_expert_analysis(self, consolidated_findings) -> bool:
        """Decide when to call external model based on tool-specific criteria"""
        pass

    @abstractmethod
    def prepare_expert_analysis_context(self, consolidated_findings) -> str:
        """Prepare context for external model call"""
        pass

    # Default execute method - delegates to workflow
    async def execute(self, arguments: dict[str, Any]) -> list:
        """Execute the workflow tool with a safety timeout and error logging.

        - Wraps execute_workflow() in asyncio.wait_for to prevent hangs
        - Timeout is controlled via WORKFLOW_STEP_TIMEOUT_SECS (default 45s)
        - On timeout, logs to centralized error sink and returns a structured error
        """
        timeout_default = 45.0
        try:
            # Adaptive per-step timeout: larger for final steps with expert validation
            req = None
            try:
                req_model = self.get_workflow_request_model()
                req = req_model(**arguments) if req_model else None
            except Exception:
                req = None

            # Determine if this is the final step
            try:
                is_final = bool(req and getattr(req, "next_step_required", True) is False)
            except Exception:
                is_final = bool(not (arguments or {}).get("next_step_required", True))

            # Determine whether expert validation is requested
            try:
                use_assistant = self.get_request_use_assistant_model(req) if req is not None else True
            except Exception:
                # Fallback to env default when request model isn't available
                _env = (os.getenv("DEFAULT_USE_ASSISTANT_MODEL") or "").strip().lower()
                use_assistant = _env not in ("false", "0", "no", "off")

            if is_final and use_assistant:
                # For final expert step: cap by expert budget + buffer, under WS ceiling
                try:
                    expert_budget = float(self.get_expert_timeout_secs(req))
                except Exception:
                    expert_budget = 90.0
                try:
                    ws_ceiling = float(os.getenv("EXAI_WS_CALL_TIMEOUT", "180"))
                except Exception:
                    ws_ceiling = 180.0
                timeout = max(5.0, min(expert_budget + 30.0, ws_ceiling - 5.0))
            else:
                # For intermediate steps: use workflow step timeout
                timeout = float(os.getenv("WORKFLOW_STEP_TIMEOUT_SECS", str(timeout_default)))
        except Exception:
            timeout = timeout_default

        try:
            return await asyncio.wait_for(self.execute_workflow(arguments), timeout=timeout)
        except asyncio.TimeoutError:
            # Log error to centralized error sink
            try:
                logger.error(f"{self.get_name()} workflow step timed out after {timeout}s", exc_info=True)
            except Exception:
                pass
            # Return a structured MCP-safe error payload
            try:
                from mcp.types import TextContent
                error_payload = {
                    "status": f"{self.get_name()}_timeout",
                    "error": f"Workflow step exceeded {timeout} seconds",
                    "step_number": arguments.get("step_number"),
                }
                return [TextContent(type="text", text=json.dumps(error_payload))]
            except Exception:
                # Fallback minimal shape
                return [{"type": "text", "text": json.dumps({"status": f"{self.get_name()}_timeout"})}]
        except Exception as e:
            # Ensure unexpected errors are logged and surfaced
            try:
                logger.error(f"{self.get_name()} workflow execution error: {e}", exc_info=True)
            except Exception:
                pass
            try:
                from mcp.types import TextContent
                error_payload = {
                    "status": f"{self.get_name()}_failed",
                    "error": str(e),
                    "step_number": arguments.get("step_number"),
                }
                return [TextContent(type="text", text=json.dumps(error_payload))]
            except Exception:
                return [{"type": "text", "text": json.dumps({"status": f"{self.get_name()}_failed"})}]
