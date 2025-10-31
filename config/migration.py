"""
File management migration configuration for EX MCP Server

Configuration for gradual migration from legacy file handlers to UnifiedFileManager.
Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
Date: 2025-10-22

Rollout Strategy:
- Shadow Mode: Run both implementations, compare results
- 1%: Initial validation, monitor for errors
- 10%: Expand to more users, gather performance data
- 50%: Majority rollout, focus on edge cases
- 100%: Full migration, decommission legacy
"""

import os
import logging

logger = logging.getLogger(__name__)


def _parse_bool_env(key: str, default: str = "true") -> bool:
    """
    Parse boolean environment variable.

    Args:
        key: Environment variable name
        default: Default value if environment variable is not set

    Returns:
        Boolean value parsed from environment variable
    """
    return os.getenv(key, default).strip().lower() == "true"


class MigrationConfig:
    """
    Configuration for file management migration.

    This class controls the gradual rollout of the UnifiedFileManager,
    allowing safe migration from legacy file handlers with feature flags
    and percentage-based rollout.
    """

    # ========================================================================
    # GLOBAL CONTROLS
    # ========================================================================

    # Master switch for unified file management
    # Set to False for emergency rollback to legacy handlers
    ENABLE_UNIFIED_MANAGER: bool = _parse_bool_env("ENABLE_UNIFIED_MANAGER", "false")

    # Enable automatic fallback to legacy on errors
    # Recommended: True during migration, False after full rollout
    ENABLE_FALLBACK_TO_LEGACY: bool = _parse_bool_env("ENABLE_FALLBACK_TO_LEGACY", "true")

    # Enable shadow mode (run both implementations and compare results)
    # Recommended: True during initial validation, False after confidence is established
    ENABLE_SHADOW_MODE: bool = _parse_bool_env("ENABLE_SHADOW_MODE", "false")

    # Shadow mode sampling rate (0.0 to 1.0)
    # 0.1 = 10% of operations run shadow mode comparison
    # Prevents overwhelming systems during high load
    SHADOW_MODE_SAMPLE_RATE: float = float(os.getenv("SHADOW_MODE_SAMPLE_RATE", "0.1"))

    # Shadow mode error threshold (0.0 to 1.0)
    # If shadow mode error rate exceeds this, auto-disable shadow mode
    # 0.05 = 5% error rate triggers circuit breaker
    SHADOW_MODE_ERROR_THRESHOLD: float = float(os.getenv("SHADOW_MODE_ERROR_THRESHOLD", "0.05"))

    # Minimum samples before evaluating error threshold
    # Prevents premature circuit breaker activation on small sample sizes
    SHADOW_MODE_MIN_SAMPLES: int = int(os.getenv("SHADOW_MODE_MIN_SAMPLES", "50"))

    # Maximum shadow mode operations per minute (rate limiting)
    # Prevents resource exhaustion during high load
    SHADOW_MODE_MAX_SAMPLES_PER_MINUTE: int = int(os.getenv("SHADOW_MODE_MAX_SAMPLES_PER_MINUTE", "100"))

    # Shadow mode duration limit in minutes (0 = unlimited)
    # Auto-disable shadow mode after this duration for safety
    SHADOW_MODE_DURATION_MINUTES: int = int(os.getenv("SHADOW_MODE_DURATION_MINUTES", "0"))

    # Cooldown period in minutes before shadow mode can be re-enabled
    # Prevents rapid on/off cycling
    SHADOW_MODE_COOLDOWN_MINUTES: int = int(os.getenv("SHADOW_MODE_COOLDOWN_MINUTES", "30"))

    # Include timing information in shadow mode comparisons
    # Useful for performance analysis
    SHADOW_MODE_INCLUDE_TIMING: bool = _parse_bool_env("SHADOW_MODE_INCLUDE_TIMING", "true")

    # Maximum retry attempts before giving up
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

    # ========================================================================
    # PER-TOOL MIGRATION FLAGS
    # ========================================================================

    # Enable migration for KimiUploadFilesTool
    # This is the first tool to migrate (lowest risk)
    ENABLE_KIMI_MIGRATION: bool = _parse_bool_env("ENABLE_KIMI_MIGRATION", "false")

    # Enable migration for SmartFileHandler
    # Migrate after Kimi is stable (medium risk)
    ENABLE_SMART_HANDLER_MIGRATION: bool = _parse_bool_env("ENABLE_SMART_HANDLER_MIGRATION", "false")

    # Enable migration for SupabaseFileHandler
    # Migrate last (highest risk due to database integration)
    ENABLE_SUPABASE_MIGRATION: bool = _parse_bool_env("ENABLE_SUPABASE_MIGRATION", "false")

    # ========================================================================
    # ROLLOUT PERCENTAGES (0-100)
    # ========================================================================

    # Percentage of Kimi uploads to route through UnifiedFileManager
    # Start at 1%, increase gradually: 1 → 10 → 50 → 100
    KIMI_ROLLOUT_PERCENTAGE: int = int(os.getenv("KIMI_ROLLOUT_PERCENTAGE", "0"))

    # Percentage of SmartFileHandler operations to route through UnifiedFileManager
    SMART_HANDLER_ROLLOUT_PERCENTAGE: int = int(os.getenv("SMART_HANDLER_ROLLOUT_PERCENTAGE", "0"))

    # Percentage of Supabase operations to route through UnifiedFileManager
    SUPABASE_ROLLOUT_PERCENTAGE: int = int(os.getenv("SUPABASE_ROLLOUT_PERCENTAGE", "0"))

    # ========================================================================
    # MONITORING AND LOGGING
    # ========================================================================

    # Enable detailed logging for migration operations
    # Recommended: True during migration for debugging
    ENABLE_DETAILED_LOGGING: bool = _parse_bool_env("ENABLE_DETAILED_LOGGING", "true")

    # Sample rate for metrics collection (0.0 to 1.0)
    # 0.1 = 10% of operations are sampled for detailed metrics
    METRICS_SAMPLE_RATE: float = float(os.getenv("METRICS_SAMPLE_RATE", "0.1"))

    @classmethod
    def get_status(cls) -> dict:
        """
        Get current migration status.

        Returns:
            Dictionary with all migration configuration values
        """
        return {
            "global": {
                "unified_enabled": cls.ENABLE_UNIFIED_MANAGER,
                "fallback_enabled": cls.ENABLE_FALLBACK_TO_LEGACY,
                "shadow_mode_enabled": cls.ENABLE_SHADOW_MODE,
                "shadow_mode_sample_rate": cls.SHADOW_MODE_SAMPLE_RATE,
                "shadow_mode_error_threshold": cls.SHADOW_MODE_ERROR_THRESHOLD,
                "max_retries": cls.MAX_RETRY_ATTEMPTS
            },
            "per_tool_flags": {
                "kimi": cls.ENABLE_KIMI_MIGRATION,
                "smart_handler": cls.ENABLE_SMART_HANDLER_MIGRATION,
                "supabase": cls.ENABLE_SUPABASE_MIGRATION
            },
            "rollout_percentages": {
                "kimi": cls.KIMI_ROLLOUT_PERCENTAGE,
                "smart_handler": cls.SMART_HANDLER_ROLLOUT_PERCENTAGE,
                "supabase": cls.SUPABASE_ROLLOUT_PERCENTAGE
            },
            "monitoring": {
                "detailed_logging": cls.ENABLE_DETAILED_LOGGING,
                "metrics_sample_rate": cls.METRICS_SAMPLE_RATE
            }
        }

    @classmethod
    def validate_rollout_percentages(cls) -> bool:
        """
        Validate that all rollout percentages are within valid range (0-100).

        Returns:
            bool: True if all percentages are valid

        Raises:
            ValueError: If any percentage is out of range
        """
        percentages = {
            "KIMI_ROLLOUT_PERCENTAGE": cls.KIMI_ROLLOUT_PERCENTAGE,
            "SMART_HANDLER_ROLLOUT_PERCENTAGE": cls.SMART_HANDLER_ROLLOUT_PERCENTAGE,
            "SUPABASE_ROLLOUT_PERCENTAGE": cls.SUPABASE_ROLLOUT_PERCENTAGE
        }

        for name, value in percentages.items():
            if not (0 <= value <= 100):
                raise ValueError(
                    f"Invalid rollout percentage {name}={value}. "
                    f"Must be between 0 and 100."
                )

        return True

    @classmethod
    def validate_shadow_mode_config(cls) -> bool:
        """
        Validate shadow mode configuration parameters.

        Returns:
            bool: True if all shadow mode config is valid

        Raises:
            ValueError: If any configuration is invalid
        """
        # Validate sample rate (0.0 to 1.0)
        if not (0.0 <= cls.SHADOW_MODE_SAMPLE_RATE <= 1.0):
            raise ValueError(
                f"Invalid SHADOW_MODE_SAMPLE_RATE={cls.SHADOW_MODE_SAMPLE_RATE}. "
                f"Must be between 0.0 and 1.0."
            )

        # Validate error threshold (0.0 to 1.0)
        if not (0.0 <= cls.SHADOW_MODE_ERROR_THRESHOLD <= 1.0):
            raise ValueError(
                f"Invalid SHADOW_MODE_ERROR_THRESHOLD={cls.SHADOW_MODE_ERROR_THRESHOLD}. "
                f"Must be between 0.0 and 1.0."
            )

        # Validate minimum samples (must be positive)
        if cls.SHADOW_MODE_MIN_SAMPLES < 1:
            raise ValueError(
                f"Invalid SHADOW_MODE_MIN_SAMPLES={cls.SHADOW_MODE_MIN_SAMPLES}. "
                f"Must be at least 1."
            )

        # Validate max samples per minute (must be positive)
        if cls.SHADOW_MODE_MAX_SAMPLES_PER_MINUTE < 1:
            raise ValueError(
                f"Invalid SHADOW_MODE_MAX_SAMPLES_PER_MINUTE={cls.SHADOW_MODE_MAX_SAMPLES_PER_MINUTE}. "
                f"Must be at least 1."
            )

        # Validate duration (must be non-negative, 0 = unlimited)
        if cls.SHADOW_MODE_DURATION_MINUTES < 0:
            raise ValueError(
                f"Invalid SHADOW_MODE_DURATION_MINUTES={cls.SHADOW_MODE_DURATION_MINUTES}. "
                f"Must be non-negative (0 = unlimited)."
            )

        # Validate cooldown (must be non-negative)
        if cls.SHADOW_MODE_COOLDOWN_MINUTES < 0:
            raise ValueError(
                f"Invalid SHADOW_MODE_COOLDOWN_MINUTES={cls.SHADOW_MODE_COOLDOWN_MINUTES}. "
                f"Must be non-negative."
            )

        return True


# Validate migration configuration on module import
try:
    MigrationConfig.validate_rollout_percentages()
    MigrationConfig.validate_shadow_mode_config()
except ValueError as e:
    logger.warning(f"Migration configuration validation failed: {e}")
    # Don't raise - allow module to load but log the warning

