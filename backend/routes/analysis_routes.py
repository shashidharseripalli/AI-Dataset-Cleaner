from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.services.dataset_service import analyze_dataset

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    csv_path: str


@router.post("/run")
async def run_analysis(payload: AnalysisRequest):
    csv_file = Path(payload.csv_path)
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    if csv_file.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        return await run_in_threadpool(analyze_dataset, str(csv_file))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
