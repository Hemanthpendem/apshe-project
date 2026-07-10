# BERT model directory

Place the exported fine-tuned BERT artifacts here after running
`notebooks/kaggle_training.ipynb` (Epic 2, Story 5-6):

- `config.json`
- `pytorch_model.bin` (or `model.safetensors`)
- `tokenizer.json`, `tokenizer_config.json`, `vocab.txt`

Until these exist, `app.py` uses the rule-based engine in
`emotion_engine.py` as a functional stand-in.
