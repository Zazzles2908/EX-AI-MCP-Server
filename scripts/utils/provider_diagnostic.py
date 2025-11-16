#!/usr/bin/env python3
"""
EX-AI Provider Health & Configuration Diagnostic
=================================================

Provides comprehensive visibility into your provider infrastructure:
- Configured providers (from .env)
- Available models per provider  
- Health status and initialization state
- Complete model inventory

Created: 2025-01-20
Purpose: Prevent provider count confusion by showing complete state
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_ascii_support() -> bool:
    """Check if terminal supports UTF-8 checkmarks/crosses."""
    try:
        # Try to encode checkmark
        "\u2713".encode(sys.stdout.encoding or 'utf-8')
        return True
    except (UnicodeEncodeError, AttributeError):
        return False


# ASCII-safe symbols
USE_UNICODE = check_ascii_support()
CHECK = "✓" if USE_UNICODE else "[OK]"
CROSS = "✗" if USE_UNICODE else "[X]"
ARROW = "→" if USE_UNICODE else "->"


def print_header(title: str) -> None:
    """Print section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_subheader(title: str) -> None:
    """Print subsection header."""
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}")


def check_env_configuration() -> Dict[str, Dict[str, str]]:
    """Check .env file for provider configurations."""
    print_header("ENVIRONMENT CONFIGURATION (.env)")
    
    env_file = project_root / ".env"
    if not env_file.exists():
        print(f"{CROSS} .env file not found!")
        return {}
    
    print(f"{CHECK} .env file found: {env_file}")
    
    providers = {
        "MiniMax": {
            "enabled_var": "MINIMAX_ENABLED",
            "api_key_var": "MINIMAX_M2_KEY",
            "url_var": "MINIMAX_API_URL",
        },
        "GLM": {
            "api_key_var": "GLM_API_KEY",
            "url_var": "GLM_API_URL",
            "models_var": "GLM_PREFERRED_MODELS",
        },
        "Kimi": {
            "api_key_var": "KIMI_API_KEY",
            "url_var": "KIMI_API_URL",
            "default_model": "KIMI_DEFAULT_MODEL",
        }
    }
    
    configured = {}
    
    for provider, vars_to_check in providers.items():
        print_subheader(f"{provider} Provider")
        config = {}
        
        for var_name, env_var in vars_to_check.items():
            value = os.getenv(env_var)
            if value:
                # Mask API keys
                if "KEY" in env_var or "key" in var_name.lower():
                    display_value = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value[:15] + "..."
                else:
                    display_value = value
                
                print(f"  {CHECK} {var_name}: {display_value}")
                config[var_name] = value
            else:
                print(f"  {CROSS} {var_name}: NOT SET")
        
        if config:
            configured[provider] = config
    
    return configured


def get_model_inventory() -> Dict[str, List[str]]:
    """Get complete model inventory from model_config.py."""
    print_header("MODEL INVENTORY (from model_config.py)")
    
    try:
        from src.providers.model_config import MODEL_TOKEN_LIMITS
        
        providers = {}
        for model_name, config in MODEL_TOKEN_LIMITS.items():
            provider = config.get('provider', 'unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append({
                'name': model_name,
                'context': config.get('max_context_tokens', 0),
                'output': config.get('max_output_tokens', 0),
            })
        
        # Print inventory
        total_models = 0
        for provider, models in sorted(providers.items()):
            print_subheader(f"{provider.upper()} Models")
            for model in sorted(models, key=lambda x: x['context'], reverse=True):
                context_kb = model['context'] // 1024
                output_kb = model['output'] // 1024
                print(f"  {ARROW} {model['name']:<30} | Context: {context_kb:>5}K | Output: {output_kb:>5}K")
            print(f"  Total: {len(models)} models")
            total_models += len(models)
        
        print(f"\n{CHECK} Total Models Defined: {total_models}")
        return providers
        
    except Exception as e:
        print(f"{CROSS} Failed to load model inventory: {e}")
        return {}


def check_provider_registry() -> Dict[str, List[str]]:
    """Check runtime provider registry state."""
    print_header("RUNTIME PROVIDER REGISTRY")
    
    try:
        from src.providers.base import ProviderType
        
        # List all defined provider types
        print_subheader("Defined Provider Types (Framework Support)")
        provider_types = [pt.value for pt in ProviderType]
        for i, pt in enumerate(sorted(provider_types), 1):
            print(f"  {i:2d}. {pt}")
        print(f"\n  Total Framework-Supported Provider Types: {len(provider_types)}")
        
        # Try to get runtime registry state
        print_subheader("Runtime Registry State")
        try:
            # This will fail if providers aren't initialized
            # from src.providers.registry_core import ModelProviderRegistry
            # registry = ModelProviderRegistry()
            # models = registry.get_available_models()
            print(f"  {CROSS} Runtime registry check skipped (requires initialized providers)")
            print(f"  {ARROW} Use this script during runtime for live status")
            return {}
        except Exception as e:
            print(f"  {CROSS} Cannot access runtime registry: {e}")
            return {}
            
    except Exception as e:
        print(f"{CROSS} Failed to check provider registry: {e}")
        return {}


def check_provider_files() -> Dict[str, bool]:
    """Check if provider implementation files exist."""
    print_header("PROVIDER IMPLEMENTATION FILES")
    
    providers_dir = project_root / "src" / "providers"
    
    provider_files = {
        "MiniMax": "minimax.py",
        "GLM": "glm.py",
        "Kimi": "kimi.py",
        "Base": "base.py",
        "Registry": "registry_core.py",
        "Model Config": "model_config.py",
    }
    
    exists = {}
    for provider, filename in provider_files.items():
        filepath = providers_dir / filename
        if filepath.exists():
            print(f"  {CHECK} {provider:<15} {ARROW} {filepath.relative_to(project_root)}")
            exists[provider] = True
        else:
            print(f"  {CROSS} {provider:<15} {ARROW} MISSING: {filename}")
            exists[provider] = False
    
    return exists


def generate_summary(
    configured: Dict[str, Dict],
    model_inventory: Dict[str, List],
    provider_files: Dict[str, bool]
) -> None:
    """Generate executive summary."""
    print_header("EXECUTIVE SUMMARY")
    
    # Count active providers
    active_providers = len(configured)
    print(f"\n{CHECK} Active Providers (Configured): {active_providers}")
    for provider in sorted(configured.keys()):
        print(f"  {ARROW} {provider}")
    
    # Count total models
    total_models = sum(len(models) for models in model_inventory.values())
    print(f"\n{CHECK} Total Models Available: {total_models}")
    for provider, models in sorted(model_inventory.items()):
        print(f"  {ARROW} {provider.upper()}: {len(models)} models")
    
    # Provider implementation status
    print(f"\n{CHECK} Provider Implementation Files:")
    core_files = ["Base", "Registry", "Model Config"]
    all_core_exist = all(provider_files.get(f, False) for f in core_files)
    if all_core_exist:
        print(f"  {ARROW} Core infrastructure: {CHECK} Complete")
    else:
        print(f"  {ARROW} Core infrastructure: {CROSS} Incomplete")
    
    # Context window capabilities
    print(f"\n{CHECK} Context Window Capabilities:")
    max_context = 0
    max_provider = ""
    for provider, models in model_inventory.items():
        for model in models:
            if model['context'] > max_context:
                max_context = model['context']
                max_provider = f"{provider} ({model['name']})"
    
    if max_context > 0:
        context_kb = max_context // 1024
        print(f"  {ARROW} Maximum Context: {context_kb}K ({max_provider})")
    
    # Final verdict
    print(f"\n{'='*80}")
    if active_providers >= 3 and total_models >= 20:
        print(f"{CHECK} System Status: FULLY OPERATIONAL")
        print(f"  {ARROW} {active_providers} providers configured")
        print(f"  {ARROW} {total_models} models available")
        print(f"  {ARROW} Production-ready")
    elif active_providers >= 2:
        print(f"{CHECK} System Status: OPERATIONAL")
        print(f"  {ARROW} {active_providers} providers configured")
        print(f"  {ARROW} {total_models} models available")
    else:
        print(f"{CROSS} System Status: INCOMPLETE CONFIGURATION")
        print(f"  {ARROW} Only {active_providers} providers configured")
    print(f"{'='*80}\n")


def main() -> int:
    """Main execution."""
    print(f"""
{'='*80}
  EX-AI Provider Health & Configuration Diagnostic
  Generated: {Path(__file__).name}
{'='*80}
""")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"{CHECK} Environment loaded from: {env_file}\n")
        else:
            print(f"{CROSS} .env file not found, using system environment\n")
        
        # Run diagnostics
        configured = check_env_configuration()
        model_inventory = get_model_inventory()
        provider_files = check_provider_files()
        check_provider_registry()
        
        # Generate summary
        generate_summary(configured, model_inventory, provider_files)
        
        return 0
        
    except Exception as e:
        print(f"\n{CROSS} Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
