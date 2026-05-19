import streamlit as st

from utils.api_client import post_json, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Results", layout="wide")
init_session_state()

st.title("Results")
st.caption("ML algorithm recommendations")

use_csv_detection = st.checkbox("Auto-detect from CSV path", value=True)
reco_csv_path = st.text_input(
    "CSV Path for Detection",
    value=st.session_state.ml_csv_path,
    key="ml_csv_path",
)
dataset_type = st.selectbox(
    "Dataset Type (manual)",
    ["classification", "regression", "clustering", "nlp", "unknown"],
    disabled=use_csv_detection,
)
feature_count = st.number_input(
    "Feature Count (manual)",
    min_value=1,
    value=10,
    step=1,
    disabled=use_csv_detection,
)
target_column = st.text_input("Target Column (optional)")
data_size = st.number_input(
    "Data Size (rows) (manual)",
    min_value=1,
    value=1000,
    step=100,
    disabled=use_csv_detection,
)

if st.button("Get Recommendations"):
    if use_csv_detection:
        payload = {
            "csv_path": reco_csv_path,
            "target_column": target_column or None,
        }
    else:
        payload = {
            "dataset_type": dataset_type,
            "feature_count": int(feature_count),
            "target_column": target_column or None,
            "data_size": int(data_size),
        }
    show_response(post_json("/ml/recommend", payload, timeout=30))
