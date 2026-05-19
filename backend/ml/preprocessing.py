from typing import Any, Dict, List, Tuple

import pandas as pd


def fill_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    updated = df.copy()
    missing_before = int(updated.isna().sum().sum())

    for col in updated.columns:
        if pd.api.types.is_numeric_dtype(updated[col]):
            fill_value = updated[col].median()
            if pd.isna(fill_value):
                fill_value = 0
        else:
            mode_series = updated[col].mode(dropna=True)
            fill_value = mode_series.iloc[0] if not mode_series.empty else "unknown"
        updated[col] = updated[col].fillna(fill_value)

    missing_after = int(updated.isna().sum().sum())
    return updated, {
        "operation": "fill_missing_values",
        "missing_before": missing_before,
        "missing_after": missing_after,
        "filled_count": missing_before - missing_after,
    }


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    before = len(df)
    updated = df.drop_duplicates().reset_index(drop=True)
    after = len(updated)
    return updated, {
        "operation": "duplicate_removal",
        "rows_before": int(before),
        "rows_after": int(after),
        "removed_duplicates": int(before - after),
    }


def encode_categorical(df: pd.DataFrame, max_unique: int = 25) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    updated = df.copy()
    encoded_columns: List[str] = []

    cat_cols = updated.select_dtypes(include=["object", "string", "category"]).columns
    for col in cat_cols:
        unique_count = updated[col].nunique(dropna=True)
        if unique_count <= max_unique:
            updated[col] = updated[col].astype("category").cat.codes
            encoded_columns.append(col)

    return updated, {
        "operation": "encoding",
        "encoded_columns": encoded_columns,
        "encoded_count": len(encoded_columns),
        "rule": f"Encoded categorical columns with <= {max_unique} unique values.",
    }


def scale_numeric(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    updated = df.copy()
    scaled_columns: List[str] = []

    for col in updated.select_dtypes(include=["number"]).columns:
        col_min = updated[col].min()
        col_max = updated[col].max()
        if pd.isna(col_min) or pd.isna(col_max) or col_max == col_min:
            continue
        updated[col] = (updated[col] - col_min) / (col_max - col_min)
        scaled_columns.append(col)

    return updated, {
        "operation": "scaling",
        "scaled_columns": scaled_columns,
        "scaled_count": len(scaled_columns),
        "method": "min-max",
    }


def handle_outliers(df: pd.DataFrame, strategy: str = "clip_iqr") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    updated = df.copy()
    outlier_changes: Dict[str, int] = {}

    for col in updated.select_dtypes(include=["number"]).columns:
        q1 = updated[col].quantile(0.25)
        q3 = updated[col].quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (updated[col] < lower) | (updated[col] > upper)
        changed = int(mask.sum())
        if changed == 0:
            continue

        if strategy == "remove":
            updated = updated[~mask]
        else:
            updated[col] = updated[col].clip(lower=lower, upper=upper)

        outlier_changes[col] = changed

    updated = updated.reset_index(drop=True)
    return updated, {
        "operation": "outlier_handling",
        "strategy": strategy,
        "affected_columns": list(outlier_changes.keys()),
        "affected_cells": int(sum(outlier_changes.values())),
        "per_column": outlier_changes,
    }
