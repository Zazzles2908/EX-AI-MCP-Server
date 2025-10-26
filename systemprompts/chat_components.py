"""
Chat-specific prompt components

These components are ONLY used by the chat tool and should not be in base_prompt.py
to avoid polluting the global namespace for other tools.

Moved from base_prompt.py as part of 4-tier architecture implementation (Phase 1.2)
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

