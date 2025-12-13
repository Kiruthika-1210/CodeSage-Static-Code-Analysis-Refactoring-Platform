import logging
from services.ai_client import call_gemini

logger = logging.getLogger(__name__)

def run_refactor_step(code, issues):
    result = {}

    try:
        with open("prompts/refactor.txt") as f:
            template = f.read()

        prompt = template + f"\n\nCODE TO REFACTOR:\n{code}"
        response = call_gemini(prompt)

        refactored = response.get("refactored_code", code)
        notes = response.get("notes", "")

        try:
            compile(refactored, "<string>", "exec")
            result["refactored_code"] = refactored
            result["notes"] = notes
        except:
            logger.exception("Invalid refactor code")
            result["refactored_code"] = code
            result["notes"] = "AI refactor invalid — fallback to original code"

    except Exception as e:
        logger.exception("Refactor step failed")
        result["refactored_code"] = code
        result["notes"] = "AI refactor failed — fallback to original code"

    return result
