"""
Model Recommendation Guide

Comprehensive guide for selecting the optimal AI model based on task requirements.
Provides data-driven recommendations with performance characteristics and use cases.

Universal Design - Works with any project and supports custom models.

Features:
- Data-driven model selection
- Custom model support via configuration
- Task-specific recommendations
- Model comparison and analysis
- Performance characteristic tracking
- Environment variable configuration
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from .universal_config import get_config, get_custom_models

logger = logging.getLogger(__name__)


class ModelCategory(Enum):
    """Model categories based on capabilities."""
    FAST = "fast"  # Optimized for speed
    BALANCED = "balanced"  # Good speed and quality
    ACCURATE = "accurate"  # Optimized for quality
    REASONING = "reasoning"  # Extended thinking
    TURBO = "turbo"  # Ultra-fast


@dataclass
class ModelSpec:
    """Model specification and characteristics."""
    name: str
    provider: str
    context_window: int
    max_output_tokens: int
    category: ModelCategory
    speed_rating: int  # 1-5 (5 is fastest)
    quality_rating: int  # 1-5 (5 is best)
    reasoning_capability: int  # 1-5 (5 is best)
    cost_efficiency: int  # 1-5 (5 is most efficient)
    use_cases: List[str]
    limitations: List[str]
    best_for: List[str]


class ModelRecommendationEngine:
    """
    Intelligent model recommendation engine.

    Analyzes task requirements and recommends optimal model with rationale.
    Supports custom models via configuration.
    """

    def __init__(self):
        """Initialize the recommendation engine."""
        self._base_models = self._get_base_models()
        self._custom_models = get_custom_models()
        # Merge custom models
        self._all_models = {**self._base_models, **self._custom_models}

    def _get_base_models(self) -> Dict[str, ModelSpec]:
        """Get base model specifications (built-in models)."""
        return {
            "kimi-k2-turbo-preview": ModelSpec(
                name="kimi-k2-turbo-preview",
                provider="Kimi (Moonshot)",
                context_window=262144,  # 256K
                max_output_tokens=16384,  # 16K
                category=ModelCategory.TURBO,
                speed_rating=5,
                quality_rating=4,
                reasoning_capability=4,
                cost_efficiency=5,
                use_cases=[
                    "Quick code reviews",
                    "Documentation generation",
                    "Simple Q&A",
                    "Pre-commit validation",
                    "Error debugging"
                ],
            limitations=[
                "Less capable for complex reasoning",
                "May struggle with very large codebases"
            ],
            best_for=[
                "Fast turnaround requirements",
                "Routine coding tasks",
                "High-volume operations"
            ]
        ),
        "kimi-k2-0905-preview": ModelSpec(
            name="kimi-k2-0905-preview",
            provider="Kimi (Moonshot)",
            context_window=262144,  # 256K
            max_output_tokens=16384,  # 16K
            category=ModelCategory.BALANCED,
            speed_rating=4,
            quality_rating=5,
            reasoning_capability=5,
            cost_efficiency=4,
            use_cases=[
                "Complex code analysis",
                "Architecture reviews",
                "Code refactoring",
                "Execution flow tracing",
                "Deep debugging"
            ],
            limitations=[
                "Slower than turbo variant",
                "Higher cost per token"
            ],
            best_for=[
                "Complex analysis tasks",
                "Large codebases",
                "Quality-critical work"
            ]
        ),
        "kimi-k2-0711-preview": ModelSpec(
            name="kimi-k2-0711-preview",
            provider="Kimi (Moonshot)",
            context_window=131072,  # 128K
            max_output_tokens=16384,  # 16K
            category=ModelCategory.BALANCED,
            speed_rating=4,
            quality_rating=4,
            reasoning_capability=4,
            cost_efficiency=4,
            use_cases=[
                "Code generation and analysis",
                "Agent capabilities",
                "General programming tasks",
                "Quick prototyping"
            ],
            limitations=[
                "Smaller context than 0905",
                "Less optimized than newer versions"
            ],
            best_for=[
                "Standard coding tasks",
                "Agent-based workflows",
                "Cost-effective operations"
            ]
        ),
        "kimi-k2-thinking": ModelSpec(
            name="kimi-k2-thinking",
            provider="Kimi (Moonshot)",
            context_window=262144,  # 256K
            max_output_tokens=32768,  # 32K
            category=ModelCategory.REASONING,
            speed_rating=2,
            quality_rating=5,
            reasoning_capability=5,
            cost_efficiency=3,
            use_cases=[
                "Long-term thinking",
                "Multi-step tool usage",
                "Complex problem solving",
                "Security audits",
                "Strategic planning"
            ],
            limitations=[
                "Slow response time",
                "Higher cost",
                "May timeout on simple tasks"
            ],
            best_for=[
                "Maximum quality requirements",
                "Complex multi-step reasoning",
                "Critical security work"
            ]
        ),
        "kimi-k2-thinking-turbo": ModelSpec(
            name="kimi-k2-thinking-turbo",
            provider="Kimi (Moonshot)",
            context_window=262144,  # 256K
            max_output_tokens=32768,  # 32K
            category=ModelCategory.REASONING,
            speed_rating=4,
            quality_rating=5,
            reasoning_capability=5,
            cost_efficiency=4,
            use_cases=[
                "Fast complex reasoning",
                "Multi-step analysis",
                "Quick security reviews",
                "Rapid planning"
            ],
            limitations=[
                "Higher cost than standard turbo",
                "May timeout on very long tasks"
            ],
            best_for=[
                "High-quality fast reasoning",
                "Time-sensitive complex analysis",
                "Balanced speed and depth"
            ]
        ),
        "kimi-thinking-preview": ModelSpec(
            name="kimi-thinking-preview",
            provider="Kimi (Moonshot)",
            context_window=131072,  # 128K
            max_output_tokens=16384,  # 16K
            category=ModelCategory.REASONING,
            speed_rating=3,
            quality_rating=4,
            reasoning_capability=4,
            cost_efficiency=4,
            use_cases=[
                "Multimodal reasoning",
                "Image analysis with text",
                "General reasoning tasks",
                "Mixed media projects"
            ],
            limitations=[
                "Only 128K context",
                "Not as capable as K2-thinking",
                "No turbo variant"
            ],
            best_for=[
                "Multimodal tasks",
                "Image + text analysis",
                "Balanced reasoning needs"
            ]
        ),
        "glm-4.6": ModelSpec(
            name="glm-4.6",
            provider="GLM (ZhipuAI)",
            context_window=200000,  # 200K
            max_output_tokens=128000,  # 128K
            category=ModelCategory.ACCURATE,
            speed_rating=3,
            quality_rating=5,
            reasoning_capability=5,
            cost_efficiency=4,
            use_cases=[
                "High-quality analysis",
                "Complex problem solving",
                "Long-form generation",
                "Technical documentation",
                "Architecture decisions"
            ],
            limitations=[
                "Smaller context than Kimi",
                "Less consistent speed"
            ],
            best_for=[
                "Long output requirements",
                "Complex reasoning",
                "Cost-conscious quality work"
            ]
        ),
        "glm-4.5-flash": ModelSpec(
            name="glm-4.5-flash",
            provider="GLM (ZhipuAI)",
            context_window=128000,  # 128K
            max_output_tokens=8192,  # 8K
            category=ModelCategory.FAST,
            speed_rating=5,
            quality_rating=3,
            reasoning_capability=3,
            cost_efficiency=5,
            use_cases=[
                "Quick debugging",
                "Simple queries",
                "Code snippets",
                "Basic explanations",
                "Rapid prototyping"
            ],
            limitations=[
                "Smaller context window",
                "Lower quality on complex tasks",
                "Limited output length"
            ],
            best_for=[
                "Quick answers",
                "Simple tasks",
                "High volume operations"
            ]
        )
    }

    @property
    def MODELS(self) -> Dict[str, ModelSpec]:
        """
        Get all models (base + custom from configuration).

        This property provides access to both built-in models and
        custom models configured via the universal configuration system.
        """
        return self._all_models

    def recommend_model(self,
                       task_type: str,
                       context_size: str = "medium",
                       quality_priority: str = "balanced",
                       speed_priority: str = "balanced",
                       output_length: str = "medium") -> Optional[ModelSpec]:
        """
        Recommend optimal model based on requirements.

        Args:
            task_type: Type of task (analyze, debug, testgen, etc.)
            context_size: small, medium, large
            quality_priority: low, balanced, high
            speed_priority: low, balanced, high
            output_length: short, medium, long

        Returns:
            Recommended model specification
        """
        # Task-specific recommendations
        task_model_map = {
            "analyze": ["kimi-k2-0905-preview", "glm-4.6"],
            "codereview": ["kimi-k2-thinking-preview", "kimi-k2-0905-preview"],
            "debug": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
            "refactor": ["kimi-k2-0905-preview", "glm-4.6"],
            "testgen": ["kimi-k2-thinking-preview", "glm-4.6"],
            "docgen": ["kimi-k2-turbo-preview", "glm-4.6"],
            "planner": ["kimi-k2-thinking-preview", "glm-4.6"],
            "tracer": ["kimi-k2-0905-preview", "glm-4.6"],
            "secaudit": ["kimi-k2-thinking-preview", "glm-4.6"],
            "precommit": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
            "consensus": ["kimi-k2-thinking-preview", "glm-4.6"],
            "chat": ["kimi-k2-turbo-preview", "glm-4.5-flash"],
            "thinkdeep": ["kimi-k2-thinking-preview", "glm-4.6"]
        }

        # Get candidate models
        candidates = task_model_map.get(task_type.lower(), list(self.MODELS.keys()))

        # Apply filters
        filtered_models = []

        for model_name in candidates:
            if model_name not in self.MODELS:
                continue

            spec = self.MODELS[model_name]

            # Context size filter
            if context_size == "large" and spec.context_window < 200000:
                continue

            # Output length filter
            if output_length == "long" and spec.max_output_tokens < 16000:
                # gl-4.6 has 128K, kimi thinking has 32K
                if "glm-4.6" not in model_name and "kimi-k2-thinking" not in model_name:
                    continue

            # Quality priority filter
            if quality_priority == "high" and spec.quality_rating < 4:
                continue
            elif quality_priority == "low" and spec.quality_rating > 3:
                # Could still be valid for simple tasks
                pass

            # Speed priority filter
            if speed_priority == "high" and spec.speed_rating < 4:
                continue

            filtered_models.append((model_name, spec))

        # Rank models
        if not filtered_models:
            # Fallback to best overall
            return self.MODELS.get("kimi-k2-0905-preview")

        # Scoring algorithm
        def score_model(spec: ModelSpec) -> float:
            score = 0.0

            # Task alignment (40% weight)
            if task_type.lower() in [uc.lower() for uc in spec.use_cases]:
                score += 40

            # Context size match (20% weight)
            if context_size == "small" and spec.speed_rating >= 4:
                score += 20
            elif context_size == "medium":
                score += 20
            elif context_size == "large" and spec.context_window >= 200000:
                score += 20

            # Quality priority (20% weight)
            if quality_priority == "high" and spec.quality_rating >= 5:
                score += 20
            elif quality_priority == "balanced":
                score += spec.quality_rating * 4

            # Speed priority (15% weight)
            if speed_priority == "high" and spec.speed_rating >= 5:
                score += 15
            elif speed_priority == "balanced":
                score += spec.speed_rating * 3

            # Output length (5% weight)
            if output_length == "long" and spec.max_output_tokens >= 16000:
                score += 5

            return score

        # Sort by score
        filtered_models.sort(key=lambda x: score_model(x[1]), reverse=True)

        return filtered_models[0][1]

    def compare_models(self, model_names: List[str]) -> str:
        """
        Generate comparison table for multiple models.

        Args:
            model_names: List of model names to compare

        Returns:
            Formatted comparison table
        """
        models = [self.MODELS.get(name) for name in model_names if name in self.MODELS]

        if not models:
            return "No valid models specified."

        # Build comparison table
        header = f"{'Model':<25} {'Provider':<15} {'Context':<10} {'Output':<10} {'Speed':<7} {'Quality':<7} {'Reason':<7}\n"
        separator = "-" * 95 + "\n"

        rows = [header, separator]
        for model in models:
            row = (
                f"{model.name:<25} "
                f"{model.provider:<15} "
                f"{model.context_window//1024}K{'':<6} "
                f"{model.max_output_tokens//1024}K{'':<6} "
                f"{'★' * model.speed_rating}{'☆' * (5-model.speed_rating):<3} "
                f"{'★' * model.quality_rating}{'☆' * (5-model.quality_rating):<3} "
                f"{'★' * model.reasoning_capability}{'☆' * (5-model.reasoning_capability):<3}\n"
            )
            rows.append(row)

        return "".join(rows)

    def get_model_details(self, model_name: str) -> Optional[ModelSpec]:
        """Get detailed specification for a model."""
        return self.MODELS.get(model_name)

    def suggest_alternatives(self, model_name: str, count: int = 3) -> List[ModelSpec]:
        """
        Suggest alternative models with similar characteristics.

        Args:
            model_name: Reference model
            count: Number of alternatives to return

        Returns:
            List of alternative model specs
        """
        if model_name not in self.MODELS:
            return []

        ref_spec = self.MODELS[model_name]
        alternatives = []

        for name, spec in self.MODELS.items():
            if name == model_name:
                continue

            # Score similarity
            similarity = 0

            # Same category
            if spec.category == ref_spec.category:
                similarity += 30

            # Similar speed
            if abs(spec.speed_rating - ref_spec.speed_rating) <= 1:
                similarity += 20

            # Similar quality
            if abs(spec.quality_rating - ref_spec.quality_rating) <= 1:
                similarity += 20

            # Similar context window
            if abs(spec.context_window - ref_spec.context_window) <= 64000:
                similarity += 15

            # Same provider
            if spec.provider == ref_spec.provider:
                similarity += 15

            alternatives.append((name, spec, similarity))

        # Sort by similarity
        alternatives.sort(key=lambda x: x[2], reverse=True)

        return [alt[1] for alt in alternatives[:count]]

    def format_recommendation(self, spec: ModelSpec, task_context: str = "") -> str:
        """Format model recommendation for display."""
        return f"""
**{spec.name}** ({spec.provider})
{'='*70}

Context Window: {spec.context_window:,} tokens ({spec.context_window//1024}K)
Max Output: {spec.max_output_tokens:,} tokens ({spec.max_output_tokens//1024}K)
Category: {spec.category.value.title()}

**Performance Ratings (1-5)**
Speed:       {'★' * spec.speed_rating}{'☆' * (5-spec.speed_rating)}
Quality:     {'★' * spec.quality_rating}{'☆' * (5-spec.quality_rating)}
Reasoning:   {'★' * spec.reasoning_capability}{'☆' * (5-spec.reasoning_capability)}
Cost Eff.:   {'★' * spec.cost_efficiency}{'☆' * (5-spec.cost_efficiency)}

**Best For**
{chr(10).join(f"  • {use_case}" for use_case in spec.best_for)}

**Use Cases**
{chr(10).join(f"  • {use_case}" for use_case in spec.use_cases)}

**Limitations**
{chr(10).join(f"  • {limitation}" for limitation in spec.limitations)}

{f'Task Context: {task_context}' if task_context else ''}
        """.strip()


def quick_recommend(task: str) -> str:
    """
    Quick model recommendation for common tasks.

    Args:
        task: Task description

    Returns:
        Recommended model name
    """
    engine = ModelRecommendationEngine()

    # Parse task keywords
    task_lower = task.lower()

    if any(word in task_lower for word in ["quick", "fast", "urgent", "simple"]):
        return "kimi-k2-turbo-preview"
    elif any(word in task_lower for word in ["analyze", "complex", "deep", "architecture"]):
        return "kimi-k2-0905-preview"
    elif any(word in task_lower for word in ["security", "audit", "critical", "thinking"]):
        return "kimi-k2-thinking-preview"
    elif any(word in task_lower for word in ["long", "document", "extensive"]):
        return "glm-4.6"
    else:
        return "kimi-k2-0905-preview"  # Default balanced choice


if __name__ == "__main__":
    # Demo usage
    engine = ModelRecommendationEngine()

    print("="*70)
    print("MODEL RECOMMENDATION GUIDE")
    print("="*70)

    # Example 1: Complex analysis
    print("\n### Example 1: Complex Code Analysis ###")
    rec = engine.recommend_model(
        task_type="analyze",
        context_size="large",
        quality_priority="high",
        speed_priority="balanced"
    )
    print(engine.format_recommendation(rec))

    # Example 2: Quick debugging
    print("\n### Example 2: Quick Debugging ###")
    rec = engine.recommend_model(
        task_type="debug",
        context_size="small",
        quality_priority="balanced",
        speed_priority="high"
    )
    print(engine.format_recommendation(rec))

    # Example 3: Model comparison
    print("\n### Example 3: Model Comparison ###")
    print(engine.compare_models(["kimi-k2-turbo-preview", "kimi-k2-0905-preview", "glm-4.6"]))
