from typing import Any, Dict, List

import pandas as pd


def _safe_label(value: Any) -> str:
    if pd.isna(value):
        return "Missing"
    return str(value)


def _build_histograms(df: pd.DataFrame, numeric_columns: List[str]) -> List[Dict[str, Any]]:
    histograms: List[Dict[str, Any]] = []

    for column in numeric_columns:
        series = df[column].dropna()
        if series.empty:
            continue

        bins = pd.cut(series, bins=10, duplicates="drop")
        counts = bins.value_counts().sort_index()

        histograms.append(
            {
                "column": column,
                "bins": [str(interval) for interval in counts.index],
                "counts": [int(value) for value in counts.values],
            }
        )

    return histograms


def _build_pie_charts(df: pd.DataFrame, categorical_columns: List[str]) -> List[Dict[str, Any]]:
    pie_charts: List[Dict[str, Any]] = []

    for column in categorical_columns:
        counts = df[column].map(_safe_label).value_counts().head(10)
        if counts.empty:
            continue

        pie_charts.append(
            {
                "column": column,
                "labels": [str(label) for label in counts.index],
                "values": [int(value) for value in counts.values],
            }
        )

    return pie_charts


def _build_correlation_matrix(df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
    if len(numeric_columns) < 2:
        return {"columns": [], "matrix": []}

    corr_df = df[numeric_columns].corr(numeric_only=True).fillna(0.0).round(4)
    matrix = corr_df.reset_index().rename(columns={"index": "row"})

    return {
        "columns": list(corr_df.columns),
        "matrix": matrix.to_dict(orient="records"),
    }


def build_visualization_payload(csv_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number"]).columns.tolist()
    missing_counts = df.isna().sum()

    return {
        "summary": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
        },
        "charts": {
            "histograms": _build_histograms(df, numeric_columns),
            "missing_heatmap": {
                "columns": list(missing_counts.index),
                "missing_counts": [int(value) for value in missing_counts.values],
            },
            "pie_charts": _build_pie_charts(df, categorical_columns),
            "correlation_matrix": _build_correlation_matrix(df, numeric_columns),
        },
    }
