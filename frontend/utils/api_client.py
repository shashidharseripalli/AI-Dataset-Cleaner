from typing import Any

import requests
import streamlit as st

from utils.session import auth_headers


def _api_base() -> str:
    return st.session_state.get("api_base", "http://127.0.0.1:8000")


def show_response(resp: requests.Response) -> None:
    st.write(f"Status: `{resp.status_code}`")
    try:
        st.json(resp.json())
    except Exception:
        st.text(resp.text)


def get(path: str, timeout: int = 20) -> requests.Response:
    return requests.get(f"{_api_base()}{path}", headers=auth_headers(), timeout=timeout)


def post_json(path: str, payload: dict[str, Any], timeout: int = 20) -> requests.Response:
    return requests.post(
        f"{_api_base()}{path}",
        json=payload,
        headers=auth_headers(),
        timeout=timeout,
    )


def post_multipart(
    path: str,
    files: dict[str, Any],
    data: dict[str, Any],
    timeout: int = 60,
) -> requests.Response:
    return requests.post(
        f"{_api_base()}{path}",
        files=files,
        data=data,
        headers=auth_headers(),
        timeout=timeout,
    )
