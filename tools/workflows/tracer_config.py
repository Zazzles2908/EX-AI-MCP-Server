"""
Tracer Workflow Configuration

Field descriptions and configuration constants for the Tracer workflow tool.
"""

# Tool-specific field descriptions for tracer workflow
TRACER_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Describe what you're currently investigating for code tracing by thinking deeply about the code structure, "
        "execution paths, and dependencies. In step 1, if trace_mode is 'ask', MUST prompt user to choose between "
        "precision or dependencies mode with clear explanations. Otherwise, clearly state your tracing plan and begin "
        "forming a systematic approach after thinking carefully about what needs to be analyzed. CRITICAL: For precision "
        "mode, focus on execution flow, call chains, and usage patterns. For dependencies mode, focus on structural "
        "relationships and bidirectional dependencies. Map out the code structure, understand the business logic, and "
        "identify areas requiring deeper tracing. In all later steps, continue exploring with precision: trace dependencies, "
        "verify call paths, and adapt your understanding as you uncover more evidence."
    ),
    "step_number": (
        "The index of the current step in the tracing sequence, beginning at 1. Each step should build upon or "
        "revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the tracing analysis. "
        "Adjust as new findings emerge."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe the "
        "tracing analysis is complete and ready for final output formatting."
    ),
    "findings": (
        "Summarize everything discovered in this step about the code being traced. Include analysis of execution "
        "paths, dependency relationships, call chains, structural patterns, and any discoveries about how the code "
        "works. Be specific and avoid vague language—document what you now know about the code and how it affects "
        "your tracing analysis. IMPORTANT: Document both the direct relationships (immediate calls, dependencies) "
        "and indirect relationships (transitive dependencies, side effects). In later steps, confirm or update past "
        "findings with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the tracing "
        "investigation so far. Include even files ruled out or found to be unrelated, as this tracks your "
        "exploration path."
    ),
    "relevant_files": (
        "Subset of files_checked (as full absolute paths) that contain code directly relevant to the tracing analysis. "
        "Only list those that are directly tied to the target method/function/class/module being traced, its "
        "dependencies, or its usage patterns. This could include implementation files, related modules, or files "
        "demonstrating key relationships."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the tracing analysis, in the format "
        "'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that are part of the "
        "execution flow, dependency chain, or represent key relationships in the tracing analysis."
    ),
    "confidence": (
        "Indicate your current confidence in the tracing analysis completeness. Use: 'exploring' (starting analysis), "
        "'low' (early investigation), 'medium' (some patterns identified), 'high' (comprehensive understanding), "
        "'very_high' (very comprehensive understanding), 'almost_certain' (nearly complete tracing), "
        "'certain' (100% confidence - tracing analysis is finished and ready for output with no need for external model validation). "
        "Do NOT use 'certain' unless the tracing analysis is thoroughly finished and you have a comprehensive understanding "
        "of the code relationships. Using 'certain' means you have complete confidence locally and prevents external model validation."
    ),
    "trace_mode": "Type of tracing: 'ask' (default - prompts user to choose mode), 'precision' (execution flow) or 'dependencies' (structural relationships)",
    "target_description": (
        "Detailed description of what to trace and WHY you need this analysis. MUST include context about what "
        "you're trying to understand, debug, analyze or find."
    ),
    "images": (
        "Optional images of system architecture diagrams, flow charts, or visual references to help "
        "understand the tracing context"
    ),
}


__all__ = ["TRACER_WORKFLOW_FIELD_DESCRIPTIONS"]

