from fastapi import APIRouter
from models.analyze_request import AnalyzeRequest
from models.analyze_response import AnalyzeResponse
from analysis.run_all import run_static_analysis
from complexity.score import complexity_score
from scoring.overall import overall_score

router = APIRouter(prefix = "/analyze",
                   tags = ['Analyze'])

@router.post("", response_model = AnalyzeResponse)
def analyze_code(request: AnalyzeRequest):
    code = request.code
    
    # Placeholder calls
    analysis_result = run_static_analysis(code)
    issues = analysis_result["issues"]
    complexity = analysis_result["complexity"] 
    quality_score = overall_score(code)["quality_score"]     # scoring placeholder

    return {
        "issues": issues,
        "complexity": complexity,   # complexity must be a dict (your model says Dict)
        "quality_score": quality_score
    }
