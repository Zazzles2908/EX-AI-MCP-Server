"""
Analyze Workflow Configuration

Field descriptions and configuration constants for the Analyze workflow tool.
"""

# Tool-specific field descriptions for analyze workflow
ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "What to analyze or look for in this step. In step 1, describe what you want to analyze and begin forming "
        "an analytical approach after thinking carefully about what needs to be examined. Consider code quality, "
        "performance implications, architectural patterns, and design decisions. Map out the codebase structure, "
        "understand the business logic, and identify areas requiring deeper analysis. In later steps, continue "
        "exploring with precision and adapt your understanding as you uncover more insights."
    ),
    "step_number": (
        "The index of the current step in the analysis sequence, beginning at 1. Each step should build upon or "
        "revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the analysis. "
        "Adjust as new findings emerge."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe the "
        "analysis is complete and ready for expert validation."
    ),
    "findings": (
        "Summarize everything discovered in this step about the code being analyzed. Include analysis of architectural "
        "patterns, design decisions, tech stack assessment, scalability characteristics, performance implications, "
        "maintainability factors, security posture, and strategic improvement opportunities. Be specific and avoid "
        "vague language—document what you now know about the codebase and how it affects your assessment. "
        "IMPORTANT: Document both strengths (good patterns, solid architecture, well-designed components) and "
        "concerns (tech debt, scalability risks, overengineering, unnecessary complexity). In later steps, confirm "
        "or update past findings with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the analysis "
        "investigation so far. Include even files ruled out or found to be unrelated, as this tracks your "
        "exploration path."
    ),
    "relevant_files": (
        "Subset of files_checked (as full absolute paths) that contain code directly relevant to the analysis or "
        "contain significant patterns, architectural decisions, or examples worth highlighting. Only list those that are "
        "directly tied to important findings, architectural insights, performance characteristics, or strategic "
        "improvement opportunities. This could include core implementation files, configuration files, or files "
        "demonstrating key patterns."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the analysis findings, in the format "
        "'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that demonstrate important "
        "patterns, represent key architectural decisions, show performance characteristics, or highlight strategic "
        "improvement opportunities."
    ),
    "backtrack_from_step": (
        "If an earlier finding or assessment needs to be revised or discarded, specify the step number from which to "
        "start over. Use this to acknowledge investigative dead ends and correct the course.\n\n"
        "IMPORTANT: This parameter is only valid when step_number > 1. You cannot backtrack from step 1. "
        "Example: If you are on step 3 and need to restart from step 1, set backtrack_from_step=1. "
        "The value must be less than the current step_number."
    ),
    "images": (
        "Optional list of absolute paths to architecture diagrams, design documents, or visual references "
        "that help with analysis context. Only include if they materially assist understanding or assessment."
    ),
    "confidence": (
        "Your confidence level in the current analysis findings: exploring (early investigation), "
        "low (some insights but more needed), medium (solid understanding), high (comprehensive insights), "
        "very_high (very comprehensive insights), almost_certain (nearly complete analysis), "
        "certain (100% confidence - complete analysis ready for expert validation)"
    ),
    "analysis_type": "Type of analysis to perform (architecture, performance, security, quality, general). Synonyms like 'comprehensive' will map to 'general'.",
    "output_format": "How to format the output (summary, detailed, actionable)",
}


__all__ = ["ANALYZE_WORKFLOW_FIELD_DESCRIPTIONS"]

