import logging

from fastapi import FastAPI
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool

from backend.database import db, models
from backend.routes import (
    analysis_router,
    auth_router,
    cleaning_router,
    dataset_router,
    upload_router,
    users_router,
)

app = FastAPI(title="AI Dataset Cleaner API")


def _ensure_sqlite_auth_columns():
    if not str(db.engine.url).startswith("sqlite"):
        return

    with db.engine.connect() as conn:
        table_info = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing_cols = {row[1] for row in table_info}
        if "hashed_password" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR"))
            conn.commit()


@app.on_event("startup")
async def on_startup():
    try:
        await run_in_threadpool(_ensure_sqlite_auth_columns)
        await run_in_threadpool(models.Base.metadata.create_all, db.engine)
    except Exception as exc:
        logging.warning(f"Could not create tables on startup: {exc}")


app.include_router(users_router)
app.include_router(dataset_router)
app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(cleaning_router)
app.include_router(auth_router)
