"""
Shared base prompt elements for all EX-AI MCP tools

This module implements a 4-tier architecture for system prompts:
- Tier 0: Utility tools (no prompts, direct execution)
- Tier 1: Core components (100% usage - all AI tools)
- Tier 2: Optional components (conditional inclusion for workflow tools)
- Tier 3: Provider-specific optimizations (Kimi vs GLM)

For chat-specific components, see chat_components.py

IMPORTANT: File handling guidance moved to configurations/file_handling_guidance.py
to avoid duplication when storing conversations (2025-10-26)
"""

# Import centralized file handling guidance
from configurations.file_handling_guidance import FILE_PATH_GUIDANCE, FILE_UPLOAD_GUIDANCE

# ============================================================================
# TIER 1: CORE COMPONENTS (100% usage - ALL AI tools)
# ============================================================================

# FILE_PATH_GUIDANCE now imported from configurations/file_handling_guidance.py
# FILE_UPLOAD_GUIDANCE now imported from configurations/file_handling_guidance.py

# Common response quality guidelines
RESPONSE_QUALITY = """
RESPONSE QUALITY
• Be concise and technically precise - assume an experienced engineering audience
• Provide concrete examples and actionable next steps
• Reference specific files, line numbers, and code when applicable
• Balance depth with clarity - avoid unnecessary verbosity
"""

# ============================================================================
# TIER 2: OPTIONAL COMPONENTS (Conditional - workflow tools only)
# ============================================================================

# Common anti-overengineering guidance
ANTI_OVERENGINEERING = """
AVOID OVERENGINEERING
• Overengineering introduces unnecessary abstraction, indirection, or configuration for complexity that doesn't exist yet
• Propose solutions proportional to current needs, not speculative future requirements
• Favor simplicity and directness over generic frameworks unless clearly justified by current scope
• Call out excessive abstraction that slows onboarding or reduces clarity
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

