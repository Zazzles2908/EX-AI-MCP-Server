"""
Orchestration Mixin for Workflow Tools

This module provides the core workflow execution engine, step processing,
pause/resume logic, and progress tracking for workflow tools.

Key Features:
- Main workflow orchestration (execute_workflow)
- Step data processing and consolidation
- Backtracking support
- Work continuation and completion handling
- Progress tracking and breadcrumbs
"""

import json
import logging
from typing import Any, Optional

from mcp.types import TextContent

from tools.shared.base_models import ConsolidatedFindings
from utils.conversation_memory import create_thread
from utils.progress import send_progress

logger = logging.getLogger(__name__)

# MCP prompt size limit (from config)
MCP_PROMPT_SIZE_LIMIT = 100_000


class OrchestrationMixin:
    """
    Mixin providing workflow orchestration for workflow tools.
    
    This class handles the main workflow execution loop, step processing,
    and coordination between different workflow phases.
    """
    
    async def handle_work_completion(self, response_data: dict, request, arguments: dict) -> dict:
        """Handle work completion logic - expert analysis decision and response building."""
        pass
    
    # ================================================================================
    # Main Workflow Orchestration
    # ================================================================================
    
    async def execute_workflow(self, arguments: dict[str, Any]) -> list[TextContent]:
        """
        Main workflow orchestration following debug tool pattern.
        
        Comprehensive workflow implementation that handles all common patterns:
        1. Request validation and step management
        2. Continuation and backtracking support
        3. Step data processing and consolidation
        4. Tool-specific field mapping and customization
        5. Completion logic with optional expert analysis
        6. Generic "certain confidence" handling
        7. Step guidance and required actions
        8. Conversation memory integration
        """
        try:
            # Store arguments for access by helper methods
            self._current_arguments = arguments  # type: ignore
            
            # Validate request using tool-specific model
            request = self.get_workflow_request_model()(**arguments)
            
            # Emit progress start breadcrumb
            try:
                send_progress(f"{self.get_name()}: Starting step {request.step_number}/{request.total_steps} - {request.step[:80] if request.step else ''}")
            except Exception:
                pass
            
            # Validate step field size (basic validation for workflow instructions)
            # If step is too large, user should use shorter instructions and put details in files
            step_content = request.step
            if step_content and len(step_content) > MCP_PROMPT_SIZE_LIMIT:
                from tools.models import ToolOutput
                
                error_output = ToolOutput(
                    status="resend_prompt",
                    content="Step instructions are too long. Please use shorter instructions and provide detailed context via file paths instead.",
                    content_type="text",
                    metadata={"prompt_size": len(step_content), "limit": MCP_PROMPT_SIZE_LIMIT},
                )
                raise ValueError(f"MCP_SIZE_CHECK:{error_output.model_dump_json()}")
            
            # Validate file paths for security (same as base tool)
            # Use try/except instead of hasattr as per coding standards
            try:
                path_error = self.validate_file_paths(request)
                if path_error:
                    from tools.models import ToolOutput
                    
                    error_output = ToolOutput(
                        status="error",
                        content=path_error,
                        content_type="text",
                    )
                    return [TextContent(type="text", text=error_output.model_dump_json())]
            except AttributeError:
                # validate_file_paths method not available - skip validation
                pass
            
            # Try to validate model availability early for production scenarios
            # For tests, defer model validation to later to allow mocks to work
            # IMPORTANT: Only resolve model early when we actually plan to use expert analysis.
            try:
                should_resolve_model = False
                try:
                    # Resolve only if this tool uses expert analysis AND caller didn't disable it
                    if self.requires_expert_analysis() and self.get_request_use_assistant_model(request):
                        should_resolve_model = True
                except Exception:
                    # Be conservative if any check fails
                    should_resolve_model = True
                
                if should_resolve_model:
                    model_name, model_context = self._resolve_model_context(arguments, request)
                    # Store for later use
                    self._current_model_name = model_name  # type: ignore
                    self._model_context = model_context  # type: ignore
                else:
                    # Skip early model resolution for local-only flows (fewer moving parts)
                    self._current_model_name = None  # type: ignore
                    self._model_context = None  # type: ignore
            except ValueError as e:
                # Model resolution failed - in production this would be an error,
                # but for tests we defer to allow mocks to handle model resolution
                logger.debug(f"Early model validation failed, deferring to later: {e}")
                self._current_model_name = None  # type: ignore
                self._model_context = None  # type: ignore
            
            # Handle continuation
            continuation_id = request.continuation_id
            
            # Adjust total steps if needed
            if request.step_number > request.total_steps:
                request.total_steps = request.step_number
            
            # Create thread for first step
            if not continuation_id and request.step_number == 1:
                clean_args = {k: v for k, v in arguments.items() if k not in ["_model_context", "_resolved_model_name"]}
                continuation_id = create_thread(self.get_name(), clean_args)
                self.initial_request = request.step  # type: ignore
                # Allow tools to store initial description for expert analysis
                self.store_initial_issue(request.step)
            
            # Handle backtracking if requested
            backtrack_step = self.get_backtrack_step(request)
            if backtrack_step:
                self._handle_backtracking(backtrack_step)
            
            # Process work step - allow tools to customize field mapping
            step_data = self.prepare_step_data(request)
            try:
                send_progress(f"{self.get_name()}: Processed step data. Updating findings...")
            except Exception:
                pass
            
            # Store in history
            self.work_history.append(step_data)  # type: ignore
            
            # Update consolidated findings
            self._update_consolidated_findings(step_data)
            
            # Handle file context appropriately based on workflow phase
            self._handle_workflow_file_context(request, arguments)
            
            # Build response with tool-specific customization
            response_data = self.build_base_response(request, continuation_id)
            
            # If work is complete, handle completion logic
            if not request.next_step_required:
                try:
                    send_progress(f"{self.get_name()}: Finalizing - calling expert analysis if required...")
                except Exception:
                    pass
                response_data = await self.handle_work_completion(response_data, request, arguments)
            else:
                # Force Claude to work before calling tool again
                response_data = self.handle_work_continuation(response_data, request)
            
            # Allow tools to customize the final response
            response_data = self.customize_workflow_response(response_data, request)
            
            # Add metadata (provider_used and model_used) to workflow response
            self._add_workflow_metadata(response_data, arguments)
            
            # Attach per-call progress log into metadata for UI clients
            try:
                from utils.progress import get_progress_log as _get_progress_log
                prog = _get_progress_log()
                if prog:
                    response_data.setdefault("metadata", {})["progress"] = prog
            except Exception:
                pass
            
            try:
                send_progress(f"{self.get_name()}: Step {request.step_number}/{request.total_steps} complete")
            except Exception:
                pass
            
            # Store in conversation memory
            if continuation_id:
                self.store_conversation_turn(continuation_id, response_data, request)
            
            return [TextContent(type="text", text=json.dumps(response_data, indent=2, ensure_ascii=False))]
        
        except Exception as e:
            logger.error(f"Error in {self.get_name()} work: {e}", exc_info=True)
            error_data = {
                "status": f"{self.get_name()}_failed",
                "error": str(e),
                "step_number": arguments.get("step_number", 0),
            }
            
            # Add metadata to error responses too
            self._add_workflow_metadata(error_data, arguments)

            return [TextContent(type="text", text=json.dumps(error_data, indent=2, ensure_ascii=False))]

    # ================================================================================
    # Step Processing and Data Management
    # ================================================================================

    def prepare_step_data(self, request) -> dict:
        """
        Prepare step data from request. Tools can override to customize field mapping.
        """
        # Optional security enforcement per Cleanup/Upgrade prompts
        try:
            from config import SECURE_INPUTS_ENFORCED
            if SECURE_INPUTS_ENFORCED:
                from pathlib import Path
                from src.core.validation.secure_input_validator import SecureInputValidator

                repo_root = Path(__file__).resolve().parents[2]
                v = SecureInputValidator(repo_root=str(repo_root))

                # Normalize relevant_files within repo
                try:
                    req_files = self.get_request_relevant_files(request) or []
                except Exception:
                    req_files = []
                if req_files:
                    normalized_files: list[str] = []
                    for f in req_files:
                        p = v.normalize_and_check(f)
                        normalized_files.append(str(p))
                    # Update request to the normalized list
                    try:
                        request.relevant_files = normalized_files
                    except Exception:
                        pass

                # Validate images count and normalize path-based images
                try:
                    imgs = self.get_request_images(request) or []
                except Exception:
                    imgs = []
                v.validate_images([0] * len(imgs), max_images=10)
                normalized_images: list[str] = []
                for img in imgs:
                    if isinstance(img, str) and (img.startswith("data:") or "base64," in img):
                        normalized_images.append(img)
                    else:
                        p = v.normalize_and_check(img)
                        normalized_images.append(str(p))
                try:
                    request.images = normalized_images
                except Exception:
                    pass
        except Exception as e:
            # Raise clear error for caller visibility
            raise ValueError(f"[workflow:security] {e}")

        step_data = {
            "step": request.step,
            "step_number": request.step_number,
            "findings": request.findings,
            "files_checked": self.get_request_files_checked(request),
            "relevant_files": self.get_request_relevant_files(request),
            "relevant_context": self.get_request_relevant_context(request),
            "issues_found": self.get_request_issues_found(request),
            "confidence": self.get_request_confidence(request),
            "hypothesis": self.get_request_hypothesis(request),
            "images": self.get_request_images(request),
        }
        return step_data

    def build_base_response(self, request, continuation_id: str = None) -> dict:
        """
        Build the base response structure. Tools can override for custom response fields.
        """
        response_data = {
            "status": f"{self.get_name()}_in_progress",
            "step_number": request.step_number,
            "total_steps": request.total_steps,
            "next_step_required": request.next_step_required,
            f"{self.get_name()}_status": {
                "files_checked": len(self.consolidated_findings.files_checked),  # type: ignore
                "relevant_files": len(self.consolidated_findings.relevant_files),  # type: ignore
                "relevant_context": len(self.consolidated_findings.relevant_context),  # type: ignore
                "issues_found": len(self.consolidated_findings.issues_found),  # type: ignore
                "images_collected": len(self.consolidated_findings.images),  # type: ignore
                "current_confidence": self.get_request_confidence(request),
            },
        }
        # Optional: attach agentic routing hints without changing behavior
        try:
            from config import AGENTIC_ENGINE_ENABLED, ROUTER_ENABLED, CONTEXT_MANAGER_ENABLED
            if AGENTIC_ENGINE_ENABLED and (ROUTER_ENABLED or CONTEXT_MANAGER_ENABLED):
                from src.core.agentic.engine import AutonomousWorkflowEngine
                engine = AutonomousWorkflowEngine()
                # Build a minimal request-like structure for routing hints
                messages = []
                try:
                    # Prefer consolidated findings if available, else synthesize from request
                    initial = self.get_initial_request(request.step)
                    messages = [{"role": "user", "content": initial or (request.findings or "") }]
                except Exception:
                    pass
                decision = engine.decide({"messages": messages})
                response_data[f"{self.get_name()}_status"]["agentic_hints"] = {
                    "platform": decision.platform,
                    "estimated_tokens": decision.estimated_tokens,
                    "images_present": decision.images_present,
                    "task_type": decision.task_type,
                }
        except Exception:
            # Silently ignore hint failures; behavior must remain unchanged
            pass

        if continuation_id:
            response_data["continuation_id"] = continuation_id

        # Add file context information based on workflow phase
        embedded_content = self.get_embedded_file_content()
        reference_note = self.get_file_reference_note()
        processed_files = self.get_actually_processed_files()

        logger.debug(
            f"[WORKFLOW_FILES] {self.get_name()}: Building response - has embedded_content: {bool(embedded_content)}, has reference_note: {bool(reference_note)}"
        )

        # Prioritize embedded content over references for final steps
        if embedded_content:
            # Final step - include embedded file information
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Adding fully_embedded file context")
            response_data["file_context"] = {
                "type": "fully_embedded",
                "files_embedded": len(processed_files),
                "context_optimization": "Full file content embedded for expert analysis",
            }
        elif reference_note:
            # Intermediate step - include file reference note
            logger.debug(f"[WORKFLOW_FILES] {self.get_name()}: Adding reference_only file context")
            response_data["file_context"] = {
                "type": "reference_only",
                "note": reference_note,
                "context_optimization": "Files referenced but not embedded to preserve Claude's context window",
            }

        # Provide a standard next_call skeleton for clients and tests expecting it.
        # Only include continuation_id inside arguments when provided (omit when None).
        try:
            next_args = {
                "step": getattr(request, "step", None),
                "step_number": getattr(request, "step_number", None),
                "total_steps": getattr(request, "total_steps", None),
                "next_step_required": getattr(request, "next_step_required", None),
            }
            if continuation_id:
                next_args["continuation_id"] = continuation_id
            response_data["next_call"] = {"tool": self.get_name(), "arguments": next_args}
        except Exception:
            # Non-fatal; keep legacy behavior if request lacks attributes
            pass

        return response_data

    # ================================================================================
    # Work Continuation and Completion
    # ================================================================================

    def handle_work_continuation(self, response_data: dict, request) -> dict:
        """
        Handle work continuation - force pause and provide guidance.
        """
        response_data["status"] = f"pause_for_{self.get_name()}"
        response_data[f"{self.get_name()}_required"] = True

        # Get tool-specific required actions
        required_actions = self.get_required_actions(
            request.step_number, self.get_request_confidence(request), request.findings, request.total_steps
        )
        response_data["required_actions"] = required_actions

        # Generate step guidance
        response_data["next_steps"] = self.get_step_guidance_message(request)

        # Provide explicit auto-continue hints for orchestrators/clients
        try:
            next_step = int(request.step_number) + 1
        except Exception:
            next_step = None
        response_data["continuation_required"] = True
        response_data["continuation_available"] = True
        if next_step is not None:
            response_data["next_step_number"] = next_step
        # Include a minimal next_call skeleton clients can use directly
        try:
            cont_id = self.get_request_continuation_id(request)
        except Exception:
            cont_id = None
        response_data["next_call"] = {
            "tool": self.get_name(),
            "arguments": {
                "step": f"Continue with step {next_step} as per required actions.",
                "step_number": next_step or (request.step_number + 1),
                "total_steps": request.total_steps,
                "next_step_required": next_step is not None and next_step < (getattr(request, 'total_steps', 2) or 2),
                "findings": "Summarize new insights and evidence from the required actions.",
                **({"continuation_id": cont_id} if cont_id else {}),
            },
        }

        return response_data

    def should_skip_expert_analysis(self, request, consolidated_findings) -> bool:
        """
        Determine if expert analysis should be skipped due to high certainty.

        Default: False (always call expert analysis)
        Override in tools like debug to check for "certain" confidence.
        """
        return False

    def handle_completion_without_expert_analysis(self, request, consolidated_findings) -> dict:
        """
        Handle completion when skipping expert analysis.

        Tools can override this for custom high-confidence completion handling.
        Default implementation provides generic response.
        """
        from tools.workflow.request_accessors import RequestAccessorMixin

        # Use accessor methods if available
        if isinstance(self, RequestAccessorMixin):
            work_summary = self.prepare_work_summary()
            continuation_id = self.get_request_continuation_id(request)

            response_data = {
                "status": self.get_completion_status(),
                f"complete_{self.get_name()}": {
                    "initial_request": self.get_initial_request(request.step),
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

            if continuation_id:
                response_data["continuation_id"] = continuation_id

            return response_data
        else:
            # Fallback for tools that don't use RequestAccessorMixin
            return {
                "status": "completion_without_expert",
                "skip_expert_analysis": True,
            }

    # ================================================================================
    # Backtracking and Findings Management
    # ================================================================================

    def _handle_backtracking(self, backtrack_step: int):
        """Handle backtracking to a previous step"""
        # Remove findings after the backtrack point
        self.work_history = [s for s in self.work_history if s["step_number"] < backtrack_step]  # type: ignore
        # Reprocess consolidated findings
        self._reprocess_consolidated_findings()

    def _update_consolidated_findings(self, step_data: dict):
        """Update consolidated findings with new step data"""
        self.consolidated_findings.files_checked.update(step_data.get("files_checked", []))  # type: ignore
        self.consolidated_findings.relevant_files.update(step_data.get("relevant_files", []))  # type: ignore
        self.consolidated_findings.relevant_context.update(step_data.get("relevant_context", []))  # type: ignore
        self.consolidated_findings.findings.append(f"Step {step_data['step_number']}: {step_data['findings']}")  # type: ignore
        if step_data.get("hypothesis"):
            self.consolidated_findings.hypotheses.append(  # type: ignore
                {
                    "step": step_data["step_number"],
                    "hypothesis": step_data["hypothesis"],
                    "confidence": step_data["confidence"],
                }
            )
        if step_data.get("issues_found"):
            self.consolidated_findings.issues_found.extend(step_data["issues_found"])  # type: ignore
        if step_data.get("images"):
            self.consolidated_findings.images.extend(step_data["images"])  # type: ignore
        # Update confidence to latest value from this step
        if step_data.get("confidence"):
            self.consolidated_findings.confidence = step_data["confidence"]  # type: ignore

    def _reprocess_consolidated_findings(self):
        """Reprocess consolidated findings after backtracking"""
        self.consolidated_findings = ConsolidatedFindings()  # type: ignore
        for step in self.work_history:  # type: ignore
            self._update_consolidated_findings(step)

    def _prepare_work_summary(self) -> str:
        """Prepare a comprehensive summary of the work"""
        summary_parts = [
            f"=== {self.get_name().upper()} WORK SUMMARY ===",
            f"Total steps: {len(self.work_history)}",  # type: ignore
            f"Files examined: {len(self.consolidated_findings.files_checked)}",  # type: ignore
            f"Relevant files identified: {len(self.consolidated_findings.relevant_files)}",  # type: ignore
            f"Methods/functions involved: {len(self.consolidated_findings.relevant_context)}",  # type: ignore
            f"Issues found: {len(self.consolidated_findings.issues_found)}",  # type: ignore
            "",
            "=== WORK PROGRESSION ===",
        ]

        for finding in self.consolidated_findings.findings:  # type: ignore
            summary_parts.append(finding)

        if self.consolidated_findings.hypotheses:  # type: ignore
            summary_parts.extend(
                [
                    "",
                    "=== HYPOTHESIS EVOLUTION ===",
                ]
            )
            for hyp in self.consolidated_findings.hypotheses:  # type: ignore
                summary_parts.append(f"Step {hyp['step']} ({hyp['confidence']} confidence): {hyp['hypothesis']}")

        if self.consolidated_findings.issues_found:  # type: ignore
            summary_parts.extend(
                [
                    "",
                    "=== ISSUES IDENTIFIED ===",
                ]
            )
            for issue in self.consolidated_findings.issues_found:  # type: ignore
                severity = issue.get("severity", "unknown")
                description = issue.get("description", "No description")
                summary_parts.append(f"[{severity.upper()}] {description}")

        return "\n".join(summary_parts)

