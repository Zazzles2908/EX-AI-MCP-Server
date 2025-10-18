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

    Note: handle_work_completion() is implemented in ConversationIntegrationMixin.
    We don't override it here to avoid MRO conflicts.
    """

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

            # AGENTIC ENHANCEMENT: Check for early termination
            # Allow tools to complete early if goal achieved with high confidence
            if request.next_step_required:
                should_terminate, termination_reason = self.should_terminate_early(request)
                if should_terminate:
                    logger.info(f"{self.get_name()}: Early termination triggered - {termination_reason}")
                    request.next_step_required = False
                    # Add termination info to response
                    self.early_termination_reason = termination_reason  # type: ignore

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
                # AUTO-EXECUTION: Continue internally instead of forcing pause
                try:
                    send_progress(f"{self.get_name()}: Auto-executing next step...")
                except Exception:
                    pass
                response_data = await self._auto_execute_next_step(response_data, request, arguments)
            
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

            # DIAGNOSTIC: Log before JSON serialization
            logger.info(f"[SERIALIZATION_DEBUG] About to serialize response_data for {self.get_name()}")
            logger.info(f"[SERIALIZATION_DEBUG] response_data type: {type(response_data)}")
            logger.info(f"[SERIALIZATION_DEBUG] response_data keys: {response_data.keys() if isinstance(response_data, dict) else 'not a dict'}")

            # DIAGNOSTIC: Try JSON serialization with detailed error handling
            try:
                json_str = json.dumps(response_data, indent=2, ensure_ascii=False)
                logger.info(f"[SERIALIZATION_DEBUG] JSON serialization successful, length: {len(json_str)}")
            except Exception as json_err:
                logger.error(f"[SERIALIZATION_DEBUG] JSON serialization FAILED: {json_err}", exc_info=True)
                logger.error(f"[SERIALIZATION_DEBUG] response_data content: {response_data}")
                # Try to identify non-serializable objects
                for key, value in response_data.items():
                    try:
                        json.dumps({key: value})
                    except Exception as key_err:
                        logger.error(f"[SERIALIZATION_DEBUG] Non-serializable key '{key}': type={type(value)}, error={key_err}")
                raise

            logger.info(f"[SERIALIZATION_DEBUG] About to create TextContent and return")
            result = [TextContent(type="text", text=json_str)]
            logger.info(f"[SERIALIZATION_DEBUG] TextContent created, about to return")
            return result
        
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
        # Agentic routing hints removed - was disabled by default and added unnecessary complexity

        if continuation_id:
            response_data["continuation_id"] = continuation_id

        # AGENTIC ENHANCEMENT: Add early termination reason if applicable
        if hasattr(self, 'early_termination_reason') and self.early_termination_reason:
            response_data["early_termination"] = True
            response_data["early_termination_reason"] = self.early_termination_reason

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
                "context_optimization": "Files referenced but not embedded to preserve the AI assistant's context window",
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

    async def _auto_execute_next_step(self, response_data: dict, request, arguments: dict):
        """
        Auto-execute the next step internally without forcing a pause.
        This replaces the forced pause mechanism with seamless auto-execution.
        """
        MAX_AUTO_STEPS = 10  # Reasonable limit to prevent runaway execution

        # Check if we've exceeded max steps
        if request.step_number >= MAX_AUTO_STEPS:
            logger.info(f"{self.get_name()}: Reached max auto-steps ({MAX_AUTO_STEPS}), completing workflow")
            request.next_step_required = False
            return await self.handle_work_completion(response_data, request, arguments)

        # Read relevant files internally
        file_contents = self._read_relevant_files(request)

        # Generate next step instructions based on required actions
        required_actions = self.get_required_actions(
            request.step_number, self.get_request_confidence(request), request.findings, request.total_steps
        )
        next_instructions = f"Continue investigation: {', '.join(required_actions)}"

        # Create next request data
        next_step_number = request.step_number + 1
        next_request_data = arguments.copy()
        next_request_data.update({
            "step_number": next_step_number,
            "step": next_instructions,
            "findings": self._consolidate_current_findings(),
            "embedded_file_contents": file_contents,
            "continuation_id": response_data.get("continuation_id")
        })

        # Create next request object
        try:
            next_request = self.get_workflow_request_model()(**next_request_data)
        except Exception as e:
            logger.error(f"{self.get_name()}: Failed to create next request: {e}")
            # Fall back to completion on error
            request.next_step_required = False
            return await self.handle_work_completion(response_data, request, arguments)

        # Process next step
        step_data = self.prepare_step_data(next_request)
        self.work_history.append(step_data)
        self._update_consolidated_findings(step_data)

        # Check if we should continue or complete
        if self._should_continue_execution(next_request):
            # Recursively continue auto-execution
            logger.info(f"{self.get_name()}: Continuing auto-execution (step {next_step_number})")
            response_data["status"] = f"{self.get_name()}_auto_executing"
            response_data["auto_execution_step"] = next_step_number
            return await self._auto_execute_next_step(response_data, next_request, next_request_data)
        else:
            # Complete the workflow
            logger.info(f"{self.get_name()}: Auto-execution complete, finalizing")
            next_request.next_step_required = False
            return await self.handle_work_completion(response_data, next_request, next_request_data)

    def _read_relevant_files(self, request) -> dict:
        """Read all relevant files internally and return their contents."""
        file_contents = {}
        relevant_files = self.get_request_relevant_files(request) or []

        for file_path in relevant_files:
            try:
                content = self._read_file_content(file_path)
                file_contents[file_path] = content
                logger.debug(f"{self.get_name()}: Read file {file_path} ({len(content)} chars)")
            except Exception as e:
                logger.warning(f"{self.get_name()}: Failed to read {file_path}: {e}")
                file_contents[file_path] = f"Error reading file: {str(e)}"

        return file_contents

    def _read_file_content(self, file_path: str) -> str:
        """Read a single file with proper encoding handling."""
        from pathlib import Path
        try:
            return Path(file_path).read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                return Path(file_path).read_text(encoding='latin-1')
            except Exception as e:
                raise Exception(f"Failed to read file with any encoding: {e}")
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")

    def _consolidate_current_findings(self) -> str:
        """Consolidate all findings from work history into a summary."""
        if not hasattr(self, 'work_history') or not self.work_history:
            return ""

        findings_parts = []
        for step in self.work_history:
            if step.get("findings"):
                findings_parts.append(f"Step {step.get('step_number', '?')}: {step['findings']}")

        return " | ".join(findings_parts) if findings_parts else ""

    def _should_continue_execution(self, request) -> bool:
        """Determine if auto-execution should continue."""
        # Check confidence level
        confidence = self.get_request_confidence(request)
        if confidence in ["certain", "very_high", "almost_certain"]:
            logger.info(f"{self.get_name()}: High confidence ({confidence}), stopping auto-execution")
            return False

        # Check information sufficiency
        try:
            assessment = self.assess_information_sufficiency(request)
            if assessment.get("sufficient"):
                logger.info(f"{self.get_name()}: Information sufficient, stopping auto-execution")
                return False
        except Exception as e:
            logger.debug(f"{self.get_name()}: Could not assess sufficiency: {e}")

        # Continue execution
        return True

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

