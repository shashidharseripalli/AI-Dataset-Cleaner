from typing import Any, Dict

from backend.ai.llm_explainer import call_gemini
from backend.ai.prompts import build_dataset_explainer_prompt
from backend.services.dataset_service import analyze_dataset


def generate_ai_explanation(csv_path: str) -> Dict[str, Any]:
    analysis_result = analyze_dataset(csv_path)
    prompt = build_dataset_explainer_prompt(analysis_result)
    ai_output = call_gemini(prompt)

    return {
        "analysis_result": analysis_result,
        "ai_explanation": ai_output,
    }
