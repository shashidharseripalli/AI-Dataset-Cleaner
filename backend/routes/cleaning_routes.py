from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.services.cleaning_service import clean_dataset

router = APIRouter(prefix="/cleaning", tags=["cleaning"])


class CleaningRequest(BaseModel):
    csv_path: str
    operations: List[str] | None = None
    outlier_strategy: str = "clip_iqr"


def _normalize_csv_path(path_value: str) -> Path:
    normalized = path_value.strip().strip("'\"")
    return Path(normalized)


@router.post("/run")
async def run_cleaning(payload: CleaningRequest):
    csv_file = _normalize_csv_path(payload.csv_path)
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    if csv_file.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        return await run_in_threadpool(
            clean_dataset,
            str(csv_file),
            payload.operations,
            payload.outlier_strategy,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cleaning failed: {exc}") from exc
