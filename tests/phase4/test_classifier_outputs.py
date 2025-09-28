from src.router.classifier import classify


def test_classifier_quick_chat():
    res = classify("short question", files_count=0)
    assert res.task_type == "quick_chat"
    assert 0 <= res.complexity <= 1


def test_classifier_long_context():
    long_txt = "word " * 2000
    res = classify(long_txt, files_count=0)
    assert res.task_type == "long_context_analysis"
    assert res.est_tokens > 1000

