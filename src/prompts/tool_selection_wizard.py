"""
Tool Selection Wizard

Interactive decision tree to help users select the right AI tool for their task.
Implements intelligent routing based on task requirements and complexity.

Universal Design - Works with any project or AI provider.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Task categories for tool selection."""
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    DEBUG = "debug"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PLANNING = "planning"
    TRACING = "tracing"
    SECURITY = "security"
    PRE_COMMIT = "pre_commit"
    CONSENSUS = "consensus"
    CHAT = "chat"
    DEEP_THINKING = "deep_thinking"


class ComplexityLevel(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"  # Quick answers, straightforward tasks
    MODERATE = "moderate"  # Some investigation needed
    COMPLEX = "complex"  # Deep analysis, multiple steps
    ARCHITECTURE = "architecture"  # High-level design decisions


@dataclass
class ToolRecommendation:
    """Tool recommendation with metadata."""
    tool_name: str
    task_type: TaskType
    recommended_models: List[str]
    complexity: ComplexityLevel
    description: str
    use_cases: List[str]
    alternatives: List[str]


class ToolSelectionWizard:
    """
    Intelligent tool selection wizard using decision tree logic.

    Provides contextual recommendations based on:
    - Task type and objectives
    - Code complexity
    - Desired output format
    - Time constraints
    """

    # Tool definitions with capabilities
    TOOLS: Dict[str, ToolRecommendation] = {
        "analyze": ToolRecommendation(
            tool_name="analyze",
            task_type=TaskType.CODE_ANALYSIS,
            recommended_models=["kimi-k2-0905-preview", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Holistic code analysis covering architecture, patterns, and strategic recommendations",
            use_cases=[
                "Architecture review",
                "Performance assessment",
                "Scalability evaluation",
                "Technical debt analysis",
                "Code quality audit"
            ],
            alternatives=["codereview", "thinkdeep"]
        ),
        "codereview": ToolRecommendation(
            tool_name="codereview",
            task_type=TaskType.CODE_REVIEW,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.MODERATE,
            description="Focused code review for security, performance, and maintainability issues",
            use_cases=[
                "Security vulnerability check",
                "Performance optimization",
                "Code quality review",
                "Bug detection",
                "Style guide compliance"
            ],
            alternatives=["analyze", "secaudit"]
        ),
        "debug": ToolRecommendation(
            tool_name="debug",
            task_type=TaskType.DEBUG,
            recommended_models=["kimi-k2-turbo-preview", "glm-4.5-flash"],
            complexity=ComplexityLevel.MODERATE,
            description="Systematic debugging with root cause analysis and fix recommendations",
            use_cases=[
                "Error investigation",
                "Root cause analysis",
                "Fix implementation",
                "Error prevention",
                "Log analysis"
            ],
            alternatives=["analyze", "chat"]
        ),
        "refactor": ToolRecommendation(
            tool_name="refactor",
            task_type=TaskType.REFACTOR,
            recommended_models=["kimi-k2-0905-preview", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Code improvement analysis focusing on maintainability and efficiency",
            use_cases=[
                "Code smell detection",
                "Design pattern improvements",
                "Modernization",
                "Decomposition planning",
                "Technical debt reduction"
            ],
            alternatives=["analyze", "codereview"]
        ),
        "testgen": ToolRecommendation(
            tool_name="testgen",
            task_type=TaskType.TESTING,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.MODERATE,
            description="Automated test case generation with high coverage and realistic scenarios",
            use_cases=[
                "Unit test creation",
                "Integration test design",
                "Edge case identification",
                "Test coverage analysis",
                "Regression test planning"
            ],
            alternatives=["analyze", "chat"]
        ),
        "docgen": ToolRecommendation(
            tool_name="docgen",
            task_type=TaskType.DOCUMENTATION,
            recommended_models=["kimi-k2-turbo-preview", "glm-4.5-flash"],
            complexity=ComplexityLevel.MODERATE,
            description="Comprehensive documentation generation for code, APIs, and systems",
            use_cases=[
                "API documentation",
                "Code documentation",
                "README creation",
                "Architecture docs",
                "Comment generation"
            ],
            alternatives=["chat", "analyze"]
        ),
        "planner": ToolRecommendation(
            tool_name="planner",
            task_type=TaskType.PLANNING,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Task breakdown and planning with actionable steps and milestones",
            use_cases=[
                "Feature planning",
                "Task breakdown",
                "Project roadmap",
                "Implementation strategy",
                "Effort estimation"
            ],
            alternatives=["thinkdeep", "chat"]
        ),
        "tracer": ToolRecommendation(
            tool_name="tracer",
            task_type=TaskType.TRACING,
            recommended_models=["kimi-k2-0905-preview", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Code execution flow and dependency mapping analysis",
            use_cases=[
                "Call chain analysis",
                "Dependency mapping",
                "Execution flow tracing",
                "Code navigation",
                "Integration understanding"
            ],
            alternatives=["analyze", "debug"]
        ),
        "secaudit": ToolRecommendation(
            tool_name="secaudit",
            task_type=TaskType.SECURITY,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Comprehensive security audit based on OWASP Top 10 and compliance",
            use_cases=[
                "Security vulnerability scan",
                "Compliance audit",
                "Risk assessment",
                "Penetration testing",
                "Security architecture review"
            ],
            alternatives=["codereview", "analyze"]
        ),
        "precommit": ToolRecommendation(
            tool_name="precommit",
            task_type=TaskType.PRE_COMMIT,
            recommended_models=["kimi-k2-turbo-preview", "glm-4.5-flash"],
            complexity=ComplexityLevel.MODERATE,
            description="Final validation before commit, focusing on future liabilities",
            use_cases=[
                "Pre-commit validation",
                "Change impact assessment",
                "Quality gate check",
                "Regression prevention",
                "Code quality enforcement"
            ],
            alternatives=["codereview", "debug"]
        ),
        "consensus": ToolRecommendation(
            tool_name="consensus",
            task_type=TaskType.CONSENSUS,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.COMPLEX,
            description="Multi-perspective analysis and consensus building for decisions",
            use_cases=[
                "Decision validation",
                "Architecture decisions",
                "Technology selection",
                "Trade-off analysis",
                "Risk assessment"
            ],
            alternatives=["thinkdeep", "analyze"]
        ),
        "chat": ToolRecommendation(
            tool_name="chat",
            task_type=TaskType.CHAT,
            recommended_models=["kimi-k2-turbo-preview", "glm-4.5-flash"],
            complexity=ComplexityLevel.SIMPLE,
            description="General Q&A and guidance for software development",
            use_cases=[
                "Quick questions",
                "General guidance",
                "Concept explanation",
                "Best practices",
                "Learning support"
            ],
            alternatives=[]
        ),
        "thinkdeep": ToolRecommendation(
            tool_name="thinkdeep",
            task_type=TaskType.DEEP_THINKING,
            recommended_models=["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.6"],
            complexity=ComplexityLevel.ARCHITECTURE,
            description="Deep investigation and analysis for complex problems",
            use_cases=[
                "Complex problem solving",
                "Multi-step analysis",
                "Hypothesis validation",
                "Research synthesis",
                "Strategic planning"
            ],
            alternatives=["analyze", "planner"]
        )
    }

    # Quick reference mapping from user intent to tools
    INTENT_TOOLS: Dict[str, List[str]] = {
        "analyze": ["analyze"],
        "review": ["codereview", "analyze"],
        "debug": ["debug", "tracer"],
        "refactor": ["refactor", "analyze"],
        "document": ["docgen", "chat"],
        "test": ["testgen", "analyze"],
        "plan": ["planner", "thinkdeep"],
        "trace": ["tracer", "debug"],
        "security": ["secaudit", "codereview"],
        "validate": ["precommit", "consensus"],
        "chat": ["chat"],
        "think": ["thinkdeep", "analyze"]
    }

    def recommend_tool(self,
                      user_intent: str,
                      code_size: str = "medium",
                      complexity: str = "moderate",
                      time_urgent: bool = False) -> List[ToolRecommendation]:
        """
        Recommend tools based on user intent and context.

        Args:
            user_intent: What the user wants to accomplish
            code_size: Size of codebase (small, medium, large)
            complexity: Task complexity (simple, moderate, complex)
            time_urgent: Whether time is a critical factor

        Returns:
            List of recommended tools ranked by suitability
        """
        user_intent = user_intent.lower().strip()

        # Direct tool match
        if user_intent in self.TOOLS:
            return [self.TOOLS[user_intent]]

        # Intent-based matching
        recommendations = []
        matched_intents = []

        for intent, tools in self.INTENT_TOOLS.items():
            if intent in user_intent or any(word in user_intent for word in intent.split()):
                matched_intents.append(intent)
                for tool_name in tools:
                    if tool_name in self.TOOLS:
                        recommendations.append(self.TOOLS[tool_name])

        # Apply context filters
        if time_urgent:
            # Prioritize faster tools for urgent requests
            recommendations.sort(key=lambda t: t.tool_name in ["chat", "debug", "precommit"])

        if code_size == "small" and complexity == "simple":
            # Prioritize simple tools for small/simple tasks
            simple_tools = ["chat", "debug", "precommit"]
            recommendations.sort(key=lambda t: t.tool_name in simple_tools, reverse=True)

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.tool_name not in seen:
                seen.add(rec.tool_name)
                unique_recommendations.append(rec)

        return unique_recommendations[:3]  # Return top 3 recommendations

    def get_tool_details(self, tool_name: str) -> Optional[ToolRecommendation]:
        """Get detailed information about a specific tool."""
        return self.TOOLS.get(tool_name)

    def list_all_tools(self) -> List[ToolRecommendation]:
        """List all available tools with summaries."""
        return list(self.TOOLS.values())

    def suggest_model(self, tool_name: str, context: str = "default") -> str:
        """
        Suggest the best model for a tool based on context.

        Args:
            tool_name: Name of the tool
            context: Context (default, fast, accurate, large_context)

        Returns:
            Recommended model name
        """
        if tool_name not in self.TOOLS:
            return "kimi-k2-turbo-preview"  # Default fallback

        tool = self.TOOLS[tool_name]
        models = tool.recommended_models

        if context == "fast":
            # Return first model (typically faster)
            return models[0] if models else "glm-4.5-flash"
        elif context == "accurate" or context == "complex":
            # Return last model (typically more capable)
            return models[-1] if models else "kimi-k2-thinking"
        elif context == "large_context":
            # Return model with largest context
            if "kimi-k2" in (models[0] if models else ""):
                return "kimi-k2-0905-preview"  # 256K context
            else:
                return "glm-4.6"  # 200K context
        else:
            # Default: return first model
            return models[0] if models else "kimi-k2-turbo-preview"

    def format_recommendation(self, tool: ToolRecommendation) -> str:
        """Format tool recommendation for display."""
        return f"""
**{tool.tool_name.upper()}**
Description: {tool.description}
Complexity: {tool.complexity.value.title()}
Recommended Models: {', '.join(tool.recommended_models)}

Use Cases:
{chr(10).join(f"  - {use_case}" for use_case in tool.use_cases)}

Alternatives: {', '.join(tool.alternatives) if tool.alternatives else 'None'}
        """.strip()


def interactive_selection() -> None:
    """
    Interactive command-line tool selection wizard.
    Prompts user with questions and provides recommendations.
    """
    wizard = ToolSelectionWizard()

    print("\n" + "="*70)
    print("AI TOOL SELECTION WIZARD")
    print("="*70 + "\n")

    # Question 1: What do you want to accomplish?
    print("Question 1: What would you like to accomplish?")
    print("Examples: analyze code, review PR, debug error, refactor, document, test")
    user_intent = input("\nYour goal: ").strip()

    if not user_intent:
        print("\nNo input provided. Showing all available tools...\n")
        tools = wizard.list_all_tools()
        for tool in tools:
            print(f"- {tool.tool_name}: {tool.description}")
        return

    # Question 2: Codebase size
    print("\nQuestion 2: What's the size of your codebase?")
    print("Options: small (<1000 lines), medium (1K-10K lines), large (>10K lines)")
    code_size = input("Size (small/medium/large) [medium]: ").strip().lower() or "medium"

    # Question 3: Complexity
    print("\nQuestion 3: How complex is your task?")
    print("Options: simple (quick answer), moderate (some investigation), complex (deep analysis)")
    complexity = input("Complexity (simple/moderate/complex) [moderate]: ").strip().lower() or "moderate"

    # Question 4: Time urgency
    print("\nQuestion 4: Is time a critical factor?")
    time_urgent = input("Urgent? (y/n) [n]: ").strip().lower().startswith('y')

    # Get recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70 + "\n")

    recommendations = wizard.recommend_tool(
        user_intent=user_intent,
        code_size=code_size,
        complexity=complexity,
        time_urgent=time_urgent
    )

    if not recommendations:
        print("No specific recommendations found. Try rephrasing your goal.")
        return

    for i, tool in enumerate(recommendations, 1):
        print(f"\nOption {i}:")
        print(wizard.format_recommendation(tool))

        # Suggest model
        context = "fast" if time_urgent else "default"
        if complexity == "complex":
            context = "accurate"
        elif code_size == "large":
            context = "large_context"

        model = wizard.suggest_model(tool.tool_name, context)
        print(f"\nRecommended Model: {model}")

    print("\n" + "="*70)
    print("HOW TO USE")
    print("="*70 + "\n")
    print("Use the selected tool with your AI provider:")
    print(f"Tool: {recommendations[0].tool_name}")
    print(f"Models: {', '.join(recommendations[0].recommended_models)}")
    print("\nNote: Customize these tools for your specific AI provider and framework.")
    print("The tools are designed to be universal and work with any setup.")
    print()


if __name__ == "__main__":
    interactive_selection()
