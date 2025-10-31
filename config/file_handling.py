"""
Centralized file handling guidance for all EXAI tools.

This module provides consistent file path and upload guidance across all tools,
preventing duplication in system prompts and providing a single source of truth.

Created: 2025-10-26
Purpose: Avoid system prompt duplication when storing conversations
"""

FILE_PATH_GUIDANCE = """
FILE PATH REQUIREMENTS
• Use FULL ABSOLUTE paths for all file references (e.g., 'c:\\Project\\file.py', not relative paths)
• When referring to code in prompts, use the files parameter to pass relevant files
• Only include function/method names or very small code snippets in text prompts when absolutely necessary
• Do NOT pass large code blocks in text prompts - use file parameters instead
"""

FILE_UPLOAD_GUIDANCE = """
FILE UPLOAD METHOD SELECTION

🎯 RECOMMENDED: Use smart_file_query tool for ALL file operations
- Automatically handles deduplication (SHA256-based)
- Intelligent provider selection (Kimi vs GLM)
- Automatic fallback on provider failure
- Centralized Supabase tracking
- Single unified interface

Example: smart_file_query(file_path="/mnt/project/...", question="Analyze this code")

LEGACY TOOLS (Still available but prefer smart_file_query):

• <50KB: Use files parameter directly (embed in prompt)
  - Fastest method, no upload needed
  - Directly embedded in AI prompt
  - Example: Pass file path in 'files' parameter

• 0.5-5MB: Use direct upload to provider
  - For Kimi: Use kimi_upload_files tool
  - For GLM: Use glm_upload_file tool
  - Fast, efficient, within API limits
  - Example: kimi_upload_files(files=[file_path])

• 5-20MB: Use Supabase gateway (RECOMMENDED)
  - For Kimi: Direct URL extraction from Supabase
  - For GLM: Pre-signed URLs with download/upload
  - Centralized tracking in Supabase
  - Single source of truth for file management
  - Example: upload_via_supabase_gateway_kimi(file_path, storage)

• 20-100MB: Use Supabase gateway (Kimi only)
  - GLM has 20MB limit (not supported)
  - Kimi supports up to 100MB via URL extraction
  - Example: upload_via_supabase_gateway_kimi(file_path, storage)

• >100MB: Contact administrator
  - Exceeds all API limits
  - Requires Supabase Storage only
  - No AI processing available

IMPORTANT: Always check file size first using select_upload_method(file_path)
See AGENT_FILE_UPLOAD_GUIDE.md for detailed instructions and code examples
"""

SMART_FILE_QUERY_GUIDANCE = """
SMART FILE QUERY - UNIFIED FILE OPERATIONS

🎯 PRIMARY INTERFACE for all file upload and query operations

⚠️ CRITICAL: FILES MUST EXIST IN ACCESSIBLE DIRECTORIES
• ACCESSIBLE: /mnt/project/EX-AI-MCP-Server/* (main project)
• ACCESSIBLE: /mnt/project/Personal_AI_Agent/* (AI agent project)
• NOT ACCESSIBLE: Any other paths (e.g., /mnt/project/Mum/*, /mnt/project/Documents/*)
• If you need to analyze external files, copy them into an accessible directory first

FEATURES:
• Automatic SHA256-based deduplication (reuses existing uploads)
• Intelligent provider selection (file size + user preference)
• Automatic fallback (GLM fails → Kimi, vice versa)
• Centralized Supabase tracking
• Path validation and security checks

USAGE:
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",  # MUST be in accessible directory
    question="Analyze this code for security issues",
    provider="auto",  # Optional: "kimi", "glm", or "auto" (default)
    model="auto"      # Optional: specific model or "auto" (default)
)

PROVIDER SELECTION LOGIC:
1. User preference (if provider specified)
2. File size:
   - <20MB: GLM (faster, cheaper)
   - 20-100MB: Kimi (larger limit)
   - >100MB: Error (exceeds all limits)
3. Automatic fallback on failure

PATH REQUIREMENTS:
• MUST use Linux paths: /mnt/project/EX-AI-MCP-Server/... or /mnt/project/Personal_AI_Agent/...
• Windows paths NOT supported: c:\\Project\\... ❌
• Relative paths NOT supported: ./file.py ❌
• Path traversal blocked: /mnt/project/../etc/passwd ❌
• Files outside accessible directories: NOT SUPPORTED ❌

DEDUPLICATION:
• Files are identified by SHA256 hash
• Same file uploaded multiple times = single upload
• Reference counting tracks usage
• Automatic cleanup of unreferenced files

SUPABASE TRACKING:
• All uploads tracked in provider_file_uploads table
• Bidirectional mapping (provider_file_id ↔ supabase_file_id)
• Upload status, timestamps, file metadata
• Centralized audit trail
"""

# Export for easy import
__all__ = ['FILE_PATH_GUIDANCE', 'FILE_UPLOAD_GUIDANCE', 'SMART_FILE_QUERY_GUIDANCE']

