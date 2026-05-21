import json
from typing import Any, Dict


def build_dataset_explainer_prompt(analysis_result: Dict[str, Any]) -> str:
    compact = json.dumps(analysis_result, ensure_ascii=True)

    return f"""
You are a senior data scientist.

Given dataset analysis JSON below, return ONLY valid JSON with this schema:
{{
  "cleaning_reasoning": [
    "short bullet point",
    "short bullet point"
  ],
  "model_recommendation_reasoning": {{
    "recommended_task": "classification|regression|clustering|time_series|unknown",
    "recommended_models": ["model_a", "model_b"],
    "why": ["reason 1", "reason 2"]
  }},
  "dataset_insights": [
    "insight 1",
    "insight 2"
  ]
}}

Rules:
- Keep points practical and concise.
- Base reasoning on missing values, duplicates, dtypes, correlations, and dataset shape.
- Do not add markdown, no code fences, only JSON.

Dataset analysis:
{compact}
""".strip()
