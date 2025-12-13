from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyzeRefactorResponse(BaseModel):
    # Static Analysis
    issues: List[Dict[str, Any]]
    complexity: Dict[str, Any]
    quality_score: int

    # AI Refactor Output
    refactored_code: str
    explanation: str
    test_cases: List[str]

    # Versioning
    session_id: str
    version_id: int
    diff_summary: str
