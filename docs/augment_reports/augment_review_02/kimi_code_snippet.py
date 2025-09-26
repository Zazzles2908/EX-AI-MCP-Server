def normalize(values):
    total = sum(values)
    if total == 0:
        return [0 for _ in values]
    return [v / total for v in values]


def topk(items, k):
    # Returns the top-k items by value descending
    return sorted(items, key=lambda x: x[1], reverse=True)[:k]


def summarize(scores):
    """Return min, max, mean for a list of numeric scores."""
    if not scores:
        return {"min": None, "max": None, "mean": None}
    mn, mx = min(scores), max(scores)
    mean = sum(scores) / len(scores)
    return {"min": mn, "max": mx, "mean": round(mean, 4)}

