#!/usr/bin/env python3
"""
Get strategic guidance from GLM-4.6 and Kimi K2-0905 for next steps.
Uses direct provider calls instead of MCP to avoid connection issues.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from src.providers.glm_chat import GLMChatProvider
from src.providers.kimi_chat import KimiChatProvider


PROMPT = """I need strategic guidance for completing Phase 2 Archaeological Dig tasks.

**CURRENT STATUS:**
- Phase 2: 7/14 tasks complete (50%)
- Task 2.I (File Inclusion Bug Validation): Bug fix applied, testing blocked by environment issues
- Task 2.K (Model Capability Documentation): ✅ COMPLETE
- Server running cleanly on ws://127.0.0.1:8079

**BLOCKERS IDENTIFIED:**
1. **Daemon Stability (P0):** Server crashes during testing
2. **Test Environment (P1):** Test script cannot initialize providers outside MCP context
3. **WebSocket Connection (P2):** Direct EXAI tool calls fail with "Not connected" after restart

**NEXT STEPS TO PRIORITIZE:**
1. Manual testing for Task 2.I (use Augment Code instead of test script)
2. Daemon stability investigation (Task 2.J)
3. Performance benchmarking (Task 2.L)
4. SimpleTool refactoring decision (Task 2.M)
5. Integration testing suite (Task 2.N)

**YOUR TASK:**
Provide strategic recommendations for:
1. Best approach to complete Task 2.I given the blockers
2. Whether to prioritize daemon stability (Task 2.J) before other testing
3. Optimal sequence for remaining tasks
4. Risk mitigation strategies
5. Any critical issues I might be missing

Be specific and actionable. Consider the systematic approach we've been following."""


async def get_glm_guidance():
    """Get guidance from GLM-4.6."""
    print("\n" + "="*60)
    print("CONSULTING GLM-4.6")
    print("="*60)
    
    try:
        provider = GLMChatProvider()
        
        messages = [{"role": "user", "content": PROMPT}]
        
        response = await provider.chat_completion(
            model="glm-4.6",
            messages=messages,
            temperature=0.3,
            stream=False
        )
        
        content = response.choices[0].message.content
        
        print("\n📊 GLM-4.6 RESPONSE:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        return content
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def get_kimi_guidance():
    """Get guidance from Kimi K2-0905."""
    print("\n" + "="*60)
    print("CONSULTING KIMI K2-0905-PREVIEW")
    print("="*60)
    
    try:
        provider = KimiChatProvider()
        
        messages = [{"role": "user", "content": PROMPT}]
        
        response = await provider.chat_completion(
            model="kimi-k2-0905-preview",
            messages=messages,
            temperature=0.3,
            stream=False
        )
        
        content = response.choices[0].message.content
        
        print("\n📊 KIMI K2-0905 RESPONSE:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        return content
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Get guidance from both models."""
    print("="*60)
    print("STRATEGIC GUIDANCE REQUEST")
    print("="*60)
    print("Consulting GLM-4.6 and Kimi K2-0905 for next steps...")
    
    # Get guidance from both models
    glm_response = await get_glm_guidance()
    kimi_response = await get_kimi_guidance()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if glm_response and kimi_response:
        print("✅ Both models consulted successfully")
        print("\nReview both responses above for strategic guidance.")
        return 0
    elif glm_response or kimi_response:
        print("⚠️  One model consulted successfully")
        print("Review the available response above.")
        return 0
    else:
        print("❌ Both models failed")
        print("Check API keys and network connectivity.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

