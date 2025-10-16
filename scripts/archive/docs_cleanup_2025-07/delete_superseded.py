"""
Delete superseded files identified by Kimi analysis.

This script reads the consolidation analysis and deletes all files
marked as superseded, creating a backup first.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_superseded_files(dry_run=True):
    """
    Delete all superseded files from the analysis.
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    
    # Load analysis
    analysis_file = Path("docs/COMPREHENSIVE_CONSOLIDATION_ANALYSIS.json")
    if not analysis_file.exists():
        logger.error(f"Analysis file not found: {analysis_file}")
        return
    
    with open(analysis_file, 'r') as f:
        batches = json.load(f)
    
    # Collect all superseded files
    superseded_files = []
    for batch in batches:
        if isinstance(batch, dict):
            superseded_files.extend(batch.get('superseded', []))
    
    logger.info(f"Found {len(superseded_files)} superseded files to delete")
    
    if dry_run:
        logger.info("=" * 80)
        logger.info("DRY RUN MODE - No files will be deleted")
        logger.info("=" * 80)
    
    # Create backup directory
    backup_dir = None
    if not dry_run:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f"docs/archive/cleanup_backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory created: {backup_dir}")
    
    # Process each file
    deleted_count = 0
    not_found_count = 0
    
    for item in superseded_files:
        if not isinstance(item, dict):
            continue
        
        file_path = item.get('file', '')
        reason = item.get('reason', 'No reason provided')
        
        if not file_path:
            continue
        
        # Convert to Path object
        full_path = Path(file_path)
        
        if not full_path.exists():
            logger.warning(f"File not found: {full_path}")
            not_found_count += 1
            continue
        
        logger.info(f"{'[DRY RUN] Would delete' if dry_run else 'Deleting'}: {full_path}")
        logger.info(f"  Reason: {reason}")
        
        if not dry_run:
            # Backup file
            backup_path = backup_dir / full_path.name
            shutil.copy2(full_path, backup_path)
            logger.info(f"  Backed up to: {backup_path}")
            
            # Delete file
            full_path.unlink()
            deleted_count += 1
        else:
            deleted_count += 1
    
    # Summary
    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total superseded files: {len(superseded_files)}")
    logger.info(f"{'Would delete' if dry_run else 'Deleted'}: {deleted_count}")
    logger.info(f"Not found: {not_found_count}")
    
    if not dry_run and backup_dir:
        logger.info(f"Backup location: {backup_dir}")
    
    if dry_run:
        logger.info("")
        logger.info("To actually delete files, run:")
        logger.info("  python scripts/docs_cleanup/delete_superseded.py --execute")

if __name__ == "__main__":
    import sys
    
    # Check for --execute flag
    execute = "--execute" in sys.argv or "-e" in sys.argv
    
    if execute:
        response = input("⚠️  This will DELETE files. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Aborted by user")
            sys.exit(0)
    
    delete_superseded_files(dry_run=not execute)

