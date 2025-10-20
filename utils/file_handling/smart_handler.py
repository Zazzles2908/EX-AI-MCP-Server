"""
Smart File Handler for EXAI MCP Server

Provides seamless file handling with automatic embed vs. upload decision.
Implements multi-factor decision logic based on file size, type, and content.

Phase 5 Implementation (2025-10-19): Seamless file handling
- Automatic file size detection (<5KB embed, >5KB upload)
- Path normalization (Windows ↔ Docker conversion)
- Transparent Kimi upload for large files
- Comprehensive error handling
"""

import os
import logging
import mimetypes
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SmartFileHandler:
    """
    Seamless file handling with automatic embed vs. upload decision.
    
    Features:
    - Automatic path normalization (Windows ↔ Docker)
    - Multi-factor decision logic (size, type, content)
    - Transparent Kimi upload for large files
    - Comprehensive error handling
    - Override options for advanced users
    """
    
    def __init__(self):
        """Initialize smart file handler with default thresholds"""
        # Configuration thresholds
        self.size_threshold = 5 * 1024  # 5KB
        self.token_threshold = 1000
        
        # File type classifications
        self.binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.img', '.iso',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz'
        }
        
        self.upload_extensions = {
            '.pdf', '.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac'
        }
        
        self.embed_extensions = {
            '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
            '.yaml', '.yml', '.md', '.txt', '.csv', '.log', '.sh',
            '.bash', '.zsh', '.fish', '.sql', '.toml', '.ini', '.conf'
        }
        
        logger.info("[SMART_FILE_HANDLER] Initialized with size_threshold=5KB, token_threshold=1000")
    
    async def handle_files(
        self, 
        file_paths: List[str], 
        context: str = "", 
        force_embed: bool = False, 
        force_upload: bool = False
    ) -> Dict[str, Any]:
        """
        Automatically handle files with best strategy.
        
        Args:
            file_paths: List of file paths to handle (Windows or Linux format)
            context: Optional context for decision making
            force_embed: Force embedding even for large files
            force_upload: Force upload even for small files
            
        Returns:
            Dictionary with:
            - embedded_content: List of embedded file contents
            - file_ids: List of uploaded file IDs
            - metadata: List of file metadata
            - errors: List of errors encountered
        """
        results = {
            'embedded_content': [],
            'file_ids': [],
            'metadata': [],
            'errors': []
        }
        
        logger.info(f"[SMART_FILE_HANDLER] Processing {len(file_paths)} files")
        
        for file_path in file_paths:
            try:
                # Step 1: Normalize path (Windows → Docker if needed)
                normalized_path = self._normalize_path(file_path)
                logger.debug(f"[SMART_FILE_HANDLER] Normalized: {file_path} → {normalized_path}")
                
                # Step 2: Validate file exists
                if not os.path.exists(normalized_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                # Step 3: Decide strategy (with overrides)
                if force_upload:
                    strategy = 'upload'
                    logger.debug(f"[SMART_FILE_HANDLER] Strategy: upload (forced)")
                elif force_embed:
                    strategy = 'embed'
                    logger.debug(f"[SMART_FILE_HANDLER] Strategy: embed (forced)")
                else:
                    strategy = self._decide_strategy(normalized_path)
                    logger.info(f"[SMART_FILE_HANDLER] Strategy: {strategy} for {os.path.basename(file_path)}")
                
                # Step 4: Execute strategy
                if strategy == 'embed':
                    content = self._read_and_embed(normalized_path)
                    results['embedded_content'].append(content)
                    logger.debug(f"[SMART_FILE_HANDLER] Embedded {len(content)} chars")
                elif strategy == 'upload':
                    file_id = await self._upload_to_kimi(normalized_path)
                    results['file_ids'].append(file_id)
                    logger.info(f"[SMART_FILE_HANDLER] Uploaded file_id: {file_id}")
                
                # Step 5: Track metadata
                file_size = os.path.getsize(normalized_path)
                results['metadata'].append({
                    'path': file_path,
                    'normalized_path': normalized_path,
                    'strategy': strategy,
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2),
                    'type': mimetypes.guess_type(normalized_path)[0]
                })
                
            except Exception as e:
                error_info = {
                    'path': file_path,
                    'error': str(e),
                    'type': type(e).__name__
                }
                results['errors'].append(error_info)
                logger.error(f"[SMART_FILE_HANDLER] Error processing {file_path}: {e}")
        
        # Summary logging
        logger.info(
            f"[SMART_FILE_HANDLER] Complete: "
            f"{len(results['embedded_content'])} embedded, "
            f"{len(results['file_ids'])} uploaded, "
            f"{len(results['errors'])} errors"
        )
        
        return results
    
    def _normalize_path(self, file_path: str) -> str:
        """
        Normalize path and determine the best access method.
        
        Handles:
        - Windows paths (C:\\...) → Docker paths (/mnt/c/...)
        - Relative paths → Absolute paths
        - Path validation
        
        Args:
            file_path: Original file path
            
        Returns:
            Normalized absolute path
        """
        # Try to resolve path in current environment first
        if os.path.exists(file_path):
            return os.path.abspath(file_path)
        
        # Handle Windows path conversion for Docker
        if ':\\' in file_path or file_path.startswith('C:'):
            # Convert Windows path to WSL/Docker path
            # C:\Project\file.txt → /mnt/c/Project/file.txt
            wsl_path = file_path.replace('\\', '/')
            
            # Handle drive letter conversion
            if ':' in wsl_path:
                drive_letter = wsl_path[0].lower()
                wsl_path = f"/mnt/{drive_letter}{wsl_path[2:]}"
            
            if os.path.exists(wsl_path):
                logger.debug(f"[PATH_NORMALIZE] Windows → Docker: {file_path} → {wsl_path}")
                return wsl_path
        
        # Try as relative path from current directory
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            return abs_path
        
        # Return original path if no conversion found
        logger.warning(f"[PATH_NORMALIZE] Could not normalize: {file_path}")
        return file_path
    
    def _decide_strategy(self, file_path: str) -> str:
        """
        Comprehensive decision logic for file handling strategy.
        
        Decision factors:
        1. Binary files → upload
        2. Large files (>5KB) → upload
        3. Document files → upload
        4. Code files → embed
        5. High token count → upload
        6. Default → embed
        
        Args:
            file_path: Normalized file path
            
        Returns:
            'embed' or 'upload'
        """
        # Get file metadata
        size = os.path.getsize(file_path)
        extension = os.path.splitext(file_path)[1].lower()
        
        # Rule 1: Binary files always upload
        if self._is_binary(file_path) or extension in self.binary_extensions:
            logger.debug(f"[DECISION] upload: binary file ({extension})")
            return 'upload'
        
        # Rule 2: Large files (>5KB) upload
        if size > self.size_threshold:
            logger.debug(f"[DECISION] upload: large file ({size} bytes > {self.size_threshold})")
            return 'upload'
        
        # Rule 3: Document files always upload
        if extension in self.upload_extensions:
            logger.debug(f"[DECISION] upload: document file ({extension})")
            return 'upload'
        
        # Rule 4: Code files embed (smaller, text-based)
        if extension in self.embed_extensions:
            logger.debug(f"[DECISION] embed: code file ({extension})")
            return 'embed'
        
        # Rule 5: Check estimated tokens for remaining text files
        try:
            content = self._read_file(file_path)
            estimated_tokens = len(content) // 4  # Rough estimate
            if estimated_tokens > self.token_threshold:
                logger.debug(f"[DECISION] upload: high token count (~{estimated_tokens} tokens)")
                return 'upload'
        except UnicodeDecodeError:
            # Binary content detected
            logger.debug(f"[DECISION] upload: binary content detected")
            return 'upload'
        
        # Default: embed small text files
        logger.debug(f"[DECISION] embed: default (small text file)")
        return 'embed'
    
    def _is_binary(self, file_path: str) -> bool:
        """
        Check if file is binary by looking for null bytes.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if binary, False if text
        """
        try:
            with open(file_path, 'tr', encoding='utf-8') as f:
                chunk = f.read(1024)
                if '\0' in chunk:
                    return True
            return False
        except (UnicodeDecodeError, OSError):
            return True
    
    def _read_file(self, file_path: str) -> str:
        """
        Read file content with proper encoding detection.
        
        Args:
            file_path: File path to read
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try latin-1 as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _read_and_embed(self, file_path: str) -> str:
        """
        Read file and format for embedding in prompt.
        
        Args:
            file_path: File path to read
            
        Returns:
            Formatted file content for embedding
        """
        content = self._read_file(file_path)
        filename = os.path.basename(file_path)
        return f"\n**File: {filename}**\nCONTENT:\n{content}\n"
    
    async def _upload_to_kimi(self, file_path: str) -> str:
        """
        Upload file to Kimi platform using provider API.

        Args:
            file_path: File path to upload

        Returns:
            Kimi file_id
        """
        import asyncio
        from src.providers.registry import ModelProviderRegistry
        from src.providers.kimi import KimiModelProvider

        try:
            # Get Kimi provider
            default_model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")
            prov = ModelProviderRegistry.get_provider_for_model(default_model)

            if not isinstance(prov, KimiModelProvider):
                # Fallback: create provider directly
                api_key = os.getenv("KIMI_API_KEY", "")
                if not api_key:
                    raise RuntimeError("KIMI_API_KEY is not configured")
                prov = KimiModelProvider(api_key=api_key)

            # Upload file (sync function, wrap in thread)
            file_id = await asyncio.to_thread(
                prov.upload_file,
                file_path,
                purpose="file-extract"
            )

            if file_id:
                logger.info(f"[KIMI_UPLOAD] Success: {os.path.basename(file_path)} → {file_id}")
                return file_id

            raise Exception("Upload failed: No file_id returned")

        except Exception as e:
            logger.error(f"[KIMI_UPLOAD] Failed: {e}")
            raise


# Singleton instance
smart_file_handler = SmartFileHandler()

