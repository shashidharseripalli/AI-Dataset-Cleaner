from fastapi import APIRouter
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.ml.recommendation_engine import recommend_algorithms

router = APIRouter(prefix="/ml", tags=["ml"])


class RecommendationRequest(BaseModel):
    dataset_type: str
    feature_count: int
    target_column: str | None = None
    data_size: int


@router.post("/recommend")
async def recommend(payload: RecommendationRequest):
    return await run_in_threadpool(
        recommend_algorithms,
        payload.dataset_type,
        payload.feature_count,
        payload.target_column,
        payload.data_size,
    )
