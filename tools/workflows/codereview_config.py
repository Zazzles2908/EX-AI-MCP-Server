"""
CodeReview Workflow Configuration

Field descriptions and configuration constants for the CodeReview workflow tool.
"""

# Tool-specific field descriptions for code review workflow
CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Describe what you're currently investigating for code review by thinking deeply about the code structure, "
        "patterns, and potential issues. In step 1, clearly state your review plan and begin forming a systematic "
        "approach after thinking carefully about what needs to be analyzed. You must begin by passing the file path "
        "for the initial code you are about to review in relevant_files. CRITICAL: Remember to thoroughly examine "
        "code quality, security implications, performance concerns, and architectural patterns. Consider not only "
        "obvious bugs and issues but also subtle concerns like over-engineering, unnecessary complexity, design "
        "patterns that could be simplified, areas where architecture might not scale well, missing abstractions, "
        "and ways to reduce complexity while maintaining functionality. Map out the codebase structure, understand "
        "the business logic, and identify areas requiring deeper analysis. In all later steps, continue exploring "
        "with precision: trace dependencies, verify assumptions, and adapt your understanding as you uncover more evidence."
        "IMPORTANT: When referring to code, use the relevant_files parameter to pass relevant files and only use the prompt to refer to "
        "function / method names or very small code snippets if absolutely necessary to explain the issue. Do NOT "
        "pass large code snippets in the prompt as this is exclusively reserved for descriptive text only. "
    ),
    "step_number": (
        "The index of the current step in the code review sequence, beginning at 1. Each step should build upon or "
        "revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the code review. "
        "Adjust as new findings emerge. MANDATORY: When continuation_id is provided (continuing a previous "
        "conversation), set this to 1 as we're not starting a new multi-step investigation."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe the "
        "code review analysis is complete and ready for expert validation. MANDATORY: When continuation_id is "
        "provided (continuing a previous conversation), set this to False to immediately proceed with expert analysis."
    ),
    "findings": (
        "Summarize everything discovered in this step about the code being reviewed. Include analysis of code quality, "
        "security concerns, performance issues, architectural patterns, design decisions, potential bugs, code smells, "
        "and maintainability considerations. Be specific and avoid vague language—document what you now know about "
        "the code and how it affects your assessment. IMPORTANT: Document both positive findings (good patterns, "
        "proper implementations, well-designed components) and concerns (potential issues, anti-patterns, security "
        "risks, performance bottlenecks). In later steps, confirm or update past findings with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the code review "
        "investigation so far. Include even files ruled out or found to be unrelated, as this tracks your "
        "exploration path."
    ),
    "relevant_files": (
        "For when this is the first step, please pass absolute file paths of relevant code to review (do not clip "
        "file paths). When used for the final step, this contains a subset of files_checked (as full absolute paths) "
        "that contain code directly relevant to the review or contain significant issues, patterns, or examples worth "
        "highlighting. Only list those that are directly tied to important findings, security concerns, performance "
        "issues, or architectural decisions. This could include core implementation files, configuration files, or "
        "files with notable patterns."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the code review findings, in the format "
        "'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that contain issues, "
        "demonstrate patterns, show security concerns, or represent key architectural decisions."
    ),
    "issues_found": (
        "List of issues identified during the investigation. Each issue should be a dictionary with 'severity' "
        "(critical, high, medium, low) and 'description' fields. Include security vulnerabilities, performance "
        "bottlenecks, code quality issues, architectural concerns, maintainability problems, over-engineering, "
        "unnecessary complexity, etc."
    ),
    "confidence": (
        "Indicate your current confidence in the assessment. Use: 'exploring' (starting analysis), 'low' (early "
        "investigation), 'medium' (some evidence gathered), 'high' (strong evidence), "
        "'very_high' (very strong evidence), 'almost_certain' (nearly complete validation), 'certain' (200% confidence - "
        "analysis is complete and all issues are identified with no need for external model validation). "
        "Do NOT use 'certain' unless the pre-commit validation is thoroughly complete, use 'very_high' or 'almost_certain' "
        "instead if not 200% sure. "
        "Using 'certain' means you have complete confidence locally and prevents external model validation. Also "
        "do NOT set confidence to 'certain' if the user has strongly requested that external validation MUST be performed."
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
        "that help with code review context. Only include if they materially assist understanding or assessment."
    ),
    "review_type": "Type of review to perform (full, security, performance, quick)",
    "focus_on": "Specific aspects to focus on or additional context that would help understand areas of concern",
    "standards": "Coding standards to enforce during the review",
    "severity_filter": "Minimum severity level to report on the issues found",
}


__all__ = ["CODEREVIEW_WORKFLOW_FIELD_DESCRIPTIONS"]

