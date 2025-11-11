"""Minimal base provider types after 98% reduction."""

from typing import Any, Dict, Optional
from enum import Enum


class ProviderType(Enum):
    """Provider type enumeration."""
    GLM = "glm"
    KIMI = "kimi"
    CUSTOM = "custom"
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    GOOGLE = "google"
    XAI = "xai"
    DIAL = "dial"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    VERTEX = "vertex"
    BEDROCK = "bedrock"
    SAGE = "sag"
    COHERE = "cohere"
    MISTRAL = "mistral"
    GROQ = "groq"
    FIREWORKS = "fireworks"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    BAICHUAN = "baichuan"
    GLM_LOCAL = "glm_local"
    KIMI_API = "kimi_api"
    PERPLEXITY = "perplexity"


class ModelCapabilities:
    """Model capabilities with default temperature constraint."""

    def __init__(self):
        # Default: GLM and similar models support temperature 0.0-1.0
        self.temperature_constraint = RangeTemperatureConstraint(min_value=0.0, max_value=1.0)


class ModelResponse:
    """Minimal model response."""
    def __init__(
        self,
        content: str,
        usage: Optional[Dict] = None,
        model_name: str = "",
        friendly_name: str = "",
        provider: Optional[ProviderType] = None,
        metadata: Optional[Dict] = None
    ):
        self.content = content
        self.usage = usage or {}
        self.model_name = model_name
        self.friendly_name = friendly_name
        self.provider = provider
        self.metadata = metadata or {}


class TemperatureConstraint:
    """Base temperature constraint."""

    def validate(self, temperature: float) -> bool:
        """Validate if temperature is within constraint."""
        raise NotImplementedError

    def get_corrected_value(self, temperature: float) -> float:
        """Get corrected temperature value."""
        raise NotImplementedError

    def get_description(self) -> str:
        """Get description of the constraint."""
        raise NotImplementedError


class FixedTemperatureConstraint(TemperatureConstraint):
    """Fixed temperature constraint - only accepts one value."""

    def __init__(self, fixed_value: float):
        self.fixed_value = fixed_value

    def validate(self, temperature: float) -> bool:
        return temperature == self.fixed_value

    def get_corrected_value(self, temperature: float) -> float:
        return self.fixed_value

    def get_description(self) -> str:
        return f"Temperature must be exactly {self.fixed_value}"


class RangeTemperatureConstraint(TemperatureConstraint):
    """Range temperature constraint - accepts values within a range."""

    def __init__(self, min_value: float, max_value: float):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, temperature: float) -> bool:
        return self.min_value <= temperature <= self.max_value

    def get_corrected_value(self, temperature: float) -> float:
        if temperature < self.min_value:
            return self.min_value
        if temperature > self.max_value:
            return self.max_value
        return temperature

    def get_description(self) -> str:
        return f"Temperature must be between {self.min_value} and {self.max_value}"


class DiscreteTemperatureConstraint(TemperatureConstraint):
    """Discrete temperature constraint - accepts only specific values."""

    def __init__(self, allowed_values: list[float]):
        self.allowed_values = sorted(allowed_values)

    def validate(self, temperature: float) -> bool:
        return temperature in self.allowed_values

    def get_corrected_value(self, temperature: float) -> float:
        # Find closest allowed value
        return min(self.allowed_values, key=lambda x: abs(x - temperature))

    def get_description(self) -> str:
        values_str = ", ".join(str(v) for v in self.allowed_values)
        return f"Temperature must be one of: {values_str}"


def create_temperature_constraint(value: float) -> TemperatureConstraint:
    """Create temperature constraint."""
    return FixedTemperatureConstraint(value)


class ModelProvider:
    """Minimal model provider."""
    pass
