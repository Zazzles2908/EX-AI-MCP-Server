"""
Tool Model Categories
Classification system for routing decisions in EX-AI-MCP-Server
"""

from enum import Enum
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ToolModelCategory(Enum):
    """Categories for tool-to-model routing decisions"""
    FAST_RESPONSE = "fast_response"
    EXTENDED_REASONING = "extended_reasoning" 
    BALANCED = "balanced"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    MATHEMATICAL = "mathematical"
    REASONING = "reasoning"


class CategoryMapping:
    """Mapping between tool categories and optimal model configurations"""
    
    # Default model recommendations by category
    DEFAULT_MODELS = {
        ToolModelCategory.FAST_RESPONSE: [
            "gpt-3.5-turbo",
            "claude-3-haiku",
            "glm-4.5-flash",
            "abab6.5g-chat"
        ],
        ToolModelCategory.EXTENDED_REASONING: [
            "gpt-4-turbo",
            "claude-3-opus", 
            "abab6.5s-chat",
            "deepseek-chat"
        ],
        ToolModelCategory.BALANCED: [
            "gpt-3.5-turbo",
            "claude-3-haiku",
            "glm-4.5-flash",
            "mixtral-8x7b-instruct"
        ],
        ToolModelCategory.CODE_GENERATION: [
            "deepseek-coder",
            "gpt-4-turbo", 
            "claude-3-opus",
            "code-llama"
        ],
        ToolModelCategory.MULTIMODAL: [
            "gpt-4-vision",
            "claude-3-haiku",
            "glm-4v"
        ],
        ToolModelCategory.CREATIVE_WRITING: [
            "gpt-4-turbo",
            "claude-3-opus",
            "abab6.5s-chat"
        ],
        ToolModelCategory.DATA_ANALYSIS: [
            "gpt-4-turbo",
            "claude-3-opus",
            "deepseek-chat"
        ],
        ToolModelCategory.MATHEMATICAL: [
            "gpt-4-turbo",
            "claude-3-opus",
            "deepseek-chat"
        ],
        ToolModelCategory.REASONING: [
            "gpt-4-turbo",
            "claude-3-opus", 
            "abab6.5s-chat"
        ]
    }
    
    # Token cost considerations (cost per 1M tokens)
    TOKEN_COSTS = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "deepseek-coder": {"input": 0.0014, "output": 0.0028},
        "deepseek-chat": {"input": 0.0014, "output": 0.0028},
        "abab6.5s-chat": {"input": 0.0025, "output": 0.0025},
        "abab6.5g-chat": {"input": 0.0025, "output": 0.0025},
        "glm-4.5-flash": {"input": 0.001, "output": 0.001}
    }
    
    # Performance characteristics
    PERFORMANCE_TRAITS = {
        "speed": ["gpt-3.5-turbo", "claude-3-haiku", "glm-4.5-flash"],
        "quality": ["gpt-4-turbo", "claude-3-opus", "deepseek-chat"],
        "coding": ["deepseek-coder", "gpt-4-turbo", "claude-3-opus"],
        "reasoning": ["gpt-4-turbo", "claude-3-opus", "abab6.5s-chat"],
        "cost_efficiency": ["gpt-3.5-turbo", "deepseek-chat", "glm-4.5-flash"]
    }
    
    @classmethod
    def get_recommended_models(
        cls, 
        category: ToolModelCategory, 
        max_cost: Optional[float] = None,
        preferred_traits: Optional[List[str]] = None
    ) -> List[str]:
        """Get recommended models for a category"""
        models = cls.DEFAULT_MODELS.get(category, [])
        
        # Filter by cost if specified
        if max_cost is not None:
            models = [
                model for model in models 
                if cls._get_model_cost(model) <= max_cost
            ]
        
        # Sort by preferred traits
        if preferred_traits:
            models = cls._sort_by_traits(models, preferred_traits)
        
        return models
    
    @classmethod
    def _get_model_cost(cls, model: str) -> float:
        """Get average cost per token for a model"""
        costs = cls.TOKEN_COSTS.get(model, {"input": 0.01, "output": 0.01})
        return (costs["input"] + costs["output"]) / 2
    
    @classmethod
    def _sort_by_traits(cls, models: List[str], traits: List[str]) -> List[str]:
        """Sort models by how well they match preferred traits"""
        def score_model(model: str) -> int:
            score = 0
            for trait in traits:
                if trait in cls.PERFORMANCE_TRAITS:
                    if model in cls.PERFORMANCE_TRAITS[trait]:
                        score += 10  # High weight for direct matches
                    elif any(
                        model.lower() in other_model 
                        for other_model in cls.PERFORMANCE_TRAITS[trait]
                    ):
                        score += 5  # Partial matches
            return score
        
        return sorted(models, key=score_model, reverse=True)
    
    @classmethod
    def get_category_for_tool(cls, tool_name: str) -> ToolModelCategory:
        """Determine appropriate category for a given tool"""
        tool_lower = tool_name.lower()
        
        # Fast response tools
        if any(keyword in tool_lower for keyword in [
            'quick', 'fast', 'simple', 'basic', 'check', 'ping', 'status'
        ]):
            return ToolModelCategory.FAST_RESPONSE
        
        # Code generation tools
        elif any(keyword in tool_lower for keyword in [
            'code', 'generate', 'create', 'build', 'compile', 'execute'
        ]):
            return ToolModelCategory.CODE_GENERATION
        
        # Mathematical tools
        elif any(keyword in tool_lower for keyword in [
            'calc', 'compute', 'math', 'calculate', 'solve'
        ]):
            return ToolModelCategory.MATHEMATICAL
        
        # Data analysis tools
        elif any(keyword in tool_lower for keyword in [
            'analyze', 'data', 'stats', 'analytics', 'report', 'summary'
        ]):
            return ToolModelCategory.DATA_ANALYSIS
        
        # Creative tools
        elif any(keyword in tool_lower for keyword in [
            'write', 'creative', 'story', 'poem', 'content', 'generate_text'
        ]):
            return ToolModelCategory.CREATIVE_WRITING
        
        # Multimodal tools
        elif any(keyword in tool_lower for keyword in [
            'image', 'vision', 'visual', 'multimodal', 'video', 'audio'
        ]):
            return ToolModelCategory.MULTIMODAL
        
        # Extended reasoning tools
        elif any(keyword in tool_lower for keyword in [
            'think', 'reason', 'analyze', 'plan', 'strategy', 'decision'
        ]):
            return ToolModelCategory.EXTENDED_REASONING
        
        # Default to balanced
        else:
            return ToolModelCategory.BALANCED
    
    @classmethod
    def get_routing_preferences(cls, category: ToolModelCategory) -> Dict[str, Any]:
        """Get routing preferences for a category"""
        preferences = {
            ToolModelCategory.FAST_RESPONSE: {
                'timeout': 30,
                'retries': 2,
                'max_tokens': 2048,
                'temperature': 0.3,
                'priority': 'speed'
            },
            ToolModelCategory.EXTENDED_REASONING: {
                'timeout': 120,
                'retries': 3,
                'max_tokens': 8192,
                'temperature': 0.7,
                'priority': 'quality'
            },
            ToolModelCategory.BALANCED: {
                'timeout': 60,
                'retries': 2,
                'max_tokens': 4096,
                'temperature': 0.5,
                'priority': 'balanced'
            },
            ToolModelCategory.CODE_GENERATION: {
                'timeout': 90,
                'retries': 2,
                'max_tokens': 4096,
                'temperature': 0.2,
                'priority': 'accuracy'
            },
            ToolModelCategory.CREATIVE_WRITING: {
                'timeout': 90,
                'retries': 2,
                'max_tokens': 6144,
                'temperature': 0.8,
                'priority': 'creativity'
            },
            ToolModelCategory.DATA_ANALYSIS: {
                'timeout': 120,
                'retries': 3,
                'max_tokens': 6144,
                'temperature': 0.4,
                'priority': 'accuracy'
            },
            ToolModelCategory.MATHEMATICAL: {
                'timeout': 90,
                'retries': 2,
                'max_tokens': 4096,
                'temperature': 0.1,
                'priority': 'precision'
            },
            ToolModelCategory.REASONING: {
                'timeout': 150,
                'retries': 3,
                'max_tokens': 8192,
                'temperature': 0.6,
                'priority': 'depth'
            },
            ToolModelCategory.MULTIMODAL: {
                'timeout': 120,
                'retries': 2,
                'max_tokens': 4096,
                'temperature': 0.5,
                'priority': 'accuracy'
            }
        }
        
        return preferences.get(category, preferences[ToolModelCategory.BALANCED])


class RoutingDecision:
    """Represents a routing decision made by the system"""
    
    def __init__(
        self,
        tool_name: str,
        category: ToolModelCategory,
        selected_model: str,
        confidence: float,
        reasoning: str,
        alternative_models: List[str] = None,
        cost_estimate: Optional[float] = None,
        performance_metrics: Dict[str, Any] = None
    ):
        self.tool_name = tool_name
        self.category = category
        self.selected_model = selected_model
        self.confidence = confidence
        self.reasoning = reasoning
        self.alternative_models = alternative_models or []
        self.cost_estimate = cost_estimate
        self.performance_metrics = performance_metrics or {}
        self.timestamp = None  # Set by caller
        self.success = None  # Set by caller
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/monitoring"""
        return {
            'tool_name': self.tool_name,
            'category': self.category.value,
            'selected_model': self.selected_model,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'alternative_models': self.alternative_models,
            'cost_estimate': self.cost_estimate,
            'performance_metrics': self.performance_metrics,
            'timestamp': self.timestamp,
            'success': self.success
        }


# Export main classes and functions
__all__ = [
    'ToolModelCategory',
    'CategoryMapping',
    'RoutingDecision'
]