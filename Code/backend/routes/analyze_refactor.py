from fastapi import APIRouter
from models.analyze_refactor_request import AnalyzeRefactorRequest
from models.analyze_refactor_response import AnalyzeRefactorResponse

from analysis.run_all import run_static_analysis
from complexity.score import complexity_score
from scoring.overall import overall_score

from services.ai_pipeline import run_ai_pipeline
from versions.versions import save_version


router = APIRouter(
    prefix="/analyze-and-refactor",
    tags=["Analyze-and-Refactor"]
)


@router.post("", response_model=AnalyzeRefactorResponse)
def analyze_refactor(request: AnalyzeRefactorRequest):
    code = request.code

    # ---------------------------
    # 1️⃣ STATIC ANALYSIS
    # ---------------------------
    analysis = run_static_analysis(code)
    issues = analysis["issues"]
    analysis_complexity = analysis["complexity"]
    
    complexity = complexity_score(code)
    
    quality = overall_score(code)
    try:
        quality = int(quality)
    except:
        quality = 0

    # ---------------------------
    # 2️⃣ AI REFACTOR PIPELINE
    # ---------------------------
    complexity_data = {
        "static": analysis_complexity,
        "score": complexity
    }

    result = run_ai_pipeline(
        code,
        issues,
        complexity_data,
        quality
    )

    refactored_code = result["refactored_code"]
    explanation = result.get("explanation", "")
    test_cases = result.get("test_cases", [])
    if not isinstance(test_cases, list):
        test_cases = []

    # ---------------------------
    # 3️⃣ SAVE VERSION SNAPSHOT
    # ---------------------------
    version_info = save_version(
        session_id=request.session_id,
        original_code=code,
        refactored_code=refactored_code,
        issues=issues,
        complexity=complexity_data,  # JSON-friendly
        quality_score=quality
    )

    print("VERSION INFO:", version_info)

    # If DB failed → return safe error response
    if not version_info.get("ok", False):
        return {
            "issues": issues,
            "complexity": complexity_data,
            "quality_score": quality,
            "refactored_code": refactored_code,
            "explanation": explanation,
            "test_cases": test_cases,
            "session_id": request.session_id,
            "version_id": -1,
            "diff_summary": "DB save failed"
        }

    # ---------------------------
    # 4️⃣ BUILD FINAL RESPONSE
    # ---------------------------
    return {
        "issues": issues,
        "complexity": complexity_data,
        "quality_score": quality,
        "refactored_code": refactored_code,
        "explanation": explanation,
        "test_cases": test_cases,

        "session_id": request.session_id,
        "version_id": version_info["version_id"],
        "diff_summary": version_info.get("diff_summary", "")
    }
