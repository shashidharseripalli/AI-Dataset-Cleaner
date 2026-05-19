from typing import Any, Dict

import pandas as pd


def detect_dataset_type(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty or df.shape[1] < 2:
        return {
            "task_type": "unknown",
            "confidence": 0.0,
            "reason": "Dataset has insufficient rows/columns for detection.",
        }

    n_rows, n_cols = df.shape
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    numeric_cols = df.select_dtypes(include=["number"]).columns

    # If most values are long text, assume NLP.
    if len(text_cols) > 0:
        sample_text = df[text_cols].astype(str).stack().head(500)
        avg_text_len = float(sample_text.str.len().mean()) if not sample_text.empty else 0.0
        if avg_text_len >= 30 and len(text_cols) >= max(1, n_cols // 3):
            return {
                "task_type": "nlp",
                "confidence": 0.85,
                "reason": "Dataset contains substantial long-form text features.",
            }

    # Heuristic: use last column as target candidate.
    target_col = df.columns[-1]
    target_series = df[target_col]
    unique_count = int(target_series.nunique(dropna=True))
    unique_ratio = unique_count / max(n_rows, 1)

    if target_col in numeric_cols:
        if unique_count <= 20 or unique_ratio <= 0.05:
            return {
                "task_type": "classification",
                "confidence": 0.8,
                "reason": "Numeric target appears categorical by cardinality.",
            }
        return {
            "task_type": "regression",
            "confidence": 0.8,
            "reason": "Numeric target appears continuous.",
        }

    if target_col in text_cols:
        if unique_count <= 50 or unique_ratio <= 0.2:
            return {
                "task_type": "classification",
                "confidence": 0.75,
                "reason": "Target-like column appears to be class labels.",
            }
        return {
            "task_type": "nlp",
            "confidence": 0.7,
            "reason": "High-cardinality text target suggests text generation/analysis.",
        }

    if len(numeric_cols) >= 2:
        return {
            "task_type": "clustering",
            "confidence": 0.65,
            "reason": "No clear target detected; numeric feature space suits clustering.",
        }

    return {
        "task_type": "unknown",
        "confidence": 0.4,
        "reason": "Heuristics could not confidently map to a learning task.",
    }
