import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"


def init_session_state() -> None:
    defaults = {
        "api_base": DEFAULT_API_BASE,
        "access_token": "",
        "current_user_id": None,
        "current_csv_path": "",
        "analysis_csv_path": "",
        "cleaning_csv_path": "",
        "ml_csv_path": "",
        "last_cleaned_file_path": "",
        "last_analysis": None,
        "last_visualization": None,
        "last_recommendations": None,
        "last_ai_explanation": None,
        "last_cleaning_report": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def auth_headers() -> dict:
    token = st.session_state.get("access_token", "")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def require_login() -> None:
    if is_authenticated():
        return

    st.warning("Please log in before using this page.")
    if hasattr(st, "switch_page"):
        st.switch_page("pages/login.py")
    st.stop()


def logout() -> None:
    st.session_state.access_token = ""
    st.session_state.current_user_id = None
    st.session_state.current_csv_path = ""
    st.session_state.analysis_csv_path = ""
    st.session_state.cleaning_csv_path = ""
    st.session_state.ml_csv_path = ""
    st.session_state.last_cleaned_file_path = ""
    st.session_state.last_analysis = None
    st.session_state.last_visualization = None
    st.session_state.last_recommendations = None
    st.session_state.last_ai_explanation = None
    st.session_state.last_cleaning_report = None
