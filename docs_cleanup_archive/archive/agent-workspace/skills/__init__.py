#!/usr/bin/env python3
"""
EXAI Skills Registry - Mini-Agent Compatible
Registers the actual working implementations of EXAI skills for Mini-Agent use.
"""

import sys
import os
from typing import Dict, Any, Callable

def register_exai_skills() -> Dict[str, Callable]:
    """Register all available EXAI skills for Mini-Agent"""
    
    # Import the actual skill implementations
    try:
        from exai_system_diagnostics import EXAISystemDiagnostics
        from exai_log_cleanup import EXAILogCleanup  
        from exai_minimax_router_test import EXAIMiniMaxRouterTest
    except ImportError as e:
        print(f"Warning: Could not import skill implementations: {e}")
        return {}
    
    # Create skill registry
    skills = {
        "exai_system_diagnostics": lambda: run_skill(EXAISystemDiagnostics().run_diagnostics),
        "exai_log_cleanup": lambda: run_skill(EXAILogCleanup().run_log_cleanup_analysis),
        "exai_minimax_router_test": lambda: run_skill(EXAIMiniMaxRouterTest().run_all_tests)
    }
    
    return skills

def run_skill(skill_func: Callable) -> Dict[str, Any]:
    """Execute a skill and return structured results"""
    try:
        result = skill_func()
        return {
            "status": "success",
            "data": result,
            "timestamp": result.get("timestamp", "unknown")
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": "unknown"
        }

def list_available_skills() -> Dict[str, str]:
    """List all available EXAI skills with descriptions"""
    return {
        "exai_system_diagnostics": "Comprehensive health check for EX-AI MCP Server system",
        "exai_log_cleanup": "Clean up duplicate messages and noise in container logs",
        "exai_minimax_router_test": "Test MiniMax M2 routing decisions and provider selection"
    }

# For direct execution
if __name__ == "__main__":
    print("[TOOLS] EXAI Skills Registry")
    print("Available skills:")
    
    skills = list_available_skills()
    for skill_name, description in skills.items():
        print(f"  * {skill_name}: {description}")
    
    print(f"\nTotal skills available: {len(skills)}")