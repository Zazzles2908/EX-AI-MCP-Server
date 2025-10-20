"""
ThinkDeep Workflow Tool - Extended Reasoning with Systematic Investigation

This tool provides step-by-step deep thinking capabilities using a systematic workflow approach.
It enables comprehensive analysis of complex problems with expert validation at completion.

Key Features:
- Systematic step-by-step thinking process
- Multi-step analysis with evidence gathering
- Confidence-based investigation flow
- Expert analysis integration with external models
- Support for focused analysis areas (architecture, performance, security, etc.)
- Confidence-based workflow optimization
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

# Progress helper
from utils.progress import send_progress

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from config import TEMPERATURE_CREATIVE
from systemprompts import THINKDEEP_PROMPT

from .thinkdeep_config import THINKDEEP_FIELD_OVERRIDES
from .thinkdeep_models import ThinkDeepWorkflowRequest
from .thinkdeep_ui import ui_build_summary, ui_summarize_text
from ..workflow.base import WorkflowTool

logger = logging.getLogger(__name__)


class ThinkDeepTool(WorkflowTool):
    """
    ThinkDeep Workflow Tool - Systematic Deep Thinking Analysis

    Provides comprehensive step-by-step thinking capabilities with expert validation.
    Uses workflow architecture for systematic investigation and analysis.
    """

    name = "thinkdeep"
    description = (
        "COMPREHENSIVE INVESTIGATION & REASONING - Multi-stage workflow for complex problem analysis. "
        "Use this when you need structured evidence-based investigation, systematic hypothesis testing, or expert validation. "
        "Perfect for: architecture decisions, complex bugs, performance challenges, security analysis. "
        "Provides methodical investigation with assumption validation, alternative solution exploration, and rigorous analysis. "
        "IMPORTANT: Choose the appropriate mode based on task complexity - 'low' for quick investigation, "
        "'medium' for standard problems, 'high' for complex issues (default), 'max' for extremely complex "
        "challenges requiring exhaustive investigation. When in doubt, err on the side of a higher mode for thorough "
        "systematic analysis and expert validation. Note: If you're not currently using a top-tier model such as Opus 4 or above, "
        "these tools can provide enhanced capabilities."
    )

    def __init__(self):
        """Initialize the ThinkDeep workflow tool"""
        super().__init__()
        # Storage for request parameters to use in expert analysis
        self.stored_request_params = {}

    def get_name(self) -> str:
        """Return the tool name"""
        return self.name

    def get_description(self) -> str:
        """Return the tool description with a minimal example"""
        return self.description + "\nExample: {\"step\":\"Evaluate routing options\",\"step_number\":1,\"total_steps\":1,\"next_step_required\":false,\"model\":\"auto\"}."

    def get_model_category(self) -> "ToolModelCategory":
        """Return the model category for this tool"""
        from tools.models import ToolModelCategory

        return ToolModelCategory.EXTENDED_REASONING

    def get_workflow_request_model(self):
        """Return the workflow request model for this tool"""
        return ThinkDeepWorkflowRequest

    def get_first_step_required_fields(self) -> list[str]:
        # Thinkdeep does not require files in step 1; it’s analysis-focused
        return []

    def get_input_schema(self) -> dict[str, Any]:
        """Generate input schema using WorkflowSchemaBuilder with thinkdeep-specific overrides."""
        from ..workflow.schema_builders import WorkflowSchemaBuilder

        # Use WorkflowSchemaBuilder with thinkdeep-specific tool fields
        return WorkflowSchemaBuilder.build_schema(
            tool_specific_fields=THINKDEEP_FIELD_OVERRIDES,
            model_field_schema=self.get_model_field_schema(),
            auto_mode=self.is_effective_auto_mode(),
            tool_name=self.get_name(),
        )

    def get_system_prompt(self) -> str:
        """Return the system prompt for this workflow tool"""
        return THINKDEEP_PROMPT

    def get_default_temperature(self) -> float:
        """Return default temperature for deep thinking"""
        return TEMPERATURE_CREATIVE

    def get_default_thinking_mode(self) -> str:
        """Return default thinking mode for thinkdeep"""
        from config import DEFAULT_THINKING_MODE_THINKDEEP
        return DEFAULT_THINKING_MODE_THINKDEEP

    # Override expert analysis timing with adaptive timeout based on thinking mode
    def get_expert_timeout_secs(self, request=None) -> float:
        """Adaptive timeout based on thinking mode to prevent premature termination.

        Uses EXPERT_ANALYSIS_TIMEOUT_SECS from .env as base, with adaptive multipliers:
        - minimal: 0.5x base (quick validation)
        - low: 0.7x base (standard validation)
        - medium: 1.0x base (thorough analysis)
        - high: 1.5x base (deep analysis)
        - max: 2.0x base (exhaustive reasoning)

        Can be overridden via THINKDEEP_EXPERT_TIMEOUT_SECS env var for manual control.
        """
        import os
        from config import TimeoutConfig

        # Allow manual override (takes precedence)
        env_timeout = os.getenv("THINKDEEP_EXPERT_TIMEOUT_SECS")
        if env_timeout:
            try:
                timeout = float(env_timeout)
                logger.info(f"[THINKDEEP_TIMEOUT] Using manual override: {timeout}s")
                return timeout
            except Exception:
                pass

        # Get base timeout from config (respects .env EXPERT_ANALYSIS_TIMEOUT_SECS)
        base_timeout = float(TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS)

        # Adaptive multipliers based on thinking mode
        thinking_mode = self.get_expert_thinking_mode(request)

        TIMEOUT_MULTIPLIERS = {
            "minimal": 0.5,   # Quick validation (e.g., 180s * 0.5 = 90s)
            "low": 0.7,       # Standard validation (e.g., 180s * 0.7 = 126s)
            "medium": 1.0,    # Thorough analysis (e.g., 180s * 1.0 = 180s)
            "high": 1.5,      # Deep analysis (e.g., 180s * 1.5 = 270s)
            "max": 2.0        # Exhaustive reasoning (e.g., 180s * 2.0 = 360s)
        }

        multiplier = TIMEOUT_MULTIPLIERS.get(thinking_mode, 1.0)  # Default to 'medium'
        timeout = base_timeout * multiplier

        logger.info(f"[THINKDEEP_TIMEOUT] thinking_mode={thinking_mode}, base={base_timeout}s, multiplier={multiplier}x → timeout={timeout}s")
        return timeout

    def get_expert_heartbeat_interval_secs(self, request=None) -> float:
        """Emit progress frequently enough to satisfy 10s idle clients.
        Uses THINKDEEP_HEARTBEAT_INTERVAL_SECS if set, else default 7s.
        """
        import os
        try:
            return float(os.getenv("THINKDEEP_HEARTBEAT_INTERVAL_SECS", "7"))
        except Exception:
            return 7.0

    def customize_workflow_response(self, response_data: dict, request, **kwargs) -> dict:
        """
        Customize the workflow response for thinkdeep-specific needs
        """
        # Store request parameters for later use in expert analysis (preserve existing if None)
        if not isinstance(getattr(self, "stored_request_params", None), dict):
            self.stored_request_params = {}
        try:
            if getattr(request, "temperature", None) is not None:
                self.stored_request_params["temperature"] = request.temperature
        except AttributeError:
            pass

        try:
            if getattr(request, "thinking_mode", None) is not None:
                self.stored_request_params["thinking_mode"] = request.thinking_mode
        except AttributeError:
            pass

        try:
            if getattr(request, "use_websearch", None) is not None:
                self.stored_request_params["use_websearch"] = request.use_websearch
        except AttributeError:
            pass
        # Store model if provided
        try:
            model_val = getattr(request, "model", None)
        except AttributeError:
            model_val = None
        if model_val is not None:
            try:
                self.stored_request_params["model"] = model_val
            except Exception:
                pass

        # Add thinking-specific context to response
        response_data.update(
            {
                "thinking_status": {
                    "current_step": request.step_number,
                    "total_steps": request.total_steps,
                    "files_checked": len(request.files_checked),
                    "relevant_files": len(request.relevant_files),
                    "thinking_confidence": request.confidence,
                    "analysis_focus": request.focus_areas or ["general"],
                }
            }
        )

        # Add thinking_complete field for final steps (test expects this)
        if not request.next_step_required:
            response_data["thinking_complete"] = True
            # Add complete_thinking summary (test expects this)
            response_data["complete_thinking"] = {
                "steps_completed": len(self.work_history),
                "final_confidence": request.confidence,
                "relevant_context": list(self.consolidated_findings.relevant_context),
                "key_findings": self.consolidated_findings.findings,
                "issues_identified": self.consolidated_findings.issues_found,
                "files_analyzed": list(self.consolidated_findings.relevant_files),
            }

        # Add thinking-specific completion message based on confidence
        if request.confidence == "certain":
            response_data["completion_message"] = (
                "Deep thinking analysis is complete with high certainty. "
                "All aspects have been thoroughly considered and conclusions are definitive."
            )
        elif not request.next_step_required:
            response_data["completion_message"] = (
                "Deep thinking analysis phase complete. Expert validation will provide additional insights and recommendations."
            )

        return response_data

    def should_skip_expert_analysis(self, request, consolidated_findings) -> bool:
        """
        ThinkDeep tool skips expert analysis when the CLI agent has "certain" confidence.
        """
        return request.confidence == "certain" and not request.next_step_required

    def get_completion_status(self) -> str:
        """ThinkDeep tools use thinking-specific status."""
        return "deep_thinking_complete_ready_for_implementation"

    def get_completion_data_key(self) -> str:
        """ThinkDeep uses 'complete_thinking' key."""
        return "complete_thinking"

    def get_final_analysis_from_request(self, request):
        """ThinkDeep tools use 'findings' field."""
        return request.findings

    def get_skip_expert_analysis_status(self) -> str:
        """Status when skipping expert analysis for certain confidence."""
        return "skipped_due_to_certain_thinking_confidence"

    def get_skip_reason(self) -> str:
        """Reason for skipping expert analysis."""
        return "Expressed 'certain' confidence in the deep thinking analysis - no additional validation needed"

    def get_completion_message(self) -> str:
        """Message for completion without expert analysis."""
        return "Deep thinking analysis complete with certain confidence. Proceed with implementation based on the analysis."

    def customize_expert_analysis_prompt(self, base_prompt: str, request, file_content: str = "") -> str:
        """
        Customize the expert analysis prompt for deep thinking validation
        """
        thinking_context = f"""
DEEP THINKING ANALYSIS VALIDATION

You are reviewing a comprehensive deep thinking analysis completed through systematic investigation.
Your role is to validate the thinking process, identify any gaps, challenge assumptions, and provide
additional insights or alternative perspectives.

ANALYSIS SCOPE:
- Problem Context: {self._get_problem_context(request)}
- Focus Areas: {', '.join(self._get_focus_areas(request))}
- Investigation Confidence: {request.confidence}
- Steps Completed: {request.step_number} of {request.total_steps}

THINKING SUMMARY:
{request.findings}

KEY INSIGHTS AND CONTEXT:
{', '.join(request.relevant_context) if request.relevant_context else 'No specific context identified'}

VALIDATION OBJECTIVES:
1. Assess the depth and quality of the thinking process
2. Identify any logical gaps, missing considerations, or flawed assumptions
3. Suggest alternative approaches or perspectives not considered
4. Validate the conclusions and recommendations
5. Provide actionable next steps for implementation

Be thorough but constructive in your analysis. Challenge the thinking where appropriate,
but also acknowledge strong insights and valid conclusions.
"""

        if file_content:
            thinking_context += f"\n\nFILE CONTEXT:\n{file_content}"

        return f"{thinking_context}\n\n{base_prompt}"

    def get_expert_analysis_instruction(self) -> str:
        """
        Return instructions for expert analysis specific to deep thinking validation
        """
        return (
            "DEEP THINKING ANALYSIS IS COMPLETE. You MUST now summarize and present ALL thinking insights, "
            "alternative approaches considered, risks and trade-offs identified, and final recommendations. "
            "Clearly prioritize the top solutions or next steps that emerged from the analysis. "
            "Provide concrete, actionable guidance based on the deep thinking—make it easy for the user to "
            "understand exactly what to do next and how to implement the best solution."
        )

    # Override hook methods to use stored request parameters for expert analysis

    def get_request_temperature(self, request) -> float:
        """Use stored temperature from initial request."""
        try:
            stored_params = self.stored_request_params
            if stored_params and stored_params.get("temperature") is not None:
                return stored_params["temperature"]
        except AttributeError:
            pass
        return super().get_request_temperature(request)

    def get_request_thinking_mode(self, request) -> str:
        """Use stored thinking mode from initial request."""
        try:
            stored_params = self.stored_request_params
            if stored_params and stored_params.get("thinking_mode") is not None:
                return stored_params["thinking_mode"]
        except AttributeError:
            pass
        return super().get_request_thinking_mode(request)

    def get_request_use_websearch(self, request) -> bool:
        """Use stored use_websearch from initial request."""
        try:
            stored_params = self.stored_request_params
            if stored_params and stored_params.get("use_websearch") is not None:
                return stored_params["use_websearch"]
        except AttributeError:
            pass
        return super().get_request_use_websearch(request)
    def get_request_use_assistant_model(self, request) -> bool:
        """Smart default for whether to call external expert analysis.

        Priority order:
        1) Respect explicit request.use_assistant_model when provided
        2) Tool-specific env override THINKDEEP_USE_ASSISTANT_MODEL_DEFAULT=true/false
        3) Global default from config.DEFAULT_USE_ASSISTANT_MODEL (defaults to true)
        4) Heuristic auto-mode as fallback:
           - If next_step_required is False AND any of these are true, return True:
             • confidence in {"high","very_high","almost_certain"}
             • >= 2 findings or any relevant_files present
             • step_number >= total_steps (final step) and findings length >= 200 chars
           - Otherwise False
        """
        # 1) Explicit request flag wins
        try:
            val = getattr(request, "use_assistant_model", None)
        except AttributeError:
            val = None
        if val is not None:
            return bool(val)

        # 2) Tool-specific env override
        import os
        env_default = os.getenv("THINKDEEP_USE_ASSISTANT_MODEL_DEFAULT")
        if env_default is not None:
            return env_default.strip().lower() == "true"

        # 3) Global default from config
        try:
            from config import DEFAULT_USE_ASSISTANT_MODEL
            return DEFAULT_USE_ASSISTANT_MODEL
        except Exception:
            pass

        # 4) Heuristic auto-mode as fallback
        try:
            final_step = bool(not request.next_step_required)
        except Exception:
            final_step = False
        try:
            conf = (request.confidence or "").lower()
        except Exception:
            conf = ""
        try:
            findings_text = request.findings or ""
        except Exception:
            findings_text = ""
        try:
            rel_files = request.relevant_files or []
        except Exception:
            rel_files = []
        try:
            step_no = int(request.step_number)
            total = int(request.total_steps)
        except Exception:
            step_no, total = 1, 1

        high_conf = conf in {"high", "very_high", "almost_certain"}
        rich_findings = len(findings_text) >= 200 or findings_text.count("\n") >= 2
        has_files = len(rel_files) > 0
        is_final = final_step or (step_no >= total)

        return is_final and (high_conf or has_files or rich_findings)


    def _get_problem_context(self, request) -> str:
        """Get problem context from request. Override for custom context handling."""
        try:
            return request.problem_context or "General analysis"
        except AttributeError:
            return "General analysis"

    def _get_focus_areas(self, request) -> list[str]:
        """Get focus areas from request. Override for custom focus area handling."""
        try:
            return request.focus_areas or ["comprehensive analysis"]
        except AttributeError:
            return ["comprehensive analysis"]

    def get_required_actions(self, step_number: int, confidence: str, findings: str, total_steps: int) -> list[str]:
        """
        Return required actions for the current thinking step.
        """
        actions = []

        if step_number == 1:
            actions.extend(
                [
                    "Begin systematic thinking analysis",
                    "Identify key aspects and assumptions to explore",
                    "Establish initial investigation approach",
                ]
            )
        elif confidence == "low":
            actions.extend(
                [
                    "Continue gathering evidence and insights",
                    "Test initial hypotheses",
                    "Explore alternative perspectives",
                ]
            )
        elif confidence == "medium":
            actions.extend(
                [
                    "Deepen analysis of promising approaches",
                    "Validate key assumptions",
                    "Consider implementation challenges",
                ]
            )
        elif confidence == "high":
            actions.extend(
                [
                    "Refine and validate key findings",
                    "Explore edge cases and limitations",
                    "Document assumptions and trade-offs",
                ]
            )
        elif confidence == "very_high":
            actions.extend(
                [
                    "Synthesize findings into cohesive recommendations",
                    "Validate conclusions against all evidence",
                    "Prepare comprehensive implementation guidance",
                ]
            )
        elif confidence == "almost_certain":
            actions.extend(
                [
                    "Finalize recommendations with high confidence",
                    "Document any remaining minor uncertainties",
                    "Prepare for expert analysis or implementation",
                ]
            )
        else:  # certain
            actions.append("Analysis complete - ready for implementation")

        return actions

    def should_call_expert_analysis(self, consolidated_findings, request=None) -> bool:
        """
        Determine if expert analysis should be called based on confidence and completion.
        """
        # Short-circuit: If assistant model is disabled, do NOT call expert analysis
        try:
            if request is not None and not self.get_request_use_assistant_model(request):
                return False
        except Exception:
            pass

        if request:
            try:
                # Don't call expert analysis if confidence is "certain"
                if request.confidence == "certain":
                    return False
            except AttributeError:
                pass

        # Call expert analysis if investigation is complete (when next_step_required is False)
        if request:
            try:
                return not request.next_step_required
            except AttributeError:
                pass

        # Fallback: call expert analysis if we have meaningful findings
        return (
            len(consolidated_findings.relevant_files) > 0
            or len(consolidated_findings.findings) >= 2
            or len(consolidated_findings.issues_found) > 0
        )

    def prepare_expert_analysis_context(self, consolidated_findings) -> str:
        """
        Prepare context for expert analysis specific to deep thinking.
        """
        context_parts = []

        context_parts.append("DEEP THINKING ANALYSIS SUMMARY:")
        context_parts.append(f"Steps completed: {len(consolidated_findings.findings)}")
        context_parts.append(f"Final confidence: {consolidated_findings.confidence}")

        if consolidated_findings.findings:
            context_parts.append("\nKEY FINDINGS:")
            for i, finding in enumerate(consolidated_findings.findings, 1):
                context_parts.append(f"{i}. {finding}")

        if consolidated_findings.relevant_context:
            context_parts.append(f"\nRELEVANT CONTEXT:\n{', '.join(consolidated_findings.relevant_context)}")

        # Get hypothesis from latest hypotheses entry if available
        if consolidated_findings.hypotheses:
            latest_hypothesis = consolidated_findings.hypotheses[-1].get("hypothesis", "")
            if latest_hypothesis:
                context_parts.append(f"\nFINAL HYPOTHESIS:\n{latest_hypothesis}")

        if consolidated_findings.issues_found:
            context_parts.append(f"\nISSUES IDENTIFIED: {len(consolidated_findings.issues_found)} issues")
            for issue in consolidated_findings.issues_found:
                context_parts.append(
                    f"- {issue.get('severity', 'unknown')}: {issue.get('description', 'No description')}"
                )

        return "\n".join(context_parts)

    def get_step_guidance_message(self, request) -> str:
        """
        Generate guidance for the next step in thinking analysis
        """
        if request.next_step_required:
            next_step_number = request.step_number + 1

            if request.confidence == "certain":
                guidance = (
                    f"Your thinking analysis confidence is CERTAIN. Consider if you truly need step {next_step_number} "
                    f"or if you should complete the analysis now with expert validation."
                )
            elif request.confidence == "almost_certain":
                guidance = (
                    f"Your thinking analysis confidence is ALMOST_CERTAIN. For step {next_step_number}, consider: "
                    f"finalizing recommendations, documenting any minor uncertainties, or preparing for implementation."
                )
            elif request.confidence == "very_high":
                guidance = (
                    f"Your thinking analysis confidence is VERY_HIGH. For step {next_step_number}, consider: "
                    f"synthesis of all findings, comprehensive validation, or creating implementation roadmap."
                )
            elif request.confidence == "high":
                guidance = (
                    f"Your thinking analysis confidence is HIGH. For step {next_step_number}, consider: "
                    f"exploring edge cases, documenting trade-offs, or stress-testing key assumptions."
                )
            elif request.confidence == "medium":
                guidance = (
                    f"Your thinking analysis confidence is MEDIUM. For step {next_step_number}, focus on: "
                    f"deepening insights, exploring alternative approaches, or gathering additional evidence."
                )
            else:  # low or exploring
                guidance = (
                    f"Your thinking analysis confidence is {request.confidence.upper()}. For step {next_step_number}, "
                    f"continue investigating: gather more evidence, test hypotheses, or explore different angles."
                )

            # Add specific thinking guidance based on progress
            if request.step_number == 1:
                guidance += (
                    " Consider: What are the key assumptions? What evidence supports or contradicts initial theories? "
                    "What alternative approaches exist?"
                )
            elif request.step_number >= request.total_steps // 2:
                guidance += (
                    " Consider: Synthesis of findings, validation of conclusions, identification of implementation "
                    "challenges, and preparation for expert analysis."
                )

            return guidance
        else:
            return "Thinking analysis is ready for expert validation and final recommendations."

    def format_final_response(self, assistant_response: str, request, **kwargs) -> dict:
        """
        Format the final response from the assistant for thinking analysis
        """
        response_data = {
            "thinking_analysis": assistant_response,
            "analysis_metadata": {
                "total_steps_completed": request.step_number,
                "final_confidence": request.confidence,
                "files_analyzed": len(request.relevant_files),
                "key_insights": len(request.relevant_context),
                "issues_identified": len(request.issues_found),
            },
        }

        # Add completion status
        if request.confidence == "certain":
            response_data["completion_status"] = "analysis_complete_with_certainty"
        else:
            response_data["completion_status"] = "analysis_complete_pending_validation"

        # UI summary for clients
        try:
            response_data["ui_summary"] = ui_build_summary(
                request,
                assistant_response,
                kwargs.get("continuation_id") if isinstance(kwargs, dict) else None,
                kwargs if isinstance(kwargs, dict) else None,
                tool_instance=self,
            )
        except Exception:
            pass

        return response_data

    def format_step_response(
        self,
        assistant_response: str,
        request,
        status: str = "pause_for_thinkdeep",
        continuation_id: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Format intermediate step responses for thinking workflow
        """
        response_data = super().format_step_response(assistant_response, request, status, continuation_id, **kwargs)

        # Add thinking-specific step guidance
        step_guidance = self.get_step_guidance_message(request)
        response_data["thinking_guidance"] = step_guidance

        # Add analysis progress indicators
        response_data["analysis_progress"] = {
            "step_completed": request.step_number,
            "remaining_steps": max(0, request.total_steps - request.step_number),
            "confidence_trend": request.confidence,
            "investigation_depth": "expanding" if request.next_step_required else "finalizing",
        }

        # UI summary for clients
        try:
            response_data["ui_summary"] = ui_build_summary(
                request,
                assistant_response,
                continuation_id,
                kwargs if isinstance(kwargs, dict) else None,
                tool_instance=self,
            )
        except Exception:
            pass

        return response_data

    # Required abstract methods from BaseTool
    def get_request_model(self):
        """Return the thinkdeep workflow-specific request model."""
        return ThinkDeepWorkflowRequest

    async def prepare_prompt(self, request) -> str:
        """Not used - workflow tools use execute_workflow()."""
        return ""  # Workflow tools use execute_workflow() directly
