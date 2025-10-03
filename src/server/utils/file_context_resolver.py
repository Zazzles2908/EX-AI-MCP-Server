"""
File context resolver for EXAI workflow tools.

Purpose:
- Expand provided glob patterns into a bounded list of absolute file paths
- Enforce an allow-list root directory (e.g., TEST_FILES_DIR) for safety
- Apply limits for max file count and total bytes
- Return a de-duplicated, sorted list of files

Design:
- Keep simple, pluggable, and safe. This module can be swapped or extended later.
- No external side effects; callers handle logging and retries.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple
import os
import glob


class FileContextError(ValueError):
    pass


def _normalize_roots(root: str | None) -> List[Path]:
    """
    Accepts a single path or a list of paths separated by comma, semicolon, or os.pathsep.
    Falls back to TEST_FILES_DIR env when root is None/empty.
    """
    raw = root or os.getenv("TEST_FILES_DIR")
    if not raw:
        raise FileContextError("TEST_FILES_DIR is not set. Configure absolute path(s) in .env/.env.example.")
    # Normalize separators: support ',', ';', and os.pathsep
    seps = [",", ";", os.pathsep]
    tmp = raw
    for s in seps:
        if s:
            tmp = tmp.replace(s, ",")
    tokens = [t.strip().strip('"').strip("'") for t in tmp.split(",") if t.strip()]
    roots: List[Path] = []
    for tok in tokens:
        p = Path(tok).resolve()
        if not p.exists() or not p.is_dir():
            continue
        roots.append(p)
    if not roots:
        raise FileContextError(f"No valid allow-list root(s) found from TEST_FILES_DIR: {raw}")
    return roots


def _is_under_any_root(path: Path, roots: List[Path]) -> bool:
    try:
        path = path.resolve()
        for r in roots:
            if r in path.parents or path == r:
                return True
        return False
    except Exception:
        return False


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path = path.resolve()
        return root in path.parents or path == root
    except Exception:
        return False


def _collect_from_globs(globs: Iterable[str], roots: List[Path], max_each: int = 50) -> List[Path]:
    out: List[Path] = []
    for g in list(globs)[:8]:
        try:
            for m in glob.glob(g, recursive=True)[:max_each]:
                if isinstance(m, str):
                    p = Path(m).resolve()
                    if p.is_file() and _is_under_any_root(p, roots):
                        out.append(p)
        except (OSError, ValueError, TypeError) as e:
            # ignore malformed patterns - log at debug level for troubleshooting
            import logging
            logging.getLogger(__name__).debug(f"Glob pattern '{g}' failed: {e}")
            continue
    return out


def _enforce_limits(paths: List[Path], max_files: int, max_bytes: int) -> Tuple[List[Path], int]:
    unique = []
    seen = set()
    total = 0
    for p in sorted(paths):
        s = str(p)
        if s in seen:
            continue
        seen.add(s)
        try:
            size = p.stat().st_size
        except (OSError, PermissionError) as e:
            # Skip files we can't stat (permissions, deleted, etc.)
            import logging
            logging.getLogger(__name__).debug(f"Cannot stat file '{p}': {e}")
            continue
        if total + size > max_bytes:
            break
        unique.append(p)
        total += size
        if len(unique) >= max_files:
            break
    return unique, total


def resolve_files(
    globs: Iterable[str] | None,
    *,
    root: str | None = None,
    max_files: int = 50,
    max_bytes: int = 5 * 1024 * 1024,
) -> List[str]:
    """
    Resolve user/tool-supplied glob patterns to a safe, bounded list of absolute files under allow-list root(s).

    - root(s): defaults to TEST_FILES_DIR when not provided (single path or list)
    - max_files: cap number of files
    - max_bytes: cap cumulative size
    """
    roots = _normalize_roots(root)
    globs = list(globs or [])
    if not globs:
        raise FileContextError("No file globs provided. Supply patterns or pre-fill files.")
    candidates = _collect_from_globs(globs, roots)
    if not candidates:
        raise FileContextError("No files matched under allow-list root(s) (TEST_FILES_DIR).")
    bounded, total = _enforce_limits(candidates, max_files=max_files, max_bytes=max_bytes)
    if not bounded:
        raise FileContextError("Matched files exceeded configured limits (files/bytes). Reduce scope.")
    return [str(p) for p in bounded]

