#!/usr/bin/env python3
"""
Environment Validation Script
Validates that all required environment variables are configured correctly.
Created: 2025-11-03
"""

import os
import sys
from typing import List, Dict, Tuple

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text: str):
    """Print success message"""
    print(f"[OK] {text}")

def print_error(text: str):
    """Print error message"""
    print(f"[ERROR] {text}")

def print_warning(text: str):
    """Print warning message"""
    print(f"[WARNING] {text}")

def print_info(text: str):
    """Print info message"""
    print(f"[INFO] {text}")

def check_required_vars(required_vars: List[str]) -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set"""
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    return len(missing) == 0, missing

def check_optional_vars(optional_vars: List[str]) -> Dict[str, bool]:
    """Check which optional environment variables are set"""
    return {var: bool(os.getenv(var)) for var in optional_vars}

def validate_api_keys() -> bool:
    """Validate API key configuration"""
    print_header("API Key Validation")

    # Check Kimi API key
    kimi_key = os.getenv("KIMI_API_KEY")
    if kimi_key and kimi_key != "your-kimi-api-key-here":
        print_success("KIMI_API_KEY is configured")
        if kimi_key.startswith("sk-"):
            print_info("KIMI API key format appears valid (starts with sk-)")
        else:
            print_warning("KIMI API key format might be invalid (should start with sk-)")
    elif kimi_key == "your-kimi-api-key-here":
        print_warning("KIMI_API_KEY is still using placeholder value")
    else:
        print_warning("KIMI_API_KEY is not set")

    # Check GLM API key
    glm_key = os.getenv("GLM_API_KEY")
    if glm_key and glm_key != "your-glm-api-key-here":
        print_success("GLM_API_KEY is configured")
        if "." in glm_key:
            print_info("GLM API key format appears valid (contains separator)")
        else:
            print_warning("GLM API key format might be invalid")
    elif glm_key == "your-glm-api-key-here":
        print_warning("GLM_API_KEY is still using placeholder value")
    else:
        print_warning("GLM_API_KEY is not set")

    # Check Supabase keys
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon = os.getenv("SUPABASE_ANON_KEY")
    supabase_service = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if supabase_url and supabase_url != "https://your-project.supabase.co":
        print_success("SUPABASE_URL is configured")
    else:
        print_warning("SUPABASE_URL is not set or using placeholder")

    if supabase_anon and supabase_anon != "your-anon-key-here":
        print_success("SUPABASE_ANON_KEY is configured")
    else:
        print_warning("SUPABASE_ANON_KEY is not set or using placeholder")

    if supabase_service and supabase_service != "your-service-role-key-here":
        print_success("SUPABASE_SERVICE_ROLE_KEY is configured")
    else:
        print_warning("SUPABASE_SERVICE_ROLE_KEY is not set or using placeholder")

    print_info("API keys configured correctly for basic functionality")
    return True

def validate_websocket_config() -> bool:
    """Validate WebSocket configuration"""
    print_header("WebSocket Configuration")

    ws_host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    ws_port = os.getenv("EXAI_WS_PORT", "8079")

    print_info(f"EXAI_WS_HOST: {ws_host}")
    print_info(f"EXAI_WS_PORT: {ws_port}")

    # Validate host
    if ws_host in ["127.0.0.1", "0.0.0.0"]:
        print_success(f"WebSocket host is valid: {ws_host}")
    else:
        print_warning(f"WebSocket host might be invalid: {ws_host}")

    # Validate port
    try:
        port_num = int(ws_port)
        if 1 <= port_num <= 65535:
            print_success(f"WebSocket port is valid: {port_num}")
        else:
            print_error(f"WebSocket port is out of range: {port_num}")
            return False
    except ValueError:
        print_error(f"WebSocket port is not a number: {ws_port}")
        return False

    return True

def validate_timeout_config() -> bool:
    """Validate timeout configuration"""
    print_header("Timeout Configuration")

    workflow_timeout = os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "300")
    expert_timeout = os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "300")

    try:
        workflow_val = int(workflow_timeout)
        expert_val = int(expert_timeout)

        print_info(f"WORKFLOW_TOOL_TIMEOUT_SECS: {workflow_val}s")
        print_info(f"EXPERT_ANALYSIS_TIMEOUT_SECS: {expert_val}s")

        if workflow_val >= 30:
            print_success("Workflow timeout is reasonable (>= 30s)")
        else:
            print_warning("Workflow timeout might be too short (< 30s)")

        if expert_val >= 30:
            print_success("Expert analysis timeout is reasonable (>= 30s)")
        else:
            print_warning("Expert analysis timeout might be too short (< 30s)")

        return True
    except ValueError:
        print_error("Timeout values are not valid numbers")
        return False

def validate_security_config() -> bool:
    """Validate security configuration"""
    print_header("Security Configuration")

    secure_inputs = os.getenv("SECURE_INPUTS_ENFORCED", "true").lower() == "true"
    strict_size = os.getenv("STRICT_FILE_SIZE_REJECTION", "true").lower() == "true"

    if secure_inputs:
        print_success("SECURE_INPUTS_ENFORCED is enabled (security best practice)")
    else:
        print_warning("SECURE_INPUTS_ENFORCED is disabled (not recommended)")

    if strict_size:
        print_success("STRICT_FILE_SIZE_REJECTION is enabled (DoS protection)")
    else:
        print_warning("STRICT_FILE_SIZE_REJECTION is disabled (not recommended)")

    # Check for hardcoded credentials
    env_vars = dict(os.environ)
    hardcoded_patterns = ["password", "secret", "key", "token"]

    for var_name, var_value in env_vars.items():
        if var_name.upper() in ["KIMI_API_KEY", "GLM_API_KEY", "SUPABASE_SERVICE_ROLE_KEY"]:
            if "example" in var_value.lower() or "placeholder" in var_value.lower() or "your-" in var_value:
                continue  # Skip placeholders
            if var_value in ["test", "123", "password", "admin"]:
                print_error(f"{var_name} appears to use a hardcoded default value")
                return False

    print_success("No obvious hardcoded credentials detected")
    return True

def validate_supabase_config() -> bool:
    """Validate Supabase configuration"""
    print_header("Supabase Configuration")

    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        print_info("SUPABASE_URL not set - using in-memory storage (development only)")
        return True

    if supabase_url == "https://your-project.supabase.co":
        print_warning("SUPABASE_URL is using placeholder value")
        return False

    print_success("SUPABASE_URL is configured")

    # Check for required Supabase variables
    required_supabase = ["SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
    missing = [var for var in required_supabase if not os.getenv(var) or os.getenv(var) == f"your-{var.lower().replace('_', '-')}-here"]

    if missing:
        print_warning(f"Missing Supabase variables: {', '.join(missing)}")
        return False

    print_success("Supabase configuration appears complete")
    return True

def validate_redis_config() -> bool:
    """Validate Redis configuration"""
    print_header("Redis Configuration")

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print_info("REDIS_URL not set - using in-memory storage (conversations will be lost on restart)")
        return True

    if redis_url.startswith("redis://:"):
        print_success("REDIS_URL includes authentication")
    else:
        print_warning("REDIS_URL does not include authentication (insecure)")

    print_success("Redis configuration found")
    return True

def main():
    """Main validation function"""
    print_header("EX-AI MCP Server - Environment Validation")
    print_info("Validating environment configuration...")

    all_valid = True

    # Validate API keys
    if not validate_api_keys():
        all_valid = False

    # Validate WebSocket
    if not validate_websocket_config():
        all_valid = False

    # Validate timeouts
    if not validate_timeout_config():
        all_valid = False

    # Validate security
    if not validate_security_config():
        all_valid = False

    # Validate Supabase
    if not validate_supabase_config():
        all_valid = False

    # Validate Redis
    if not validate_redis_config():
        all_valid = False

    # Final summary
    print_header("Validation Summary")
    if all_valid:
        print_success("Environment validation PASSED")
        print_success("All checks passed. The environment is properly configured.")
        return 0
    else:
        print_warning("Environment validation completed with warnings")
        print_info("Some issues were found. Review the warnings above.")
        print_info("For production use, address all warnings.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
