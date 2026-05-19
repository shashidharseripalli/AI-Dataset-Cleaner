import streamlit as st

from utils.api_client import post_json, show_response
from utils.session import init_session_state

st.set_page_config(page_title="Signup", layout="wide")
init_session_state()

st.title("Signup")

username = st.text_input("Username", key="signup_username")
password = st.text_input("Password", type="password", key="signup_password")

if st.button("Signup"):
    resp = post_json("/auth/signup", {"username": username, "password": password})
    show_response(resp)
    if resp.ok:
        st.session_state.access_token = resp.json().get("access_token", "")
        st.success("Signup successful. Token saved.")
