from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.ml.dataset_detector import detect_dataset_type
from backend.ml.recommendation_engine import recommend_algorithms

router = APIRouter(prefix="/ml", tags=["ml"])


class RecommendationRequest(BaseModel):
    dataset_type: str | None = None
    feature_count: int | None = None
    target_column: str | None = None
    data_size: int | None = None
    csv_path: str | None = None


def _normalize_csv_path(path_value: str) -> Path:
    return Path(path_value.strip().strip("'\""))


@router.post("/recommend")
async def recommend(payload: RecommendationRequest):
    dataset_type = payload.dataset_type
    feature_count = payload.feature_count
    data_size = payload.data_size

    if payload.csv_path:
        csv_file = _normalize_csv_path(payload.csv_path)
        if not csv_file.exists():
            raise HTTPException(status_code=404, detail="CSV file not found")
        if csv_file.suffix.lower() != ".csv":
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        df = await run_in_threadpool(pd.read_csv, str(csv_file))
        detected = await run_in_threadpool(detect_dataset_type, df)
        dataset_type = detected.get("task_type", "unknown")
        feature_count = int(df.shape[1])
        data_size = int(df.shape[0])

    if dataset_type is None or feature_count is None or data_size is None:
        raise HTTPException(
            status_code=400,
            detail="Provide csv_path for auto-detection, or provide dataset_type, feature_count, and data_size.",
        )

    return await run_in_threadpool(
        recommend_algorithms,
        dataset_type,
        feature_count,
        payload.target_column,
        data_size,
    )
