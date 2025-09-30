"""Kimi file upload functionality."""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def upload_file(client: Any, file_path: str, purpose: str = "file-extract") -> str:
    """Upload a local file to Moonshot (Kimi) and return file_id.
    
    Args:
        client: OpenAI-compatible client instance
        file_path: Path to a local file
        purpose: Moonshot purpose tag (e.g., 'file-extract', 'assistants')
        
    Returns:
        The provider-assigned file id string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file exceeds size limit
        RuntimeError: If upload fails or doesn't return an ID
    """
    # Resolve relative paths from project root if not absolute
    p = Path(file_path)
    if not p.is_absolute():
        try:
            project_root = Path.cwd()
            p = (project_root / p).resolve()
        except Exception:
            p = p
    
    if not p.exists():
        # Friendlier message: show CWD and suggest possible path
        cwd = str(Path.cwd())
        raise FileNotFoundError(f"File not found: {file_path} (cwd={cwd})")
    
    # Optional client-side size guardrail (helps before provider returns 4xx)
    try:
        max_mb_env = os.getenv("KIMI_FILES_MAX_SIZE_MB", "")
        if max_mb_env:
            max_bytes = float(max_mb_env) * 1024 * 1024
            if p.stat().st_size > max_bytes:
                raise ValueError(f"Kimi upload exceeds max size {max_mb_env} MB: {p.name}")
    except ValueError:
        # Re-raise ValueError (size exceeded)
        raise
    except Exception:
        # Never block upload if env is malformed; rely on provider errors
        pass
    
    result = client.files.create(file=p, purpose=purpose)
    file_id = getattr(result, "id", None) or (result.get("id") if isinstance(result, dict) else None)
    if not file_id:
        raise RuntimeError("Moonshot upload did not return a file id")
    return file_id


__all__ = ["upload_file"]

