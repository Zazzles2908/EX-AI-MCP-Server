#!/usr/bin/env python3
"""
EXAI MCP Server - Claude Code Connection Setup Script

This script automates the process of connecting Claude Code to the EXAI MCP Server.
It generates the necessary `.mcp.json` configuration files and validates the connection.

Usage:
    python scripts/setup_claude_connection.py --project-path /path/to/your/project
    python scripts/setup_claude_connection.py --global-setup
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Paths
EXAI_PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ROOT = Path("c:/Users/Jazeel-Home/.claude")
EXAI_VENV_PYTHON = EXAI_PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
WS_SHIM_SCRIPT = EXAI_PROJECT_ROOT / "scripts" / "runtime" / "run_ws_shim.py"
ENV_FILE = EXAI_PROJECT_ROOT / ".env"

# JWT Token for Claude
EXAI_JWT_TOKEN_CLAUDE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0"

def generate_mcp_config():
    """Generate the complete MCP configuration for EXAI."""

    config = {
        "mcpServers": {
            "claude-enhancements": {
                "command": "python",
                "args": ["c:/Users/Jazeel-Home/.claude/claude_enhancements_mcp/server.py"],
                "env": {
                    "PYTHONPATH": "c:/Users/Jazeel-Home/.claude"
                }
            },
            "exai-mcp": {
                "command": str(EXAI_VENV_PYTHON),
                "args": [
                    "-u",
                    str(WS_SHIM_SCRIPT)
                ],
                "env": {
                    "ENV_FILE": str(ENV_FILE),
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONIOENCODING": "utf-8",
                    "LOG_LEVEL": "INFO",
                    "EXAI_WS_HOST": "127.0.0.1",
                    "EXAI_WS_PORT": "8079",
                    "EXAI_JWT_TOKEN": EXAI_JWT_TOKEN_CLAUDE,
                    "EX_SESSION_SCOPE_STRICT": "true",
                    "EX_SESSION_SCOPE_ALLOW_CROSS_SESSION": "false",
                    "SIMPLE_TOOL_TIMEOUT_SECS": "60",
                    "WORKFLOW_TOOL_TIMEOUT_SECS": "120",
                    "EXPERT_ANALYSIS_TIMEOUT_SECS": "90",
                    "GLM_TIMEOUT_SECS": "90",
                    "KIMI_TIMEOUT_SECS": "120",
                    "KIMI_WEB_SEARCH_TIMEOUT_SECS": "150"
                }
            }
        }
    }

    return config

def write_mcp_config(project_path):
    """Write the MCP configuration to the project's .mcp.json file."""

    project_path = Path(project_path)
    mcp_config_path = project_path / ".mcp.json"

    config = generate_mcp_config()

    with open(mcp_config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Created {mcp_config_path}")
    return mcp_config_path

def setup_global_config():
    """Set up global MCP configuration for all projects."""

    global_config_path = CLAUDE_ROOT / "mcp_config_exai.json"

    config = {
        "mcpServers": {
            "exai-mcp": {
                "command": str(EXAI_VENV_PYTHON),
                "args": [
                    "-u",
                    str(WS_SHIM_SCRIPT)
                ],
                "env": {
                    "ENV_FILE": str(ENV_FILE),
                    "PYTHONUNBUFFERED": "1",
                    "LOG_LEVEL": "INFO",
                    "EXAI_WS_HOST": "127.0.0.1",
                    "EXAI_WS_PORT": "8079",
                    "EXAI_JWT_TOKEN": EXAI_JWT_TOKEN_CLAUDE
                }
            }
        }
    }

    with open(global_config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Created global config: {global_config_path}")
    return global_config_path

def validate_exai_server():
    """Validate that the EXAI MCP server is running."""

    try:
        # Check if port 8079 is listening
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8079))
        sock.close()

        if result == 0:
            print("✅ EXAI MCP Server is running on port 8079")
            return True
        else:
            print("❌ EXAI MCP Server is NOT running on port 8079")
            print("\nTo start the server:")
            print("  cd /c/Project/EX-AI-MCP-Server")
            print("  docker-compose up -d")
            return False

    except Exception as e:
        print(f"❌ Error checking EXAI server: {e}")
        return False

def validate_python_path():
    """Validate that the Python path in config is correct."""

    if not EXAI_VENV_PYTHON.exists():
        print(f"❌ Python executable not found at: {EXAI_VENV_PYTHON}")
        print("\nTo fix this, ensure the EXAI project is properly set up:")
        print("  cd /c/Project/EX-AI-MCP-Server")
        print("  .venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        return False

    print(f"✅ Python executable found: {EXAI_VENV_PYTHON}")
    return True

def print_usage_instructions(project_path):
    """Print instructions for using the MCP connection."""

    print("\n" + "="*70)
    print("🎉 CONNECTION SETUP COMPLETE!")
    print("="*70)

    print(f"\n📁 Configuration created at:")
    print(f"   {project_path}/.mcp.json")

    print("\n🚀 Next Steps:")
    print("   1. Open Claude Code")
    print("   2. Open your project folder")
    print("   3. The EXAI MCP server will auto-connect!")

    print("\n✅ Test the connection in Claude Code:")
    print("   @exai-mcp status")
    print("   @exai-mcp chat \"Hello from Claude Code!\"")

    print("\n📚 Available Tools (33 total):")
    print("   Essential: status, chat, planner")
    print("   Core: analyze, codereview, debug, refactor, testgen")
    print("   Advanced: consensus, docgen, secaudit, tracer")

    print("\n📖 Full documentation:")
    print("   /c/Project/EX-AI-MCP-Server/CLAUDE_CODE_CONNECTION_GUIDE.md")

def main():
    parser = argparse.ArgumentParser(
        description="Set up Claude Code to connect to EXAI MCP Server"
    )

    parser.add_argument(
        "--project-path",
        type=str,
        help="Path to the project to configure (creates .mcp.json)"
    )

    parser.add_argument(
        "--global-setup",
        action="store_true",
        help="Set up global MCP configuration for all projects"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the EXAI server and configuration"
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("🔌 EXAI MCP Server - Claude Code Connection Setup")
    print("="*70 + "\n")

    # Validation
    print("🔍 Validating EXAI MCP Server...")
    server_ok = validate_exai_server()

    print("\n🔍 Validating Python configuration...")
    python_ok = validate_python_path()

    if not server_ok or not python_ok:
        print("\n❌ Validation failed. Please fix the issues above.")
        sys.exit(1)

    if args.validate_only:
        print("\n✅ All validations passed!")
        sys.exit(0)

    # Setup
    if args.global_setup:
        print("\n📝 Setting up global MCP configuration...")
        config_path = setup_global_config()
        print("\n✅ Global setup complete!")
        print(f"\nAdd this to your Claude Code settings:")
        print(f"  \"mcpServers\": {{\"exai-mcp\": {{\"command\": \"...\"}}}}")

    elif args.project_path:
        print(f"\n📝 Setting up project: {args.project_path}")
        config_path = write_mcp_config(args.project_path)
        print_usage_instructions(Path(args.project_path))

    else:
        print("\n❌ Please specify either --project-path or --global-setup")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
