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

if st.button("Run Analysis"):
    show_response(post_json("/analysis/run", {"csv_path": csv_path}, timeout=90))
