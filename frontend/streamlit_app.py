import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"


def auth_headers():
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def show_response(resp: requests.Response):
    st.write(f"Status: `{resp.status_code}`")
    try:
        st.json(resp.json())
    except Exception:
        st.text(resp.text)


st.set_page_config(page_title="AI Dataset Cleaner - API Tester", layout="wide")
st.title("AI Dataset Cleaner - Backend Tester")

if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "last_cleaned_file_path" not in st.session_state:
    st.session_state.last_cleaned_file_path = ""

api_base = st.sidebar.text_input("API Base URL", value=DEFAULT_API_BASE)
st.sidebar.caption("Make sure FastAPI is running before testing.")

tab_auth, tab_users, tab_dataset, tab_upload, tab_analysis, tab_cleaning, tab_ml = st.tabs(
    ["Auth", "Users", "Datasets", "Upload", "Analysis", "Cleaning", "ML Reco"]
)

with tab_auth:
    st.subheader("Signup")
    su_col1, su_col2 = st.columns(2)
    with su_col1:
        signup_username = st.text_input("Signup Username", key="signup_username")
    with su_col2:
        signup_password = st.text_input(
            "Signup Password", type="password", key="signup_password"
        )
    if st.button("Signup"):
        payload = {"username": signup_username, "password": signup_password}
        resp = requests.post(f"{api_base}/auth/signup", json=payload, timeout=20)
        show_response(resp)
        if resp.ok:
            token = resp.json().get("access_token", "")
            st.session_state.access_token = token

    st.subheader("Login")
    li_col1, li_col2 = st.columns(2)
    with li_col1:
        login_username = st.text_input("Login Username", key="login_username")
    with li_col2:
        login_password = st.text_input(
            "Login Password", type="password", key="login_password"
        )
    if st.button("Login"):
        payload = {"username": login_username, "password": login_password}
        resp = requests.post(f"{api_base}/auth/login", json=payload, timeout=20)
        show_response(resp)
        if resp.ok:
            token = resp.json().get("access_token", "")
            st.session_state.access_token = token
            st.success("Token saved in session.")

    st.subheader("Token")
    st.code(st.session_state.access_token or "No token yet")
    if st.button("Get /auth/me"):
        resp = requests.get(
            f"{api_base}/auth/me",
            headers=auth_headers(),
            timeout=20,
        )
        show_response(resp)

with tab_users:
    st.subheader("Create User")
    new_username = st.text_input("New Username")
    if st.button("Create User (/users/)"):
        resp = requests.post(
            f"{api_base}/users/",
            json={"username": new_username},
            headers=auth_headers(),
            timeout=20,
        )
        show_response(resp)

    st.subheader("List Users")
    if st.button("List Users (/users/)"):
        resp = requests.get(
            f"{api_base}/users/",
            headers=auth_headers(),
            timeout=20,
        )
        show_response(resp)

with tab_dataset:
    st.subheader("Create Dataset Metadata")
    d_name = st.text_input("Dataset Name")
    d_desc = st.text_input("Dataset Description")
    d_owner = st.number_input("Owner ID", min_value=1, value=1, step=1)
    if st.button("Create Dataset (/datasets/)"):
        resp = requests.post(
            f"{api_base}/datasets/",
            json={"name": d_name, "description": d_desc, "owner_id": int(d_owner)},
            headers=auth_headers(),
            timeout=20,
        )
        show_response(resp)

    st.subheader("List Datasets")
    if st.button("List Datasets (/datasets/)"):
        resp = requests.get(
            f"{api_base}/datasets/",
            headers=auth_headers(),
            timeout=20,
        )
        show_response(resp)

with tab_upload:
    st.subheader("Upload CSV")
    up_owner = st.number_input("Upload Owner ID", min_value=1, value=1, step=1)
    up_name = st.text_input("Optional Dataset Name", value="")
    up_desc = st.text_input("Optional Description", value="")
    uploaded_file = st.file_uploader("Select CSV file", type=["csv"])
    if st.button("Upload to /datasets/upload"):
        if not uploaded_file:
            st.error("Please choose a CSV file first.")
        else:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            data = {
                "owner_id": str(int(up_owner)),
                "dataset_name": up_name,
                "description": up_desc,
            }
            resp = requests.post(
                f"{api_base}/datasets/upload",
                files=files,
                data=data,
                headers=auth_headers(),
                timeout=60,
            )
            show_response(resp)

with tab_analysis:
    st.subheader("Run Analysis")
    analysis_csv_path = st.text_input(
        "CSV Path",
        value=str(Path("uploads/raw/sample.csv")),
        help="Use the saved_path returned from upload API.",
    )
    if st.button("Analyze (/analysis/run)"):
        resp = requests.post(
            f"{api_base}/analysis/run",
            json={"csv_path": analysis_csv_path},
            headers=auth_headers(),
            timeout=90,
        )
        show_response(resp)

with tab_cleaning:
    st.subheader("Run Cleaning")
    cleaning_csv_path = st.text_input(
        "Cleaning CSV Path",
        value=str(Path("uploads/raw/sample.csv")),
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
    if st.button("Clean (/cleaning/run)"):
        payload = {
            "csv_path": cleaning_csv_path,
            "operations": selected_ops,
            "outlier_strategy": outlier_strategy,
        }
        resp = requests.post(
            f"{api_base}/cleaning/run",
            json=payload,
            headers=auth_headers(),
            timeout=120,
        )
        show_response(resp)
        if resp.ok:
            cleaned_file_path = resp.json().get("cleaned_file_path", "")
            st.session_state.last_cleaned_file_path = cleaned_file_path

    st.subheader("Preview Cleaned Dataset")
    preview_path = st.text_input(
        "Cleaned CSV Path",
        value=st.session_state.last_cleaned_file_path,
        help="Uses cleaned_file_path returned by /cleaning/run.",
    )
    preview_rows = st.slider("Rows to preview", min_value=5, max_value=200, value=20)
    if st.button("Load Cleaned Dataset"):
        try:
            cleaned_df = pd.read_csv(preview_path)
            st.success(f"Loaded {cleaned_df.shape[0]} rows x {cleaned_df.shape[1]} columns")
            st.dataframe(cleaned_df.head(preview_rows), use_container_width=True)
        except Exception as exc:
            st.error(f"Could not load cleaned dataset: {exc}")

with tab_ml:
    st.subheader("Algorithm Recommendation")
    use_csv_detection = st.checkbox("Auto-detect from CSV path", value=True)
    reco_csv_path = st.text_input(
        "CSV Path for Detection",
        value="",
        help="If provided, backend detects dataset type, feature count, and data size automatically.",
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
    target_column = st.text_input("Target Column (optional)", value="")
    data_size = st.number_input(
        "Data Size (rows) (manual)",
        min_value=1,
        value=1000,
        step=100,
        disabled=use_csv_detection,
    )

    if st.button("Recommend (/ml/recommend)"):
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
        resp = requests.post(
            f"{api_base}/ml/recommend",
            json=payload,
            headers=auth_headers(),
            timeout=30,
        )
        show_response(resp)

st.divider()
st.caption("Run with: streamlit run frontend/streamlit_app.py")
