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

Based on file size, select the optimal upload method:

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

# Export for easy import
__all__ = ['FILE_PATH_GUIDANCE', 'FILE_UPLOAD_GUIDANCE']

