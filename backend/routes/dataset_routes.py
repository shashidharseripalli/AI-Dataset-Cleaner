from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.database import crud, db, schemas

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/", response_model=schemas.Dataset)
async def create_dataset(
    dataset: schemas.DatasetCreate,
    db_session: Session = Depends(db.get_db),
):
    owner = await run_in_threadpool(crud.get_user, db_session, dataset.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    return await run_in_threadpool(crud.create_dataset, db_session, dataset)


@router.get("/", response_model=List[schemas.Dataset])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(db.get_db),
):
    return await run_in_threadpool(crud.get_datasets, db_session, skip, limit)


@router.get("/{dataset_id}", response_model=schemas.Dataset)
async def get_dataset(dataset_id: int, db_session: Session = Depends(db.get_db)):
    db_dataset = await run_in_threadpool(crud.get_dataset, db_session, dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset


@router.put("/{dataset_id}", response_model=schemas.Dataset)
async def update_dataset(
    dataset_id: int,
    dataset_update: schemas.DatasetUpdate,
    db_session: Session = Depends(db.get_db),
):
    db_dataset = await run_in_threadpool(
        crud.update_dataset,
        db_session,
        dataset_id,
        dataset_update,
    )
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset


@router.delete("/{dataset_id}", response_model=schemas.Dataset)
async def delete_dataset(dataset_id: int, db_session: Session = Depends(db.get_db)):
    db_dataset = await run_in_threadpool(crud.delete_dataset, db_session, dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset
