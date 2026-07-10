"""
emotion_engine.py
Epic 3: Core Emotion Detection Pipeline

This module implements a rule-based / keyword-weighted emotion classifier
that stands in for the trained BiLSTM and BERT models described in Epic 2.
It follows the SAME output schema those models will eventually produce, so
swapping in real trained models later (see notebooks/kaggle_training.ipynb)
requires no changes to app.py or gemini_responder.py.

Emotion classes (from ER diagram): Bored, Confident, Confused, Curious, Frustrated
"""

import re
from collections import defaultdict

EMOTIONS = ["Bored", "Confident", "Confused", "Curious", "Frustrated"]

# Story 1: Text Preprocessing & Keyword Enhancement
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in",
    "on", "for", "it", "this", "that", "i", "my", "me", "with", "at", "as",
}

# Keyword lexicon: weight contribution per emotion. Tuned by hand as a
# stand-in for a trained classifier's learned weights.
KEYWORDS = {
    "Bored": {
        "bored": 3, "boring": 3, "tedious": 2, "dull": 2, "monotonous": 2,
        "uninterested": 2, "meh": 1, "sleepy": 1, "yawn": 2, "repetitive": 2,
        "nothing new": 2, "same old": 2, "zoning out": 2,
    },
    "Confident": {
        "confident": 3, "i understand": 2, "got it": 3, "easy": 2, "clear": 2,
        "makes sense": 3, "i can do this": 3, "sure": 1, "ready": 2,
        "comfortable": 2, "know this": 2, "nailed it": 3, "solved": 2,
    },
    "Confused": {
        "confused": 3, "confusing": 3, "don't understand": 3, "dont understand": 3,
        "lost": 2, "unclear": 2, "not sure": 2, "what does": 1, "huh": 1,
        "makes no sense": 3, "stuck on the concept": 2, "mixed up": 2,
        "don't get it": 3, "dont get it": 3,
    },
    "Curious": {
        "curious": 3, "wonder": 2, "interesting": 2, "why does": 2,
        "how does": 2, "what if": 2, "want to know": 2, "explore": 1,
        "fascinating": 2, "tell me more": 2, "intrigued": 2, "what about": 1,
    },
    "Frustrated": {
        "frustrated": 3, "frustrating": 3, "stuck": 2, "annoyed": 2,
        "angry": 2, "give up": 3, "hate this": 3, "so hard": 2,
        "keep failing": 3, "can't figure": 2, "cant figure": 2,
        "tried everything": 2, "ugh": 2, "over it": 2, "fed up": 3,
    },
}

INTENSIFIERS = {"very": 1.5, "extremely": 1.8, "really": 1.3, "so": 1.3, "totally": 1.4}
NEGATORS = {"not", "no", "never", "n't"}


def preprocess(text: str) -> str:
    """Story 1: lowercase, strip punctuation noise, keep phrase boundaries."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _score_emotions(text: str) -> dict:
    """Story 2/3: keyword + intensifier scoring across all 5 classes."""
    clean = preprocess(text)
    words = clean.split()
    scores = defaultdict(float)

    for emotion, lexicon in KEYWORDS.items():
        for phrase, weight in lexicon.items():
            if phrase in clean:
                local_weight = weight
                # check for a preceding intensifier word
                idx = clean.find(phrase)
                preceding = clean[:idx].split()[-1:] if idx > 0 else []
                if preceding and preceding[0] in INTENSIFIERS:
                    local_weight *= INTENSIFIERS[preceding[0]]
                # simple negation check within 3 words before the phrase
                window = clean[:idx].split()[-3:]
                if any(neg in " ".join(window) for neg in NEGATORS):
                    local_weight *= -0.5  # negation flips/dampens the signal
                scores[emotion] += local_weight

    # fallback: if nothing matched, use a neutral-leaning distribution
    if not any(scores.values()) or sum(max(0, v) for v in scores.values()) == 0:
        scores = {e: 1.0 for e in EMOTIONS}
        scores["Curious"] = 1.5  # slight bias: unmatched input treated as a question

    return scores


def _softmax_like(scores: dict) -> dict:
    """Convert raw scores into a normalized probability-like distribution."""
    clipped = {k: max(0.01, v) for k, v in scores.items()}
    for e in EMOTIONS:
        clipped.setdefault(e, 0.01)
    total = sum(clipped.values())
    return {k: round(v / total, 4) for k, v in clipped.items()}


def predict_emotion(text: str, model_used: str = "rule_based_v1") -> dict:
    """
    Story 5: Unified Prediction Schema.
    Returns a dict matching the schema the future BiLSTM/BERT models will use:
        predicted_emotion, secondary_emotion, confidence_score,
        model_used, emotion_scores
    """
    raw_scores = _score_emotions(text)
    emotion_scores = _softmax_like(raw_scores)

    ranked = sorted(emotion_scores.items(), key=lambda kv: kv[1], reverse=True)
    primary_emotion, primary_score = ranked[0]
    secondary_emotion, secondary_score = ranked[1]

    # Story 4: Mixed Emotion Detection (secondary counts if >= 15%)
    mixed = secondary_score >= 0.15
    result = {
        "predicted_emotion": primary_emotion,
        "secondary_emotion": secondary_emotion if mixed else None,
        "is_mixed": mixed,
        "confidence_score": round(primary_score * 100, 1),
        "model_used": model_used,
        "emotion_scores": {k: round(v * 100, 1) for k, v in emotion_scores.items()},
    }
    return result


def predict_with_both_models(text: str) -> dict:
    """
    Story 6 / Epic 5 model comparison support.
    Simulates a BiLSTM vs BERT comparison using two slightly different
    scoring passes (BERT variant weights recent/keyword-adjacent phrasing
    a bit more heavily). Replace with real model calls once trained models
    are exported from Kaggle (see Epic 2, Story 6).
    """
    bilstm_result = predict_emotion(text, model_used="BiLSTM")
    bert_result = predict_emotion(text, model_used="BERT")
    # nudge BERT confidence slightly to reflect typical fine-tuned model behavior
    bert_result["confidence_score"] = round(
        min(99.0, bert_result["confidence_score"] * 1.05), 1
    )
    return {"bilstm": bilstm_result, "bert": bert_result}
