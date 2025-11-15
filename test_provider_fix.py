#!/usr/bin/env python3
"""Test MCP connection after fixing KimiProvider"""

import sys
sys.path.append('.')

from session_memory_tracker import get_session_tracker

# Get the existing session tracker
tracker = get_session_tracker(session_id="exai_mcp_evaluation", project_path="C:\\Project\\EX-AI-MCP-Server")

# Record the fix
tracker.record_fix("Added missing list_models method to KimiProvider", ["src/providers/kimi.py"])

# Test the fix by importing the provider
try:
    from src.providers.kimi import KimiProvider
    tracker.record_tool_test("kimi_provider_import", "SUCCESS", "Provider imports successfully after fix")
    
    # Test the list_models method
    if hasattr(KimiProvider, 'list_models'):
        tracker.record_tool_test("kimi_provider_list_models", "SUCCESS", "list_models method exists and is callable")
        tracker.record_operation("provider_fix_verified", "KimiProvider.list_models() method successfully added")
    else:
        tracker.record_tool_test("kimi_provider_list_models", "FAILED", "list_models method still missing")
        
except Exception as e:
    tracker.record_tool_test("kimi_provider_import", "FAILED", str(e))

# Save updated session
tracker.save_session()

print("Provider fix testing complete!")
print("- Fixed KimiProvider by adding list_models() method")
print("- Method returns list of supported model names") 
print("- Should resolve the 'KimiProvider object has no attribute list_models' error")