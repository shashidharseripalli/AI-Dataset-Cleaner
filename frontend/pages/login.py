import streamlit as st

from utils.api_client import post_json, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Login", layout="wide")
init_session_state()

st.title("Login")

username = st.text_input("Username", key="login_username")
password = st.text_input("Password", type="password", key="login_password")

if st.button("Login"):
    resp = post_json("/auth/login", {"username": username, "password": password})
    show_response(resp)
    if resp.ok:
        st.session_state.access_token = resp.json().get("access_token", "")
        st.success("Logged in. Token saved.")
