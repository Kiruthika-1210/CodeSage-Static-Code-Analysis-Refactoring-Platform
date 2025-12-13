from fastapi import APIRouter
import logging
from models.ai_request import AIRequest

from services.refactor import run_refactor_step
from services.explain import run_explain_step
from services.testcases import run_testcases_step
from services.ai_pipeline import run_ai_pipeline

router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger(__name__)


@router.post("/refactor")
def api_refactor(payload: AIRequest):
    code = payload.code
    result = run_refactor_step(code, payload.issues)
    return {
        "refactored_code": result["refactored_code"],
        "notes": result["notes"],
        "ai_model": "gemini-1.5-flash"
    }


@router.post("/explain")
def api_explain(payload: AIRequest):
    result = run_explain_step(payload.code, payload.issues)
    return {
        "explanation": result["explanation"],
        "ai_model": "gemini-1.5-flash"
    }


@router.post("/testcases")
def api_testcases(payload: AIRequest):
    result = run_testcases_step(payload.code, payload.issues)
    return {
        "test_cases": result["test_cases"],
        "ai_model": "gemini-1.5-flash"
    }


@router.post("/full")
def api_full(payload: AIRequest):
    return run_ai_pipeline(
        payload.code,
        payload.issues,
        payload.complexity,
        payload.quality
    )
