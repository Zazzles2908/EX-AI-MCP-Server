"""
Provider Restrictions Module

Handles model restriction validation and auto mode validation.
"""

import logging

logger = logging.getLogger(__name__)


def validate_model_restrictions():
    """
    Validate and log model restrictions.
    
    Checks restriction service for configured restrictions and validates
    them against known models from registered providers.
    """
    from utils.model.restrictions import get_restriction_service
    from src.providers.registry import ModelProviderRegistry
    from src.providers.base import ProviderType
    
    restriction_service = get_restriction_service()
    restrictions = restriction_service.get_restriction_summary()
    
    if not restrictions:
        logger.info("No model restrictions configured - all models allowed")
        return
    
    # Log restrictions
    logger.info("Model restrictions configured:")
    for provider_name, allowed_models in restrictions.items():
        if isinstance(allowed_models, list):
            logger.info(f"  {provider_name}: {', '.join(allowed_models)}")
        else:
            logger.info(f"  {provider_name}: {allowed_models}")
    
    # Validate restrictions against known models
    provider_instances = {}
    provider_types_to_validate = [
        ProviderType.KIMI,
        ProviderType.GLM,
        ProviderType.CUSTOM,
        ProviderType.OPENROUTER,
    ]
    
    for provider_type in provider_types_to_validate:
        provider = ModelProviderRegistry.get_provider(provider_type)
        if provider:
            provider_instances[provider_type] = provider
    
    if provider_instances:
        restriction_service.validate_against_known_models(provider_instances)


def validate_auto_mode():
    """
    Validate that auto mode has available models after restrictions.
    
    Raises:
        ValueError: If auto mode is enabled but no models are available
    """
    from config import IS_AUTO_MODE
    from src.providers.registry import ModelProviderRegistry
    
    if not IS_AUTO_MODE:
        return
    
    available_models = ModelProviderRegistry.get_available_models(respect_restrictions=True)
    
    if not available_models:
        logger.error(
            "Auto mode is enabled but no models are available after applying restrictions. "
            "Please check your OPENAI_ALLOWED_MODELS and GOOGLE_ALLOWED_MODELS settings."
        )
        raise ValueError(
            "No models available for auto mode due to restrictions. "
            "Please adjust your allowed model settings or disable auto mode."
        )

