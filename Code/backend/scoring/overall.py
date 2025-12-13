from scoring.documentation import analyze_documentation
from scoring.maintainability import analyze_maintainability
from scoring.readability import analyze_readability
from scoring.style import analyze_style

def overall_score(code: str):
    # Run all scorers
    readability_result = analyze_readability(code)
    maintainability_result = analyze_maintainability(code)
    documentation_result = analyze_documentation(code)
    style_result = analyze_style(code)

    # Extract numeric scores
    r_score = readability_result["readability_score"]
    m_score = maintainability_result["maintainability_score"]
    d_score = documentation_result["documentation_score"]
    s_score = style_result["style_score"]

    # Convert scores to penalties
    readability_penalty = 25 - r_score
    maintainability_penalty = 25 - m_score
    documentation_penalty = 25 - d_score
    style_penalty = 25 - s_score

    # Total penalty
    total_penalty = (
        readability_penalty +
        maintainability_penalty +
        documentation_penalty +
        style_penalty
    )

    # Final quality score (0–100)
    quality_score = max(0, 100 - total_penalty)

    return {
        "quality_score": quality_score
    }
