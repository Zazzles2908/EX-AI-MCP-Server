"""
OpenAI Compatible Provider - Capabilities Module

Handles model capabilities, validation, and feature detection.
Provides abstract methods for subclasses to implement and common
capability checks for OpenAI-compatible models.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities (this file)
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class
"""

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .base import ModelCapabilities, ProviderType

logger = logging.getLogger(__name__)


class OpenAICapabilities:
    """
    Manages model capabilities and validation for OpenAI-compatible providers.

    Handles:
    - Model capability retrieval (abstract)
    - Provider type retrieval (abstract)
    - Model name validation (abstract)
    - Extended thinking mode support
    - Vision/image support detection
    - Parameter validation
    """

    @abstractmethod
    def get_capabilities(self, model_name: str) -> "ModelCapabilities":
        """
        Get capabilities for a specific model.

        Must be implemented by subclasses to return ModelCapabilities
        for the specific model.

        Args:
            model_name: Name of the model

        Returns:
            ModelCapabilities object describing model features
        """
        pass

    @abstractmethod
    def get_provider_type(self) -> "ProviderType":
        """
        Get the provider type.

        Must be implemented by subclasses to return their ProviderType.

        Returns:
            ProviderType enum value
        """
        pass

    @abstractmethod
    def validate_model_name(self, model_name: str) -> bool:
        """
        Validate if the model name is supported.

        Must be implemented by subclasses to check if a model is supported.

        Args:
            model_name: Name of the model to validate

        Returns:
            True if model is supported, False otherwise
        """
        pass

    def supports_thinking_mode(self, model_name: str) -> bool:
        """
        Check if the model supports extended thinking mode.

        Default is False for OpenAI-compatible providers.
        Subclasses should override if they support extended thinking.

        Args:
            model_name: Name of the model

        Returns:
            True if model supports extended thinking mode
        """
        return False

    def _supports_vision(self, model_name: str) -> bool:
        """
        Check if the model supports vision (image processing).

        Default implementation for OpenAI-compatible providers.
        Subclasses should override with specific model support.

        Args:
            model_name: Name of the model

        Returns:
            True if model supports vision/image processing
        """
        # Common vision-capable models - only include models that actually support images
        vision_models = {
            "gpt-5",
            "gpt-5-mini",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4-vision-preview",
            "gpt-4.1-2025-04-14",
            "o3",
            "o3-mini",
            "o3-pro",
            "o4-mini",
            # Note: Claude models would be handled by a separate provider
        }

        supports = model_name.lower() in vision_models
        logging.debug(f"Model '{model_name}' vision support: {supports}")
        return supports

    def validate_parameters(
        self,
        model_name: str,
        temperature: float,
        **kwargs
    ) -> None:
        """
        Validate model parameters.

        For proxy providers, this may use generic capabilities.

        Args:
            model_name: Model to validate for
            temperature: Temperature to validate
            **kwargs: Additional parameters to validate

        Raises:
            ValueError: If parameters are invalid
        """
        try:
            capabilities = self.get_capabilities(model_name)

            # Check if we're using generic capabilities
            if hasattr(capabilities, "_is_generic"):
                logging.debug(
                    f"Using generic parameter validation for {model_name}. "
                    "Actual model constraints may differ."
                )

            # Validate temperature using parent class method
            self._validate_temperature(model_name, temperature, **kwargs)

        except Exception as e:
            # For proxy providers, we might not have accurate capabilities
            # Log warning but don't fail
            logging.warning(f"Parameter validation limited for {model_name}: {e}")

    def _validate_temperature(
        self,
        model_name: str,
        temperature: float,
        **kwargs
    ) -> None:
        """
        Validate temperature parameter.

        Args:
            model_name: Model name
            temperature: Temperature value
            **kwargs: Additional parameters

        Raises:
            ValueError: If temperature is invalid
        """
        # Get temperature constraint from capabilities
        try:
            capabilities = self.get_capabilities(model_name)
            constraint = getattr(capabilities, "temperature_constraint", None)

            if constraint and hasattr(constraint, "validate"):
                constraint.validate(temperature)
            else:
                # Basic validation if no constraint available
                if not 0.0 <= temperature <= 2.0:
                    raise ValueError(
                        f"Temperature must be between 0.0 and 2.0, got {temperature}"
                    )
        except Exception as e:
            logging.warning(f"Failed to validate temperature: {e}")
