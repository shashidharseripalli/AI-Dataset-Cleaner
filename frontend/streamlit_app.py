from pathlib import Path

import requests
import streamlit as st

from utils.api_client import get, post_json, post_multipart
from utils.session import auth_headers, init_session_state, is_authenticated, logout

st.set_page_config(page_title="AI Dataset Cleaner", layout="wide")
init_session_state()

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _store_current_user() -> None:
    me_resp = get("/auth/me")
    if me_resp.ok:
        st.session_state.current_user_id = me_resp.json().get("id")


def _auth_screen() -> None:
    st.title("AI Dataset Cleaner")
    st.caption("Login or register to start cleaning and understanding your dataset.")

    with st.expander("Backend settings", expanded=False):
        st.session_state.api_base = st.text_input(
            "API Base URL",
            value=st.session_state.api_base,
        )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        username = st.text_input("Username", key="main_login_username")
        password = st.text_input("Password", type="password", key="main_login_password")

        if st.button("Login", type="primary"):
            resp = post_json("/auth/login", {"username": username, "password": password})
            if resp.ok:
                st.session_state.access_token = resp.json().get("access_token", "")
                _store_current_user()
                st.rerun()
            st.error(resp.text)

    with register_tab:
        username = st.text_input("Username", key="main_signup_username")
        password = st.text_input("Password", type="password", key="main_signup_password")

        if st.button("Register", type="primary"):
            resp = post_json("/auth/signup", {"username": username, "password": password})
            if resp.ok:
                st.session_state.access_token = resp.json().get("access_token", "")
                _store_current_user()
                st.rerun()
            st.error(resp.text)


def _run_pipeline(saved_path: str) -> None:
    progress = st.progress(0, text="Analyzing dataset...")

    analysis_resp = post_json("/analysis/run", {"csv_path": saved_path}, timeout=90)
    if not analysis_resp.ok:
        st.error(f"Analysis failed: {analysis_resp.text}")
        return
    st.session_state.last_analysis = analysis_resp.json()
    progress.progress(20, text="Creating visualizations...")

    visualization_resp = post_json("/analysis/visualize", {"csv_path": saved_path}, timeout=120)
    if visualization_resp.ok:
        st.session_state.last_visualization = visualization_resp.json()
    else:
        st.warning(f"Visualization failed: {visualization_resp.text}")
    progress.progress(40, text="Cleaning dataset...")

    cleaning_resp = post_json(
        "/cleaning/run",
        {
            "csv_path": saved_path,
            "operations": [
                "fill_missing_values",
                "duplicate_removal",
                "encoding",
                "scaling",
                "outlier_handling",
            ],
            "outlier_strategy": "clip_iqr",
        },
        timeout=120,
    )
    if cleaning_resp.ok:
        cleaning_payload = cleaning_resp.json()
        st.session_state.last_cleaned_file_path = cleaning_payload.get("cleaned_file_path", "")
        st.session_state.last_cleaning_report = cleaning_payload.get("cleaning_report", {})
    else:
        st.warning(f"Cleaning failed: {cleaning_resp.text}")
    progress.progress(60, text="Finding ML recommendations...")

    reco_resp = post_json(
        "/ml/recommend",
        {"csv_path": saved_path, "target_column": None},
        timeout=60,
    )
    if reco_resp.ok:
        st.session_state.last_recommendations = reco_resp.json()
    else:
        st.warning(f"Recommendation failed: {reco_resp.text}")
    progress.progress(80, text="Generating AI explanation...")

    ai_resp = post_json("/ai/explain", {"csv_path": saved_path}, timeout=120)
    if ai_resp.ok:
        st.session_state.last_ai_explanation = ai_resp.json().get("ai_explanation", {})
    else:
        st.warning(f"AI explanation failed: {ai_resp.text}")

    progress.progress(100, text="Complete")


def _render_visualizations() -> None:
    viz = st.session_state.last_visualization or {}
    charts = viz.get("charts", {})

    if not charts:
        st.info("No visualization data available yet.")
        return

    st.subheader("Visualizations")

    histograms = charts.get("histograms", [])
    if histograms:
        st.write("Histograms")
        for item in histograms[:4]:
            st.caption(item["column"])
            st.bar_chart({"count": item["counts"]})

    missing = charts.get("missing_heatmap", {})
    if missing.get("columns"):
        st.write("Missing Values")
        st.bar_chart({"missing": missing["missing_counts"]})

    correlation = charts.get("correlation_matrix", {})
    if correlation.get("matrix"):
        st.write("Correlation Matrix")
        st.dataframe(correlation["matrix"], use_container_width=True)


def _render_recommendations() -> None:
    st.subheader("Recommendations")

    recommendations = st.session_state.last_recommendations or {}
    input_summary = recommendations.get("input", {})
    if input_summary:
        st.caption(
            f"Detected task: {input_summary.get('dataset_type', 'unknown')} | "
            f"Rows: {input_summary.get('data_size', '-')}"
        )

    for item in recommendations.get("recommendations", []):
        st.write(f"**{item.get('algorithm', 'Model')}**")
        st.caption(item.get("reason", "Recommended for this dataset."))

    ai = st.session_state.last_ai_explanation or {}
    insights = ai.get("dataset_insights", [])
    cleaning = ai.get("cleaning_reasoning", [])
    model_reasoning = ai.get("model_recommendation_reasoning", {})

    if insights or cleaning or model_reasoning:
        st.subheader("Reason In Brief")
        for point in cleaning[:3]:
            st.write(f"- {point}")
        for point in insights[:3]:
            st.write(f"- {point}")
        if model_reasoning:
            why = model_reasoning.get("why", [])
            for point in why[:2]:
                st.write(f"- {point}")


def _render_download() -> None:
    cleaned_path = st.session_state.last_cleaned_file_path
    if not cleaned_path:
        return

    api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
    response = requests.get(
        f"{api_base}/download/cleaned",
        params={"file_path": cleaned_path},
        headers=auth_headers(),
        timeout=60,
    )
    if response.status_code == 200:
        st.download_button(
            "Download Cleaned Dataset",
            data=response.content,
            file_name=Path(cleaned_path).name or "cleaned_dataset.csv",
            mime="text/csv",
        )
    else:
        st.warning(f"Cleaned file is not ready for download: {response.text}")


def _workspace() -> None:
    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.title("AI Dataset Cleaner")
        st.caption("Upload a CSV and the app will process, visualize, clean, and explain it.")
    with header_right:
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

    if uploaded_file and st.button("Upload And Process", type="primary"):
        owner_id = int(st.session_state.current_user_id or 1)
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        data = {
            "owner_id": str(owner_id),
            "dataset_name": Path(uploaded_file.name).stem,
            "description": "Uploaded from Streamlit guided workflow",
        }

        upload_resp = post_multipart("/datasets/upload", files=files, data=data, timeout=90)
        if not upload_resp.ok:
            st.error(f"Upload failed: {upload_resp.text}")
            return

        saved_path = upload_resp.json().get("saved_path", "")
        st.session_state.current_csv_path = saved_path
        st.session_state.analysis_csv_path = saved_path
        st.session_state.cleaning_csv_path = saved_path
        st.session_state.ml_csv_path = saved_path
        _run_pipeline(saved_path)

    if st.session_state.current_csv_path:
        st.success(f"Processed file: {st.session_state.current_csv_path}")

    if st.session_state.last_analysis:
        summary = st.session_state.last_analysis.get("summary", {})
        st.subheader("Dataset Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", summary.get("rows", 0))
        c2.metric("Columns", summary.get("columns", 0))
        c3.metric("Cleaned File", "Ready" if st.session_state.last_cleaned_file_path else "Pending")

        _render_visualizations()
        _render_recommendations()
        _render_download()


if is_authenticated():
    _workspace()
else:
    _auth_screen()
