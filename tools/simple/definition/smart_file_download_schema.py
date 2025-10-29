"""
MCP Tool Schema for Smart File Download

This schema defines the smart_file_download tool for the MCP protocol,
making it visible and usable by external agents (Claude, other AI assistants).

The tool provides seamless file download capabilities with automatic caching,
integrity verification, and provider fallback.
"""

from pydantic import BaseModel, Field
from typing import Optional


class SmartFileDownloadInput(BaseModel):
    """Input schema for smart_file_download tool."""
    
    file_id: str = Field(
        ...,
        description=(
            "REQUIRED. Provider file ID to download. "
            "This can be a Kimi/Moonshot file ID (e.g., 'file_abc123') or Supabase file ID. "
            "The tool automatically determines which provider has the file and downloads from the appropriate source."
        )
    )
    
    destination: Optional[str] = Field(
        None,
        description=(
            "Optional destination path for the downloaded file. "
            "Can be either a directory path or a full file path. "
            "MUST be within /mnt/project/ directory (Docker container path). "
            "If not specified, defaults to /mnt/project/downloads/. "
            "Examples: '/mnt/project/downloads/', '/mnt/project/scripts/my_file.py'"
        )
    )


# Tool definition for MCP protocol
SMART_FILE_DOWNLOAD_TOOL = {
    "name": "smart_file_download_EXAI-WS-VSCode2",
    "description": (
        "SEAMLESS FILE DOWNLOAD - Download files from AI providers with automatic caching and integrity verification.\n\n"
        "🎯 USE THIS FOR:\n"
        "- Download AI-generated files (code, documents, images)\n"
        "- Retrieve previously uploaded files from Kimi/Moonshot\n"
        "- Download files with automatic integrity verification\n"
        "- Batch download multiple files\n\n"
        "⚡ INTELLIGENT FEATURES:\n"
        "- Cache-first strategy: Local cache → Kimi API → Supabase Storage (automatic fallback)\n"
        "- SHA256 integrity verification on all downloads (detects corruption)\n"
        "- Provider auto-detection (automatically determines Kimi vs Supabase)\n"
        "- Concurrent download protection (prevents duplicate downloads of same file)\n"
        "- Download tracking (records download history, performance metrics, analytics)\n"
        "- Error handling with automatic retry (exponential backoff, max 3 attempts)\n"
        "- Size-based cache expiry: Small files (14 days), Medium (7 days), Large (3 days)\n\n"
        "🔌 PROVIDER SUPPORT:\n"
        "- ✅ Kimi/Moonshot: Full support (persistent files, 30+ days retention)\n"
        "- ✅ Supabase: Full support (permanent storage)\n"
        "- ❌ GLM/Z.ai: NOT SUPPORTED (files are session-bound only, cannot be downloaded)\n\n"
        "📁 FILE PATHS:\n"
        "- All downloads MUST be within /mnt/project/ directory\n"
        "- Default destination: /mnt/project/downloads/\n"
        "- Accessible paths: /mnt/project/EX-AI-MCP-Server/*, /mnt/project/Personal_AI_Agent/*\n\n"
        "🔒 SECURITY:\n"
        "- Automatic SHA256 hash verification\n"
        "- Path validation (prevents directory traversal)\n"
        "- Corrupted files automatically deleted\n\n"
        "💡 USAGE EXAMPLES:\n"
        "1. Simple download: smart_file_download(file_id='file_abc123')\n"
        "2. Custom destination: smart_file_download(file_id='file_abc123', destination='/mnt/project/scripts/')\n"
        "3. Batch download: [smart_file_download(file_id=id) for id in file_ids]\n\n"
        "⚠️ LIMITATIONS & ERROR HANDLING:\n"
        "- GLM/Z.ai files CANNOT be downloaded (session-bound only, no download API)\n"
        "- Network timeouts: Automatic retry with exponential backoff (max 3 attempts)\n"
        "- Provider failures: Automatic fallback to Supabase storage\n"
        "- Corrupted files: Automatically detected and re-downloaded\n"
        "- Invalid file_id: Validated before attempting download\n\n"
        "📊 PERFORMANCE:\n"
        "- Small files (<10MB): <2 seconds (cache hit: <0.1s)\n"
        "- Medium files (10-100MB): <30 seconds (cache hit: <0.5s)\n"
        "- Large files (>100MB): <5 minutes (cache hit: <2s)\n"
        "- Cache hit rate: Typically >80% for frequently accessed files\n\n"
        "Perfect for: downloading AI-generated content, retrieving uploaded files, batch downloads, file backup operations, cross-session file access."
    ),
    "inputSchema": SmartFileDownloadInput.model_json_schema()
}


def get_tool_definition():
    """Return the tool definition for registration."""
    return SMART_FILE_DOWNLOAD_TOOL

