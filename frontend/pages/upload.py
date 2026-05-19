import streamlit as st

from utils.api_client import post_multipart, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Upload", layout="wide")
init_session_state()

st.title("Upload")

owner_id = st.number_input("Owner ID", min_value=1, value=1, step=1)
dataset_name = st.text_input("Optional Dataset Name")
description = st.text_input("Optional Description")
uploaded_file = st.file_uploader("Select CSV file", type=["csv"])

if st.button("Upload CSV"):
    if not uploaded_file:
        st.error("Please select a CSV file.")
    else:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        data = {
            "owner_id": str(int(owner_id)),
            "dataset_name": dataset_name,
            "description": description,
        }
        resp = post_multipart("/datasets/upload", files=files, data=data)
        show_response(resp)
        if resp.ok:
            saved_path = resp.json().get("saved_path", "")
            st.session_state.current_csv_path = saved_path
            st.session_state.analysis_csv_path = saved_path
            st.session_state.cleaning_csv_path = saved_path
            st.session_state.ml_csv_path = saved_path
            st.success("CSV path copied to Analysis/Cleaning/Results pages.")
