"""
Precommit Workflow Configuration

Field descriptions and configuration constants for the Precommit workflow tool.
"""

# Tool-specific field descriptions for precommit workflow
PRECOMMIT_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "Describe what you're currently investigating for pre-commit validation by thinking deeply about the changes "
        "and their potential impact. In step 1, clearly state your investigation plan and begin forming a systematic "
        "approach after thinking carefully about what needs to be validated. CRITICAL: Remember to thoroughly examine "
        "all git repositories, staged/unstaged changes, and understand the scope and intent of modifications. "
        "Consider not only immediate correctness but also potential future consequences, security implications, "
        "performance impacts, and maintainability concerns. Map out changed files, understand the business logic, "
        "and identify areas requiring deeper analysis. In all later steps, continue exploring with precision: "
        "trace dependencies, verify hypotheses, and adapt your understanding as you uncover more evidence."
        "IMPORTANT: When referring to code, use the relevant_files parameter to pass relevant files and only use the prompt to refer to "
        "function / method names or very small code snippets if absolutely necessary to explain the issue. Do NOT "
        "pass large code snippets in the prompt as this is exclusively reserved for descriptive text only. "
    ),
    "step_number": (
        "The index of the current step in the pre-commit investigation sequence, beginning at 1. Each step should "
        "build upon or revise the previous one."
    ),
    "total_steps": (
        "Your current estimate for how many steps will be needed to complete the pre-commit investigation. "
        "Adjust as new findings emerge. IMPORTANT: When continuation_id is provided (continuing a previous "
        "conversation), set this to 1 as we're not starting a new multi-step investigation."
    ),
    "next_step_required": (
        "Set to true if you plan to continue the investigation with another step. False means you believe the "
        "pre-commit analysis is complete and ready for expert validation. IMPORTANT: When continuation_id is "
        "provided (continuing a previous conversation), set this to False to immediately proceed with expert analysis."
    ),
    "findings": (
        "Summarize everything discovered in this step about the changes being committed. Include analysis of git diffs, "
        "file modifications, new functionality, potential issues identified, code quality observations, and security "
        "considerations. Be specific and avoid vague language—document what you now know about the changes and how "
        "they affect your assessment. IMPORTANT: Document both positive findings (good patterns, proper implementations) "
        "and concerns (potential bugs, missing tests, security risks). In later steps, confirm or update past findings "
        "with additional evidence."
    ),
    "files_checked": (
        "List all files (as absolute paths, do not clip or shrink file names) examined during the pre-commit "
        "investigation so far. Include even files ruled out or found to be unchanged, as this tracks your "
        "exploration path."
    ),
    "relevant_files": (
        "Subset of files_checked (as full absolute paths) that contain changes or are directly relevant to the "
        "commit validation. Only list those that are directly tied to the changes being committed, their dependencies, "
        "or files that need validation. This could include modified files, related configuration, tests, or "
        "documentation."
    ),
    "relevant_context": (
        "List methods, functions, classes, or modules that are central to the changes being committed, in the format "
        "'ClassName.methodName', 'functionName', or 'module.ClassName'. Prioritize those that are modified, added, "
        "or significantly affected by the changes."
    ),
    "issues_found": (
        "List of issues identified during the investigation. Each issue should be a dictionary with 'severity' "
        "(critical, high, medium, low) and 'description' fields. Include potential bugs, security concerns, "
        "performance issues, missing tests, incomplete implementations, etc."
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
        "start over. Use this to acknowledge investigative dead ends and correct the course."
    ),
    "images": (
        "Optional list of absolute paths to screenshots, UI mockups, or visual references that help validate the "
        "changes. Only include if they materially assist understanding or assessment of the commit."
    ),
    "path": (
        "Starting absolute path to the directory to search for git repositories (must be FULL absolute paths - "
        "DO NOT SHORTEN)."
    ),
    "compare_to": (
        "Optional: A git ref (branch, tag, commit hash) to compare against. Check remote branches if local does not exist."
        "If not provided, investigates local staged and unstaged changes."
    ),
    "include_staged": "Include staged changes in the investigation. Only applies if 'compare_to' is not set.",
    "include_unstaged": "Include uncommitted (unstaged) changes in the investigation. Only applies if 'compare_to' is not set.",
    "focus_on": "Specific aspects to focus on (e.g., 'security implications', 'performance impact', 'test coverage').",
    "severity_filter": "Minimum severity level to report on the changes.",
}


__all__ = ["PRECOMMIT_WORKFLOW_FIELD_DESCRIPTIONS"]

