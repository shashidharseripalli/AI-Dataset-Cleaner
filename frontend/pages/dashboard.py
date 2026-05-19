import streamlit as st

from utils.api_client import get, post_json, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Dashboard", layout="wide")
init_session_state()

st.title("Dashboard")

st.subheader("Auth Status")
st.code(st.session_state.access_token or "No token")
if st.button("Check /auth/me"):
    show_response(get("/auth/me"))

st.subheader("Users")
new_username = st.text_input("New Username")
if st.button("Create User"):
    show_response(post_json("/users/", {"username": new_username}))

if st.button("List Users"):
    show_response(get("/users/"))

st.subheader("Datasets")
d_name = st.text_input("Dataset Name")
d_desc = st.text_input("Dataset Description")
d_owner = st.number_input("Owner ID", min_value=1, value=1, step=1)
if st.button("Create Dataset Metadata"):
    show_response(
        post_json(
            "/datasets/",
            {"name": d_name, "description": d_desc, "owner_id": int(d_owner)},
        )
    )

if st.button("List Datasets"):
    show_response(get("/datasets/"))
