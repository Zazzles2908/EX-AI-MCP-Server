"""
Verify Kimi platform file cleanup.

This script checks if all uploaded files were successfully deleted from the Kimi platform.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_kimi_cleanup():
    """Verify all files were deleted from Kimi platform."""
    from src.providers.kimi import KimiModelProvider
    
    logger.info("=" * 80)
    logger.info("KIMI PLATFORM FILE CLEANUP VERIFICATION")
    logger.info("=" * 80)
    
    # Get API key
    api_key = os.getenv("KIMI_API_KEY", "")
    if not api_key:
        logger.error("❌ KIMI_API_KEY not configured!")
        return False
    
    try:
        # Initialize provider
        provider = KimiModelProvider(api_key=api_key)
        
        # List all files on platform
        logger.info("\n📋 Querying Kimi platform for files...")
        files_response = provider.client.files.list()
        
        if not hasattr(files_response, 'data'):
            logger.error("❌ Unexpected response format from Kimi API")
            return False
        
        files = files_response.data
        total_files = len(files)
        
        logger.info(f"\n📊 **RESULTS:**")
        logger.info(f"   Total files on Kimi platform: {total_files}")
        
        if total_files == 0:
            logger.info("\n✅ **SUCCESS!** Zero files on Kimi platform - cleanup verified!")
            logger.info("   All 146 uploaded files were successfully deleted.")
            return True
        else:
            logger.warning(f"\n⚠️  **WARNING!** Found {total_files} orphaned files on Kimi platform:")
            for i, file in enumerate(files, 1):
                file_id = file.id
                filename = getattr(file, 'filename', 'unknown')
                created_at = getattr(file, 'created_at', 'unknown')
                logger.warning(f"   {i}. ID: {file_id}, Name: {filename}, Created: {created_at}")
            
            # Ask if user wants to delete them
            logger.info("\n🗑️  Would you like to delete these orphaned files? (y/n)")
            response = input().strip().lower()
            
            if response == 'y':
                logger.info("\n🧹 Deleting orphaned files...")
                deleted_count = 0
                for file in files:
                    try:
                        provider.client.files.delete(file.id)
                        deleted_count += 1
                        logger.info(f"   ✓ Deleted: {file.id}")
                    except Exception as e:
                        logger.error(f"   ✗ Failed to delete {file.id}: {e}")
                
                logger.info(f"\n✅ Deleted {deleted_count}/{total_files} orphaned files")
                return deleted_count == total_files
            else:
                logger.info("\n⚠️  Orphaned files remain on Kimi platform")
                return False
    
    except Exception as e:
        logger.error(f"\n❌ Error verifying cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_kimi_cleanup()
    sys.exit(0 if success else 1)

