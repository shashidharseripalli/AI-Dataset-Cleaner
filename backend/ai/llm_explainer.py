import json
import os
from typing import Any, Dict

import requests


class LLMExplainerError(Exception):
    pass


def _gemini_endpoint(model: str, api_key: str) -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )


def _extract_text(resp_json: Dict[str, Any]) -> str:
    try:
        return resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        raise LLMExplainerError(f"Unexpected Gemini response format: {resp_json}") from exc


def call_gemini(prompt: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    if not api_key:
        raise LLMExplainerError("Missing GEMINI_API_KEY")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1200},
    }

    response = requests.post(
        _gemini_endpoint(model, api_key),
        json=payload,
        timeout=60,
    )

    if response.status_code >= 400:
        raise LLMExplainerError(f"Gemini API error {response.status_code}: {response.text}")

    raw_text = _extract_text(response.json()).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "cleaning_reasoning": ["Model returned non-JSON output."],
            "model_recommendation_reasoning": {
                "recommended_task": "unknown",
                "recommended_models": [],
                "why": ["Could not parse model output as JSON."],
            },
            "dataset_insights": [raw_text[:800]],
        }
