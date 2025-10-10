from __future__ import annotations
import math
from typing import Iterable


def _word_count(text: str) -> int:
    return len((text or "").strip().split())


def estimate_tokens(text: str, token_per_word: float = 1.33) -> int:
    """
    Rough token estimator: ~1.33 tokens per English word (heuristic).
    """
    wc = _word_count(text)
    return int(math.ceil(wc * token_per_word))

