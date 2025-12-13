import logging
from services.ai_client import call_gemini

logger = logging.getLogger(__name__)

def run_explain_step(code, issues):
    result = {}

    try:
        with open("prompts/explain.txt") as f:
            template = f.read()

        prompt = template + f"\n\nCODE TO ANALYZE:\n" + code
        response = call_gemini(prompt)

        explanation = response.get("explanation", "")
        result["explanation"] = explanation

    except:
        logger.exception("Explain step failed")
        result["explanation"] = ""

    return result
