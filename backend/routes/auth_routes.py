from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.auth.auth_handler import (
    authenticate_user,
    create_user_with_password,
    get_user_by_username,
)
from backend.auth.dependencies import get_current_user
from backend.auth.jwt_handler import create_access_token
from backend.database import db, models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.TokenResponse)
async def signup(payload: schemas.AuthSignup, db_session: Session = Depends(db.get_db)):
    existing = await run_in_threadpool(get_user_by_username, db_session, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = await run_in_threadpool(
        create_user_with_password,
        db_session,
        payload.username,
        payload.password,
    )
    token = create_access_token({"sub": str(user.id), "username": user.username})
    return schemas.TokenResponse(access_token=token)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.AuthLogin, db_session: Session = Depends(db.get_db)):
    user = await run_in_threadpool(
        authenticate_user,
        db_session,
        payload.username,
        payload.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.User)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
