# BiLSTM model directory

Place the exported BiLSTM artifacts here after running
`notebooks/kaggle_training.ipynb` (Epic 2, Story 6):

- `bilstm_model.h5` or `bilstm_model.pt`
- `tokenizer.pkl`
- `label_encoder.pkl`

Until these exist, `app.py` uses the rule-based engine in
`emotion_engine.py` as a functional stand-in.
