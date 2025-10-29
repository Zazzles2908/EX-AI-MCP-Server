"""
Test helper utilities for file download system tests.
"""

import asyncio
import hashlib
from pathlib import Path
from typing import List, Tuple


def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_test_file(path: str, size_bytes: int, content: bytes = None) -> str:
    """Create a test file with specified size."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    if content:
        with open(path, 'wb') as f:
            f.write(content)
    else:
        with open(path, 'wb') as f:
            f.write(b'x' * size_bytes)
    
    return path


def create_test_files(base_dir: str, count: int = 5) -> List[Tuple[str, str]]:
    """Create multiple test files and return list of (path, hash) tuples."""
    files = []
    for i in range(count):
        file_path = f"{base_dir}/test_file_{i}.bin"
        create_test_file(file_path, 1024 * (i + 1))  # 1KB, 2KB, 3KB, etc.
        file_hash = calculate_sha256(file_path)
        files.append((file_path, file_hash))
    return files


async def simulate_concurrent_downloads(
    download_func,
    file_ids: List[str],
    concurrency: int = 5
) -> List[Tuple[str, bool, str]]:
    """
    Simulate concurrent downloads and return results.
    
    Returns:
        List of (file_id, success, result_or_error)
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    
    async def download_with_semaphore(file_id):
        async with semaphore:
            try:
                result = await download_func(file_id)
                return (file_id, True, result)
            except Exception as e:
                return (file_id, False, str(e))
    
    tasks = [download_with_semaphore(fid) for fid in file_ids]
    results = await asyncio.gather(*tasks)
    return results


def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
    """Verify file integrity by comparing SHA256 hashes."""
    actual_hash = calculate_sha256(file_path)
    return actual_hash == expected_hash


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return Path(file_path).stat().st_size

