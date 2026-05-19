import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"


def init_session_state() -> None:
    defaults = {
        "api_base": DEFAULT_API_BASE,
        "access_token": "",
        "current_csv_path": "",
        "analysis_csv_path": "",
        "cleaning_csv_path": "",
        "ml_csv_path": "",
        "last_cleaned_file_path": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def auth_headers() -> dict:
    token = st.session_state.get("access_token", "")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}
