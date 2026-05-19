from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.database import crud, db, schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db_session: Session = Depends(db.get_db)):
    existing = await run_in_threadpool(
        crud.get_user_by_username,
        db_session,
        user.username,
    )
    if existing:
        raise HTTPException(status_code=400, detail="username already exists")
    return await run_in_threadpool(crud.create_user, db_session, user)


@router.get("/", response_model=List[schemas.User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(db.get_db),
):
    return await run_in_threadpool(crud.get_users, db_session, skip, limit)


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db_session: Session = Depends(db.get_db)):
    db_user = await run_in_threadpool(crud.get_user, db_session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db_session: Session = Depends(db.get_db),
):
    db_user = await run_in_threadpool(crud.get_user, db_session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.username:
        existing = await run_in_threadpool(
            crud.get_user_by_username,
            db_session,
            user_update.username,
        )
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="username already exists")
    return await run_in_threadpool(crud.update_user, db_session, user_id, user_update)


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db_session: Session = Depends(db.get_db)):
    db_user = await run_in_threadpool(crud.delete_user, db_session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
