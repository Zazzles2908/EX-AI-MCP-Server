"""
Model Management Mixin for Zen MCP Tools

This module provides model provider integration, model selection logic,
and model context resolution for tools.

Key Components:
- ModelManagementMixin: Handles model provider integration and selection
- Model field schema generation
- Temperature validation
- Model context resolution
"""

import logging
import os
from typing import Any, Optional

from src.providers import ModelProvider, ModelProviderRegistry

logger = logging.getLogger(__name__)


class ModelManagementMixin:
    """
    Mixin providing model management functionality for tools.
    
    This class handles:
    - Model provider integration
    - Model selection and validation
    - Model field schema generation
    - Temperature validation
    - Model context resolution
    """

    def __init__(self):
        """Initialize the mixin."""
        # Use singleton to ensure we see the same registry the daemon initialized
        from src.providers.registry_core import get_registry_instance
        self._registry = get_registry_instance()

    # ================================================================================
    # Model Selection and Validation
    # ================================================================================
    
    def is_effective_auto_mode(self) -> bool:
        """
        Check if we're in effective auto mode for schema generation.
        
        This determines whether the model parameter should be required in the tool schema.
        Used at initialization time when schemas are generated.
        
        Returns:
            bool: True if model parameter should be required in the schema
        """
        from config import DEFAULT_MODEL
        
        # Hidden router: if enabled and DEFAULT_MODEL is a sentinel, do NOT require model in schema
        try:
            if os.getenv("HIDDEN_MODEL_ROUTER_ENABLED", "true").strip().lower() == "true":
                sentinels = {
                    s.strip().lower()
                    for s in os.getenv("ROUTER_SENTINEL_MODELS", "glm-4.5-flash,auto").split(",")
                    if s.strip()
                }
                if DEFAULT_MODEL.strip().lower() in sentinels:
                    return False
        except Exception:
            pass
        
        # Case 1: Explicit auto mode
        if DEFAULT_MODEL.lower() == "auto":
            return True
        
        # Case 2: Model not available (fallback to auto mode)
        if DEFAULT_MODEL.lower() != "auto":
            provider = self._registry.get_provider_for_model(DEFAULT_MODEL)
            if not provider:
                # If hidden router is enabled, do not require model selection in schema
                if os.getenv("HIDDEN_MODEL_ROUTER_ENABLED", "true").strip().lower() == "true":
                    return False
                return True
        
        return False
    
    def _should_require_model_selection(self, model_name: str) -> bool:
        """
        Check if we should require Claude to select a model at runtime.
        
        This is called during request execution to determine if we need
        to return an error asking Claude to provide a model parameter.
        
        Args:
            model_name: The model name from the request or DEFAULT_MODEL
        
        Returns:
            bool: True if we should require model selection
        """
        # Case 1: Model is explicitly "auto"
        # Hidden router sentinel should not force runtime selection
        if os.getenv("HIDDEN_MODEL_ROUTER_ENABLED", "true").strip().lower() == "true":
            sentinels = {s.strip().lower() for s in os.getenv("ROUTER_SENTINEL_MODELS", "glm-4.5-flash,auto").split(",") if s.strip()}
            if model_name.strip().lower() in sentinels:
                return False
        if model_name.lower() == "auto":
            return True
        
        # Case 2: Requested model is not available
        provider = self._registry.get_provider_for_model(model_name)
        if not provider:
            logger.warning(f"Model '{model_name}' is not available with current API keys. Requiring model selection.")
            return True
        
        return False
    
    def _get_available_models(self) -> list[str]:
        """
        Get list of models available from enabled providers.
        
        Only returns models from providers that have valid API keys configured.
        This fixes the namespace collision bug where models from disabled providers
        were shown to Claude, causing routing conflicts.
        
        Returns:
            List of model names from enabled providers only
        """
        # Get models from enabled providers only (those with valid API keys)
        all_models = self._registry.get_available_model_names()
        
        # Add OpenRouter models if OpenRouter is configured
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            try:
                registry = self._get_openrouter_registry()
                # Add all aliases from the registry (includes OpenRouter cloud models)
                for alias in registry.list_aliases():
                    if alias not in all_models:
                        all_models.append(alias)
            except Exception as e:
                logging.debug(f"Failed to add OpenRouter models to enum: {e}")
        
        # Add custom models if custom API is configured
        custom_url = os.getenv("CUSTOM_API_URL")
        if custom_url:
            try:
                registry = self._get_openrouter_registry()
                # Find all custom models (is_custom=true)
                for alias in registry.list_aliases():
                    config = registry.resolve(alias)
                    # Check if this is a custom model that requires custom endpoints
                    if config and config.is_custom:
                        if alias not in all_models:
                            all_models.append(alias)
            except Exception as e:
                logging.debug(f"Failed to add custom models to enum: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in all_models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)
        
        return unique_models
    
    def get_model_provider(self, model_name: str) -> ModelProvider:
        """
        Get the appropriate model provider for the given model name.

        This method performs runtime validation to ensure the requested model
        is actually available with the current API key configuration.

        Args:
            model_name: Name of the model to get provider for

        Returns:
            ModelProvider: The provider instance for the model

        Raises:
            ValueError: If the model is not available or provider not found
        """
        try:
            logger.info(f"TOOL_MODEL_DEBUG: get_model_provider called for model '{model_name}' in tool '{self.name}'")
            provider = self._registry.get_provider_for_model(model_name)
            logger.info(f"TOOL_MODEL_DEBUG: get_provider_for_model returned: {provider}")
            if not provider:
                logger.error(f"No provider found for model '{model_name}' in {self.name} tool")
                available_models = self._registry.get_available_models()
                logger.error(f"TOOL_MODEL_DEBUG: Available models from registry: {available_models}")
                raise ValueError(f"Model '{model_name}' is not available. Available models: {available_models}")

            return provider
        except Exception as e:
            logger.error(f"Failed to get provider for model '{model_name}' in {self.name} tool: {e}")
            raise

    # ================================================================================
    # Model Context Resolution
    # ================================================================================

    def _resolve_model_context(self, arguments: dict, request) -> tuple[str, Any]:
        """
        Resolve model context and name using centralized logic.

        This method extracts the model resolution logic from execute() so it can be
        reused by tools that override execute() (like debug tool) without duplicating code.

        Args:
            arguments: Dictionary of arguments from the MCP client
            request: The validated request object

        Returns:
            tuple[str, ModelContext]: (resolved_model_name, model_context)

        Raises:
            ValueError: If model resolution fails or model selection is required
        """
        # MODEL RESOLUTION NOW HAPPENS AT MCP BOUNDARY
        # Extract pre-resolved model context from server.py
        model_context = arguments.get("_model_context")
        resolved_model_name = arguments.get("_resolved_model_name")

        if model_context and resolved_model_name:
            # Model was already resolved at MCP boundary
            model_name = resolved_model_name
            logger.debug(f"Using pre-resolved model '{model_name}' from MCP boundary")
        else:
            # Fallback for direct execute calls
            model_name = getattr(request, "model", None)
            if not model_name:
                from config import DEFAULT_MODEL
                model_name = DEFAULT_MODEL
            logger.debug(f"Using fallback model resolution for '{model_name}' (test mode)")

            # Hidden router: resolve to a real model if sentinel
            if os.getenv("HIDDEN_MODEL_ROUTER_ENABLED", "true").strip().lower() == "true":
                sentinels = {s.strip().lower() for s in os.getenv("ROUTER_SENTINEL_MODELS", "glm-4.5-flash,auto").split(",") if s.strip()}
                if model_name.strip().lower() in sentinels:
                    from src.router.service import RouterService
                    routed = RouterService().choose_model(model_name)
                    if routed and getattr(routed, "chosen", None):
                        logger.debug(f"Hidden-router selected '{routed.chosen}' reason='{routed.reason}'")
                        model_name = routed.chosen

            # For tests: Check if we should require model selection
            if self._should_require_model_selection(model_name):
                from src.providers.registry_core import ModelProviderRegistry
                tool_category = self.get_model_category()
                suggested_model = ModelProviderRegistry.get_preferred_fallback_model(tool_category)
                available_models = self._get_available_models()
                error_message = (
                    f"Model '{model_name}' is not available with current API keys. "
                    f"Available models: {', '.join(available_models)}. "
                    f"Suggested model for {self.get_name()}: '{suggested_model}' "
                    f"(category: {tool_category.value})"
                )
                raise ValueError(error_message)

            # Create model context for tests
            from utils.model.context import ModelContext
            model_context = ModelContext(model_name)

        return model_name, model_context

    # ================================================================================
    # Temperature Validation
    # ================================================================================

    def validate_and_correct_temperature(self, temperature: float, model_context: Any) -> tuple[float, list[str]]:
        """
        Validate and correct temperature for the specified model.

        This method ensures that the temperature value is within the valid range
        for the specific model being used. Different models have different temperature
        constraints (e.g., o1 models require temperature=1.0, GPT models support 0-2).

        Args:
            temperature: Temperature value to validate
            model_context: Model context object containing model name, provider, and capabilities

        Returns:
            Tuple of (corrected_temperature, warning_messages)
        """
        try:
            # Use model context capabilities directly - clean OOP approach
            capabilities = model_context.capabilities
            constraint = capabilities.temperature_constraint

            warnings = []
            if not constraint.validate(temperature):
                corrected = constraint.get_corrected_value(temperature)
                warning = (
                    f"Temperature {temperature} invalid for {model_context.model_name}. "
                    f"{constraint.get_description()}. Using {corrected} instead."
                )
                warnings.append(warning)
                return corrected, warnings

            return temperature, warnings

        except Exception as e:
            # If validation fails for any reason, use the original temperature
            # and log a warning (but don't fail the request)
            logger.warning(f"Temperature validation failed for {model_context.model_name}: {e}")
            return temperature, [f"Temperature validation failed: {e}"]

    # ================================================================================
    # Model Field Schema Generation
    # ================================================================================

    def get_model_field_schema(self) -> dict[str, Any]:
        """
        Generate the model field schema based on auto mode configuration.

        When auto mode is enabled, the model parameter becomes required
        and includes detailed descriptions of each model's capabilities.

        Returns:
            dict containing the model field JSON schema
        """
        from config import DEFAULT_MODEL

        # Check if OpenRouter is configured
        has_openrouter = bool(
            os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_API_KEY") != "your_openrouter_api_key_here"
        )

        # Use the centralized effective auto mode check
        if self.is_effective_auto_mode():
            # In auto mode, model is required and we provide detailed descriptions
            model_desc_parts = [
                "IMPORTANT: Use the model specified by the user if provided, OR select the most suitable model "
                "for this specific task based on the requirements and capabilities listed below:"
            ]

            # Get descriptions from enabled providers
            from src.providers.base import ProviderType

            # Map provider types to readable names
            provider_names = {
                ProviderType.GOOGLE: "Gemini models",
                ProviderType.OPENAI: "OpenAI models",
                ProviderType.XAI: "X.AI GROK models",
                ProviderType.DIAL: "DIAL models",
                ProviderType.CUSTOM: "Custom models",
                ProviderType.OPENROUTER: "OpenRouter models",
            }

            # Check available providers and add their model descriptions
            # Start with native providers
            from src.providers.registry_core import get_registry_instance
            registry = get_registry_instance()

            for provider_type in [ProviderType.GOOGLE, ProviderType.OPENAI, ProviderType.XAI, ProviderType.DIAL]:
                # Only if this is registered / available
                provider = registry.get_provider(provider_type)
                if provider:
                    provider_section_added = False
                    for model_name in provider.list_models(respect_restrictions=True):
                        try:
                            # Get model config to extract description
                            model_config = provider.SUPPORTED_MODELS.get(model_name)
                            if model_config and model_config.description:
                                if not provider_section_added:
                                    model_desc_parts.append(
                                        f"\n{provider_names[provider_type]} - Available when {provider_type.value.upper()}_API_KEY is configured:"
                                    )
                                    provider_section_added = True
                                model_desc_parts.append(f"- '{model_name}': {model_config.description}")
                        except Exception:
                            # Skip models without descriptions
                            continue

            # Add custom models if custom API is configured
            custom_url = os.getenv("CUSTOM_API_URL")
            if custom_url:
                # Load custom models from registry
                try:
                    registry = self._get_openrouter_registry()
                    model_desc_parts.append(f"\nCustom models via {custom_url}:")

                    # Find all custom models (is_custom=true)
                    for alias in registry.list_aliases():
                        config = registry.resolve(alias)
                        # Check if this is a custom model that requires custom endpoints
                        if config and config.is_custom:
                            # Format context window
                            context_tokens = config.context_window
                            if context_tokens >= 1_000_000:
                                context_str = f"{context_tokens // 1_000_000}M"
                            elif context_tokens >= 1_000:
                                context_str = f"{context_tokens // 1_000}K"
                            else:
                                context_str = str(context_tokens)

                            desc_line = f"- '{alias}' ({context_str} context): {config.description}"
                            if desc_line not in model_desc_parts:  # Avoid duplicates
                                model_desc_parts.append(desc_line)
                except Exception as e:
                    logging.debug(f"Failed to load custom model descriptions: {e}")
                    model_desc_parts.append(f"\nCustom models: Models available via {custom_url}")

            if has_openrouter:
                # Add OpenRouter models with descriptions
                try:
                    registry = self._get_openrouter_registry()

                    # Group models by their model_name to avoid duplicates
                    seen_models = set()
                    model_configs = []

                    for alias in registry.list_aliases():
                        config = registry.resolve(alias)
                        if config and config.model_name not in seen_models:
                            seen_models.add(config.model_name)
                            model_configs.append((alias, config))

                    # Sort by context window (descending) then by alias
                    model_configs.sort(key=lambda x: (-x[1].context_window, x[0]))

                    if model_configs:
                        model_desc_parts.append("\nOpenRouter models (use these aliases):")
                        for alias, config in model_configs:  # Show ALL models so Claude can choose
                            # Format context window in human-readable form
                            context_tokens = config.context_window
                            if context_tokens >= 1_000_000:
                                context_str = f"{context_tokens // 1_000_000}M"
                            elif context_tokens >= 1_000:
                                context_str = f"{context_tokens // 1_000}K"
                            else:
                                context_str = str(context_tokens)

                            # Build description line
                            if config.description:
                                desc = f"- '{alias}' ({context_str} context): {config.description}"
                            else:
                                # Fallback to showing the model name if no description
                                desc = f"- '{alias}' ({context_str} context): {config.model_name}"
                            model_desc_parts.append(desc)

                        # Show all models - no truncation needed
                except Exception as e:
                    # Log for debugging but don't fail
                    logging.debug(f"Failed to load OpenRouter model descriptions: {e}")
                    # Fallback to simple message
                    model_desc_parts.append(
                        "\nOpenRouter models: If configured, you can also use ANY model available on OpenRouter."
                    )

            # Get all available models for the enum (canonicalized)
            all_models = self._get_available_models()

            # Canonicalize names by resolving aliases to provider base names
            def _canonicalize(models: list[str]) -> list[str]:
                canon_set = []
                seen = set()
                for m in models:
                    cm = m
                    try:
                        provider = self._registry.get_provider_for_model(m)
                        if provider:
                            caps = provider.get_capabilities(m)
                            cm = caps.model_name or m
                    except Exception:
                        cm = m
                    # Normalize alt uppercase canonical to lowercase variant
                    if cm == "GLM-4":
                        cm = "glm-4"
                    # Filter obvious provider ids
                    low = cm.lower()
                    if low in {"z-ai"}:
                        continue
                    if any(s in low for s in ["-250414", "-airx"]):
                        continue
                    if cm not in seen:
                        seen.add(cm)
                        canon_set.append(cm)
                return canon_set

            all_models = _canonicalize(all_models)

            # Allow 'auto' as a valid option for strict clients; server resolves it
            if "auto" not in all_models:
                all_models = ["auto"] + all_models

            return {
                "type": "string",
                "description": "\n".join(model_desc_parts),
                "enum": all_models,
            }
        else:
            # Normal mode - model is optional with default
            available_models = self._get_available_models()

            # Canonicalize + filter questionable names from being exposed in schemas
            def _canonicalize_and_filter(models: list[str]) -> list[str]:
                disallow_exact = {"z-ai"}
                # REMOVED: "-preview", "-0711", "-0905" from disallow list
                # These are valid K2 model names that user prefers (kimi-k2-0905-preview, etc.)
                # Only filter out truly invalid/internal model IDs
                disallow_substrings = ["-250414", "-airx"]
                seen = set()
                cleaned: list[str] = []
                for m in models:
                    ml = (m or "").strip()
                    if not ml:
                        continue
                    # Resolve alias to canonical base model when possible
                    cm = ml
                    try:
                        provider = self._registry.get_provider_for_model(ml)
                        if provider:
                            caps = provider.get_capabilities(ml)
                            cm = caps.model_name or ml
                    except Exception:
                        cm = ml
                    # Normalize canonical variations
                    if cm == "GLM-4":
                        cm = "glm-4"
                    low = cm.lower()
                    if low in disallow_exact:
                        continue
                    if any(s in low for s in disallow_substrings):
                        continue
                    if cm not in seen:
                        seen.add(cm)
                        cleaned.append(cm)
                return cleaned

            canon_models = _canonicalize_and_filter(available_models)
            if "auto" not in canon_models:
                canon_models = ["auto"] + canon_models
            models_str = ", ".join(f"'{m}'" for m in canon_models)

            description = f"Model to use. Native models: {models_str}. Use 'auto' to let the server select the best model."
            if has_openrouter:
                # Add OpenRouter aliases
                try:
                    registry = self._get_openrouter_registry()
                    aliases = registry.list_aliases()

                    # Show ALL aliases from the configuration
                    if aliases:
                        # Show all aliases so clients know options
                        all_aliases = sorted(aliases)
                        alias_list = ", ".join(f"'{a}'" for a in all_aliases)
                        description += f" OpenRouter aliases: {alias_list}."
                    else:
                        description += " OpenRouter: Any model available on openrouter.ai."
                except Exception:
                    description += (
                        " OpenRouter: Any model available on openrouter.ai "
                        "(e.g., 'gpt-4', 'claude-4-opus', 'mistral-large')."
                    )
            description += f" Defaults to '{DEFAULT_MODEL}' if not specified."

            return {
                "type": "string",
                "description": description,
            }

