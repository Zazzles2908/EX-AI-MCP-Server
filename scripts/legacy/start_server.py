#!/usr/bin/env python3
"""
EXAI MCP Server Startup Script

This script starts the EXAI MCP Server with proper error handling
and dependency checks.

Fixed Issues:
- ModuleNotFoundError for storage module (fixed with __init__.py and relative imports)
- Import path errors in storage_manager.py (fixed with relative imports)
- Missing __init__.py files in packages (created for daemon, infrastructure, storage)
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []

    try:
        import supabase
        logger.info("✓ supabase package found")
    except ImportError:
        missing_deps.append("supabase")
        logger.error("✗ supabase package not found")

    try:
        import websockets
        logger.info("✓ websockets package found")
    except ImportError:
        missing_deps.append("websockets")
        logger.error("✗ websockets package not found")

    return missing_deps

def setup_paths():
    """Setup Python paths for imports"""
    # Add project root and src to path
    # Project root is needed for absolute imports like "from src.resilience..."
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    src_path = os.path.join(project_root, 'src')
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"Added {project_root} to Python path (position 0)")
    if src_path not in sys.path:
        sys.path.insert(1, src_path)
        logger.info(f"Added {src_path} to Python path (position 1)")

def test_imports():
    """Test that critical imports work"""
    try:
        # Test storage imports (this was failing before the fix)
        from storage.storage_manager import SupabaseStorageManager
        from storage.storage_exceptions import RetryableError, NonRetryableError
        logger.info("✓ storage module imports working correctly")

        # Test daemon imports
        from daemon.monitoring_endpoint import start_monitoring_server
        logger.info("✓ daemon module imports working correctly")

        return True
    except ImportError as e:
        logger.error(f"✗ Import test failed: {e}")
        return False

def start_daemon():
    """Start the WebSocket daemon"""
    try:
        from scripts.ws.run_ws_daemon import main as run_daemon
        logger.info("Starting EXAI WebSocket Daemon...")
        run_daemon()
    except Exception as e:
        logger.error(f"Failed to start daemon: {e}")
        raise

def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("EXAI MCP Server Startup")
    logger.info("=" * 60)

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ required")
        sys.exit(1)

    logger.info(f"Python version: {sys.version}")

    # Setup paths
    setup_paths()

    # Check dependencies
    logger.info("\nChecking dependencies...")
    missing = check_dependencies()
    if missing:
        logger.error(f"\nMissing dependencies: {', '.join(missing)}")
        logger.error("Please install with: pip install -r requirements.txt")
        sys.exit(1)

    # Test imports
    logger.info("\nTesting imports...")
    if not test_imports():
        logger.error("Import tests failed. Please check the fixes.")
        sys.exit(1)

    # Start daemon
    logger.info("\nStarting server...")
    start_daemon()

if __name__ == "__main__":
    main()
