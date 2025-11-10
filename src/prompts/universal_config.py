"""
Universal Configuration System

Provides flexible configuration for all EXAI prompt systems.
Supports environment variables, config files, and runtime parameters.

This makes the systems completely universal and usable by any project.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class StorageConfig:
    """Storage configuration settings."""
    timeout_monitor_path: str
    performance_metrics_path: str
    create_directories: bool = True


@dataclass
class ModelConfig:
    """Model configuration settings."""
    # Can be extended with custom models
    custom_models: Dict[str, Dict[str, Any]] = None
    # Model capability overrides
    capability_overrides: Dict[str, Dict[str, int]] = None
    # Task preference overrides
    task_preference_overrides: Dict[str, Dict[str, List[str]]] = None


@dataclass
class ProviderConfig:
    """Provider configuration settings."""
    # Additional providers beyond Kimi and GLM
    custom_providers: List[str] = None
    # Provider-specific settings
    provider_settings: Dict[str, Dict[str, Any]] = None


@dataclass
class SystemConfig:
    """Main configuration for all systems."""
    storage: StorageConfig = None
    models: ModelConfig = None
    providers: ProviderConfig = None
    # Global settings
    alert_threshold: float = 0.05
    min_samples: int = 10
    quality_threshold: float = 0.8
    cost_alert_threshold: float = 100.0


class UniversalConfig:
    """
    Universal configuration manager.

    Supports:
    - Environment variables
    - Config files
    - Runtime parameters
    - Default values
    """

    # Environment variable prefixes
    ENV_PREFIX = "EXAI_PROMPTS_"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Optional path to config file (JSON/YAML)
        """
        self.config_path = config_path
        self._config = SystemConfig()

        # Load configuration
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)

        # Override with environment variables
        self._load_from_env()

        # Set defaults
        self._set_defaults()

    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            self._apply_config(data)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Storage paths
        if os.getenv(f"{self.ENV_PREFIX}TIMEOUT_MONITOR_PATH"):
            if not self._config.storage:
                self._config.storage = StorageConfig(
                    timeout_monitor_path="",
                    performance_metrics_path=""
                )
            self._config.storage.timeout_monitor_path = os.getenv(
                f"{self.ENV_PREFIX}TIMEOUT_MONITOR_PATH"
            )

        if os.getenv(f"{self.ENV_PREFIX}PERFORMANCE_METRICS_PATH"):
            if not self._config.storage:
                self._config.storage = StorageConfig(
                    timeout_monitor_path="",
                    performance_metrics_path=""
                )
            self._config.storage.performance_metrics_path = os.getenv(
                f"{self.ENV_PREFIX}PERFORMANCE_METRICS_PATH"
            )

        # Alert threshold
        alert_threshold = os.getenv(f"{self.ENV_PREFIX}ALERT_THRESHOLD")
        if alert_threshold:
            try:
                self._config.alert_threshold = float(alert_threshold)
            except ValueError:
                pass

        # Cost alert threshold
        cost_alert = os.getenv(f"{self.ENV_PREFIX}COST_ALERT_THRESHOLD")
        if cost_alert:
            try:
                self._config.cost_alert_threshold = float(cost_alert)
            except ValueError:
                pass

    def _apply_config(self, data: Dict[str, Any]) -> None:
        """Apply configuration from dictionary."""
        if "storage" in data:
            storage_data = data["storage"]
            self._config.storage = StorageConfig(
                timeout_monitor_path=storage_data.get(
                    "timeout_monitor_path",
                    "data/timeout_monitor.json"
                ),
                performance_metrics_path=storage_data.get(
                    "performance_metrics_path",
                    "data/performance_metrics.json"
                ),
                create_directories=storage_data.get("create_directories", True)
            )

        if "models" in data:
            models_data = data["models"]
            self._config.models = ModelConfig(
                custom_models=models_data.get("custom_models", {}),
                capability_overrides=models_data.get("capability_overrides", {}),
                task_preference_overrides=models_data.get("task_preference_overrides", {})
            )

        if "providers" in data:
            providers_data = data["providers"]
            self._config.providers = ProviderConfig(
                custom_providers=providers_data.get("custom_providers", []),
                provider_settings=providers_data.get("provider_settings", {})
            )

        if "alert_threshold" in data:
            self._config.alert_threshold = data["alert_threshold"]

        if "min_samples" in data:
            self._config.min_samples = data["min_samples"]

        if "quality_threshold" in data:
            self._config.quality_threshold = data["quality_threshold"]

        if "cost_alert_threshold" in data:
            self._config.cost_alert_threshold = data["cost_alert_threshold"]

    def _set_defaults(self) -> None:
        """Set default configuration values."""
        if not self._config.storage:
            # Get from environment or use default
            default_path = os.path.expanduser("~/.exai-prompts/data")
            self._config.storage = StorageConfig(
                timeout_monitor_path=os.getenv(
                    f"{self.ENV_PREFIX}TIMEOUT_MONITOR_PATH",
                    os.path.join(default_path, "timeout_monitor.json")
                ),
                performance_metrics_path=os.getenv(
                    f"{self.ENV_PREFIX}PERFORMANCE_METRICS_PATH",
                    os.path.join(default_path, "performance_metrics.json")
                )
            )

        if not self._config.models:
            self._config.models = ModelConfig()

        if not self._config.providers:
            self._config.providers = ProviderConfig()

    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration."""
        return self._config.storage

    def get_model_config(self) -> ModelConfig:
        """Get model configuration."""
        return self._config.models

    def get_provider_config(self) -> ProviderConfig:
        """Get provider configuration."""
        return self._config.providers

    def get_global_config(self) -> SystemConfig:
        """Get global configuration."""
        return self._config

    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to file."""
        with open(config_path, 'w') as f:
            json.dump(asdict(self._config), f, indent=2)

    @classmethod
    def create_config_template(cls, config_path: str) -> None:
        """
        Create a configuration template file.

        Args:
            config_path: Path to create template file
        """
        template = {
            "storage": {
                "timeout_monitor_path": "~/.exai-prompts/data/timeout_monitor.json",
                "performance_metrics_path": "~/.exai-prompts/data/performance_metrics.json",
                "create_directories": True
            },
            "models": {
                "custom_models": {},
                "capability_overrides": {},
                "task_preference_overrides": {}
            },
            "providers": {
                "custom_providers": [],
                "provider_settings": {}
            },
            "alert_threshold": 0.05,
            "min_samples": 10,
            "quality_threshold": 0.8,
            "cost_alert_threshold": 100.0
        }

        with open(config_path, 'w') as f:
            json.dump(template, f, indent=2)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"UniversalConfig(storage={self._config.storage}, models={self._config.models}, providers={self._config.providers})"


# Global configuration instance
_global_config: Optional[UniversalConfig] = None


def get_config(config_path: Optional[str] = None) -> UniversalConfig:
    """
    Get or create global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        UniversalConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = UniversalConfig(config_path)
    return _global_config


def set_config(config: UniversalConfig) -> None:
    """
    Set global configuration instance.

    Args:
        config: UniversalConfig instance
    """
    global _global_config
    _global_config = config


# Convenience functions
def get_storage_path(key: str) -> str:
    """
    Get storage path from configuration.

    Args:
        key: 'timeout_monitor' or 'performance_metrics'

    Returns:
        Configured storage path
    """
    config = get_config()
    storage_config = config.get_storage_config()

    if key == "timeout_monitor":
        return storage_config.timeout_monitor_path
    elif key == "performance_metrics":
        return storage_config.performance_metrics_path
    else:
        raise ValueError(f"Unknown storage key: {key}")


def get_custom_models() -> Dict[str, Dict[str, Any]]:
    """Get custom models from configuration."""
    config = get_config()
    model_config = config.get_model_config()
    return model_config.custom_models or {}


def get_capability_overrides() -> Dict[str, Dict[str, int]]:
    """Get model capability overrides."""
    config = get_config()
    model_config = config.get_model_config()
    return model_config.capability_overrides or {}


def get_task_preference_overrides() -> Dict[str, Dict[str, List[str]]]:
    """Get task preference overrides."""
    config = get_config()
    model_config = config.get_model_config()
    return model_config.task_preference_overrides or {}


def get_custom_providers() -> List[str]:
    """Get custom providers from configuration."""
    config = get_config()
    provider_config = config.get_provider_config()
    return provider_config.custom_providers or []


if __name__ == "__main__":
    # Create example configuration
    config = UniversalConfig()
    print(config)

    # Create template
    UniversalConfig.create_config_template("exai-prompts-config.json")
    print("\nCreated configuration template: exai-prompts-config.json")
