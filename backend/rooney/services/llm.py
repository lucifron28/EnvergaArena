"""
llm.py — Calls Gemini API with the grounded context.
Returns a structured response: answer_text, grounded, source_labels, refusal_reason.
"""
import json
import os
import re
from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are Rooney, the official AI FAQ assistant for Enverga Arena — the MSEUF intramurals management portal.

STRICT RULES:
1. You ONLY answer questions using the GROUNDING DATA provided below.
2. If the question cannot be answered from the grounding data, you MUST refuse.
3. NEVER speculate, predict, or invent data. No "probably", "likely", or guesses.
4. NEVER answer questions unrelated to MSEUF intramurals (weather, general trivia, etc.).

GROUNDING DATA:
{context}
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer_text": {"type": "string"},
        "grounded": {"type": "boolean"},
        "source_labels": {"type": "array", "items": {"type": "string"}},
        "refusal_reason": {"type": "string"},
    },
    "required": ["answer_text", "grounded", "source_labels", "refusal_reason"],
}


def query_rooney(question: str, context: str) -> dict:
    """
    Calls Gemini API with the question and grounding context.
    Returns a structured dict.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return {
            "answer_text": "",
            "grounded": False,
            "source_labels": [],
            "refusal_reason": "Rooney AI is not configured. Please contact the administrator.",
        }

    client = genai.Client(api_key=api_key)
    prompt = SYSTEM_PROMPT.replace("{context}", context)
    full_prompt = f"{prompt}\n\nUSER QUESTION: {question}"

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=512,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
            )
        )
        raw_text = response.text.strip()
        print("[Rooney raw]", repr(raw_text[:500]))  # debug

        # Clean trailing commas (thinking models sometimes emit them)
        cleaned = re.sub(r',\s*([}\]])', r'\1', raw_text)
        result = json.loads(cleaned)

        # Validate required keys
        required = {"answer_text", "grounded", "source_labels", "refusal_reason"}
        if not required.issubset(result.keys()):
            raise ValueError("Incomplete response structure")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "answer_text": "",
            "grounded": False,
            "source_labels": [],
            "refusal_reason": f"[DEBUG] {type(e).__name__}: {str(e)}",
        }
