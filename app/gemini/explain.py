"""Thin wrapper around the Gemini API for generating human‑readable explanations."""

import os
import time
from google import genai

# Models to try in order
_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash"]
_MAX_RETRIES = 3
_RETRY_DELAY = 2  # seconds


def _get_client() -> genai.Client:
    """Configure and return the Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "Set the GEMINI_API_KEY environment variable before running the app.\n"
            "  Windows:  $env:GEMINI_API_KEY = 'your-key-here'\n"
            "  Linux:    export GEMINI_API_KEY=your-key-here"
        )
    return genai.Client(api_key=api_key)


def generate_explanation(score_row: dict) -> str:
    """Turn a single compatibility‑score row into a plain‑English explanation.

    Parameters
    ----------
    score_row : dict
        Must contain at least `overall_score` and any `gap_*` keys.

    Returns
    -------
    str
        A human‑readable paragraph suitable for a parent or admin.
    """
    prompt = (
        "You are a child‑welfare support assistant. Given the following "
        "compatibility scores between a child and a prospective family, "
        "write a short, empathetic, jargon‑free paragraph explaining:\n"
        "  1. The overall compatibility.\n"
        "  2. Which areas are well‑matched.\n"
        "  3. Where gaps exist and what support might help.\n\n"
        f"Scores: {score_row}\n\n"
    try:
        client = _get_client()
    except Exception as exc:
        return f"[Gemini unavailable] {exc}"

    for model in _MODELS:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:
                err_str = str(exc)
                # Retry on 503 / UNAVAILABLE / rate-limit errors
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    if attempt < _MAX_RETRIES:
                        time.sleep(_RETRY_DELAY * attempt)
                        continue
                    # Exhausted retries for this model — try the next one
                    break
                # 404 = model not available — skip to next model immediately
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break
                # Non‑retryable error
                return f"[Gemini error]  {exc}"

    return "[Gemini unavailable – all models are overloaded. Please try again in a moment.]"
