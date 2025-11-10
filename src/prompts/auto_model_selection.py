"""
Auto-Model Selection System

Intelligently selects the optimal AI model for each task based on:
- Task requirements and complexity
- Historical performance data
- Timeout statistics
- Quality and speed requirements
- Context size needs

Phase 1.4 Implementation - Intelligent Model Selection
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math

from .model_recommendation_guide import ModelRecommendationEngine, ModelSpec
from .timeout_monitoring import get_timeout_monitor

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"


class TaskType(Enum):
    """Task categories for model selection."""
    CHAT = "chat"
    CODE_REVIEW = "codereview"
    DEBUG = "debug"
    ANALYZE = "analyze"
    REFACTOR = "refactor"
    TESTING = "testgen"
    DOCUMENTATION = "docgen"
    PLANNING = "planner"
    TRACING = "tracer"
    SECURITY = "secaudit"
    PRE_COMMIT = "precommit"
    CONSENSUS = "consensus"
    DEEP_THINKING = "thinkdeep"


@dataclass
class SelectionContext:
    """Context for model selection."""
    task_type: TaskType
    complexity: TaskComplexity
    quality_priority: str  # low, balanced, high
    speed_priority: str  # low, balanced, high
    context_size: str  # small, medium, large
    output_length: str  # short, medium, long
    budget_constraint: Optional[str] = None  # low, medium, high
    reliability_requirement: str = "normal"  # low, normal, high


@dataclass
class ModelSelectionResult:
    """Result of model selection."""
    selected_model: str
    confidence: float
    alternative_models: List[str]
    reasoning: List[str]
    estimated_performance: Dict[str, Any]
    warnings: List[str]


class AutoModelSelector:
    """
    Intelligent model selection system.

    Analyzes task requirements and selects the optimal model from available
    options considering performance, cost, reliability, and quality.
    """

    def __init__(self):
        """Initialize the auto-model selector."""
        self.recommendation_engine = ModelRecommendationEngine()
        self.timeout_monitor = get_timeout_monitor()

        # Model capability matrix
        self.model_capabilities = {
            "kimi-k2-turbo-preview": {
                "speed": 5,
                "quality": 4,
                "context": 5,
                "reasoning": 4,
                "cost_efficiency": 5,
                "reliability": 4
            },
            "kimi-k2-0905-preview": {
                "speed": 4,
                "quality": 5,
                "context": 5,
                "reasoning": 5,
                "cost_efficiency": 4,
                "reliability": 5
            },
            "kimi-k2-thinking-preview": {
                "speed": 2,
                "quality": 5,
                "context": 5,
                "reasoning": 5,
                "cost_efficiency": 3,
                "reliability": 5
            },
            "glm-4.6": {
                "speed": 3,
                "quality": 5,
                "context": 4,
                "reasoning": 5,
                "cost_efficiency": 4,
                "reliability": 4
            },
            "glm-4.5-flash": {
                "speed": 5,
                "quality": 3,
                "context": 3,
                "reasoning": 3,
                "cost_efficiency": 5,
                "reliability": 4
            }
        }

        # Task-specific model preferences
        self.task_preferences = {
            TaskType.CHAT: {
                "primary": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": ["kimi-k2-thinking-preview"]
            },
            TaskType.CODE_REVIEW: {
                "primary": ["kimi-k2-thinking-preview", "kimi-k2-0905-preview"],
                "secondary": ["glm-4.6"],
                "avoid": ["glm-4.5-flash"]
            },
            TaskType.DEBUG: {
                "primary": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": []
            },
            TaskType.ANALYZE: {
                "primary": ["kimi-k2-0905-preview", "glm-4.6"],
                "secondary": ["kimi-k2-thinking-preview"],
                "avoid": ["glm-4.5-flash"]
            },
            TaskType.REFACTOR: {
                "primary": ["kimi-k2-0905-preview", "glm-4.6"],
                "secondary": ["kimi-k2-thinking-preview"],
                "avoid": []
            },
            TaskType.SECURITY: {
                "primary": ["kimi-k2-thinking-preview", "glm-4.6"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": ["glm-4.5-flash"]
            },
            TaskType.TESTING: {
                "primary": ["kimi-k2-thinking-preview", "glm-4.6"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": []
            },
            TaskType.DOCUMENTATION: {
                "primary": ["kimi-k2-turbo-preview", "glm-4.6"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": []
            },
            TaskType.PLANNING: {
                "primary": ["kimi-k2-thinking-preview", "glm-4.6"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": ["glm-4.5-flash"]
            },
            TaskType.CONSENSUS: {
                "primary": ["kimi-k2-thinking-preview", "glm-4.6"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": []
            },
            TaskType.TRACING: {
                "primary": ["kimi-k2-0905-preview", "glm-4.6"],
                "secondary": [],
                "avoid": []
            },
            TaskType.PRE_COMMIT: {
                "primary": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
                "secondary": ["kimi-k2-0905-preview"],
                "avoid": []
            },
            TaskType.DEEP_THINKING: {
                "primary": ["kimi-k2-thinking-preview", "glm-4.6"],
                "secondary": [],
                "avoid": ["kimi-k2-turbo-preview", "glm-4.5-flash"]
            }
        }

    def select_model(self, context: SelectionContext) -> ModelSelectionResult:
        """
        Select the optimal model for the given context.

        Args:
            context: Task context with requirements

        Returns:
            ModelSelectionResult with chosen model and alternatives
        """
        # Get initial recommendation from engine
        tool_name = context.task_type.value
        engine_rec = self.recommendation_engine.recommend_model(
            task_type=tool_name,
            context_size=context.context_size,
            quality_priority=context.quality_priority,
            speed_priority=context.speed_priority,
            output_length=context.output_length
        )

        if not engine_rec:
            # Fallback to default
            return ModelSelectionResult(
                selected_model="kimi-k2-0905-preview",
                confidence=0.5,
                alternative_models=["glm-4.6"],
                reasoning=["No recommendation available, using default"],
                estimated_performance={},
                warnings=["Using fallback model selection"]
            )

        # Score all available models
        model_scores = self._score_models(context, engine_rec.name)

        # Get top models
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        selected_model = sorted_models[0][0]
        confidence = min(sorted_models[0][1] / 100.0, 1.0)

        # Get alternatives
        alternatives = [m[0] for m in sorted_models[1:3]]

        # Generate reasoning
        reasoning = self._generate_reasoning(context, selected_model, model_scores)

        # Get estimated performance
        estimated_performance = self._estimate_performance(selected_model, context)

        # Check for warnings
        warnings = self._check_warnings(context, selected_model)

        return ModelSelectionResult(
            selected_model=selected_model,
            confidence=confidence,
            alternative_models=alternatives,
            reasoning=reasoning,
            estimated_performance=estimated_performance,
            warnings=warnings
        )

    def _score_models(self, context: SelectionContext, preferred_model: str) -> Dict[str, float]:
        """
        Score all models for the given context.

        Args:
            context: Task context
            preferred_model: Model preferred by recommendation engine

        Returns:
            Dictionary mapping model names to scores (0-100)
        """
        scores = {}

        for model_name, capabilities in self.model_capabilities.items():
            score = 0.0
            reasons = []

            # Base score from recommendation engine alignment
            if model_name == preferred_model:
                score += 40
                reasons.append("Aligns with recommendation engine")

            # Task-specific preferences
            task_pref = self.task_preferences.get(context.task_type, {})
            if model_name in task_pref.get("primary", []):
                score += 30
                reasons.append(f"Primary choice for {context.task_type.value}")
            elif model_name in task_pref.get("secondary", []):
                score += 15
                reasons.append(f"Secondary choice for {context.task_type.value}")
            elif model_name in task_pref.get("avoid", []):
                score -= 20
                reasons.append(f"Should avoid for {context.task_type.value}")

            # Quality priority
            if context.quality_priority == "high":
                score += capabilities["quality"] * 5
                reasons.append("High quality priority")
            elif context.quality_priority == "balanced":
                score += capabilities["quality"] * 3
            else:  # low
                score += capabilities["quality"] * 1

            # Speed priority
            if context.speed_priority == "high":
                score += capabilities["speed"] * 5
                reasons.append("High speed priority")
            elif context.speed_priority == "balanced":
                score += capabilities["speed"] * 3
            else:  # low
                score += capabilities["speed"] * 1

            # Context size
            if context.context_size == "large":
                score += capabilities["context"] * 4
                reasons.append("Large context requirement")
            elif context.context_size == "medium":
                score += capabilities["context"] * 2
            else:  # small
                score += capabilities["context"] * 1

            # Complexity
            if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
                score += capabilities["reasoning"] * 4
                reasons.append("Complex task requires reasoning")
            else:
                score += capabilities["reasoning"] * 2

            # Budget constraint
            if context.budget_constraint == "low":
                score += capabilities["cost_efficiency"] * 3
                reasons.append("Budget constraint: cost efficiency important")
            elif context.budget_constraint == "medium":
                score += capabilities["cost_efficiency"] * 2

            # Reliability requirement
            if context.reliability_requirement == "high":
                score += capabilities["reliability"] * 3
                reasons.append("High reliability requirement")
            else:
                score += capabilities["reliability"] * 1

            # Timeout history (bonus for models with good timeout stats)
            timeout_stats = self.timeout_monitor.get_stats(
                context.task_type.value,
                model_name
            )
            if timeout_stats and timeout_stats.timeout_rate < 0.05:  # <5% timeout rate
                score += 10
                reasons.append("Low timeout rate")

            scores[model_name] = score

        return scores

    def _generate_reasoning(self,
                          context: SelectionContext,
                          selected_model: str,
                          scores: Dict[str, float]) -> List[str]:
        """Generate reasoning for model selection."""
        reasoning = []
        model_name = selected_model

        # Get task preferences
        task_pref = self.task_preferences.get(context.task_type, {})
        if model_name in task_pref.get("primary", []):
            reasoning.append(f"Primary choice for {context.task_type.value} tasks")

        # Check capabilities
        capabilities = self.model_capabilities.get(model_name, {})
        if context.quality_priority == "high" and capabilities.get("quality", 0) >= 4:
            reasoning.append("High quality capability")

        if context.speed_priority == "high" and capabilities.get("speed", 0) >= 4:
            reasoning.append("High speed capability")

        if context.context_size == "large" and capabilities.get("context", 0) >= 4:
            reasoning.append("Large context window support")

        if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            if capabilities.get("reasoning", 0) >= 4:
                reasoning.append("Strong reasoning capability")

        # Check timeout performance
        timeout_stats = self.timeout_monitor.get_stats(
            context.task_type.value,
            model_name
        )
        if timeout_stats and timeout_stats.timeout_rate < 0.05:
            reasoning.append("Excellent timeout performance")

        return reasoning

    def _estimate_performance(self, model_name: str, context: SelectionContext) -> Dict[str, Any]:
        """Estimate performance metrics for the selected model."""
        capabilities = self.model_capabilities.get(model_name, {})

        # Estimate response time based on complexity and model speed
        base_time = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MODERATE: 5,
            TaskComplexity.COMPLEX: 15,
            TaskComplexity.CRITICAL: 30
        }

        response_time = base_time.get(context.complexity, 5)
        response_time = response_time * (6 - capabilities.get("speed", 3)) / 3

        # Estimate quality score
        quality_score = capabilities.get("quality", 3) * 20

        # Estimate success probability
        success_prob = 0.95 - (capabilities.get("speed", 3) - 3) * 0.05
        success_prob = max(0.7, min(0.99, success_prob))

        return {
            "estimated_response_time_seconds": round(response_time, 1),
            "estimated_quality_score": quality_score,
            "estimated_success_probability": round(success_prob, 2),
            "capabilities": capabilities
        }

    def _check_warnings(self, context: SelectionContext, model_name: str) -> List[str]:
        """Check for potential issues with the selection."""
        warnings = []
        capabilities = self.model_capabilities.get(model_name, {})

        # Check for capability gaps
        if context.quality_priority == "high" and capabilities.get("quality", 0) < 4:
            warnings.append("Model may not meet high quality requirements")

        if context.speed_priority == "high" and capabilities.get("speed", 0) < 4:
            warnings.append("Model may not meet high speed requirements")

        if context.context_size == "large" and capabilities.get("context", 0) < 4:
            warnings.append("Model may struggle with large context")

        if context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            if capabilities.get("reasoning", 0) < 4:
                warnings.append("Model may struggle with complex reasoning")

        # Check timeout history
        timeout_stats = self.timeout_monitor.get_stats(
            context.task_type.value,
            model_name
        )
        if timeout_stats and timeout_stats.timeout_rate > 0.1:
            warnings.append(f"High timeout rate ({timeout_stats.timeout_rate*100:.1f}%) for this tool/model")

        return warnings

    def explain_selection(self, result: ModelSelectionResult) -> str:
        """
        Generate a human-readable explanation of the model selection.

        Args:
            result: Model selection result

        Returns:
            Formatted explanation string
        """
        explanation = []
        explanation.append("="*70)
        explanation.append("AUTO-MODEL SELECTION RESULT")
        explanation.append("="*70)
        explanation.append("")
        explanation.append(f"Selected Model: {result.selected_model}")
        explanation.append(f"Confidence: {result.confidence*100:.0f}%")
        explanation.append("")

        if result.reasoning:
            explanation.append("REASONING:")
            for reason in result.reasoning:
                explanation.append(f"  - {reason}")
            explanation.append("")

        if result.estimated_performance:
            perf = result.estimated_performance
            explanation.append("ESTIMATED PERFORMANCE:")
            explanation.append(f"  Response Time: {perf['estimated_response_time_seconds']}s")
            explanation.append(f"  Quality Score: {perf['estimated_quality_score']}/100")
            explanation.append(f"  Success Probability: {perf['estimated_success_probability']*100:.0f}%")
            explanation.append("")

        if result.alternative_models:
            explanation.append("ALTERNATIVE MODELS:")
            for alt in result.alternative_models:
                explanation.append(f"  - {alt}")
            explanation.append("")

        if result.warnings:
            explanation.append("WARNINGS:")
            for warning in result.warnings:
                explanation.append(f"  ! {warning}")
            explanation.append("")

        return "\n".join(explanation)


def quick_select(task_type: str,
                complexity: str = "moderate",
                quality_priority: str = "balanced",
                speed_priority: str = "balanced") -> ModelSelectionResult:
    """
    Quick model selection for common scenarios.

    Args:
        task_type: Type of task
        complexity: Task complexity
        quality_priority: Quality vs speed preference
        speed_priority: Speed requirement

    Returns:
        ModelSelectionResult
    """
    selector = AutoModelSelector()

    # Parse inputs
    try:
        task_enum = TaskType(task_type)
    except ValueError:
        # Default to analyze if unknown
        task_enum = TaskType.ANALYZE

    complexity_map = {
        "simple": TaskComplexity.SIMPLE,
        "moderate": TaskComplexity.MODERATE,
        "complex": TaskComplexity.COMPLEX,
        "critical": TaskComplexity.CRITICAL
    }

    context = SelectionContext(
        task_type=task_enum,
        complexity=complexity_map.get(complexity, TaskComplexity.MODERATE),
        quality_priority=quality_priority,
        speed_priority=speed_priority,
        context_size="medium",
        output_length="medium"
    )

    return selector.select_model(context)


if __name__ == "__main__":
    # Demo
    print("AUTO-MODEL SELECTION DEMO")
    print("="*70)

    selector = AutoModelSelector()

    # Test different scenarios
    scenarios = [
        ("Simple chat", TaskType.CHAT, TaskComplexity.SIMPLE, "balanced", "high"),
        ("Complex analysis", TaskType.ANALYZE, TaskComplexity.COMPLEX, "high", "balanced"),
        ("Security audit", TaskType.SECURITY, TaskComplexity.CRITICAL, "high", "low"),
        ("Quick debug", TaskType.DEBUG, TaskComplexity.SIMPLE, "balanced", "high")
    ]

    for name, task, complexity, quality, speed in scenarios:
        print(f"\n### {name} ###")
        context = SelectionContext(
            task_type=task,
            complexity=complexity,
            quality_priority=quality,
            speed_priority=speed,
            context_size="medium",
            output_length="medium"
        )
        result = selector.select_model(context)
        print(f"Selected: {result.selected_model} (confidence: {result.confidence*100:.0f}%)")
        print(f"Reasoning: {result.reasoning[0] if result.reasoning else 'N/A'}")
