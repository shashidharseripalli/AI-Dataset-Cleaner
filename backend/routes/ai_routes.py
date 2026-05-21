from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.ai.dataset_chat import generate_ai_explanation

router = APIRouter(prefix="/ai", tags=["ai"])


class AIExplainRequest(BaseModel):
    csv_path: str


def _normalize_csv_path(path_value: str) -> Path:
    normalized = path_value.strip().strip("'\"")
    return Path(normalized)


@router.post("/explain")
async def explain_dataset(payload: AIExplainRequest):
    csv_file = _normalize_csv_path(payload.csv_path)

    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    if csv_file.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        return await run_in_threadpool(generate_ai_explanation, str(csv_file))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI explanation failed: {exc}") from exc
