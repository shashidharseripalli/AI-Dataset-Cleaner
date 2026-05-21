from pathlib import Path

import streamlit as st

from utils.api_client import post_json, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Analysis", layout="wide")
init_session_state()

st.title("Analysis")

csv_path = st.text_input(
    "CSV Path",
    value=st.session_state.analysis_csv_path or str(Path("uploads/raw/sample.csv")),
    key="analysis_csv_path",
)

# layout columns for action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Run Analysis"):
        show_response(post_json("/analysis/run", {"csv_path": csv_path}, timeout=90))

with col2:
    if st.button("Generate Visualizations"):
        viz_resp = post_json("/analysis/visualize", {"csv_path": csv_path}, timeout=120)
        show_response(viz_resp)

        if viz_resp.status_code == 200:
            viz = viz_resp.json()
        else:
            viz = {}

        if isinstance(viz, dict) and "charts" in viz:
            charts = viz.get("charts", {})

            st.subheader("Histograms")
            for item in charts.get("histograms", []):
                st.write(f"Column: {item['column']}")
                st.bar_chart(
                    data={"count": item["counts"]},
                    x=list(range(len(item["bins"]))),
                    y="count",
                )
                st.caption("Bins: " + ", ".join(item["bins"]))

            st.subheader("Missing Values Heatmap (column-wise)")
            mh = charts.get("missing_heatmap", {})
            if mh.get("columns"):
                st.bar_chart(
                    data={"missing": mh["missing_counts"]},
                    x=list(range(len(mh["columns"]))),
                    y="missing",
                )
                st.caption("Columns: " + ", ".join(mh["columns"]))

            st.subheader("Pie Charts (Top Categories)")
            for item in charts.get("pie_charts", []):
                st.write(f"Column: {item['column']}")
                # Streamlit native fallback table (simple template)
                pie_df = {"label": item["labels"], "value": item["values"]}
                st.dataframe(pie_df, use_container_width=True)

            st.subheader("Correlation Matrix")
            cm = charts.get("correlation_matrix", {})
            if cm.get("matrix"):
                st.dataframe(cm["matrix"], use_container_width=True)

with col3:
    if st.button("AI Explain (Gemini)"):
        ai_resp = post_json("/ai/explain", {"csv_path": csv_path}, timeout=120)
        show_response(ai_resp)

        if ai_resp.status_code != 200:
            st.stop()

        payload = ai_resp.json()
        ai = payload.get("ai_explanation", {})

        st.subheader("Cleaning Reasoning")
        for item in ai.get("cleaning_reasoning", []):
            st.write(f"- {item}")

        st.subheader("Model Recommendation Reasoning")
        st.json(ai.get("model_recommendation_reasoning", {}))

        st.subheader("Dataset Insights")
        for item in ai.get("dataset_insights", []):
            st.write(f"- {item}")
