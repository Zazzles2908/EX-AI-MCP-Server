"""
Tool Argument Validation Utility for External Agents

This module provides utilities to validate tool arguments BEFORE sending them to EXAI MCP tools.
This prevents "Additional properties are not allowed" errors.

Usage:
    from src.server.utils.tool_validator import validate_tool_args

    # Validate arguments before calling tool
    is_valid, error = validate_tool_args("analyze", {
        "step": "Investigate issue",
        "step_number": 1,
        "total_steps": 3,
        "next_step_required": True,
        "findings": "Found problem in auth module"
    })

    if not is_valid:
        print(f"Validation failed: {error}")
        # Fix arguments
        args = fix_tool_args("analyze", args)
        # Retry
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Tool schema definitions
# These match the Pydantic models defined in tools/*_models.py
TOOL_SCHEMAS = {
    "analyze": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "relevant_context", "issues_found",
            "backtrack_from_step", "images", "analysis_type", "output_format",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Comprehensive code analysis with expert validation"
    },
    "debug": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "relevant_context", "images",
            "backtrack_from_step", "hypothesis", "model", "temperature",
            "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Debugging and root cause analysis"
    },
    "codereview": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "focus_on", "hypothesis", "images",
            "backtrack_from_step", "model", "temperature", "thinking_mode",
            "use_websearch", "continuation_id"
        ],
        "description": "Code review and validation"
    },
    "refactor": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "focus_areas", "hypothesis", "images",
            "backtrack_from_step", "refactor_type", "model", "temperature",
            "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Code refactoring analysis"
    },
    "testgen": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "relevant_context", "images",
            "backtrack_from_step", "model", "temperature", "thinking_mode",
            "use_websearch", "continuation_id"
        ],
        "description": "Test generation"
    },
    "thinkdeep": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "focus_areas", "hypothesis", "images",
            "backtrack_from_step", "model", "temperature", "thinking_mode",
            "use_websearch", "continuation_id"
        ],
        "description": "Deep thinking and investigation"
    },
    "consensus": {
        "required": ["step", "step_number", "total_steps", "next_step_required"],
        "optional": [
            "findings", "relevant_files", "model", "temperature", "thinking_mode",
            "use_websearch", "continuation_id"
        ],
        "description": "Multi-model consensus"
    },
    "precommit": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "compare_to", "focus_on", "relevant_files", "severity_filter",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Pre-commit validation"
    },
    "tracer": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "target_description", "trace_mode", "relevant_files", "relevant_context",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Code execution tracing"
    },
    "docgen": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "num_files_documented", "total_files_to_document", "document_complexity",
            "document_flow", "update_existing", "comments_on_complex_logic",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Documentation generation"
    },
    "secaudit": {
        "required": ["step", "step_number", "total_steps", "next_step_required", "findings"],
        "optional": [
            "files_checked", "relevant_files", "audit_focus", "security_scope",
            "threat_level", "compliance_requirements", "severity_filter",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Security auditing"
    },
    "smart_file_query": {
        "required": ["file_path", "question"],
        "optional": ["model", "provider"],
        "description": "Unified file upload/query interface"
    },
    "smart_file_download": {
        "required": ["file_path"],
        "optional": ["model"],
        "description": "Unified file download interface"
    },
    "status": {
        "required": [],
        "optional": ["doctor", "include_tools", "probe", "tail_lines"],
        "description": "System status"
    },
    "health": {
        "required": [],
        "optional": ["tail_lines"],
        "description": "Health checks"
    },
    "planner": {
        "required": ["step", "step_number", "total_steps", "next_step_required"],
        "optional": [
            "branch_id", "is_branch_point", "is_step_revision", "revises_step_number",
            "model", "temperature", "thinking_mode", "use_websearch", "continuation_id"
        ],
        "description": "Task planning"
    },
    "chat": {
        "required": ["prompt"],
        "optional": ["model", "temperature", "use_websearch"],
        "description": "Basic communication"
    },
    "version": {
        "required": [],
        "optional": [],
        "description": "Version information"
    },
    "listmodels": {
        "required": [],
        "optional": ["model"],
        "description": "List available models"
    },
}


def validate_tool_args(tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate tool arguments against the expected schema.

    Args:
        tool_name: Name of the tool to validate
        args: Arguments to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error string if invalid
    """
    if tool_name not in TOOL_SCHEMAS:
        return False, f"Unknown tool: {tool_name}. Available tools: {', '.join(TOOL_SCHEMAS.keys())}"

    schema = TOOL_SCHEMAS[tool_name]
    required_fields = schema["required"]
    optional_fields = schema["optional"]

    # Check for extra fields
    all_valid_fields = set(required_fields) | set(optional_fields)
    provided_fields = set(args.keys())
    extra_fields = provided_fields - all_valid_fields

    if extra_fields:
        # Map common mistakes to correct field names
        field_corrections = {
            "stepnum": "step_number",
            "step_number": "step_number",
            "totalsteps": "total_steps",
            "total_steps": "total_steps",
            "nextsteprequired": "next_step_required",
            "next_step_required": "next_step_required",
            "problem_context": None,  # This field doesn't exist in any tool
            "context": None,  # Too generic, not in schema
            "findings": "findings",
        }

        # Check if extra fields are close to valid fields
        close_matches = []
        for field in extra_fields:
            if field in field_corrections:
                if field_corrections[field] is None:
                    close_matches.append(f"'{field}' is not a valid parameter for {tool_name} tool")
                else:
                    close_matches.append(f"'{field}' should be '{field_corrections[field]}'")
            else:
                close_matches.append(f"'{field}' is not a valid parameter for {tool_name} tool")

        # Get the list of valid fields
        valid_fields_list = ", ".join(sorted(all_valid_fields))
        error_msg = (
            f"Invalid arguments for '{tool_name}' tool:\n"
            f"{' ; '.join(close_matches)}\n"
            f"\nValid parameters for {tool_name}:\n"
            f"  Required: {', '.join(required_fields)}\n"
            f"  Optional: {', '.join(optional_fields)}\n"
            f"\nNote: Only use the exact field names listed above."
        )
        return False, error_msg

    # Check for missing required fields
    missing_fields = [field for field in required_fields if field not in args or args[field] is None]
    if missing_fields:
        error_msg = (
            f"Missing required fields for '{tool_name}' tool:\n"
            f"  {', '.join(missing_fields)}\n"
            f"\nRequired fields: {', '.join(required_fields)}\n"
            f"All valid fields: {', '.join(sorted(all_valid_fields))}"
        )
        return False, error_msg

    # Type validation for workflow tools
    if tool_name in ["analyze", "debug", "codereview", "refactor", "testgen", "thinkdeep", "consensus", "precommit", "tracer", "docgen", "secaudit", "planner"]:
        # Validate step_number is an integer
        if "step_number" in args:
            try:
                step_num = args["step_number"]
                if isinstance(step_num, str) and step_num.isdigit():
                    # Auto-convert string digits to int
                    args["step_number"] = int(step_num)
                elif not isinstance(step_num, int):
                    return False, f"Field 'step_number' must be an integer, got {type(step_num).__name__}"
            except (ValueError, TypeError):
                return False, f"Field 'step_number' must be a valid integer"

        # Validate total_steps is an integer
        if "total_steps" in args:
            try:
                total = args["total_steps"]
                if isinstance(total, str) and total.isdigit():
                    args["total_steps"] = int(total)
                elif not isinstance(total, int):
                    return False, f"Field 'total_steps' must be an integer, got {type(total).__name__}"
            except (ValueError, TypeError):
                return False, f"Field 'total_steps' must be a valid integer"

        # Validate next_step_required is a boolean
        if "next_step_required" in args:
            if isinstance(args["next_step_required"], str):
                val = args["next_step_required"].lower()
                if val in ("true", "1", "yes", "on"):
                    args["next_step_required"] = True
                elif val in ("false", "0", "no", "off"):
                    args["next_step_required"] = False
                else:
                    return False, f"Field 'next_step_required' must be a boolean (true/false), got '{val}'"
            elif not isinstance(args["next_step_required"], bool):
                return False, f"Field 'next_step_required' must be a boolean, got {type(args['next_step_required']).__name__}"

    return True, None


def fix_tool_args(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt to fix common mistakes in tool arguments.

    Args:
        tool_name: Name of the tool
        args: Arguments to fix

    Returns:
        Fixed arguments dictionary
    """
    if tool_name not in TOOL_SCHEMAS:
        return args

    schema = TOOL_SCHEMAS[tool_name]
    all_valid_fields = set(schema["required"]) | set(schema["optional"])

    # Remove extra fields
    fixed_args = {k: v for k, v in args.items() if k in all_valid_fields}

    # Fix common field name mistakes
    field_corrections = {
        "stepnum": "step_number",
        "totalsteps": "total_steps",
        "nextsteprequired": "next_step_required",
    }

    for wrong_name, correct_name in field_corrections.items():
        if wrong_name in args and correct_name not in args:
            fixed_args[correct_name] = args[wrong_name]
            logger.info(f"Fixed field name: {wrong_name} -> {correct_name}")

    # Auto-convert numeric strings for workflow tools
    if tool_name in ["analyze", "debug", "codereview", "refactor", "testgen", "thinkdeep", "consensus", "precommit", "tracer", "docgen", "secaudit", "planner"]:
        for field in ["step_number", "total_steps"]:
            if field in fixed_args and isinstance(fixed_args[field], str):
                try:
                    if fixed_args[field].isdigit():
                        fixed_args[field] = int(fixed_args[field])
                except (ValueError, TypeError):
                    pass

        # Auto-convert boolean strings
        if "next_step_required" in fixed_args and isinstance(fixed_args["next_step_required"], str):
            val = fixed_args["next_step_required"].lower()
            if val in ("true", "1", "yes", "on"):
                fixed_args["next_step_required"] = True
            elif val in ("false", "0", "no", "off"):
                fixed_args["next_step_required"] = False

    return fixed_args


def suggest_tool(tool_name: str, args: Dict[str, Any]) -> Optional[str]:
    """
    Suggest the correct tool based on arguments.

    Args:
        tool_name: Provided tool name
        args: Arguments provided

    Returns:
        Suggested tool name or None
    """
    # Check if file_path is provided
    if "file_path" in args:
        if "question" in args:
            return "smart_file_query"
        else:
            return "smart_file_download"

    # Check if prompt is provided
    if "prompt" in args:
        return "chat"

    # Check for workflow patterns
    if any(field in args for field in ["step", "step_number", "total_steps", "next_step_required", "findings"]):
        # Determine based on common patterns
        if "analysis_type" in args or "output_format" in args:
            return "analyze"
        if "focus_on" in args:
            return "codereview"
        if "focus_areas" in args:
            return "refactor"
        if "hypothesis" in args:
            return "debug"

    return None


def validate_and_suggest(tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate arguments and provide suggestions.

    Args:
        tool_name: Name of the tool
        args: Arguments to validate

    Returns:
        Tuple of (is_valid, error_message, suggestion)
    """
    is_valid, error = validate_tool_args(tool_name, args)

    if not is_valid:
        suggestion = suggest_tool(tool_name, args)
        if suggestion and suggestion != tool_name:
            error += f"\n\nSuggestion: Did you mean to use '{suggestion}' tool instead?"
    else:
        suggestion = None

    return is_valid, error, suggestion


# Convenience functions for common tools
def validate_workflow_args(tool_name: str, step: str, step_number: int, total_steps: int,
                          next_step_required: bool, findings: str) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to validate workflow tool arguments.

    Args:
        tool_name: Name of the workflow tool
        step: Current step description
        step_number: Current step number
        total_steps: Total steps
        next_step_required: Whether another step is needed
        findings: Findings from this step

    Returns:
        Tuple of (is_valid, error_message)
    """
    args = {
        "step": step,
        "step_number": step_number,
        "total_steps": total_steps,
        "next_step_required": next_step_required,
        "findings": findings
    }
    return validate_tool_args(tool_name, args)


# Example usage
if __name__ == "__main__":
    # Test validation
    test_cases = [
        ("analyze", {
            "step": "Analyze code",
            "step_number": "1",  # String - should auto-convert
            "total_steps": 3,
            "next_step_required": "true",  # String - should auto-convert
            "findings": "Found issue",
            "problem_context": "Production"  # Invalid
        }),
        ("analyze", {
            "step": "Analyze code",
            "step_number": 1,
            "total_steps": 3,
            "next_step_required": True,
            "findings": "Found issue"
        }),
        ("smart_file_query", {
            "file_path": "/path/to/file.py",
            "question": "What is this?"
        }),
    ]

    for tool_name, args in test_cases:
        is_valid, error = validate_tool_args(tool_name, args)
        print(f"\n{tool_name}:")
        print(f"  Valid: {is_valid}")
        if not is_valid:
            print(f"  Error: {error}")
        else:
            fixed = fix_tool_args(tool_name, args)
            if fixed != args:
                print(f"  Fixed: {fixed}")
