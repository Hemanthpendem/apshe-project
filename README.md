# 🎓 AI-Powered Learning Assistant

An emotion-aware learning support tool built with Streamlit. Students
describe a problem or how they're feeling about a subject; the app detects
their emotional state (Bored, Confident, Confused, Curious, Frustrated —
including mixed emotions) and generates empathetic, field-aware guidance
using Google's Gemini AI.

## Features

- 🧠 5-class emotion detection with mixed-emotion support
- 💬 AI-generated empathetic responses (Gemini) with offline fallback templates
- 📊 Interactive analytics dashboard (Plotly charts)
- 🔬 Side-by-side model comparison view
- 🗂️ CSV-based session history logging
- 📓 Ready-to-run Kaggle notebook to train real BiLSTM/BERT models

## What's included right now

- **`emotion_engine.py`** — working keyword/rule-based 5-class emotion
  classifier with mixed-emotion detection and a unified prediction schema.
  This runs immediately with no training or GPU required.
- **`gemini_responder.py`** — builds emotion-aware prompts for Gemini and
  falls back to hand-written empathetic templates when no API key is set
  (or if the API call fails).
- **`data_logger.py`** — CSV persistence of every analysis (matches the
  `Emotion_Records` entity from the ER diagram).
- **`app.py`** — full Streamlit UI: analyze tab, BiLSTM-vs-BERT comparison
  tab (currently both point at the rule-based engine), and an analytics
  dashboard with charts.
- **`notebooks/kaggle_training.ipynb`** — ready-to-run notebook scaffold
  for training the real BiLSTM and BERT models on Kaggle GPUs (Epic 2).

## Quickstart

```bash
# 1. Set up environment (Epic 1)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. (Optional) enable real Gemini responses
cp .env.example .env
# then edit .env and paste your key from https://aistudio.google.com/

# 3. Run the app
streamlit run app.py
```

Without a Gemini key, the app works fully using the fallback templates —
nothing is blocked.

## Upgrading to trained models (Epic 2)

1. Open `notebooks/kaggle_training.ipynb` on [Kaggle](https://www.kaggle.com/),
   enable a GPU, attach a labeled dataset (columns: `text,label`, labels ∈
   {Bored, Confident, Confused, Curious, Frustrated}).
2. Run all cells. It trains a BiLSTM from scratch, does a domain-adaptive
   fine-tuning pass, then fine-tunes `bert-base-uncased` with class
   weighting.
3. Download the exported folders from the Kaggle Output tab and place them
   at `models/bltsm/` and `models/bert_emotion_model_final/` locally.
4. Swap `emotion_engine.predict_emotion()` to load and call the real
   models instead of the keyword scorer — the rest of the app
   (`app.py`, `gemini_responder.py`, `data_logger.py`) needs no changes
   since they all consume the same output schema:
   ```python
   {
     "predicted_emotion": str, "secondary_emotion": str | None,
     "is_mixed": bool, "confidence_score": float,
     "model_used": str, "emotion_scores": dict
   }
   ```

## Project structure

```
app.py                 Streamlit UI (Epic 5, 6)
emotion_engine.py       Emotion detection pipeline (Epic 3)
gemini_responder.py     AI guidance + fallback templates (Epic 4)
data_logger.py          CSV persistence (Epic 3/4)
requirements.txt
.env.example
models/
  bltsm/                BiLSTM model artifacts go here
  bert_emotion_model_final/  BERT model artifacts go here
data/                    emotion_records.csv gets created here at runtime
notebooks/
  kaggle_training.ipynb  Full training pipeline for Epic 2
```

## Data model (from ER diagram)

Two entities, one-to-many: **Users** (`email` PK) → **Emotion_Records**
(`record_id` PK, `email` FK). See `data_logger.py` for the exact fields
persisted.
