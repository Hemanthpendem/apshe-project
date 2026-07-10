"""
data_logger.py
Epic 3, Story 6: CSV Persistence & Cached Model Loading (persistence half)
Epic 4, Story 4: Session History Management and CSV Logging

Mirrors the Emotion_Records entity from the ER diagram:
record_id, email, field, input_text, predicted_emotion, secondary_emotion,
confidence_score, model_used, ai_response, response_type, emotion_scores,
timestamp, csv_logged
"""

import csv
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOG_PATH = os.path.join(DATA_DIR, "emotion_records.csv")

FIELDNAMES = [
    "record_id", "email", "field", "input_text", "predicted_emotion",
    "secondary_emotion", "confidence_score", "model_used", "ai_response",
    "response_type", "emotion_scores", "timestamp",
]


def _ensure_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_record(email: str, field: str, input_text: str, prediction: dict,
               ai_response: str, response_type: str) -> str:
    """Appends one Emotion_Record row. Returns the generated record_id."""
    _ensure_file()
    record_id = str(uuid.uuid4())[:8]
    row = {
        "record_id": record_id,
        "email": email or "anonymous",
        "field": field,
        "input_text": input_text,
        "predicted_emotion": prediction["predicted_emotion"],
        "secondary_emotion": prediction.get("secondary_emotion") or "",
        "confidence_score": prediction["confidence_score"],
        "model_used": prediction["model_used"],
        "ai_response": ai_response,
        "response_type": response_type,
        "emotion_scores": str(prediction["emotion_scores"]),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)
    return record_id


def load_history(email: str | None = None):
    """Returns list of dict rows, optionally filtered by user email."""
    _ensure_file()
    with open(LOG_PATH, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if email:
        rows = [r for r in rows if r["email"] == email]
    return rows


def clear_history():
    """Resets the CSV log (used by a UI reset control)."""
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    _ensure_file()
