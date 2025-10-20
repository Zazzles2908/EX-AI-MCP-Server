"""
Shared base prompt elements for all EX-AI MCP tools

This module contains common patterns extracted from all system prompts to reduce redundancy
and ensure consistency across tools.
"""

# Common anti-overengineering guidance
ANTI_OVERENGINEERING = """
AVOID OVERENGINEERING
• Overengineering introduces unnecessary abstraction, indirection, or configuration for complexity that doesn't exist yet
• Propose solutions proportional to current needs, not speculative future requirements
• Favor simplicity and directness over generic frameworks unless clearly justified by current scope
• Call out excessive abstraction that slows onboarding or reduces clarity
"""

# Common file path instructions
FILE_PATH_GUIDANCE = """
FILE PATH REQUIREMENTS
• Use FULL ABSOLUTE paths for all file references (e.g., 'c:\\Project\\file.py', not relative paths)
• When referring to code in prompts, use the files parameter to pass relevant files
• Only include function/method names or very small code snippets in text prompts when absolutely necessary
• Do NOT pass large code blocks in text prompts - use file parameters instead
"""

# File handling strategy guidance (TRACK 1 FIX - 2025-10-17)
FILE_HANDLING_GUIDANCE = """
FILE HANDLING STRATEGY

Two approaches for providing files to AI models:

1. EMBED AS TEXT (files parameter):
   • Use for: Small files (<5KB general guideline), code snippets, configuration files
   • Behavior: File content is read and embedded directly in prompt
   • Pros: Immediate availability, no upload needed
   • Cons: Consumes tokens, not persistent across calls
   • Example: files=["path/to/config.py"]

2. UPLOAD TO PLATFORM (kimi_upload_files tool):
   • Use for: Large files (>5KB), documents, persistent reference
   • Behavior: Files uploaded to Moonshot platform, returns file_ids
   • Pros: Token-efficient, persistent, can reference in multiple calls
   • Cons: Requires separate tool call, upload time
   • Example: kimi_upload_files(files=["path/to/large_doc.pdf"])
   • Then use: kimi_chat_with_files(prompt="...", file_ids=["file_id_1", "file_id_2"])

DECISION MATRIX:
• File <5KB + single use → Embed as text (files parameter)
• File >5KB or multi-turn → Upload to platform (kimi_upload_files)
• Multiple large files → Upload to platform
• Quick code review → Embed as text
• Document analysis → Upload to platform

IMPORTANT: Always use FULL absolute paths for file references.
NOTE: The 5KB threshold is a general guideline - adjust based on content density and use case.
"""

# Common EX-AI MCP Server context
SERVER_CONTEXT = """
EX-AI MCP SERVER CONTEXT
• Default manager: GLM-4.5-flash (fast, routing-friendly). Kimi specializes in files, extraction, and long reasoning
• Conversation continuity: Use continuation_id offered by responses. Do not invent custom IDs
• File paths: Prefer FULL ABSOLUTE paths. Kimi file tools accept relative paths but absolute is recommended
• Streaming: Providers may stream; metadata.streamed=true indicates partial content
• Privacy: Limit external web calls; summarize sources and include URLs when browsing is used
"""

# Common response quality guidelines
RESPONSE_QUALITY = """
RESPONSE QUALITY
• Be concise and technically precise - assume an experienced engineering audience
• Provide concrete examples and actionable next steps
• Reference specific files, line numbers, and code when applicable
• Balance depth with clarity - avoid unnecessary verbosity
"""

# Common escalation pattern
ESCALATION_PATTERN = """
TOOL ESCALATION
When a different tool is better suited, suggest switching with minimal params:
• analyze: strategic architectural assessment (params: relevant_files)
• codereview: systematic code-level review (params: relevant_files)
• debug: root cause investigation (params: step, findings, hypothesis)
• thinkdeep: extended hypothesis-driven reasoning (params: step, findings)
Provide one-sentence rationale and exact call outline.
"""

# Standard role format
def format_role(role_description: str) -> str:
    """
    Format a role definition consistently for system prompts.

    Args:
        role_description: The role description text to format

    Returns:
        Formatted role section with "ROLE" header

    Example:
        >>> format_role("You are an expert code reviewer")
        'ROLE\\nYou are an expert code reviewer'
    """
    return f"ROLE\n{{role_description}}"

# Standard scope format
def format_scope(scope_items: list[str]) -> str:
    """
    Format scope and focus section consistently for system prompts.

    Args:
        scope_items: List of scope/focus bullet points

    Returns:
        Formatted scope section with "SCOPE & FOCUS" header and bulleted items

    Example:
        >>> format_scope(["Review code quality", "Check security"])
        'SCOPE & FOCUS\\n• Review code quality\\n• Check security'
    """
    items = "\n".join(f"• {{item}}" for item in scope_items)
    return f"SCOPE & FOCUS\n{{items}}"

# Standard deliverable format
def format_deliverable(sections: dict[str, str]) -> str:
    """
    Format deliverable section consistently for system prompts.

    Args:
        sections: Dictionary mapping section names to descriptions

    Returns:
        Formatted deliverable section with headers and content

    Example:
        >>> format_deliverable({{"Summary": "Brief overview", "Details": "Full analysis"}})
        'DELIVERABLE FORMAT\\n## Summary\\nBrief overview\\n\\n## Details\\nFull analysis\\n'
    """
    parts = ["DELIVERABLE FORMAT\n"]
    for section_name, section_desc in sections.items():
        parts.append(f"## {{section_name}}\n{{section_desc}}\n")
    return "\n".join(parts)

