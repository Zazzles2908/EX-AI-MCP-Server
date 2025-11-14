#!/usr/bin/env python3
"""
Comprehensive MCP Server Diagnostic Tool
Checks all MCP servers and provides detailed status report.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


def print_section(title: str):
    """Print section header."""
    print(f"\n{BLUE}::{title}{NC}")


def check_result(name: str, status: bool, message: str = ""):
    """Print check result."""
    if status:
        print(f"{GREEN}✓{NC} {name}")
        if message:
            print(f"  {message}")
    else:
        print(f"{RED}✗{NC} {name}")
        if message:
            print(f"  {RED}ERROR: {message}{NC}")


def check_exai_daemon() -> bool:
    """Check if EXAI daemon is running."""
    print_section("EXAI Daemon Health Check")

    try:
        import requests
        response = requests.get("http://127.0.0.1:3002/health", timeout=2)
        if response.status_code == 200:
            health = response.json()
            check_result("EXAI Daemon", True, f"Status: {health.get('status', 'unknown')}")
            return True
        else:
            check_result("EXAI Daemon", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        check_result("EXAI Daemon", False, str(e))
        return False


def check_docker_services() -> bool:
    """Check Docker services."""
    print_section("Docker Services Check")

    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            check_result("Docker Compose", True, f"Found {len(services)} service(s)")
            for line in result.stdout.split('\n'):
                if 'exai-mcp-daemon' in line:
                    check_result("exai-mcp-daemon", True)
            return True
        else:
            check_result("Docker Compose", False, result.stderr)
            return False
    except Exception as e:
        check_result("Docker Compose", False, str(e))
        return False


def check_environment() -> bool:
    """Check environment configuration."""
    print_section("Environment Configuration")

    required_vars = [
        "EXAI_WS_TOKEN",
        "EXAI_WS_PORT",
        "SHIM_LISTEN_PORT",
        "GLM_API_KEY",
        "KIMI_API_KEY",
    ]

    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = value[:10] + "..." if len(value) > 10 else value
            check_result(f"{var}", True, f"Set to: {display_value}")
        else:
            check_result(f"{var}", False, "Not set")
            all_ok = False

    return all_ok


def check_python_environment() -> bool:
    """Check Python environment."""
    print_section("Python Environment")

    check_result("Python Version", True, f"{sys.version.split()[0]}")

    # Check virtual environment
    venv_path = Path(__file__).parent.parent / ".venv"
    if venv_path.exists():
        check_result("Virtual Environment", True, str(venv_path))
    else:
        check_result("Virtual Environment", False, ".venv not found")

    # Check pip dependencies
    required_packages = ["mcp", "websockets", "python-dotenv"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            check_result(f"Package: {package}", True)
        except ImportError:
            check_result(f"Package: {package}", False, "Not installed")
            check_result("Python Dependencies", False)

    return True


def check_ws_shim() -> bool:
    """Check WebSocket Shim."""
    print_section("WebSocket Shim Check")

    # Check if port 3005 is in use
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_in_use = sock.connect_ex(("127.0.0.1", 3005)) == 0
    sock.close()

    if port_in_use:
        check_result("Shim Port 3005", True, "Port is in use (shim may be running)")
    else:
        check_result("Shim Port 3005", False, "Port is available (shim not running)")

    # Check shim scripts
    shim_script = Path(__file__).parent / "runtime" / "run_ws_shim.py"
    safe_script = Path(__file__).parent / "runtime" / "start_ws_shim_safe.py"

    if shim_script.exists():
        check_result("run_ws_shim.py", True)
    else:
        check_result("run_ws_shim.py", False, "Script not found")

    if safe_script.exists():
        check_result("start_ws_shim_safe.py", True)
    else:
        check_result("start_ws_shim_safe.py", False, "Script not found")

    # Check logs
    logs_dir = Path(__file__).parent.parent / "logs"
    ws_shim_logs = list(logs_dir.glob("ws_shim_*.log"))

    check_result("Shim Logs", True, f"Found {len(ws_shim_logs)} log file(s)")

    return not port_in_use  # Return False if shim is running


def test_mcp_servers() -> Dict[str, Tuple[bool, str]]:
    """Test each MCP server."""
    print_section("MCP Server Tests")

    results = {}

    # Load .mcp.json
    mcp_config_path = Path(__file__).parent.parent / ".mcp.json"
    if not mcp_config_path.exists():
        check_result(".mcp.json", False, "Configuration file not found")
        return results

    with open(mcp_config_path, 'r') as f:
        config = json.load(f)

    for server_name, server_config in config['mcpServers'].items():
        print(f"\n  Testing {server_name}...")

        command = server_config['command']
        args = server_config['args']

        # Check if command exists
        if command == "npx":
            # Test npx
            try:
                result = subprocess.run(
                    ["npx", "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    check_result(f"npx", True, f"v{result.stdout.decode().strip()}")
                else:
                    check_result(f"npx", False)
            except Exception as e:
                check_result(f"npx", False, str(e))
                results[server_name] = (False, "npx not available")
                continue
        elif command == "uvx":
            # Test uvx
            try:
                result = subprocess.run(
                    ["uv", "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    check_result(f"uv", True, result.stdout.decode().strip())
                else:
                    check_result(f"uv", False)
            except Exception as e:
                check_result(f"uv", False, str(e))
                results[server_name] = (False, "uv not available")
                continue
        elif command.startswith("C:/"):
            # Python script
            python_path = command
            if Path(python_path).exists():
                check_result(f"Python: {python_path}", True)
            else:
                check_result(f"Python: {python_path}", False, "Path not found")
                results[server_name] = (False, "Python executable not found")
                continue
        else:
            check_result(f"Command: {command}", False, "Unknown command type")
            results[server_name] = (False, "Unknown command")
            continue

        # Test server startup (with timeout)
        test_cmd = [command] + args
        try:
            proc = subprocess.Popen(
                test_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            # Send initialization message
            init_msg = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }) + "\n"

            try:
                stdout, stderr = proc.communicate(input=init_msg, timeout=3)
                if proc.returncode == 0:
                    check_result(f"{server_name}", True, "Server responds to initialization")
                    results[server_name] = (True, "OK")
                else:
                    check_result(f"{server_name}", False, f"Exit code: {proc.returncode}")
                    if stderr:
                        print(f"    stderr: {stderr[:100]}")
                    results[server_name] = (False, f"Exit code: {proc.returncode}")
            except subprocess.TimeoutExpired:
                proc.kill()
                check_result(f"{server_name}", True, "Server started (no response in 3s - likely waiting for MCP)")
                results[server_name] = (True, "OK (started but waiting)")
        except Exception as e:
            check_result(f"{server_name}", False, str(e))
            results[server_name] = (False, str(e))

    return results


def check_provider_registry() -> bool:
    """Check provider registry."""
    print_section("Provider Registry Check")

    try:
        # Try to import and use the registry
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from src.providers.registry import get_registry
        registry = get_registry()

        # Get providers
        providers = registry.providers
        check_result("Provider Registry", True, f"Found {len(providers)} provider(s): {list(providers.keys())}")

        # Test each provider
        for name, provider in providers.items():
            if hasattr(provider, 'get_model_configurations'):
                configs = provider.get_model_configurations()
                check_result(f"  {name}.get_model_configurations", True, f"{len(configs)} models")
            else:
                check_result(f"  {name}.get_model_configurations", False, "Method missing")

        return True
    except Exception as e:
        check_result("Provider Registry", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def generate_summary(results: Dict):
    """Generate summary report."""
    print_header("SUMMARY REPORT")

    print(f"\n{'-' * 70}")
    print("MCP Server Status:")
    print(f"{'-' * 70}")

    working = sum(1 for ok, _ in results.values() if ok)
    total = len(results)

    for server_name, (ok, msg) in results.items():
        status = f"{GREEN}✓ WORKING{NC}" if ok else f"{RED}✗ FAILED{NC}"
        print(f"{status:15} {server_name:25} {msg}")

    print(f"\n{'-' * 70}")
    print(f"Total: {working}/{total} MCP servers working")
    print(f"{'-' * 70}\n")

    # Recommendations
    print(f"{BLUE}RECOMMENDATIONS:{NC}\n")

    if working < total:
        print("1. Fix failed MCP servers by:")
        print("   - Checking dependencies (npm, npx, uv)")
        print("   - Verifying .mcp.json configuration")
        print("   - Checking Python environment")

    print("\n2. Start WS Shim:")
    print("   python scripts/runtime/start_ws_shim_safe.py")

    print("\n3. Test MCP connection:")
    print("   Use Claude Code MCP client to connect")

    print("\n4. Monitor logs:")
    print("   tail -f logs/ws_daemon.log")
    print("   tail -f logs/ws-shim.log")


def main():
    """Main diagnostic function."""
    print_header("EX-AI MCP Server Diagnostic Tool")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all checks
    checks = [
        ("EXAI Daemon", check_exai_daemon),
        ("Docker Services", check_docker_services),
        ("Environment", check_environment),
        ("Python Environment", check_python_environment),
        ("WS Shim", check_ws_shim),
        ("Provider Registry", check_provider_registry),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"{RED}Error in {name}: {e}{NC}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Test MCP servers
    mcp_results = test_mcp_servers()

    # Generate summary
    generate_summary(mcp_results)

    return 0 if all(mcp_results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
