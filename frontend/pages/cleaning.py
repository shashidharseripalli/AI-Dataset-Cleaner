from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from utils.api_client import post_json, show_response
from utils.session import auth_headers
from utils.session import init_session_state, require_login

st.set_page_config(page_title="Cleaning", layout="wide")
init_session_state()
require_login()

st.title("Cleaning")

csv_path = st.text_input(
    "Cleaning CSV Path",
    value=st.session_state.cleaning_csv_path or str(Path("uploads/raw/sample.csv")),
    key="cleaning_csv_path",
)

selected_ops = st.multiselect(
    "Operations",
    [
        "fill_missing_values",
        "duplicate_removal",
        "encoding",
        "scaling",
        "outlier_handling",
    ],
    default=[
        "fill_missing_values",
        "duplicate_removal",
        "encoding",
        "scaling",
        "outlier_handling",
    ],
)
outlier_strategy = st.selectbox("Outlier Strategy", ["clip_iqr", "remove"])

if st.button("Run Cleaning"):
    resp = post_json(
        "/cleaning/run",
        {
            "csv_path": csv_path,
            "operations": selected_ops,
            "outlier_strategy": outlier_strategy,
        },
        timeout=120,
    )
    show_response(resp)
    if resp.ok:
        cleaned_path = resp.json().get("cleaned_file_path", "")
        st.session_state.last_cleaned_file_path = cleaned_path
        st.success("Cleaned dataset generated.")

st.subheader("Preview Cleaned Dataset")
preview_path = st.text_input(
    "Cleaned CSV Path",
    value=st.session_state.last_cleaned_file_path,
)
preview_rows = st.slider("Rows to preview", min_value=5, max_value=200, value=20)
if st.button("Load Cleaned Dataset"):
    try:
        cleaned_df = pd.read_csv(preview_path)
        st.success(f"Loaded {cleaned_df.shape[0]} rows x {cleaned_df.shape[1]} columns")
        st.dataframe(cleaned_df.head(preview_rows), use_container_width=True)
    except Exception as exc:
        st.error(f"Could not load cleaned dataset: {exc}")

if st.button("Prepare Download"):
    try:
        api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
        response = requests.get(
            f"{api_base}/download/cleaned",
            params={"file_path": preview_path},
            headers=auth_headers(),
            timeout=60,
        )
        if response.status_code != 200:
            st.error(f"Download failed: {response.text}")
        else:
            st.download_button(
                "Download Cleaned Dataset",
                data=response.content,
                file_name=Path(preview_path).name or "cleaned_dataset.csv",
                mime="text/csv",
            )
    except Exception as exc:
        st.error(f"Could not prepare download: {exc}")
