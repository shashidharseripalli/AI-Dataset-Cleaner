import logging

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from backend.database import db, models
from backend.routes import analysis_router, dataset_router, upload_router, users_router

app = FastAPI(title="AI Dataset Cleaner API")


@app.on_event("startup")
async def on_startup():
    try:
        await run_in_threadpool(models.Base.metadata.create_all, db.engine)
    except Exception as exc:
        logging.warning(f"Could not create tables on startup: {exc}")


app.include_router(users_router)
app.include_router(dataset_router)
app.include_router(upload_router)
app.include_router(analysis_router)
