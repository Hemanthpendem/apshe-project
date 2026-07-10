"""
app.py
Epic 5: Streamlit UI Implementation
Epic 6: User Interaction

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()  # Epic 1, Story 4: pulls GOOGLE_API_KEY from .env if present

from emotion_engine import predict_emotion, predict_with_both_models, EMOTIONS
from gemini_responder import generate_response
from data_logger import log_record, load_history, clear_history

st.set_page_config(page_title="AI Learning Assistant", page_icon="🎓", layout="wide")

# ---------------------------------------------------------------------------
# Story 1: Responsive Layout and Session State Management
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []          # in-memory session list of results
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "email" not in st.session_state:
    st.session_state.email = "guest@learner.app"

st.title("🎓 AI-Powered Learning Assistant")
st.caption("Emotion-aware learning support — describe a problem, get guidance tuned to how you're feeling.")

tab_analyze, tab_compare, tab_dashboard = st.tabs(
    ["📝 Analyze", "🔬 Model Comparison", "📊 Analytics Dashboard"]
)

# ---------------------------------------------------------------------------
# TAB 1 — Story 2 (form controls) + Story 3 (form validation/errors)
# ---------------------------------------------------------------------------
with tab_analyze:
    col1, col2 = st.columns([1, 2])

    with col1:
        field = st.selectbox(
            "Field of study",
            ["Computer Science", "Mathematics", "Physics", "Biology",
             "History", "Languages", "Economics", "Other"],
        )
        st.session_state.email = st.text_input("Email (optional, for your history)",
                                                 value=st.session_state.email)
        run_clicked = st.button("Analyze my message", type="primary", use_container_width=True)
        clear_clicked = st.button("Clear session history", use_container_width=True)

    with col2:
        problem_text = st.text_area(
            "Describe what you're working on or how it's going",
            height=140,
            placeholder="e.g. I keep getting stuck on this recursion problem and I don't understand why it's not working...",
        )

    if clear_clicked:
        st.session_state.history = []
        st.session_state.last_result = None
        clear_history()
        st.success("Session history cleared.")

    if run_clicked:
        # Story 3: validation & error handling
        if not problem_text or not problem_text.strip():
            st.error("Please describe your problem or feeling before analyzing.")
        else:
            with st.spinner("Analyzing emotion and generating guidance..."):
                prediction = predict_emotion(problem_text, model_used="rule_based_v1")
                ai = generate_response(
                    field=field,
                    problem_text=problem_text,
                    emotion=prediction["predicted_emotion"],
                    secondary_emotion=prediction.get("secondary_emotion"),
                    confidence=prediction["confidence_score"],
                )
                record_id = log_record(
                    email=st.session_state.email,
                    field=field,
                    input_text=problem_text,
                    prediction=prediction,
                    ai_response=ai["text"],
                    response_type=ai["response_type"],
                )
                result = {
                    "record_id": record_id, "field": field, "input_text": problem_text,
                    **prediction, "ai_response": ai["text"], "response_type": ai["response_type"],
                }
                st.session_state.last_result = result
                st.session_state.history.append(result)

    if st.session_state.last_result:
        r = st.session_state.last_result
        st.divider()
        badge_col, conf_col = st.columns([2, 1])
        with badge_col:
            emo_label = r["predicted_emotion"]
            if r["is_mixed"]:
                emo_label += f" (with {r['secondary_emotion']} undertones)"
            st.subheader(f"Detected: {emo_label}")
        with conf_col:
            st.metric("Confidence", f"{r['confidence_score']}%")

        st.info(r["ai_response"])
        st.caption(
            f"Response type: {'Gemini AI' if r['response_type']=='gemini' else 'Fallback template'} "
            f"• Model: {r['model_used']} • Record ID: {r['record_id']}"
        )

        # Story 4: Visualize scores
        scores_df = pd.DataFrame(
            {"Emotion": list(r["emotion_scores"].keys()), "Score (%)": list(r["emotion_scores"].values())}
        )
        fig = px.bar(scores_df, x="Emotion", y="Score (%)", color="Emotion", title="Emotion score breakdown")
        st.plotly_chart(fig, use_container_width=True)

        if st.button("🔄 Regenerate response"):
            with st.spinner("Regenerating..."):
                ai2 = generate_response(
                    field=r["field"], problem_text=r["input_text"],
                    emotion=r["predicted_emotion"], secondary_emotion=r.get("secondary_emotion"),
                    confidence=r["confidence_score"],
                )
                st.session_state.last_result["ai_response"] = ai2["text"]
                st.session_state.last_result["response_type"] = ai2["response_type"]
                st.rerun()

# ---------------------------------------------------------------------------
# TAB 2 — Model Comparison (BiLSTM vs BERT stand-ins)
# ---------------------------------------------------------------------------
with tab_compare:
    st.subheader("Compare BiLSTM vs BERT predictions")
    compare_text = st.text_area("Enter text to compare model outputs", height=100, key="compare_input")
    if st.button("Compare models"):
        if not compare_text.strip():
            st.error("Enter some text first.")
        else:
            both = predict_with_both_models(compare_text)
            c1, c2 = st.columns(2)
            for col, key, label in [(c1, "bilstm", "BiLSTM"), (c2, "bert", "BERT")]:
                res = both[key]
                with col:
                    st.markdown(f"### {label}")
                    st.write(f"**Emotion:** {res['predicted_emotion']}")
                    st.write(f"**Confidence:** {res['confidence_score']}%")
                    if res["is_mixed"]:
                        st.write(f"**Secondary:** {res['secondary_emotion']}")
                    df = pd.DataFrame(
                        {"Emotion": list(res["emotion_scores"].keys()),
                         "Score": list(res["emotion_scores"].values())}
                    )
                    st.plotly_chart(px.bar(df, x="Emotion", y="Score"), use_container_width=True)
    st.caption(
        "Note: both models currently run the same rule-based engine as a placeholder. "
        "Swap in real BiLSTM/BERT inference once trained models are exported from Kaggle "
        "(see notebooks/kaggle_training.ipynb and Epic 2)."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Story 4: Analytics Dashboard and Interactive Charts
# ---------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("Session & historical analytics")
    rows = load_history()
    if not rows:
        st.info("No history yet — analyze a message in the first tab to populate this dashboard.")
    else:
        df = pd.DataFrame(rows)
        df["confidence_score"] = pd.to_numeric(df["confidence_score"], errors="coerce")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total sessions logged", len(df))
        c2.metric("Avg. confidence", f"{df['confidence_score'].mean():.1f}%")
        c3.metric("Unique fields", df["field"].nunique())

        colA, colB = st.columns(2)
        with colA:
            emo_counts = df["predicted_emotion"].value_counts().reset_index()
            emo_counts.columns = ["Emotion", "Count"]
            st.plotly_chart(
                px.pie(emo_counts, names="Emotion", values="Count", title="Emotion distribution"),
                use_container_width=True,
            )
        with colB:
            field_counts = df["field"].value_counts().reset_index()
            field_counts.columns = ["Field", "Count"]
            st.plotly_chart(
                px.bar(field_counts, x="Field", y="Count", title="Sessions by field of study"),
                use_container_width=True,
            )

        st.markdown("#### Session history")
        st.dataframe(
            df[["timestamp", "field", "predicted_emotion", "secondary_emotion",
                "confidence_score", "model_used", "response_type"]],
            use_container_width=True,
        )
