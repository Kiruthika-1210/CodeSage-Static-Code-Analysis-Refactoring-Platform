from fastapi import APIRouter
from models.refactor_request import RefactorRequest
from models.refactor_response import RefactorResponse
from services.ai_pipeline import run_ai_pipeline
from services.analysis_engine import analyze_code   # 👈 ADD THIS

router = APIRouter(
    prefix="/refactor",
    tags=["Refactor"]
)

@router.post("", response_model=RefactorResponse)
def refactor_code(request: RefactorRequest):
    code = request.code

    # If issues come from frontend, use them. Otherwise analyze here.
    if request.issues:
        issues = request.issues
    else:
        # 👇 Run static analysis to generate issues
        analysis = analyze_code(code)
        issues = analysis["issues"]
        complexity = analysis["complexity"]
        quality = analysis["quality_score"]

        # Call AI pipeline with all required parameters
        result = run_ai_pipeline(code, issues, complexity, quality)

        test_cases = result.get("test_cases")
        
        # FORCE FIX: Convert empty string or None to empty list
        if not isinstance(test_cases, list):
            test_cases = []
            
        return {
            "refactored_code": result["refactored_code"],
            "explanation": result["explanation"],
            "test_cases": test_cases
        }


    # If frontend sends issues but not complexity & quality
    # we still need to compute them
    analysis = analyze_code(code)
    complexity = analysis["complexity"]
    quality = analysis["quality_score"]

    result = run_ai_pipeline(code, issues, complexity, quality)

    return {
        "refactored_code": result["refactored_code"],
        "explanation": result["explanation"],
        "test_cases": result["test_cases"]
    }
