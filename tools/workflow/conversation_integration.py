"""
Conversation Integration Mixin for Workflow Tools

This module provides conversation threading, turn management, and cross-tool
context transfer for workflow tools.

Key Features:
- Thread reconstruction and turn management
- Continuation offers for multi-step workflows
- Cross-tool context transfer
- Clean content extraction for conversation history
- Workflow metadata tracking
- Storage backend abstraction (memory/supabase/dual)
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConversationIntegrationMixin:
    """
    Mixin providing conversation integration for workflow tools.

    This class handles conversation threading, turn storage, and metadata
    management for multi-step workflows with continuation support.

    Updated to use storage factory pattern for Supabase integration.
    """

    # CRITICAL FIX: Removed stub _call_expert_analysis() method that was shadowing
    # the real implementation in ExpertAnalysisMixin due to Python's MRO.
    # The stub method (which just did 'pass' and returned None) was being called
    # instead of the real implementation because ConversationIntegrationMixin
    # comes before ExpertAnalysisMixin in BaseWorkflowMixin's inheritance list.

    # ================================================================================
    # Conversation Turn Storage
    # ================================================================================

    def store_conversation_turn(self, continuation_id: str, response_data: dict, request):
        """
        Store the conversation turn using storage factory pattern.
        Tools can override for custom memory storage.
        """
        # CRITICAL: Extract clean content for conversation history (exclude internal workflow metadata)
        clean_content = self._extract_clean_workflow_content_for_history(response_data)

        # CRITICAL FIX: Use cached storage backend to avoid creating 60+ instances
        from utils.conversation.threads import _get_storage_backend

        storage = _get_storage_backend()
        if not storage:
            logger.warning(f"{self.get_name()}: Storage backend not available for turn storage")
            return

        storage.add_turn(
            continuation_id=continuation_id,
            role="assistant",
            content=clean_content,  # Use cleaned content instead of full response_data
            tool_name=self.get_name(),
            files=self.get_request_relevant_files(request),
            images=self.get_request_images(request),
        )
    
    def _extract_clean_workflow_content_for_history(self, response_data: dict) -> str:
        """
        Extract clean content from workflow response suitable for conversation history.
        
        This method removes internal workflow metadata, continuation offers, and
        status information that should not appear when the conversation is
        reconstructed for expert models or other tools.
        
        Args:
            response_data: The full workflow response data
        
        Returns:
            str: Clean content suitable for conversation history storage
        """
        # Create a clean copy with only essential content for conversation history
        clean_data = {}
        
        # Include core content if present
        if "content" in response_data:
            clean_data["content"] = response_data["content"]
        
        # Include expert analysis if present (but clean it)
        if "expert_analysis" in response_data:
            expert_analysis = response_data["expert_analysis"]
            if isinstance(expert_analysis, dict):
                # Only include the actual analysis content, not metadata
                clean_expert = {}
                if "raw_analysis" in expert_analysis:
                    clean_expert["analysis"] = expert_analysis["raw_analysis"]
                elif "content" in expert_analysis:
                    clean_expert["analysis"] = expert_analysis["content"]
                if clean_expert:
                    clean_data["expert_analysis"] = clean_expert
        
        # Include findings/issues if present (core workflow output)
        if "complete_analysis" in response_data:
            complete_analysis = response_data["complete_analysis"]
            if isinstance(complete_analysis, dict):
                clean_complete = {}
                # Include essential analysis data without internal metadata
                for key in ["findings", "issues_found", "relevant_context", "insights"]:
                    if key in complete_analysis:
                        clean_complete[key] = complete_analysis[key]
                if clean_complete:
                    clean_data["analysis_summary"] = clean_complete
        
        # Include step information for context but remove internal workflow metadata
        if "step_number" in response_data:
            clean_data["step_info"] = {
                "step": response_data.get("step", ""),
                "step_number": response_data.get("step_number", 1),
                "total_steps": response_data.get("total_steps", 1),
            }
        
        # Exclude problematic fields that should never appear in conversation history:
        # - continuation_id (confuses LLMs with old IDs)
        # - status (internal workflow state)
        # - next_step_required (internal control flow)
        # - analysis_status (internal tracking)
        # - file_context (internal optimization info)
        # - required_actions (internal workflow instructions)
        
        return json.dumps(clean_data, indent=2, ensure_ascii=False)
    
    # ================================================================================
    # Workflow Metadata Management
    # ================================================================================
    
    def _add_workflow_metadata(self, response_data: dict, arguments: dict[str, Any]) -> None:
        """
        Add metadata (provider_used and model_used) to workflow response.
        
        This ensures workflow tools have the same metadata as regular tools,
        making it consistent across all tool types for tracking which provider
        and model were used for the response.
        
        Args:
            response_data: The response data dictionary to modify
            arguments: The original arguments containing model context
        """
        try:
            # Get model information from arguments (set by server.py)
            resolved_model_name = arguments.get("_resolved_model_name")
            model_context = arguments.get("_model_context")
            
            if resolved_model_name and model_context:
                # Extract provider information from model context
                provider = model_context.provider
                provider_name = provider.get_provider_type().value if provider else "unknown"
                
                # Create metadata dictionary
                metadata = {
                    "tool_name": self.get_name(),
                    "model_used": resolved_model_name,
                    "provider_used": provider_name,
                }
                
                # Preserve existing metadata and add workflow metadata
                if "metadata" not in response_data:
                    response_data["metadata"] = {}
                response_data["metadata"].update(metadata)
                
                logger.debug(
                    f"[WORKFLOW_METADATA] {self.get_name()}: Added metadata - "
                    f"model: {resolved_model_name}, provider: {provider_name}"
                )
            else:
                # Fallback - try to get model info from arguments directly
                # Don't re-validate the request as arguments may have been modified during execution
                model_name = arguments.get("model", "unknown")

                # Basic metadata without provider info
                metadata = {
                    "tool_name": self.get_name(),
                    "model_used": model_name,
                    "provider_used": "unknown",
                }

                # Preserve existing metadata and add workflow metadata
                if "metadata" not in response_data:
                    response_data["metadata"] = {}
                response_data["metadata"].update(metadata)

                logger.debug(
                    f"[WORKFLOW_METADATA] {self.get_name()}: Added fallback metadata - "
                    f"model: {model_name}, provider: unknown"
                )
        
        except Exception as e:
            # Don't fail the workflow if metadata addition fails
            logger.warning(f"[WORKFLOW_METADATA] {self.get_name()}: Failed to add metadata: {e}")
            # Still add basic metadata with tool name
            response_data["metadata"] = {"tool_name": self.get_name()}
    
    # ================================================================================
    # Work Completion Handling
    # ================================================================================
    
    async def handle_work_completion(self, response_data: dict, request, arguments: dict) -> dict:
        """
        Handle work completion logic - expert analysis decision and response building.
        """
        response_data[f"{self.get_name()}_complete"] = True

        # DEBUG: Log consolidated findings state
        print(f"[DEBUG_COMPLETION] Tool: {self.get_name()}")
        print(f"[DEBUG_COMPLETION] consolidated_findings.relevant_files: {len(self.consolidated_findings.relevant_files) if hasattr(self.consolidated_findings, 'relevant_files') else 'N/A'}")  # type: ignore
        print(f"[DEBUG_COMPLETION] consolidated_findings.findings: {len(self.consolidated_findings.findings) if hasattr(self.consolidated_findings, 'findings') else 'N/A'}")  # type: ignore
        print(f"[DEBUG_COMPLETION] requires_expert_analysis(): {self.requires_expert_analysis()}")  # type: ignore
        print(f"[DEBUG_COMPLETION] should_call_expert_analysis(): {self.should_call_expert_analysis(self.consolidated_findings, request)}")  # type: ignore
        print(f"[DEBUG_COMPLETION] should_skip_expert_analysis(): {self.should_skip_expert_analysis(request, self.consolidated_findings)}")  # type: ignore

        # Check if tool wants to skip expert analysis due to high certainty
        if self.should_skip_expert_analysis(request, self.consolidated_findings):  # type: ignore
            # Handle completion without expert analysis
            print(f"[DEBUG_COMPLETION] Skipping expert analysis (should_skip returned True)")
            completion_response = self.handle_completion_without_expert_analysis(request, self.consolidated_findings)  # type: ignore
            response_data.update(completion_response)
        elif self.requires_expert_analysis() and self.should_call_expert_analysis(self.consolidated_findings, request):  # type: ignore
            # Standard expert analysis path
            print(f"[DEBUG_COMPLETION] Calling expert analysis")
            response_data["status"] = "calling_expert_analysis"

            # DEBUG: Print to verify execution
            print(f"[DEBUG_EXPERT] About to call _call_expert_analysis for {self.get_name()}")
            print(f"[DEBUG_EXPERT] use_assistant_model={self.get_request_use_assistant_model(request)}")
            print(f"[DEBUG_EXPERT] consolidated_findings.findings count={len(self.consolidated_findings.findings)}")  # type: ignore

            # DIAGNOSTIC: Check method existence and type
            print(f"[DEBUG_MRO] _call_expert_analysis exists: {hasattr(self, '_call_expert_analysis')}")
            print(f"[DEBUG_MRO] _call_expert_analysis callable: {callable(getattr(self, '_call_expert_analysis', None))}")
            import inspect
            method = getattr(self, '_call_expert_analysis', None)
            if method:
                print(f"[DEBUG_MRO] _call_expert_analysis is coroutine function: {inspect.iscoroutinefunction(method)}")
                print(f"[DEBUG_MRO] _call_expert_analysis module: {method.__module__ if hasattr(method, '__module__') else 'unknown'}")
                print(f"[DEBUG_MRO] _call_expert_analysis qualname: {method.__qualname__ if hasattr(method, '__qualname__') else 'unknown'}")

            # DIAGNOSTIC: Check MRO
            print(f"[DEBUG_MRO] Class MRO: {[cls.__name__ for cls in self.__class__.__mro__]}")
            for cls in self.__class__.__mro__:
                if hasattr(cls, '_call_expert_analysis') and '_call_expert_analysis' in cls.__dict__:
                    print(f"[DEBUG_MRO] _call_expert_analysis defined in class: {cls.__name__}")
                    print(f"[DEBUG_MRO] Method from {cls.__name__}: {cls.__dict__['_call_expert_analysis']}")
                    break

            # Call expert analysis with timeout protection
            print(f"[DEBUG_EXPERT] About to await _call_expert_analysis...")
            import asyncio
            import os
            from config import TimeoutConfig
            # Use centralized timeout configuration (EXAI Fix #3 - 2025-10-21)
            timeout_secs = float(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", str(TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS)))
            try:
                expert_analysis = await asyncio.wait_for(
                    self._call_expert_analysis(arguments, request),
                    timeout=timeout_secs
                )
                print(f"[DEBUG_EXPERT] _call_expert_analysis completed successfully")
            except asyncio.TimeoutError:
                print(f"[DEBUG_EXPERT] CRITICAL: _call_expert_analysis timed out after {timeout_secs}s!")
                logger.error(f"Expert analysis timed out after {timeout_secs}s for {self.get_name()}")
                expert_analysis = {
                    "error": f"Expert analysis timed out after {timeout_secs} seconds",
                    "status": "analysis_timeout",
                    "raw_analysis": "",
                    "timeout_duration": f"{timeout_secs}s"
                }
            except Exception as e:
                print(f"[DEBUG_EXPERT] CRITICAL: _call_expert_analysis raised exception: {e}")
                logger.error(f"Expert analysis failed for {self.get_name()}: {e}", exc_info=True)
                expert_analysis = {
                    "error": f"Expert analysis failed: {str(e)}",
                    "status": "analysis_error",
                    "raw_analysis": ""
                }

            # DEBUG: Print result
            print(f"[DEBUG_EXPERT] _call_expert_analysis returned: {type(expert_analysis)}")
            print(f"[DEBUG_EXPERT] expert_analysis is None: {expert_analysis is None}")
            if expert_analysis:
                print(f"[DEBUG_EXPERT] expert_analysis keys: {expert_analysis.keys() if isinstance(expert_analysis, dict) else 'not a dict'}")

            # SAFETY CHECK: Ensure expert_analysis is never None
            if expert_analysis is None:
                print(f"[DEBUG_EXPERT] WARNING: expert_analysis is None! This should never happen!")
                import traceback
                expert_analysis = {
                    "error": "CRITICAL BUG: Expert analysis returned None instead of dict",
                    "status": "analysis_error",
                    "raw_analysis": f"The _call_expert_analysis() method returned None, which should be impossible based on the code. This indicates a serious bug. Tool: {self.get_name()}, use_assistant_model: {self.get_request_use_assistant_model(request)}, findings_count: {len(self.consolidated_findings.findings)}",  # type: ignore
                    "debug_info": {
                        "tool_name": self.get_name(),
                        "use_assistant_model": self.get_request_use_assistant_model(request),
                        "findings_count": len(self.consolidated_findings.findings),  # type: ignore
                        "relevant_files_count": len(self.consolidated_findings.relevant_files),  # type: ignore
                        "issues_found_count": len(self.consolidated_findings.issues_found),  # type: ignore
                    }
                }

            response_data["expert_analysis"] = expert_analysis
            
            # Handle special expert analysis statuses
            if isinstance(expert_analysis, dict) and expert_analysis.get("status") in [
                "files_required_to_continue",
                "investigation_paused",
                "refactoring_paused",
            ]:
                # Promote the special status to the main response
                special_status = expert_analysis["status"]
                response_data["status"] = special_status
                response_data["content"] = expert_analysis.get(
                    "raw_analysis", json.dumps(expert_analysis, ensure_ascii=False)
                )
                del response_data["expert_analysis"]
                
                # Update next steps for special status
                if special_status == "files_required_to_continue":
                    response_data["next_steps"] = "Provide the requested files and continue the analysis."
                else:
                    response_data["next_steps"] = expert_analysis.get(
                        "next_steps", "Continue based on expert analysis."
                    )
            elif isinstance(expert_analysis, dict) and expert_analysis.get("status") in ["analysis_error", "analysis_timeout"]:
                # Expert analysis failed or timed out - promote error status
                # BUG FIX: analysis_timeout was falling through to success path
                response_data["status"] = "error"
                response_data["content"] = expert_analysis.get("error", "Expert analysis failed")
                response_data["content_type"] = "text"
                if expert_analysis.get("status") == "analysis_timeout":
                    response_data["timeout_duration"] = "180s"
                del response_data["expert_analysis"]
            else:
                # Expert analysis was successfully executed - include expert guidance
                response_data["next_steps"] = self.get_completion_next_steps_message(expert_analysis_used=True)
                
                # Add expert analysis guidance as important considerations
                expert_guidance = self.get_expert_analysis_guidance()
                if expert_guidance:
                    response_data["important_considerations"] = expert_guidance
            
            # Prepare complete work summary
            work_summary = self._prepare_work_summary()
            response_data[f"complete_{self.get_name()}"] = {
                "initial_request": self.get_initial_request(request.step),
                "steps_taken": len(self.work_history),  # type: ignore
                "files_examined": list(self.consolidated_findings.files_checked),  # type: ignore
                "relevant_files": list(self.consolidated_findings.relevant_files),  # type: ignore
                "relevant_context": list(self.consolidated_findings.relevant_context),  # type: ignore
                "issues_found": self.consolidated_findings.issues_found,  # type: ignore
                "work_summary": work_summary,
            }
        else:
            # Tool doesn't require expert analysis or local work was sufficient
            if not self.requires_expert_analysis():
                # Tool is self-contained (like planner)
                response_data["status"] = f"{self.get_name()}_complete"
                response_data["next_steps"] = (
                    f"{self.get_name().capitalize()} work complete. Present results to the user."
                )
            else:
                # Local work was sufficient for tools that support expert analysis
                response_data["status"] = "local_work_complete"
                response_data["next_steps"] = (
                    f"Local {self.get_name()} complete with sufficient confidence. Present findings "
                    "and recommendations to the user based on the work results."
                )
        
        return response_data

