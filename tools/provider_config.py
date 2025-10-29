"""
Provider Configuration for Supabase Universal File Hub
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Centralized configuration for provider-specific settings.
"""

# Provider file size limits (in bytes)
PROVIDER_LIMITS = {
    "kimi": {
        "max_size_mb": 100,
        "max_size_bytes": 100 * 1024 * 1024,
        "timeout_seconds": 300,
        "supports_download": True,
        "persistent_files": True,
        "description": "Kimi (Moonshot) - Persistent files, 100MB limit"
    },
    "glm": {
        "max_size_mb": 20,
        "max_size_bytes": 20 * 1024 * 1024,
        "timeout_seconds": 180,
        "supports_download": False,
        "persistent_files": False,
        "session_bound": True,
        "description": "GLM (ZhipuAI) - Session-bound files, 20MB limit"
    },
    "supabase_only": {
        "max_size_mb": 5000,  # 5GB Supabase limit
        "max_size_bytes": 5000 * 1024 * 1024,
        "timeout_seconds": 600,
        "supports_download": True,
        "persistent_files": True,
        "description": "Supabase only - Large files, no provider upload"
    }
}


def get_provider_limit(provider: str, limit_type: str = "max_size_bytes"):
    """
    Get provider-specific limit.
    
    Args:
        provider: Provider name ('kimi', 'glm', 'supabase_only')
        limit_type: Type of limit to retrieve
    
    Returns:
        Limit value or None if not found
    """
    if provider in PROVIDER_LIMITS:
        return PROVIDER_LIMITS[provider].get(limit_type)
    return None


def validate_file_size(file_size: int, provider: str) -> tuple[bool, str]:
    """
    Validate file size against provider limits.
    
    Args:
        file_size: File size in bytes
        provider: Provider name
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if provider not in PROVIDER_LIMITS:
        return False, f"Unknown provider: {provider}"
    
    max_size = PROVIDER_LIMITS[provider]["max_size_bytes"]
    max_size_mb = PROVIDER_LIMITS[provider]["max_size_mb"]
    
    if file_size > max_size:
        file_size_mb = file_size / (1024 * 1024)
        return False, f"File too large for {provider}: {file_size_mb:.1f}MB > {max_size_mb}MB"
    
    return True, ""


def auto_select_provider(file_size: int, preferred_provider: str = None) -> str:
    """
    Auto-select provider based on file size and preferences.
    
    Args:
        file_size: File size in bytes
        preferred_provider: Optional preferred provider
    
    Returns:
        Selected provider name
    """
    # If preferred provider specified and file fits, use it
    if preferred_provider and preferred_provider in PROVIDER_LIMITS:
        is_valid, _ = validate_file_size(file_size, preferred_provider)
        if is_valid:
            return preferred_provider
    
    # Auto-select based on file size
    if file_size <= PROVIDER_LIMITS["glm"]["max_size_bytes"]:
        return "glm"  # Default for small files
    elif file_size <= PROVIDER_LIMITS["kimi"]["max_size_bytes"]:
        return "kimi"  # For medium files
    else:
        return "supabase_only"  # Large files only in Supabase

