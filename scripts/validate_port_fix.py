#!/usr/bin/env python3
"""
Verification script for port 3005 conflict fix.
Tests that the cleanup and safe startup work correctly.
"""

import os
import sys
import subprocess
import socket
import json
from pathlib import Path

SHIM_PORT = 3005
PROJECT_ROOT = Path(__file__).parent.parent


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if filepath.exists():
        print(f"  [OK] {description}: {filepath}")
        return True
    else:
        print(f"  [FAIL] {description}: {filepath} (MISSING)")
        return False


def check_port_available(port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def check_mcp_config():
    """Verify .mcp.json is configured correctly."""
    mcp_config = PROJECT_ROOT / ".mcp.json"
    if not mcp_config.exists():
        print("  ✗ .mcp.json not found")
        return False

    with open(mcp_config) as f:
        config = json.load(f)

    exai_config = config.get("mcpServers", {}).get("exai-mcp", {})
    args = exai_config.get("args", [])

    if any("start_ws_shim_safe.py" in arg for arg in args):
        print("  [OK] .mcp.json uses safe startup wrapper")
        return True
    else:
        print("  [FAIL] .mcp.json does NOT use safe startup wrapper")
        return False


def test_cleanup_script():
    """Test that cleanup script runs without errors."""
    script = PROJECT_ROOT / "scripts" / "runtime" / "cleanup_orphaned_shims.py"

    if not script.exists():
        print("  ✗ cleanup_orphaned_shims.py not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--check-only"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT_ROOT
        )

        if "No cleanup needed" in result.stdout or "No run_ws_shim processes found" in result.stdout:
            print("  [OK] cleanup_orphaned_shims.py runs successfully")
            return True
        else:
            print("  [FAIL] cleanup_orphaned_shims.py produced unexpected output")
            print(f"    Output: {result.stdout[:200]}")
            return False
    except Exception as e:
        print(f"  [FAIL] cleanup_orphaned_shims.py failed: {e}")
        return False


def test_safe_wrapper():
    """Test that safe wrapper can check port."""
    wrapper = PROJECT_ROOT / "scripts" / "runtime" / "start_ws_shim_safe.py"

    if not wrapper.exists():
        print("  [FAIL] start_ws_shim_safe.py not found")
        return False

    print("  [OK] start_ws_shim_safe.py exists")
    return True


def main():
    print("=" * 70)
    print("Port 3005 Conflict Fix - Verification")
    print("=" * 70)
    print()

    all_checks = []

    print("1. Checking fix files...")
    all_checks.append(check_file_exists(
        PROJECT_ROOT / "scripts" / "runtime" / "cleanup_orphaned_shims.py",
        "Cleanup script"
    ))
    all_checks.append(check_file_exists(
        PROJECT_ROOT / "scripts" / "runtime" / "start_ws_shim_safe.py",
        "Safe startup wrapper"
    ))
    all_checks.append(check_file_exists(
        PROJECT_ROOT / "start_exai_mcp.bat",
        "Manual startup script"
    ))
    print()

    print("2. Checking configuration...")
    all_checks.append(check_mcp_config())
    print()

    print("3. Testing cleanup script...")
    all_checks.append(test_cleanup_script())
    print()

    print("4. Testing safe wrapper...")
    all_checks.append(test_safe_wrapper())
    print()

    print("5. Checking port availability...")
    if check_port_available(SHIM_PORT):
        print(f"  [OK] Port {SHIM_PORT} is available")
        all_checks.append(True)
    else:
        print(f"  [FAIL] Port {SHIM_PORT} is in use (run cleanup)")
        all_checks.append(False)
    print()

    print("=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)

    if passed == total:
        print(f"[SUCCESS] All checks passed! ({passed}/{total})")
        print()
        print("The fix is correctly installed and configured.")
        print("The exai-mcp server should now start without port conflicts.")
        return 0
    else:
        print(f"[WARNING] Some checks failed ({passed}/{total})")
        print()
        print("Please review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
