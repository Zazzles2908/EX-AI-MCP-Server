from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from utils.token_estimator import estimate_tokens


@dataclass
class ClassificationResult:
    task_type: str
    complexity: float  # 0.0 - 1.0
    est_tokens: int


def classify(prompt: str, files_count: int = 0, images_count: int = 0) -> ClassificationResult:
    """
    Very lightweight heuristic classifier to guide routing hints.
    - Long prompts or many files -> long_context_analysis
    - Otherwise -> quick_chat
    """
    tks = estimate_tokens(prompt or "")
    score = min(1.0, (tks / 4000.0) + (files_count * 0.05) + (images_count * 0.03))
    if tks > 1200 or files_count >= 2:
        ttype = "long_context_analysis"
    else:
        ttype = "quick_chat"
    return ClassificationResult(task_type=ttype, complexity=round(score, 3), est_tokens=tks)

