from typing import Any, Dict

import pandas as pd

from backend.ml.dataset_detector import detect_dataset_type


def _safe_float(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    return float(value)


def analyze_dataset(csv_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)

    missing_per_column = df.isna().sum().to_dict()
    null_percentages = ((df.isna().mean() * 100).round(2)).to_dict()
    duplicates_count = int(df.duplicated().sum())
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    unique_values = {col: int(df[col].nunique(dropna=True)) for col in df.columns}

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] >= 2:
        corr_df = numeric_df.corr(numeric_only=True).round(4).fillna(0.0)
        correlations = {
            row: {col: _safe_float(corr_df.loc[row, col]) for col in corr_df.columns}
            for row in corr_df.index
        }
    else:
        correlations = {}

    dataset_type_info = detect_dataset_type(df)

    return {
        "summary": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": list(df.columns),
        },
        "analysis": {
            "missing_values": {k: int(v) for k, v in missing_per_column.items()},
            "duplicates": duplicates_count,
            "null_percentages": {k: _safe_float(v) for k, v in null_percentages.items()},
            "data_types": dtypes,
            "correlations": correlations,
            "unique_values": unique_values,
        },
        "detected_task": dataset_type_info,
    }
