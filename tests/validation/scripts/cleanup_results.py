"""
Cleanup Results - Manage test result history

This script manages test result storage:
- Archive old results to history/
- Compress archived results
- Delete results older than N days
- Clean up cache directories
- Free up disk space

Usage:
    python scripts/cleanup_results.py [--keep-days 30] [--compress] [--dry-run]

Created: 2025-10-05
"""

import argparse
import gzip
import json
import logging
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_directory_size(path):
    """Calculate total size of directory in bytes."""
    total = 0
    for entry in path.rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total


def format_size(bytes_size):
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def archive_latest_results(dry_run=False):
    """Archive latest results to history."""
    latest_dir = Path("tool_validation_suite/results/latest")
    history_dir = Path("tool_validation_suite/results/history")
    
    if not latest_dir.exists():
        logger.warning("No latest results to archive")
        return None
    
    # Create timestamp-based archive name
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_name = f"results_{timestamp}"
    archive_path = history_dir / archive_name
    
    if dry_run:
        logger.info(f"[DRY RUN] Would archive: {latest_dir} -> {archive_path}")
        return None
    
    # Create history directory
    history_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy latest to history
    logger.info(f"Archiving: {latest_dir} -> {archive_path}")
    shutil.copytree(latest_dir, archive_path)
    
    return archive_path


def compress_archive(archive_path, dry_run=False):
    """Compress archived results."""
    if not archive_path or not archive_path.exists():
        return
    
    # Compress JSON files
    json_files = list(archive_path.rglob("*.json"))
    
    for json_file in json_files:
        gz_file = json_file.with_suffix('.json.gz')
        
        if dry_run:
            logger.info(f"[DRY RUN] Would compress: {json_file}")
            continue
        
        try:
            with open(json_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original
            json_file.unlink()
            logger.info(f"Compressed: {json_file.name}")
        
        except Exception as e:
            logger.error(f"Failed to compress {json_file}: {e}")


def delete_old_results(keep_days, dry_run=False):
    """Delete results older than keep_days."""
    history_dir = Path("tool_validation_suite/results/history")
    
    if not history_dir.exists():
        logger.warning("No history directory found")
        return 0
    
    cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
    deleted_count = 0
    freed_space = 0
    
    for result_dir in history_dir.iterdir():
        if not result_dir.is_dir():
            continue
        
        # Get directory modification time
        mtime = datetime.fromtimestamp(result_dir.stat().st_mtime)
        
        if mtime < cutoff_date:
            size = get_directory_size(result_dir)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would delete: {result_dir.name} ({format_size(size)})")
            else:
                logger.info(f"Deleting: {result_dir.name} ({format_size(size)})")
                shutil.rmtree(result_dir)
                freed_space += size
            
            deleted_count += 1
    
    return freed_space


def clean_cache(dry_run=False):
    """Clean conversation cache directories."""
    cache_dirs = [
        Path("tool_validation_suite/cache/kimi"),
        Path("tool_validation_suite/cache/glm")
    ]
    
    freed_space = 0
    
    for cache_dir in cache_dirs:
        if not cache_dir.exists():
            continue
        
        size = get_directory_size(cache_dir)
        
        if dry_run:
            logger.info(f"[DRY RUN] Would clean cache: {cache_dir} ({format_size(size)})")
        else:
            logger.info(f"Cleaning cache: {cache_dir} ({format_size(size)})")
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            freed_space += size
    
    return freed_space


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Cleanup test results")
    parser.add_argument("--keep-days", type=int, default=30, help="Keep results for N days")
    parser.add_argument("--compress", action="store_true", help="Compress archived results")
    parser.add_argument("--clean-cache", action="store_true", help="Clean conversation cache")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual deletion")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    print("\n" + "="*60)
    print("  RESULTS CLEANUP")
    print("="*60)
    print(f"Keep Days: {args.keep_days}")
    print(f"Compress: {args.compress}")
    print(f"Clean Cache: {args.clean_cache}")
    print(f"Dry Run: {args.dry_run}")
    print("="*60 + "\n")
    
    total_freed = 0
    
    try:
        # Archive latest results
        logger.info("Archiving latest results...")
        archive_path = archive_latest_results(args.dry_run)
        
        if archive_path and args.compress:
            logger.info("Compressing archive...")
            compress_archive(archive_path, args.dry_run)
        
        # Delete old results
        logger.info(f"Deleting results older than {args.keep_days} days...")
        freed = delete_old_results(args.keep_days, args.dry_run)
        total_freed += freed
        
        # Clean cache
        if args.clean_cache:
            logger.info("Cleaning conversation cache...")
            freed = clean_cache(args.dry_run)
            total_freed += freed
        
        # Print summary
        print("\n" + "="*60)
        print("  CLEANUP COMPLETE")
        print("="*60)
        
        if args.dry_run:
            print("\n[DRY RUN] No files were actually deleted")
        else:
            print(f"\nSpace Freed: {format_size(total_freed)}")
        
        print("\n✅ Cleanup complete!")
        
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        print(f"\n❌ Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

