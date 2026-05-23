from typing import Any, Dict

from backend.ai.llm_explainer import LLMExplainerError, call_gemini
from backend.ai.prompts import build_dataset_explainer_prompt
from backend.services.dataset_service import analyze_dataset


def _fallback_explanation(analysis_result: Dict[str, Any], reason: str) -> Dict[str, Any]:
    summary = analysis_result.get("summary", {})
    analysis = analysis_result.get("analysis", {})
    detected = analysis_result.get("detected_task", {})

    missing_values = analysis.get("missing_values", {})
    missing_columns = [column for column, count in missing_values.items() if count]
    duplicates = int(analysis.get("duplicates", 0))
    task_type = detected.get("task_type", "unknown")

    cleaning_reasoning = []
    if missing_columns:
        cleaning_reasoning.append(
            f"Missing values were found in {len(missing_columns)} column(s), so imputation or removal is needed."
        )
    else:
        cleaning_reasoning.append("No missing values were detected, so missing-value cleaning is minimal.")

    if duplicates:
        cleaning_reasoning.append(f"{duplicates} duplicate row(s) were detected and should be removed.")
    else:
        cleaning_reasoning.append("No duplicate rows were detected.")

    cleaning_reasoning.append("Encoding and scaling are useful before ML because the dataset may mix column types.")

    return {
        "cleaning_reasoning": cleaning_reasoning,
        "model_recommendation_reasoning": {
            "recommended_task": task_type,
            "recommended_models": [],
            "why": [
                detected.get("reason", "The task type was inferred from the dataset structure."),
                "Use the ML recommendation section for concrete model choices.",
            ],
        },
        "dataset_insights": [
            f"The dataset has {summary.get('rows', 0)} rows and {summary.get('columns', 0)} columns.",
            f"Detected task type is {task_type} with confidence {detected.get('confidence', 0)}.",
            "AI explanation is using local fallback because Gemini is not available.",
        ],
    }


def generate_ai_explanation(csv_path: str) -> Dict[str, Any]:
    analysis_result = analyze_dataset(csv_path)
    prompt = build_dataset_explainer_prompt(analysis_result)
    try:
        ai_output = call_gemini(prompt)
    except LLMExplainerError as exc:
        ai_output = _fallback_explanation(analysis_result, str(exc))

    return {
        "analysis_result": analysis_result,
        "ai_explanation": ai_output,
    }
