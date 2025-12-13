from services.refactor import run_refactor_step
from services.explain import run_explain_step
from services.testcases import run_testcases_step

def run_ai_pipeline(code, issues, complexity, quality):

    ref = run_refactor_step(code, issues)
    exp = run_explain_step(code, issues)
    tst = run_testcases_step(ref["refactored_code"], issues)

    # ⭐ FIX: Ensure test_cases is ALWAYS a list
    test_cases = tst.get("test_cases")
    if not isinstance(test_cases, list):
        test_cases = []

    return {
        "refactored_code": ref["refactored_code"],
        "explanation": exp["explanation"],
        "test_cases": test_cases,
        "notes": ref["notes"],
        "ai_model": "gemini-1.5-flash"
    }

