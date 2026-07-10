"""
gemini_responder.py
Epic 4: AI-Powered Guidance and Regeneration Engine

Story 1: Capture field + problem context, build a Gemini-ready prompt with
          emotion/confidence embedded.
Story 2: Generate empathetic, field-aware responses; fall back to templates
          if no API key is configured or the call fails.
Story 3: Regeneration support (stateless — caller just calls again).
"""

import os
import random

# ---------------------------------------------------------------------------
# Story 1: Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(field: str, problem_text: str, emotion: str,
                  secondary_emotion: str | None, confidence: float) -> str:
    mixed_note = f" with a secondary undertone of {secondary_emotion}" if secondary_emotion else ""
    return (
        f"You are a warm, encouraging tutor. A student studying '{field}' just wrote:\n"
        f'"{problem_text}"\n\n'
        f"Detected emotional state: {emotion}{mixed_note} (confidence: {confidence}%).\n\n"
        "Write a short, empathetic response (3-5 sentences) that:\n"
        "1. Acknowledges how the student seems to be feeling\n"
        "2. Gives one concrete, actionable next step for their specific problem\n"
        "3. Ends with an encouraging note\n"
        "Keep it warm but not saccharine, and specific to their field and problem."
    )


# ---------------------------------------------------------------------------
# Story 2: Fallback templates (used when no GOOGLE_API_KEY is set, or on error)
# ---------------------------------------------------------------------------

FALLBACK_TEMPLATES = {
    "Bored": [
        "It sounds like {field} isn't grabbing you right now, and that's a normal part of learning. "
        "Try connecting '{problem}' to a real-world example you actually care about — it often makes "
        "dry material click. Small wins here will build momentum.",
        "Feeling bored with {field} usually means the material needs a new angle. For '{problem}', "
        "try teaching it out loud to an imaginary student, or switch to a hands-on example. "
        "You've got this — sometimes the fix is just changing the format, not the effort.",
    ],
    "Confident": [
        "Great energy on {field}! Since you're feeling solid on '{problem}', try pushing a bit further — "
        "attempt a harder variation or explain it to someone else to lock it in. Keep that momentum going.",
        "Nice work — confidence like this is exactly when deeper learning happens. Challenge yourself with "
        "a follow-up problem related to '{problem}' to stretch what you already know.",
    ],
    "Confused": [
        "Confusion around '{problem}' in {field} is completely normal — it usually means you're right at "
        "the edge of a new concept. Try breaking it into the smallest possible sub-step and just solve that "
        "piece first. You're closer than it feels.",
        "It's okay to feel lost on '{problem}'. A good next step: rewrite the question in your own words, "
        "then look up just one term you're unsure about in {field}. Small clarity steps add up fast.",
    ],
    "Curious": [
        "Love the curiosity about '{problem}'! Follow that thread — look up one related concept in {field} "
        "that you're genuinely wondering about. Curiosity is the fastest path to real understanding.",
        "That question about '{problem}' is a great one. Try exploring it with a quick example or analogy "
        "in {field} — curiosity like yours usually leads to the deepest learning.",
    ],
    "Frustrated": [
        "Frustration with '{problem}' in {field} is a sign you're pushing through something hard — that's "
        "actually progress. Take a 5-minute break, then come back and try just one small piece of it again.",
        "It's tough when '{problem}' isn't clicking. Step away for a moment, then re-approach with a simpler "
        "version of the question. You're not stuck forever — you're mid-process, and that's normal in {field}.",
    ],
}


def _fallback_response(field: str, problem_text: str, emotion: str) -> str:
    templates = FALLBACK_TEMPLATES.get(emotion, FALLBACK_TEMPLATES["Curious"])
    template = random.choice(templates)
    short_problem = (problem_text[:80] + "...") if len(problem_text) > 80 else problem_text
    return template.format(field=field, problem=short_problem)


# ---------------------------------------------------------------------------
# Story 2: Main response generator (Gemini call with graceful fallback)
# ---------------------------------------------------------------------------

def generate_response(field: str, problem_text: str, emotion: str,
                       secondary_emotion: str | None = None,
                       confidence: float = 0.0) -> dict:
    """
    Returns {"text": str, "response_type": "gemini" | "template"}
    Uses GOOGLE_API_KEY from environment if present; otherwise (or on any
    error) returns a fallback template response so the app never breaks.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()

    if not api_key:
        return {
            "text": _fallback_response(field, problem_text, emotion),
            "response_type": "template",
        }

    try:
        import google.generativeai as genai  # lazy import, only needed if key exists

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = build_prompt(field, problem_text, emotion, secondary_emotion, confidence)
        result = model.generate_content(prompt)
        text = (result.text or "").strip()
        if not text:
            raise ValueError("Empty response from Gemini")
        return {"text": text, "response_type": "gemini"}

    except Exception:
        # Story 2: graceful fallback on any API/network/quota error
        return {
            "text": _fallback_response(field, problem_text, emotion),
            "response_type": "template",
        }
