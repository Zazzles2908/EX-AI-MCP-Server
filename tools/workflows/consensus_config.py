"""
Consensus tool configuration - Field descriptions and stance prompts

This module contains configuration constants for the consensus workflow tool,
including field descriptions for the input schema and stance-specific prompts
for multi-model consensus gathering.
"""

from src.prompts import CONSENSUS_PROMPT

# Tool-specific field descriptions for consensus workflow
CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS = {
    "step": (
        "In step 1: Provide the EXACT question or proposal that ALL models will evaluate. This should be phrased as a clear "
        "question or problem statement, NOT as 'I will analyze...' or 'Let me examine...'. For example: 'Should we build a "
        "search component in SwiftUI for use in an AppKit app?' or 'Evaluate the proposal to migrate our database from MySQL "
        "to PostgreSQL'. This exact text will be sent to all models for their independent evaluation. "
        "In subsequent steps (2+): This field is for internal tracking only - you can provide notes about the model response "
        "you just received. This will NOT be sent to other models (they all receive the original proposal from step 1)."
    ),
    "step_number": (
        "The index of the current step in the consensus workflow, beginning at 1. Step 1 is your analysis, "
        "steps 2+ are for processing individual model responses."
    ),
    "total_steps": (
        "Total number of steps needed. This equals the number of models to consult. "
        "Step 1 includes your analysis + first model consultation on return of the call. Final step includes "
        "last model consultation + synthesis."
    ),
    "next_step_required": ("Set to true if more models need to be consulted. False when ready for final synthesis."),
    "findings": (
        "In step 1: Provide YOUR OWN comprehensive analysis of the proposal/question. This is where you share your "
        "independent evaluation, considering technical feasibility, risks, benefits, and alternatives. This analysis "
        "is NOT sent to other models - it's recorded for the final synthesis. "
        "In steps 2+: Summarize the key points from the model response received, noting agreements and disagreements "
        "with previous analyses."
    ),
    "relevant_files": (
        "Files that are relevant to the consensus analysis. Include files that help understand the proposal, "
        "provide context, or contain implementation details."
    ),
    "models": (
        "List of model configurations to consult. Each can have a model name, stance (for/against/neutral), "
        "and optional custom stance prompt. The same model can be used multiple times with different stances, "
        "but each model + stance combination must be unique. "
        "Example: [{'model': 'o3', 'stance': 'for'}, {'model': 'o3', 'stance': 'against'}, "
        "{'model': 'flash', 'stance': 'neutral'}]"
    ),
    "current_model_index": (
        "Internal tracking of which model is being consulted (0-based index). Used to determine which model "
        "to call next."
    ),
    "model_responses": ("Accumulated responses from models consulted so far. Internal field for tracking progress."),
    "images": (
        "Optional list of image paths or base64 data URLs for visual context. Useful for UI/UX discussions, "
        "architecture diagrams, mockups, or any visual references that help inform the consensus analysis."
    ),
}

# Stance-specific prompts for consensus workflow
STANCE_PROMPTS = {
    "for": """SUPPORTIVE PERSPECTIVE WITH INTEGRITY

You are tasked with advocating FOR this proposal, but with CRITICAL GUARDRAILS:

MANDATORY ETHICAL CONSTRAINTS:
- This is NOT a debate for entertainment. You MUST act in good faith and in the best interest of the questioner
- You MUST think deeply about whether supporting this idea is safe, sound, and passes essential requirements
- You MUST be direct and unequivocal in saying "this is a bad idea" when it truly is
- There must be at least ONE COMPELLING reason to be optimistic, otherwise DO NOT support it

WHEN TO REFUSE SUPPORT (MUST OVERRIDE STANCE):
- If the idea is fundamentally harmful to users, project, or stakeholders
- If implementation would violate security, privacy, or ethical standards
- If the proposal is technically infeasible within realistic constraints
- If costs/risks dramatically outweigh any potential benefits

YOUR SUPPORTIVE ANALYSIS SHOULD:
- Identify genuine strengths and opportunities
- Propose solutions to overcome legitimate challenges
- Highlight synergies with existing systems
- Suggest optimizations that enhance value
- Present realistic implementation pathways

Remember: Being "for" means finding the BEST possible version of the idea IF it has merit, not blindly supporting bad ideas.""",
    "against": """CRITICAL PERSPECTIVE WITH RESPONSIBILITY

You are tasked with critiquing this proposal, but with ESSENTIAL BOUNDARIES:

MANDATORY FAIRNESS CONSTRAINTS:
- You MUST NOT oppose genuinely excellent, common-sense ideas just to be contrarian
- You MUST acknowledge when a proposal is fundamentally sound and well-conceived
- You CANNOT give harmful advice or recommend against beneficial changes
- If the idea is outstanding, say so clearly while offering constructive refinements

WHEN TO MODERATE CRITICISM (MUST OVERRIDE STANCE):
- If the proposal addresses critical user needs effectively
- If it follows established best practices with good reason
- If benefits clearly and substantially outweigh risks
- If it's the obvious right solution to the problem

YOUR CRITICAL ANALYSIS SHOULD:
- Identify legitimate risks and failure modes
- Point out overlooked complexities
- Suggest more efficient alternatives
- Highlight potential negative consequences
- Question assumptions that may be flawed

Remember: Being "against" means rigorous scrutiny to ensure quality, not undermining good ideas that deserve support.""",
    "neutral": """BALANCED PERSPECTIVE

Provide objective analysis considering both positive and negative aspects. However, if there is overwhelming evidence
that the proposal clearly leans toward being exceptionally good or particularly problematic, you MUST accurately
reflect this reality. Being "balanced" means being truthful about the weight of evidence, not artificially creating
50/50 splits when the reality is 90/10.

Your analysis should:
- Present all significant pros and cons discovered
- Weight them according to actual impact and likelihood
- If evidence strongly favors one conclusion, clearly state this
- Provide proportional coverage based on the strength of arguments
- Help the questioner see the true balance of considerations

Remember: Artificial balance that misrepresents reality is not helpful. True balance means accurate representation
of the evidence, even when it strongly points in one direction.""",
}


def get_stance_enhanced_prompt(stance: str, custom_stance_prompt: str | None = None) -> str:
    """
    Get the system prompt with stance injection.

    Args:
        stance: The stance to use ("for", "against", or "neutral")
        custom_stance_prompt: Optional custom stance prompt to override default

    Returns:
        System prompt with stance-specific guidance injected
    """
    base_prompt = CONSENSUS_PROMPT

    if custom_stance_prompt:
        return base_prompt.replace("{stance_prompt}", custom_stance_prompt)

    stance_prompt = STANCE_PROMPTS.get(stance, STANCE_PROMPTS["neutral"])
    return base_prompt.replace("{stance_prompt}", stance_prompt)


__all__ = [
    "CONSENSUS_WORKFLOW_FIELD_DESCRIPTIONS",
    "STANCE_PROMPTS",
    "get_stance_enhanced_prompt",
]

