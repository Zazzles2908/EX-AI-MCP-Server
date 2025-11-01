"""
Schema Enhancement Utilities for EXAI MCP Tools

This module provides utilities for enhancing tool input schemas with
capability hints, decision matrices, and metadata to help AI agents
discover and use tools effectively without external documentation.

Created: 2025-11-01 (Phase 6.3 - Extract Schema Enhancement Logic)
Extracted from: tools/shared/base_tool_core.py (lines 154-237)
"""

from typing import Any, Dict, List, Optional


class SchemaEnhancer:
    """
    Utility class for enhancing tool input schemas with capability metadata.
    
    This class provides methods to add capability hints, decision matrices,
    and relationship metadata to tool schemas, making them self-documenting
    for AI agents.
    
    The enhanced schema is backward-compatible with standard JSON Schema validators.
    All enhancements use x- prefixed properties which are ignored by standard validators.
    """
    
    @staticmethod
    def enhance_schema(
        base_schema: Dict[str, Any],
        related_tools: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Enhance a base schema with capability hints and metadata.
        
        Args:
            base_schema: The base JSON schema to enhance
            related_tools: Optional dictionary of related tools for escalation/alternatives
            
        Returns:
            Enhanced schema with capability metadata
        """
        # Create a copy to avoid modifying the original
        enhanced_schema = base_schema.copy()
        
        # Add capability hints to different parameter types
        SchemaEnhancer._add_file_capability_hints(enhanced_schema)
        SchemaEnhancer._add_continuation_capability_hints(enhanced_schema)
        SchemaEnhancer._add_model_capability_hints(enhanced_schema)
        SchemaEnhancer._add_websearch_capability_hints(enhanced_schema)
        
        # Add tool relationship metadata
        enhanced_schema["x-related-tools"] = related_tools or {
            "escalation": [],
            "alternatives": []
        }
        
        return enhanced_schema
    
    @staticmethod
    def _add_file_capability_hints(schema: Dict[str, Any]) -> None:
        """
        Add capability hints for file parameters.
        
        Provides guidance on when to use embedded files vs. file upload tools,
        including token savings and usage patterns.
        """
        if "properties" in schema and "files" in schema["properties"]:
            schema["properties"]["files"]["x-capability-hints"] = {
                "threshold": "5KB",
                "alternative_tool": "kimi_upload_files",
                "benefit": "Saves 70-80% tokens for large files",
                "usage": "Use 'files' parameter for <5KB files, 'kimi_upload_files' tool for >5KB files"
            }
            schema["properties"]["files"]["x-decision-matrix"] = {
                "file_size": {
                    "<5KB": "Use 'files' parameter - embeds content as text in prompt",
                    ">5KB": "Use 'kimi_upload_files' tool - saves 70-80% tokens, enables persistent reference"
                }
            }
    
    @staticmethod
    def _add_continuation_capability_hints(schema: Dict[str, Any]) -> None:
        """
        Add capability hints for continuation_id parameter.
        
        Explains multi-turn conversation support and how to maintain context
        across multiple tool calls.
        """
        if "properties" in schema and "continuation_id" in schema["properties"]:
            schema["properties"]["continuation_id"]["x-capability-hints"] = {
                "usage_pattern": "Multi-turn conversations",
                "how_it_works": "Automatically retrieves conversation history",
                "benefit": "Enables coherent multi-turn workflows without repeating context"
            }
            schema["properties"]["continuation_id"]["x-examples"] = [
                {
                    "scenario": "First call",
                    "returns": "continuation_id='abc123'",
                    "next_call": "Include continuation_id='abc123' in subsequent calls"
                }
            ]
    
    @staticmethod
    def _add_model_capability_hints(schema: Dict[str, Any]) -> None:
        """
        Add capability hints for model parameter.
        
        Provides model selection guidance based on task complexity,
        including performance and cost trade-offs.
        """
        if "properties" in schema and "model" in schema["properties"]:
            schema["properties"]["model"]["x-capability-hints"] = {
                "default": "glm-4.5-flash",
                "recommended": {
                    "simple_tasks": "glm-4.5-flash (fast, cost-effective)",
                    "complex_analysis": "glm-4.6 (comprehensive reasoning)",
                    "vision_tasks": "glm-4.5v (image understanding)"
                }
            }
            schema["properties"]["model"]["x-decision-matrix"] = {
                "task_complexity": {
                    "simple": "glm-4.5-flash - Quick responses, lower cost",
                    "moderate": "glm-4.5 - Balanced performance",
                    "complex": "glm-4.6 - Deep reasoning, comprehensive analysis"
                }
            }
    
    @staticmethod
    def _add_websearch_capability_hints(schema: Dict[str, Any]) -> None:
        """
        Add capability hints for use_websearch parameter.
        
        Explains when to enable web search and the associated overhead,
        helping agents make informed decisions about search usage.
        """
        if "properties" in schema and "use_websearch" in schema["properties"]:
            schema["properties"]["use_websearch"]["x-capability-hints"] = {
                "when_to_enable": [
                    "Researching best practices",
                    "Exploring frameworks/technologies",
                    "Finding current documentation",
                    "Architectural design discussions"
                ],
                "overhead": "Adds payload size and processing time even when not actively searching",
                "recommendation": "Enable selectively for tools that benefit from external knowledge"
            }


def get_default_related_tools() -> Dict[str, List[str]]:
    """
    Get default related tools configuration.
    
    Returns empty escalation and alternatives lists that can be
    overridden by specific tools to provide custom relationships.
    
    Returns:
        Dictionary with 'escalation' and 'alternatives' keys
    """
    return {
        "escalation": [],
        "alternatives": []
    }

