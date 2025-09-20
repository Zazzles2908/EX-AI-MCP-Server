"""
OrchestrateAuto tool - v0.2 lightweight multi-tool orchestrator

Goal: Given a natural prompt, infer and execute a small plan using existing Zen tools
with plug-and-play defaults. This MVP focuses on orchestrating the Analyze workflow
in two steps, automatically filling required fields (model, step metadata, files).

Future iterations will support tool-introspection, model-driven planning, and
multi-tool routing (codereview, testgen, tracer, etc.).
"""

from __future__ import annotations

import os
import json
import logging
from typing import Any, Optional, Literal

from pydantic import Field

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class OrchestrateRequest(ToolRequest):
    """Request model for OrchestrateAuto tool (v0.2)

    Fields:
    - user_prompt: free-form instruction describing what to do
    - relevant_files: optional absolute paths; if missing, basic heuristics infer a small set
    - step_budget: max steps to execute (v0.2 supports 1-3)
    - dry_run: if true, return the plan only (no execution)
    """

    user_prompt: str = Field(..., description="High-level instruction. The orchestrator infers steps and tools.")
    tool: Literal["analyze", "codereview", "debug", "testgen", "refactor", "tracer", "secaudit", "precommit", "chat", "kimi_multi_file_chat"] | None = Field(
        default=None,
        description="Optional tool to run (default inferred). When omitted, orchestrator picks based on prompt.",
    )
    relevant_files: list[str] | None = Field(
        default=None,
        description="Optional absolute paths to relevant files. If not provided, the tool infers a small set.",
    )
    step_budget: int = Field(
        default=2, description="Max steps to execute. v0.2 supports 1-3 steps depending on intent."
    )
    # Optional pass-throughs for analyze
    analysis_type: Literal["architecture", "performance", "security", "quality", "general"] | None = Field(
        default=None, description="Optional analysis type to pass through to analyze (default general)."
    )
    output_format: Literal["summary", "detailed", "actionable"] | None = Field(
        default=None, description="Optional output format to pass through to analyze (default step-based)."
    )
    # Optional pass-throughs for codereview
    review_type: Literal["full", "security", "performance", "quick"] | None = Field(
        default=None, description="Optional codereview review_type when tool='codereview' (default full)."
    )
    focus_on: Optional[str] = Field(
        default=None, description="Optional codereview focus area when tool='codereview'."
    )
    dry_run: bool = Field(default=False, description="If true, plan only; do not execute underlying tools.")


class OrchestrateAutoTool(BaseTool):
    """v0.2 Orchestrator that infers intent and executes a small multi-step plan.

    Behavior:
    - Builds a minimal plan to run the inferred tool for up to 3 steps
    - Auto-fills model and file context; auto-enables websearch when useful
    - Emits consolidated summary and guidance
    """

    def get_name(self) -> str:
        return "orchestrate_auto"

    def get_description(self) -> str:
        return (
            "AUTO-ORCHESTRATOR v0.2 - Given a natural prompt, infer intent, create a short plan, and execute "
            "tools with required fields auto-filled. Supports multi-tool routing (lightweight heuristics), "
            "up to 3 steps, auto websearch opt-in, and file-extraction pre-steps when appropriate."
        )

    def get_system_prompt(self) -> str:
        # Not used for MVP (we do not call an LLM within this tool yet)
        return ""

    def requires_model(self) -> bool:
        # The tool itself does not call a model directly in the MVP
        return False

    def get_request_model(self):
        return OrchestrateRequest

    def get_input_schema(self) -> dict[str, Any]:
        # Provide optional model for downstream tools; respect auto-mode requirements
        return {
            "type": "object",
            "properties": {
                "user_prompt": {
                    "type": "string",
                    "description": "High-level instruction. The orchestrator infers steps and tools.",
                },
                "relevant_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional absolute paths to relevant files. If not provided, the tool infers a small set.",
                },
                "step_budget": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3,
                    "default": 2,
                    "description": "Max steps to execute (1-3). v0.2 enables up to 3 with actionable step.",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, plan only; do not execute underlying tools.",
                },
                # Optional pass-throughs for analyze tool
                "analysis_type": {
                    "type": "string",
                    "enum": ["architecture", "performance", "security", "quality", "general"],
                    "description": "Optional analysis type to pass through to analyze (default general)",
                },
                "output_format": {
                    "type": "string",
                    "enum": ["summary", "detailed", "actionable"],
                    "description": "Optional output format to pass through to analyze (default step-based)",
                },
                # Let callers optionally override model; tool will fallback to env default
                "model": self.get_model_field_schema(),
                "continuation_id": {
                    "type": "string",
                    "description": "Continuation ID for conversation carry-over across orchestrated steps.",
                },
            },
            "required": ["user_prompt"] + (["model"] if self.is_effective_auto_mode() else []),
        }


    async def prepare_prompt(self, request) -> str:
        """Satisfy BaseTool's abstract interface.

        MVP orchestrator does not call a model directly; return a minimal
        synthesized string using the provided user prompt when available.
        """
        try:
            user_prompt = getattr(request, "user_prompt", None)
            if user_prompt is None and isinstance(request, dict):
                user_prompt = request.get("user_prompt")
        except Exception:
            user_prompt = None
        user_prompt = (user_prompt or "").strip()
        return f"OrchestrateAuto v0.2 request: {user_prompt}" if user_prompt else "OrchestrateAuto v0.2 request"

    # ---------------------
    # Execution
    # ---------------------

    async def execute(self, arguments: dict[str, Any]) -> list:
        """Plan and (optionally) execute a two-step analyze workflow.

        Returns a single consolidated text content describing the plan, any execution results,
        and suggested next steps.
        """
        # Validate request
        RequestModel = self.get_request_model()
        try:
            req = RequestModel.model_validate(arguments)
        except Exception as e:
            return [
                {
                    "type": "text",
                    "text": f"Invalid request for orchestrate_auto: {type(e).__name__}: {e}",
                }
            ]

        # Resolve model for downstream tools
        model_name = arguments.get("model") or os.getenv("ORCHESTRATOR_DEFAULT_MODEL") or "glm-4.5-flash"

        # Infer relevant files if not provided
        relevant_files = self._ensure_abs_paths(req.relevant_files) if req.relevant_files else self._infer_relevant_files()

        # Descriptor-driven validation of first-step requirements for selected tool
        selected_tool = (arguments.get("tool") or req.tool or "analyze").strip().lower()
        registry = ToolRegistry()
        registry.build_tools()
        descriptors = {}
        try:
            descriptors = registry.list_descriptors()
        except Exception:
            descriptors = {}
        first_step_reqs = []
        try:
            first_step_reqs = (
                descriptors.get(selected_tool, {})
                .get("annotations", {})
                .get("first_step_required_fields", [])
            )
        except Exception:
            first_step_reqs = []

        # Validate minimally required context for first step based on descriptor
        if "relevant_files" in first_step_reqs and not relevant_files:
            guidance = (
                "OrchestrateAuto could not infer any relevant files. Please provide at least one FULL absolute path "
                "to a file or directory under your repository in the 'relevant_files' parameter. Example: \n"
                f"  - {os.path.join(os.getcwd(), 'zen-mcp-server', 'server.py')}\n"
                f"  - {os.path.join(os.getcwd(), 'zen-mcp-server')} (directory)"
            )
            return [{"type": "text", "text": guidance}]

        # Select tool: explicit or heuristic (v0.2)
        selected_tool = (arguments.get("tool") or req.tool or "").strip().lower()
        if not selected_tool:
            selected_tool = self._infer_tool_from_prompt(req.user_prompt)
        if selected_tool not in {"analyze", "codereview", "debug", "testgen", "refactor", "tracer", "secaudit", "precommit", "chat"}:
            selected_tool = "analyze"

        # Descriptors already loaded above; reuse for plan construction
        # (avoid redundant registry.build_tools()/list_descriptors() calls)

        # Build simple plan: run selected workflow (multi-tool aware) for up to 3 steps
        plan = [
            {
                "tool": selected_tool,
                "step_number": 1,
                "description": f"Kick off {selected_tool} with specified/inferred files. Report goals and plan.",
            }
        ]
        if req.step_budget >= 2:
            plan.append(
                {
                    "tool": selected_tool,
                    "step_number": 2,
                    "description": f"Summarize concrete findings and early recommendations ({selected_tool}).",
                }
            )
        if req.step_budget >= 3 and selected_tool in {"analyze", "codereview", "secaudit", "debug"}:
            plan.append(
                {
                    "tool": selected_tool,
                    "step_number": 3,
                    "description": f"Actionable next steps or quick fixes ({selected_tool}).",
                }
            )

        # Dry run: return only plan preview (with basic metadata)
        if req.dry_run:
            return [
                {
                    "type": "text",
                    "text": self._format_plan_only(req.user_prompt, model_name, relevant_files, plan),
                    "status": "plan_preview",
                    "next_steps": "Run with dry_run=false to execute the plan.",
                    "continuation_id": arguments.get("continuation_id"),
                }
            ]

        # Auto pre-step: file extract via Kimi if prompt implies and allowed
        if self._should_do_file_extract(req.user_prompt, relevant_files):
            try:
                from tools.kimi_upload import KimiUploadAndExtractTool
                up = KimiUploadAndExtractTool()
                # As we don't have paths yet, this is a guided message to user to attach files next
                # Keep it conservative: we only inform; do not block flow
                guidance_msg = "Consider using kimi_upload_and_extract to ingest your files; orchestrator detected a file-oriented request."
            except Exception:
                guidance_msg = None
        else:
            guidance_msg = None

        # Execute the plan via ToolRegistry
        registry = ToolRegistry()
        registry.build_tools()

        outputs: list[str] = []
        guidance: list[str] = []
        cont_id = arguments.get("continuation_id")

        for step in plan:
            tool_name = step["tool"]
            try:
                tool_impl = registry.get_tool(tool_name)
            except Exception as e:
                outputs.append(f"Failed to load tool '{tool_name}': {e}")
                break

            step_num = step["step_number"]
            total_steps = max(step_num, min(req.step_budget, 2))

            # Prepare minimal valid payloads for workflow tools (analyze, codereview)
            if step_num == 1:
                step_text = f"Start {tool_name}: {req.user_prompt}"
                args = {
                    "model": model_name,
                    "step": step_text,
                    "step_number": 1,
                    "total_steps": total_steps,
                    "next_step_required": total_steps > 1,
                    "findings": "Plan initial investigation and identify target files.",
                    "relevant_files": relevant_files,
                    "files_checked": [],
                }
                # Analyze-specific pass-throughs
                if tool_name == "analyze":
                    args["analysis_type"] = arguments.get("analysis_type") or "general"
                    args["output_format"] = arguments.get("output_format") or "summary"
                # Codereview-specific optional pass-throughs
                if tool_name == "codereview":
                    if arguments.get("review_type"):
                        args["review_type"] = arguments["review_type"]
                    if arguments.get("focus_on"):
                        args["focus_on"] = arguments["focus_on"]
            else:  # step 2
                args = {
                    "model": model_name,
                    "step": f"Report concrete findings and recommendations based on investigation ({tool_name}).",
                    "step_number": 2,
                    "total_steps": total_steps,
                    "next_step_required": False,
                    "findings": (
                        "Summarized findings: initial goals reviewed; files examined; next actions identified."
                    ),
                    "relevant_files": relevant_files,
                    "files_checked": relevant_files,
                }
                if tool_name == "analyze":
                    args["analysis_type"] = arguments.get("analysis_type") or "general"
                    args["output_format"] = arguments.get("output_format") or "actionable"

            if cont_id:
                args["continuation_id"] = cont_id

            # Execute workflow step
            try:
                # Auto-enable websearch if intent suggests
                if "use_websearch" not in args:
                    args["use_websearch"] = self._should_enable_websearch(req.user_prompt)
                result_chunks = await tool_impl.execute(args)
                # Render full output for visibility
                rendered = self._render_chunks(result_chunks)
                outputs.append(f"[{tool_name} step {step_num}]\n{rendered}")
                if guidance_msg:
                    outputs.append(f"[hint] {guidance_msg}")

                # Try to parse JSON response to extract continuation_id and next_steps
                try:
                    # Use the first text chunk as JSON payload
                    first_text = None
                    if result_chunks:
                        ch0 = result_chunks[0]
                        if isinstance(ch0, dict):
                            first_text = ch0.get("text")
                        else:
                            first_text = getattr(ch0, "text", None)
                    if first_text:
                        data = json.loads(first_text)
                        # Capture guidance
                        ns = data.get("next_steps")
                        if ns:
                            guidance.append(f"Step {step_num}: {ns}")
                        # Update continuation id for subsequent steps when not provided initially
                        cid = data.get("continuation_id")
                        if cid:
                            cont_id = cid
                except Exception:
                    # Non-JSON or unexpected structure; skip extraction but continue
                    pass
            except Exception as e:
                outputs.append(f"{tool_name} step {step_num} failed: {type(e).__name__}: {e}")
                break

        final_text = self._format_consolidated_output(
            req.user_prompt, model_name, relevant_files, plan, outputs, guidance
        )
        return [{
            "type": "text",
            "text": final_text,
            "status": "orchestration_complete",
            "next_steps": "Review results and consider next steps.",
            "continuation_id": cont_id,
        }]
    def _infer_tool_from_prompt(self, text: str) -> str:
        """Heuristic intent routing for v0.2 (no model call, safe).
        Returns one of: analyze, codereview, debug, testgen, refactor, tracer, secaudit, precommit, chat
        """
        t = (text or "").lower()
        # Very lightweight patterns; prefer conservative routing to analyze
        if any(k in t for k in ["bug", "error", "traceback", "stacktrace", "failure", "repro"]):
            return "debug"
        if any(k in t for k in ["test", "unit test", "pytest", "coverage", "mock"]):
            return "testgen"
        if any(k in t for k in ["refactor", "rename", "extract method", "clean up", "cleanup"]):
            return "refactor"
        if any(k in t for k in ["security", "owasp", "vuln", "xss", "sql injection", "secrets"]):
            return "secaudit"
        if any(k in t for k in ["review", "code review", "diff", "pull request", "pr review"]):
            return "codereview"
        if any(k in t for k in ["trace", "call chain", "entry point", "dependencies"]):
            return "tracer"
        if any(k in t for k in ["precommit", "pre-commit", "pre commit", "commit checks"]):
            return "precommit"
        if any(k in t for k in ["chat", "ask", "explain", "summarize"]):
            return "chat"
        return "analyze"

    # ---------------------
    # Helpers
    # ---------------------
    def _should_enable_websearch(self, text: str) -> bool:
        t = (text or "").lower()
        if os.getenv("EX_WEBSEARCH_ENABLED", "true").lower() == "false":
            return False
        # Default on if EX_WEBSEARCH_DEFAULT_ON=true
        default_on = os.getenv("EX_WEBSEARCH_DEFAULT_ON", "false").lower() == "true"
        keywords = ["latest", "news", "docs", "documentation", "today", "current", "update", "release", "changelog", "how to", "api"]
        return default_on or any(k in t for k in keywords)

    def _should_do_file_extract(self, text: str, files: list[str] | None) -> bool:
        if files:
            return False
        t = (text or "").lower()
        return any(k in t for k in ["pdf", "doc", "docx", "ppt", "pptx", "xlsx", "csv", "upload", "file"])

    def _ensure_abs_paths(self, paths: list[str]) -> list[str]:
        """Validate and normalize paths to absolute within project root."""
        abs_list: list[str] = []
        project_root = os.path.abspath(os.getcwd())
        for p in paths:
            if not p:
                continue
            abs_p = os.path.abspath(p)
            # Restrict to project boundary and existing paths only
            if abs_p.startswith(project_root) and os.path.exists(abs_p):
                abs_list.append(abs_p)
        return abs_list

    def _infer_relevant_files(self) -> list[str]:
        """Very conservative file inference: prefer core Zen files if present.
        Returns up to 3 absolute paths.
        """
        project_root = os.path.abspath(os.getcwd())
        candidates = [
            os.path.join(project_root, "zen-mcp-server", "server.py"),
            os.path.join(project_root, "zen-mcp-server", "pyproject.toml"),
            os.path.join(project_root, "examples", "end_to_end_demo.py"),
        ]
        inferred = [p for p in candidates if os.path.exists(p)]
        if inferred:
            return inferred[:3]

        # Fallback: first few Python files under zen-mcp-server (bounded to project root)
        root = os.path.join(project_root, "zen-mcp-server")
        picks: list[str] = []
        for dirpath, _, filenames in os.walk(root):
            # Ensure we stay within project boundary
            if os.path.commonpath([project_root, dirpath]) != project_root:
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    full = os.path.join(dirpath, fn)
                    picks.append(full)
                    if len(picks) >= 3:
                        return picks
        return picks

    def _render_chunks(self, chunks: list) -> str:
        parts: list[str] = []
        for ch in chunks or []:
            try:
                if isinstance(ch, dict) and ch.get("type") == "text":
                    parts.append(str(ch.get("text", "")))
                else:
                    # Fallback for other content formats (e.g., TextContent)
                    txt = getattr(ch, "text", None)
                    parts.append(str(txt) if txt is not None else str(ch))
            except Exception:
                parts.append(str(ch))
        return "\n".join([p for p in parts if p])

    def _format_plan_only(self, user_prompt: str, model_name: str, files: list[str], plan: list[dict]) -> str:
        plan_lines = [
            "Planned steps (v0.2):",
            f"- {plan[0]['tool']} step 1 (files={len(files)})" if plan else "- analyze step 1",
        ]
        if any(s.get("step_number") == 2 for s in plan):
            plan_lines.append(f"- {plan[0]['tool']} step 2 (finalize)" if plan else "- analyze step 2 (finalize)")
        return (
            f"OrchestrateAuto (v0.2)\nRequest: {user_prompt}\nModel: {model_name}\nFiles:\n"
            + "\n".join(f"  - {f}" for f in files)
            + "\n\n"
            + "\n".join(plan_lines)
        )

    def _format_consolidated_output(
        self,
        user_prompt: str,
        model_name: str,
        files: list[str],
        plan: list[dict],
        outputs: list[str],
        guidance: list[str] | None = None,
    ) -> str:
        header = [
            "=== ORCHESTRATION SUMMARY (MVP) ===",
            f"Prompt: {user_prompt}",
            f"Model: {model_name}",
            "Files:",
            *[f"  - {f}" for f in files],
            "",
            "Plan:",
            *[f"  - {s['tool']} step {s['step_number']}: {s['description']}" for s in plan],
            "",
            "Execution Results:",
        ]
        body = []
        for out in outputs:
            body.append(out)
            body.append("")
        # Include guidance extracted from analyze tool (next_steps / required actions)
        guidance = guidance or []
        if guidance:
            body.append("Required Actions / Next Steps from Analyze:")
            body.extend([f"- {g}" for g in guidance])
            body.append("")
        footer = [
            "Next: Expand orchestrator to multi-tool routing (testgen, tracer) using descriptors,",
            "add model-driven planning and cost-aware tool selection.",
        ]
        return "\n".join(header + body + footer)

