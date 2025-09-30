"""
ThinkDeep Workflow Configuration

Configuration constants and field overrides for the ThinkDeep workflow tool.
"""

# ThinkDeep workflow-specific field overrides for schema building
THINKDEEP_FIELD_OVERRIDES = {
    "problem_context": {
        "type": "string",
        "description": "Provide additional context about the problem or goal. Be as expressive as possible. More information will be very helpful for the analysis.",
    },
    "focus_areas": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Specific aspects to focus on (architecture, performance, security, etc.)",
    },
}


__all__ = ["THINKDEEP_FIELD_OVERRIDES"]

