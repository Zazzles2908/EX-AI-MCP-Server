"""
Timeout configuration for EX MCP Server

This module implements a coordinated timeout hierarchy to ensure proper
timeout behavior across all layers of the application.

Hierarchy (from inner to outer):
1. Tool Level (primary) - Tools set their own timeout based on complexity
2. Daemon Level (secondary) - Catches tools that don't implement timeout properly
3. Shim Level (tertiary) - Catches daemon failures
4. Client Level (final) - Prevents infinite hangs

Rule: Each outer timeout = 1.5x inner timeout (50% buffer)
"""

import os
import logging

logger = logging.getLogger(__name__)


class TimeoutConfig:
    """Centralized timeout configuration with coordinated hierarchy.

    TRACK 2 FIX (2025-10-16): Updated defaults to 30s for MCP tools to prevent indefinite hangs.
    Previous defaults (90-150s) were too high and caused poor user experience.

    EXAI INSIGHT (2025-10-21): Adaptive timeouts based on model complexity.
    Different models have different processing speeds and thinking depths.
    """

    # Tool-level timeouts (primary)
    SIMPLE_TOOL_TIMEOUT_SECS = int(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "30"))
    WORKFLOW_TOOL_TIMEOUT_SECS = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "45"))
    EXPERT_ANALYSIS_TIMEOUT_SECS = int(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "60"))

    # Provider timeouts
    # PHASE 2.3 FIX (2025-10-25): Increased Kimi timeout from 30s to 40s
    # Root cause: Connection pool exhaustion + timeout too aggressive for non-cached requests
    GLM_TIMEOUT_SECS = int(os.getenv("GLM_TIMEOUT_SECS", "30"))
    KIMI_TIMEOUT_SECS = int(os.getenv("KIMI_TIMEOUT_SECS", "40"))  # Increased from 30s to 40s
    KIMI_WEB_SEARCH_TIMEOUT_SECS = int(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "30"))

    # EXAI INSIGHT (2025-10-21): Model-specific timeout multipliers
    # Based on observed performance during comprehensive testing
    MODEL_TIMEOUT_MULTIPLIERS = {
        # Thinking models need more time for deep reasoning
        "kimi-thinking-preview": 1.5,
        "glm-4.6": 1.3,
        "kimi-k2-0905-preview": 1.2,

        # Fast models can use less time
        "glm-4.5-flash": 0.7,
        "kimi-k2-turbo-preview": 0.8,
        "glm-4.5-air": 0.6,

        # Standard models use base timeout
        "glm-4.5": 1.0,
        "moonshot-v1-128k": 1.0,
        "moonshot-v1-32k": 1.0,
        "moonshot-v1-8k": 1.0,
    }

    @classmethod
    def get_model_timeout(cls, model_name: str, base_timeout: float) -> float:
        """
        Get adaptive timeout for a specific model.

        EXAI INSIGHT (2025-10-21): Different models need different timeouts.
        Thinking models need more time, fast models can use less.

        Args:
            model_name: Name of the model
            base_timeout: Base timeout in seconds

        Returns:
            Adjusted timeout based on model complexity

        Example:
            >>> TimeoutConfig.get_model_timeout("glm-4.6", 300)
            390.0  # 300 * 1.3 multiplier
            >>> TimeoutConfig.get_model_timeout("glm-4.5-flash", 300)
            210.0  # 300 * 0.7 multiplier
        """
        multiplier = cls.MODEL_TIMEOUT_MULTIPLIERS.get(model_name, 1.0)
        return base_timeout * multiplier

    @classmethod
    def get_daemon_timeout(cls) -> int:
        """
        Get daemon timeout (1.5x max tool timeout).

        Returns:
            int: Daemon timeout in seconds (default: 180s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 1.5)

    @classmethod
    def get_shim_timeout(cls) -> int:
        """
        Get shim timeout (2x max tool timeout).

        Returns:
            int: Shim timeout in seconds (default: 240s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.0)

    @classmethod
    def get_client_timeout(cls) -> int:
        """
        Get client timeout (2.5x max tool timeout).

        Returns:
            int: Client timeout in seconds (default: 300s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.5)

    @classmethod
    def validate_all(cls) -> None:
        """
        Comprehensive timeout validation.
        Week 2 Fix #7 (2025-10-21): Validate all timeout configuration at startup.

        Validates:
        1. All timeout values are positive and reasonable
        2. Timeout hierarchy is maintained
        3. Provider timeouts are reasonable

        Raises:
            ValueError: If any validation fails
        """
        # 1. Validate individual timeout values
        cls._validate_timeout_values()

        # 2. Validate timeout hierarchy
        cls.validate_hierarchy()

        # 3. Log configuration for debugging
        cls._log_timeout_config()

    @classmethod
    def _validate_timeout_values(cls) -> None:
        """
        Validate individual timeout values are within reasonable bounds.
        Week 2 Fix #7 (2025-10-21): Ensure all timeouts are positive and reasonable.
        """
        timeouts = {
            "SIMPLE_TOOL_TIMEOUT_SECS": cls.SIMPLE_TOOL_TIMEOUT_SECS,
            "WORKFLOW_TOOL_TIMEOUT_SECS": cls.WORKFLOW_TOOL_TIMEOUT_SECS,
            "EXPERT_ANALYSIS_TIMEOUT_SECS": cls.EXPERT_ANALYSIS_TIMEOUT_SECS,
            "GLM_TIMEOUT_SECS": cls.GLM_TIMEOUT_SECS,
            "KIMI_TIMEOUT_SECS": cls.KIMI_TIMEOUT_SECS,
            "KIMI_WEB_SEARCH_TIMEOUT_SECS": cls.KIMI_WEB_SEARCH_TIMEOUT_SECS,
        }

        for name, value in timeouts.items():
            if value <= 0:
                raise ValueError(f"Timeout {name} must be positive, got {value}")

            # Set reasonable upper bounds (1 hour max for any timeout)
            if value > 3600:
                raise ValueError(f"Timeout {name} seems too large: {value} seconds (max: 3600)")

            # Warn about very short timeouts (< 5 seconds)
            if value < 5:
                logger.warning(f"Timeout {name} is very short: {value} seconds - may cause premature failures")

    @classmethod
    def _log_timeout_config(cls) -> None:
        """
        Log timeout configuration for debugging.
        Week 2 Fix #7 (2025-10-21): Log all timeout values at startup.
        """
        logger.info("=== TIMEOUT CONFIGURATION ===")
        logger.info(f"Tool Timeouts:")
        logger.info(f"  Simple Tool: {cls.SIMPLE_TOOL_TIMEOUT_SECS}s")
        logger.info(f"  Workflow Tool: {cls.WORKFLOW_TOOL_TIMEOUT_SECS}s")
        logger.info(f"  Expert Analysis: {cls.EXPERT_ANALYSIS_TIMEOUT_SECS}s")
        logger.info(f"Provider Timeouts:")
        logger.info(f"  GLM: {cls.GLM_TIMEOUT_SECS}s")
        logger.info(f"  Kimi: {cls.KIMI_TIMEOUT_SECS}s")
        logger.info(f"  Kimi Web Search: {cls.KIMI_WEB_SEARCH_TIMEOUT_SECS}s")
        logger.info(f"Calculated Timeouts:")
        logger.info(f"  Daemon: {cls.get_daemon_timeout()}s (1.5x workflow)")
        logger.info(f"  Shim: {cls.get_shim_timeout()}s (2.0x workflow)")
        logger.info(f"  Client: {cls.get_client_timeout()}s (2.5x workflow)")
        logger.info("=== END TIMEOUT CONFIGURATION ===")

    @classmethod
    def validate_hierarchy(cls) -> bool:
        """
        Validate that timeout hierarchy is correct.

        The hierarchy must follow: tool < daemon < shim < client
        Each outer timeout should be at least 1.5x the inner timeout.

        Returns:
            bool: True if hierarchy is valid

        Raises:
            ValueError: If timeout hierarchy is invalid
        """
        tool = cls.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = cls.get_daemon_timeout()
        shim = cls.get_shim_timeout()
        client = cls.get_client_timeout()

        # Check hierarchy: tool < daemon < shim < client
        if not (tool < daemon < shim < client):
            raise ValueError(
                f"Invalid timeout hierarchy: "
                f"tool={tool}s, daemon={daemon}s, shim={shim}s, client={client}s. "
                f"Expected: tool < daemon < shim < client"
            )

        # Check buffer ratios
        daemon_ratio = daemon / tool
        shim_ratio = shim / tool
        client_ratio = client / tool

        if daemon_ratio < 1.5:
            raise ValueError(
                f"Daemon timeout ratio too low: {daemon_ratio:.2f}x tool timeout. "
                f"Expected at least 1.5x"
            )

        if shim_ratio < 2.0:
            raise ValueError(
                f"Shim timeout ratio too low: {shim_ratio:.2f}x tool timeout. "
                f"Expected at least 2.0x"
            )

        if client_ratio < 2.5:
            raise ValueError(
                f"Client timeout ratio too low: {client_ratio:.2f}x tool timeout. "
                f"Expected at least 2.5x"
            )

        return True

    @classmethod
    def get_timeout_summary(cls) -> dict:
        """
        Get summary of all timeout values.

        Returns:
            dict: Dictionary containing all timeout values and ratios
        """
        tool = cls.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = cls.get_daemon_timeout()
        shim = cls.get_shim_timeout()
        client = cls.get_client_timeout()

        return {
            "tool_timeouts": {
                "simple": cls.SIMPLE_TOOL_TIMEOUT_SECS,
                "workflow": cls.WORKFLOW_TOOL_TIMEOUT_SECS,
                "expert_analysis": cls.EXPERT_ANALYSIS_TIMEOUT_SECS,
            },
            "infrastructure_timeouts": {
                "daemon": daemon,
                "shim": shim,
                "client": client,
            },
            "provider_timeouts": {
                "glm": cls.GLM_TIMEOUT_SECS,
                "kimi": cls.KIMI_TIMEOUT_SECS,
                "kimi_web_search": cls.KIMI_WEB_SEARCH_TIMEOUT_SECS,
            },
            "ratios": {
                "daemon_to_tool": round(daemon / tool, 2),
                "shim_to_tool": round(shim / tool, 2),
                "client_to_tool": round(client / tool, 2),
            },
            "hierarchy_valid": cls.validate_hierarchy(),
        }


# Validate timeout hierarchy on module import
try:
    TimeoutConfig.validate_hierarchy()
except ValueError as e:
    logger.warning(f"Timeout hierarchy validation failed: {e}")
    # Don't raise - allow module to load but log the warning

