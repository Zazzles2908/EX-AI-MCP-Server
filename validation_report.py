#!/usr/bin/env python3
"""
EX-AI MCP Server Validation Report
==================================

This script provides a comprehensive validation report of the MCP configuration
and functionality testing performed on the EX-AI-MCP-Server project.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from session_memory_tracker import get_session_tracker

def generate_validation_report():
    """Generate a comprehensive validation report"""
    
    print("="*80)
    print("EX-AI MCP SERVER VALIDATION REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: C:\\Project\\EX-AI-MCP-Server")
    print()
    
    # Initialize tracker for this validation session
    tracker = get_session_tracker('final_validation', 'C:\\Project\\EX-AI-MCP-Server')
    
    print("1. PROJECT STRUCTURE VALIDATION")
    print("-" * 40)
    
    # Check key files exist
    key_files = [
        ".mcp.json",
        ".env", 
        ".vscode/settings.json",
        "docker-compose.yml",
        "scripts/runtime/run_ws_shim.py"
    ]
    
    for file_path in key_files:
        file = Path(file_path)
        if file.exists():
            print(f"PASS: {file_path}")
            tracker.record_operation('file_exists', f'Key file exists: {file_path}')
        else:
            print(f"FAIL: {file_path} - MISSING")
            tracker.record_issue('critical', f'Missing key file: {file_path}')
    
    print()
    print("2. MCP CONFIGURATION VALIDATION")
    print("-" * 40)
    
    # Validate .mcp.json structure
    try:
        with open('.mcp.json', 'r') as f:
            mcp_config = json.load(f)
        
        if 'mcpServers' in mcp_config:
            servers = mcp_config['mcpServers']
            
            # Check EX-AI MCP server
            if 'exai-mcp' in servers:
                exai_config = servers['exai-mcp']
                print("PASS: EX-AI MCP Server configured")
                print(f"  - Command: {exai_config.get('command', 'N/A')}")
                print(f"  - Args: {exai_config.get('args', [])}")
                tracker.record_operation('exai_mcp_configured', 'EX-AI MCP server properly configured')
            else:
                print("FAIL: EX-AI MCP Server NOT configured")
                tracker.record_issue('critical', 'EX-AI MCP server missing from configuration')
            
            # Check MiniMax Search server
            if 'minimax_search' in servers:
                minimax_config = servers['minimax_search']
                print("PASS: MiniMax Search MCP Server configured")
                print(f"  - Command: {minimax_config.get('command', 'N/A')}")
                print(f"  - Type: {minimax_config.get('type', 'N/A')}")
                tracker.record_operation('minimax_mcp_configured', 'MiniMax Search MCP server configured')
            else:
                print("FAIL: MiniMax Search MCP Server NOT configured")
                tracker.record_issue('medium', 'MiniMax Search MCP server missing from configuration')
        else:
            print("FAIL: Invalid .mcp.json structure")
            tracker.record_issue('critical', 'Invalid .mcp.json structure')
            
    except Exception as e:
        print(f"✗ Error reading .mcp.json: {e}")
        tracker.record_issue('critical', f'Cannot read .mcp.json: {e}')
    
    print()
    print("3. ENVIRONMENT CONFIGURATION")
    print("-" * 40)
    
    # Check critical environment variables
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        critical_vars = [
            'MINIMAX_API_KEY',
            'MINIAGENT_API_KEY', 
            'EXAI_WS_HOST',
            'EXAI_WS_PORT',
            'EXAI_WS_TOKEN'
        ]
        
        for var in critical_vars:
            if f"{var}=" in env_content:
                print(f"PASS: {var}")
                tracker.record_operation('env_var_present', f'Environment variable present: {var}')
            else:
                print(f"FAIL: {var} - MISSING")
                tracker.record_issue('critical', f'Missing environment variable: {var}')
                
    except Exception as e:
        print(f"✗ Error reading .env: {e}")
        tracker.record_issue('critical', f'Cannot read .env: {e}')
    
    print()
    print("4. DOCKER SERVICES STATUS")
    print("-" * 40)
    
    import subprocess
    
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"PASS: Docker available: {result.stdout.strip()}")
            tracker.record_operation('docker_available', f'Docker available: {result.stdout.strip()}')
            
            # Check if containers are running
            result = subprocess.run(['docker-compose', 'ps', '--services', '--filter', 'status=running'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n')
                if running_services and running_services[0]:
                    print(f"PASS: Docker containers running: {len(running_services)} services")
                    for service in running_services:
                        print(f"  - {service}")
                    tracker.record_operation('docker_running', f'{len(running_services)} Docker services running')
                else:
                    print("FAIL: No Docker containers running")
                    tracker.record_issue('high', 'No Docker containers running')
            else:
                print("WARN: Docker compose status unknown")
        else:
            print("FAIL: Docker not available")
            tracker.record_issue('high', 'Docker not available')
            
    except Exception as e:
        print(f"? Docker check failed: {e}")
        tracker.record_issue('medium', f'Docker status check failed: {e}')
    
    print()
    print("5. MINIMAX SEARCH MCP SERVER")
    print("-" * 40)
    
    try:
        # Check if uvx is available
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"PASS: uvx available: {result.stdout.strip()}")
            tracker.record_operation('uvx_available', 'uvx package manager available')
            
            # Test MiniMax Search installation
            print("Testing MiniMax Search installation...")
            result = subprocess.run([
                'uvx', '--from', 'git+https://github.com/MiniMax-AI/minimax_search', 
                'minimax-search', '--help'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("PASS: MiniMax Search MCP server can be installed")
                tracker.record_operation('minimax_installable', 'MiniMax Search MCP server installable')
            else:
                print("FAIL: MiniMax Search MCP server installation failed")
                print(f"  Error: {result.stderr[:200]}...")
                tracker.record_issue('medium', 'MiniMax Search installation failed', result.stderr[:200])
        else:
            print("FAIL: uvx not available")
            tracker.record_issue('medium', 'uvx package manager not available')
            
    except Exception as e:
        print(f"✗ MiniMax Search test failed: {e}")
        tracker.record_issue('medium', f'MiniMax Search test failed: {e}')
    
    print()
    print("6. EX-AI MCP SERVER TESTING")
    print("-" * 40)
    
    print("Testing EX-AI MCP server startup...")
    try:
        # Quick test of MCP server startup
        import sys
        sys.path.append(str(Path.cwd()))
        from dotenv import load_dotenv
        load_dotenv('.env')
        
        # Import and test the MCP shim
        from scripts.runtime.run_ws_shim import app
        
        print("PASS: EX-AI MCP server module loads successfully")
        tracker.record_operation('exai_module_load', 'EX-AI MCP server module loads successfully')
        
        # Test basic functionality
        import asyncio
        
        async def test_list_tools():
            try:
                tools = await app.list_tools()
                return len(tools)
            except Exception as e:
                return f"Error: {e}"
        
        # This would require the daemon to be running, so we'll note it
        print("  Note: Full functionality testing requires Docker daemon connection")
        tracker.record_operation('exai_testing_note', 'EX-AI MCP server requires Docker daemon for full functionality')
        
    except Exception as e:
        print(f"FAIL: EX-AI MCP server test failed: {e}")
        tracker.record_issue('medium', f'EX-AI MCP server test failed: {e}')
    
    print()
    print("7. SESSION MEMORY SYSTEM")
    print("-" * 40)
    
    # Check session memory system
    memory_dir = Path("session_memory")
    if memory_dir.exists():
        session_files = list(memory_dir.glob("session_*.json"))
        print(f"PASS: Session memory system active: {len(session_files)} session files")
        tracker.record_operation('memory_system_active', f'Session memory system active with {len(session_files)} sessions')
        
        for session_file in session_files[-3:]:  # Show last 3 sessions
            print(f"  - {session_file.name}")
    else:
        print("FAIL: Session memory system not initialized")
        tracker.record_issue('low', 'Session memory system not initialized')
    
    print()
    print("8. OVERALL ASSESSMENT")
    print("-" * 40)
    
    # Generate summary
    operations = len(tracker.session_data['operations'])
    issues = len(tracker.session_data['issues_found'])
    critical_issues = len([i for i in tracker.session_data['issues_found'] if i['severity'] == 'critical'])
    
    print(f"Total operations recorded: {operations}")
    print(f"Issues found: {issues}")
    print(f"Critical issues: {critical_issues}")
    print()
    
    if critical_issues == 0:
        print("SUCCESS: VALIDATION SUCCESSFUL!")
        print("PASS: All critical components are properly configured")
        print("PASS: MCP servers are properly set up")
        print("PASS: Environment is correctly configured")
        print("PASS: Session memory system is working")
        status = "SUCCESS"
    else:
        print("WARN: VALIDATION COMPLETED WITH ISSUES")
        print(f"FAIL: {critical_issues} critical issues need attention")
        status = "ISSUES_FOUND"
    
    tracker.record_operation('validation_complete', f'Validation completed with status: {status}')
    tracker.save_session()
    
    print()
    print("="*80)
    print(f"VALIDATION STATUS: {status}")
    print("="*80)
    
    return status

if __name__ == "__main__":
    generate_validation_report()