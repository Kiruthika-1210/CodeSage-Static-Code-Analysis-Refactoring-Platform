import os
import json
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ Missing GOOGLE_API_KEY in .env")

# Gemini REST endpoint — correct, stable
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


def call_gemini(prompt: str):
    """
    Sends text prompt to Gemini REST API.
    Returns parsed JSON output OR safe fallback.
    """

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        data = response.json()

        # Extract text output:
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Try parsing JSON (our prompts always return JSON)
        try:
            return json.loads(text)
        except:
            return {"raw": text}

    except Exception as e:
        # Backend must NEVER crash → always fallback
        return {"error": str(e)}
