"""
Refactor Workflow Configuration

Field descriptions and configuration constants for the Refactor workflow tool.
"""

# Tool-specific field descriptions for refactor workflow
REFACTOR_FIELD_DESCRIPTIONS = {
    "step": (
        "Describe what you're currently investigating for refactoring by thinking deeply about the code structure, "
        "patterns, and potential improvements. In step 1, clearly state your refactoring investigation plan and begin "
        "forming a systematic approach after thinking carefully about what needs to be analyzed. CRITICAL: Remember to "
        "thoroughly examine code quality, performance implications, maintainability concerns, and architectural patterns. "
        "Consider not only obvious code smells and issues but also opportunities for decomposition, modernization, "
        "organization improvements, and ways to reduce complexity while maintaining functionality. Map out the codebase "
        "structure, understand the business logic, and identify areas requiring refactoring. In all later steps, continue "
        "exploring with precision: trace dependencies, verify assumptions, and adapt your understanding as you uncover "
        "more refactoring opportunities."
        "IMPORTANT: When referring to code, use the relevant_files parameter to pass relevant files and only use the prompt to refer to "
        "function / method names or very small code snippets if absolutely necessary to explain the issue. Do NOT "
        "pass large code snippets in the prompt as this is exclusively reserved for descriptive text only. "
    ),
    "step_number": (
        "The index of the current step in the refactoring investigation sequence, beginning at 1. Each step should "
        "build upon or revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the refactoring investigation. "
        "Adjust as new opportunities emerge."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe the "
        "refactoring analysis is complete and ready for expert validation."
    ),
    "findings": (
        "Summarize everything discovered in this step about refactoring opportunities in the code. Include analysis of "
        "code smells, decomposition opportunities, modernization possibilities, organization improvements, architectural "
        "patterns, design decisions, potential performance optimizations, and maintainability enhancements. Be specific "
        "and avoid vague language—document what you now know about the code and how it could be improved. IMPORTANT: "
        "Document both positive aspects (good patterns, well-designed components) and improvement opportunities (code "
        "smells, overly complex functions, outdated patterns, organization issues). In later steps, confirm or update "
        "past findings with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the refactoring "
        "investigation so far. Include even files ruled out or found to need no refactoring, as this tracks your "
        "exploration path."
    ),
    "relevant_files": (
        "Subset of files_checked (as full absolute paths) that contain code requiring refactoring or are directly "
        "relevant to the refactoring opportunities identified. Only list those that are directly tied to specific "
        "refactoring opportunities, code smells, decomposition needs, or improvement areas. This could include files "
        "with code smells, overly large functions/classes, outdated patterns, or organization issues."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the refactoring opportunities, in the format "
        "'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that need refactoring, "
        "demonstrate patterns worth improving, or represent key architectural decisions."
    ),
    "issues_found": (
        "List of refactoring opportunities identified during the investigation. Each opportunity should be a dictionary "
        "with 'severity' (critical, high, medium, low), 'type' (codesmells, decompose, modernize, organization), and "
        "'description' fields. Include code smells, decomposition opportunities, modernization possibilities, organization "
        "improvements, performance optimizations, maintainability enhancements, etc."
    ),
    "confidence": (
        "Indicate your current confidence in the refactoring analysis completeness. Use: "
        "'exploring' (starting analysis), "
        "'low' (just started or significant work remaining - equivalent to original 'incomplete'), "
        "'medium' (some refactoring opportunities identified but more analysis needed - equivalent to original 'partial'), "
        "'high' (strong analysis with most opportunities identified), "
        "'very_high' (comprehensive analysis with nearly all opportunities identified), "
        "'almost_certain' (nearly complete analysis), "
        "'certain' (100% confidence - comprehensive refactoring analysis finished with all major opportunities identified "
        "and the CLI agent can handle confidently without help - equivalent to original 'complete'). "
        "Use 'certain' ONLY when you have fully analyzed all code, identified all significant refactoring opportunities, "
        "and can provide comprehensive recommendations without expert assistance. When files are too large to read fully "
        "or analysis is uncertain, use 'medium' or 'high'. Using 'certain' or 'almost_certain' prevents expert analysis "
        "to save time and money. Do NOT set confidence to 'certain' if the user has strongly requested that external "
        "validation MUST be performed. "
        "NOTE: The refactor tool originally used custom confidence levels (incomplete/partial/complete) which have been "
        "mapped to the standard enum for consistency while preserving semantic meaning."
    ),
    "backtrack_from_step": (
        "If an earlier finding or assessment needs to be revised or discarded, specify the step number from which to "
        "start over. Use this to acknowledge investigative dead ends and correct the course.\n\n"
        "IMPORTANT: This parameter is only valid when step_number > 1. You cannot backtrack from step 1. "
        "Example: If you are on step 3 and need to restart from step 1, set backtrack_from_step=1. "
        "The value must be less than the current step_number."
    ),
    "images": (
        "Optional list of absolute paths to architecture diagrams, UI mockups, design documents, or visual references "
        "that help with refactoring context. Only include if they materially assist understanding or assessment."
    ),
    "refactor_type": "Type of refactoring analysis to perform (codesmells, decompose, modernize, organization)",
    "focus_areas": "Specific areas to focus on (e.g., 'performance', 'readability', 'maintainability', 'security')",
    "style_guide_examples": (
        "Optional existing code files to use as style/pattern reference (must be FULL absolute paths to real files / "
        "folders - DO NOT SHORTEN). These files represent the target coding style and patterns for the project."
    ),
}


__all__ = ["REFACTOR_FIELD_DESCRIPTIONS"]

