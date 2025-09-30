"""
Consensus tool schema builder - Input schema generation

This module contains the schema building logic for the consensus workflow tool.
It generates the MCP input schema with consensus-specific field definitions.
"""

from typing import Any

from .consensus_config import CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS


def build_consensus_schema(tool_name: str, model_field_schema: dict[str, Any]) -> dict[str, Any]:
    """
    Generate input schema for consensus workflow.

    Args:
        tool_name: Name of the tool (should be "consensus")
        model_field_schema: Schema for the model field from the tool

    Returns:
        Complete input schema dictionary for MCP
    """
    from ..workflow.schema_builders import WorkflowSchemaBuilder

    # Consensus tool-specific field definitions
    consensus_field_overrides = {
        # Override standard workflow fields that need consensus-specific descriptions
        "step": {
            "type": "string",
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["step"],
        },
        "step_number": {
            "type": "integer",
            "minimum": 1,
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["step_number"],
        },
        "total_steps": {
            "type": "integer",
            "minimum": 1,
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["total_steps"],
        },
        "next_step_required": {
            "type": "boolean",
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["next_step_required"],
        },
        "findings": {
            "type": "string",
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["findings"],
        },
        "relevant_files": {
            "type": "array",
            "items": {"type": "string"},
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["relevant_files"],
        },
        # consensus-specific fields (not in base workflow)
        "models": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "stance": {"type": "string", "enum": ["for", "against", "neutral"], "default": "neutral"},
                    "stance_prompt": {"type": "string"},
                },
                "required": ["model"],
            },
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["models"],
        },
        "current_model_index": {
            "type": "integer",
            "minimum": 0,
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["current_model_index"],
        },
        "model_responses": {
            "type": "array",
            "items": {"type": "object"},
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["model_responses"],
        },
        "images": {
            "type": "array",
            "items": {"type": "string"},
            "description": CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS["images"],
        },
    }

    # Define excluded fields for consensus workflow
    excluded_workflow_fields = [
        "files_checked",  # Not used in consensus workflow
        "relevant_context",  # Not used in consensus workflow
        "issues_found",  # Not used in consensus workflow
        "hypothesis",  # Not used in consensus workflow
        "backtrack_from_step",  # Not used in consensus workflow
        "confidence",  # Not used in consensus workflow
        "findings",  # Consensus handles findings as optional except step 1 via validator
    ]

    excluded_common_fields = [
        "model",  # Consensus uses 'models' field instead
        "temperature",  # Not used in consensus workflow
        "thinking_mode",  # Not used in consensus workflow
        "use_websearch",  # Not used in consensus workflow
    ]

    # Build schema with proper field exclusion
    # Include model field for compatibility but don't require it
    schema = WorkflowSchemaBuilder.build_schema(
        tool_specific_fields=consensus_field_overrides,
        model_field_schema=model_field_schema,
        auto_mode=False,  # Consensus doesn't require model at MCP boundary
        tool_name=tool_name,
        excluded_workflow_fields=excluded_workflow_fields,
        excluded_common_fields=excluded_common_fields,
    )
    return schema


__all__ = ["build_consensus_schema"]

