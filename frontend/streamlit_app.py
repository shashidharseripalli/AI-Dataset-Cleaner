import streamlit as st

from utils.session import init_session_state

st.set_page_config(page_title="AI Dataset Cleaner", layout="wide")
init_session_state()

st.title("AI Dataset Cleaner")
st.caption("Frontend -> FastAPI backend workflow tester")

st.sidebar.subheader("Backend")
st.session_state.api_base = st.sidebar.text_input(
    "API Base URL",
    value=st.session_state.api_base,
)

st.write("Use the pages in the left sidebar:")
st.write("- Login")
st.write("- Signup")
st.write("- Dashboard")
st.write("- Upload")
st.write("- Analysis")
st.write("- Cleaning")
st.write("- Results")
