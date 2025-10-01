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
    """Format a role definition consistently."""
    return f"ROLE\n{role_description}"

# Standard scope format
def format_scope(scope_items: list[str]) -> str:
    """Format scope and focus section consistently."""
    items = "\n".join(f"• {item}" for item in scope_items)
    return f"SCOPE & FOCUS\n{items}"

# Standard deliverable format
def format_deliverable(sections: dict[str, str]) -> str:
    """Format deliverable section consistently."""
    parts = ["DELIVERABLE FORMAT\n"]
    for section_name, section_desc in sections.items():
        parts.append(f"## {section_name}\n{section_desc}\n")
    return "\n".join(parts)

