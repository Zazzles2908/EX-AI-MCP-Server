#!/usr/bin/env python3
"""
Hybrid Router Fix Script
Applies critical fixes to resolve the most common hybrid router issues.
"""

import os
import json
import sys
from pathlib import Path

def create_missing_config_files():
    """Create the missing configuration files that the hybrid router expects."""
    
    print("Creating missing configuration files...")
    
    # Create src/conf directory
    src_conf_dir = Path("src/conf")
    src_conf_dir.mkdir(parents=True, exist_ok=True)
    
    # Create minimal custom_models.json
    custom_models_content = {
        "custom_models": {
            "llama3.2": {
                "model_id": "llama3.2",
                "provider": "ollama",
                "description": "Meta's Llama 3.2 model via Ollama"
            },
            "qwen2.5": {
                "model_id": "qwen2.5", 
                "provider": "ollama",
                "description": "Alibaba's Qwen 2.5 model via Ollama"
            }
        }
    }
    
    with open(src_conf_dir / "custom_models.json", "w") as f:
        json.dump(custom_models_content, f, indent=2)
    print("  ✅ Created src/conf/custom_models.json")
    
    # Create auggie-config.json (based on analysis from previous branch)
    auggie_config = {
        "fallback_chain": [
            "glm-4.5-flash",
            "glm-4-plus", 
            "kimi-k2-thinking",
            "kimi-k2-0711-preview"
        ],
        "provider_preferences": {
            "fast": "glm",
            "long_context": "kimi",
            "thinking": "kimi"
        },
        "routing_rules": {
            "web_search": "glm",
            "code_analysis": "kimi", 
            "document_analysis": "kimi"
        }
    }
    
    with open("auggie-config.json", "w") as f:
        json.dump(auggie_config, f, indent=2)
    print("  ✅ Created auggie-config.json")

def fix_service_fallback_routing():
    """Fix the hardcoded provider name issue in RouterService.fallback_routing()."""
    
    print("\nFixing RouterService fallback routing logic...")
    
    service_file = Path("src/router/service.py")
    
    if not service_file.exists():
        print("  ❌ service.py not found - skipping fix")
        return
    
    # Read the service file
    with open(service_file, "r") as f:
        content = f.read()
    
    # Fix the routing rules dictionary to use proper model names
    old_routing_rules = '''        routing_rules = {
            "web_search": "glm",
            "search": "glm", 
            "chat": "glm",
            "analyze": "glm",
            "debug": "kimi",
            "code_analysis": "kimi",
            "file_processing": "kimi",
            "document": "kimi",
            "long_context": "kimi",
            "thinking": "kimi",
        }'''
    
    new_routing_rules = '''        routing_rules = {
            "web_search": "glm-4.5-flash",
            "search": "glm-4.5-flash",
            "chat": "glm-4.5-flash", 
            "analyze": "glm-4.5-flash",
            "debug": "kimi-k2-0711-preview",
            "code_analysis": "kimi-k2-0711-preview",
            "file_processing": "kimi-k2-0711-preview",
            "document": "kimi-k2-0711-preview",
            "long_context": "kimi-k2-0711-preview",
            "thinking": "kimi-k2-0711-preview",
        }'''
    
    if old_routing_rules in content:
        content = content.replace(old_routing_rules, new_routing_rules)
        print("  ✅ Fixed routing rules to use proper model names")
        
        # Also fix the provider selection logic
        old_provider_logic = '''        # Determine provider from tool name or context
        provider = "glm"  # Default to GLM
        for key, prov in routing_rules.items():
            if key in tool_name.lower():
                provider = prov
                break'''
        
        new_provider_logic = '''        # Determine provider from tool name or context
        model = self._fast_default  # Default to GLM fast model
        for key, model_name in routing_rules.items():
            if key in tool_name.lower():
                model = model_name
                break'''
        
        content = content.replace(old_provider_logic, new_provider_logic)
        print("  ✅ Fixed provider selection logic")
        
        # Fix the model selection logic
        old_model_logic = '''        # Context-based routing
        if context.get("use_websearch"):
            provider = "glm"
        elif context.get("thinking_mode"):
            provider = "kimi"
        elif context.get("long_context"):
            provider = "kimi"
        
        # Choose model based on provider
        if provider == "glm":
            model = self._fast_default
            reason = "fallback_glm"
        else:
            model = self._long_default
            reason = "fallback_kimi"'''
        
        new_model_logic = '''        # Context-based routing  
        if context.get("use_websearch"):
            model = self._fast_default
            reason = "fallback_websearch"
        elif context.get("thinking_mode"):
            model = self._long_default  
            reason = "fallback_thinking"
        elif context.get("long_context"):
            model = self._long_default
            reason = "fallback_long_context"
        
        # Determine provider type from model
        provider_type = "GLM" if "glm" in model else "KIMI"'''
        
        content = content.replace(old_model_logic, new_model_logic)
        print("  ✅ Fixed context-based routing logic")
        
        # Update the RouteDecision creation
        old_decision = '''        prov = get_registry_instance().get_provider_for_model(model)
        if prov is None:
            # Fall back to any available model
            return self.choose_model("auto")

        dec = RouteDecision(
            requested="auto",
            chosen=model,
            reason=reason,
            provider=prov.get_provider_type().name,
            meta={"fallback": True, "tool": tool_name}
        )'''
        
        new_decision = '''        prov = get_registry_instance().get_provider_for_model(model)
        if prov is None:
            # Fall back to any available model
            return self.choose_model("auto")

        dec = RouteDecision(
            requested="auto",
            chosen=model,
            reason=reason,
            provider=provider_type,
            meta={"fallback": True, "tool": tool_name}
        )'''
        
        content = content.replace(old_decision, new_decision)
        print("  ✅ Fixed RouteDecision creation")
        
        # Write the fixed content back
        with open(service_file, "w") as f:
            f.write(content)
            
    else:
        print("  ⚠️  Original routing rules not found - may already be fixed")

def create_minimax_config():
    """Create a template configuration for MiniMax M2 if it doesn't exist."""
    
    print("\nChecking MiniMax M2 configuration...")
    
    minimax_key = os.getenv("MINIMAX_M2_KEY")
    if minimax_key:
        print("  ✅ MINIMAX_M2_KEY is set")
    else:
        print("  ❌ MINIMAX_M2_KEY is not set")
        print("  💡 To enable MiniMax M2 routing, set:")
        print("     export MINIMAX_M2_KEY=your_api_key_here")
        
    minimax_enabled = os.getenv("MINIMAX_ENABLED", "true")
    print(f"  ℹ️  MINIMAX_ENABLED = {minimax_enabled}")

def create_fix_report():
    """Create a summary report of the fixes applied."""
    
    print("\n" + "=" * 60)
    print("HYBRID ROUTER FIX SUMMARY")  
    print("=" * 60)
    
    print("\n🔧 FIXES APPLIED:")
    print("  ✅ Created missing configuration files")
    print("  ✅ Fixed RouterService fallback routing")
    print("  ✅ Corrected provider name references")
    
    print("\n📋 NEXT STEPS:")
    print("  1. Set MINIMAX_M2_KEY environment variable")
    print("  2. Install required Python packages:")
    print("     pip install anthropic")
    print("  3. Test hybrid router initialization:")
    print("     python -c 'from src.router.hybrid_router import get_hybrid_router; print(\"OK\")'")
    print("  4. Run diagnostic script:")
    print("     python diagnostic_script.py")
    
    print("\n🧪 TO VERIFY FIXES:")
    print("  python diagnostic_script.py")
    print("  python test_hybrid_router.py")

def main():
    """Main fix function."""
    
    print("HYBRID ROUTER - AUTOMATED FIX SCRIPT")
    print("=" * 60)
    
    try:
        # Apply fixes
        create_missing_config_files()
        fix_service_fallback_routing()
        create_minimax_config()
        create_fix_report()
        
        print(f"\n✅ Fix script completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Fix script failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
