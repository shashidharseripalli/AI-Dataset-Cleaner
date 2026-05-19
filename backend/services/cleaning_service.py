from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from backend.ml import preprocessing


DEFAULT_OPERATIONS = [
    "fill_missing_values",
    "duplicate_removal",
    "encoding",
    "scaling",
    "outlier_handling",
]


def clean_dataset(
    csv_path: str,
    operations: List[str] | None = None,
    outlier_strategy: str = "clip_iqr",
) -> Dict[str, Any]:
    source_path = Path(csv_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    if source_path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")

    df = pd.read_csv(source_path)
    selected_ops = operations or DEFAULT_OPERATIONS
    report_steps: List[Dict[str, Any]] = []
    cleaned_df = df.copy()

    op_map = {
        "fill_missing_values": preprocessing.fill_missing_values,
        "duplicate_removal": preprocessing.remove_duplicates,
        "encoding": preprocessing.encode_categorical,
        "scaling": preprocessing.scale_numeric,
    }

    for op_name in selected_ops:
        if op_name == "outlier_handling":
            cleaned_df, step_report = preprocessing.handle_outliers(
                cleaned_df,
                strategy=outlier_strategy,
            )
            report_steps.append(step_report)
            continue

        op_fn = op_map.get(op_name)
        if not op_fn:
            report_steps.append(
                {
                    "operation": op_name,
                    "status": "skipped",
                    "reason": "Unknown cleaning operation.",
                }
            )
            continue

        cleaned_df, step_report = op_fn(cleaned_df)
        report_steps.append(step_report)

    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / "cleaned" / "processed_files"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = f"{source_path.stem}_cleaned.csv"
    output_path = output_dir / output_name
    cleaned_df.to_csv(output_path, index=False)

    cleaning_report = {
        "input_file": str(source_path),
        "output_file": str(output_path),
        "operations_selected": selected_ops,
        "rows_before": int(df.shape[0]),
        "rows_after": int(cleaned_df.shape[0]),
        "columns_before": int(df.shape[1]),
        "columns_after": int(cleaned_df.shape[1]),
        "steps": report_steps,
    }

    return {
        "cleaned_file_path": str(output_path),
        "cleaning_report": cleaning_report,
    }
