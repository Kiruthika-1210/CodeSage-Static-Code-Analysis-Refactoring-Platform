def analyze_code(code: str):
    """
    Minimal placeholder static analysis engine.
    Returns empty issues but valid keys for complexity and quality.
    """

    return {
        "issues": [],
        "complexity": {
            "loops": {"total_loops": 0},
            "nesting": {"max_nesting_depth": 0},
            "big_o": "O(1)",
            "score": 100
        },
        "quality_score": 100
    }
