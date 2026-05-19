import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.database import crud, db, schemas

router = APIRouter(prefix="/datasets", tags=["uploads"])


@router.post("/upload", response_model=schemas.FileUploadResponse)
async def upload_dataset_file(
    owner_id: int = Form(...),
    file: UploadFile = File(...),
    db_session: Session = Depends(db.get_db),
):
    owner = await run_in_threadpool(crud.get_user, db_session, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    await run_in_threadpool(lambda: upload_dir.mkdir(parents=True, exist_ok=True))

    safe_name = f"{uuid.uuid4()}_{file.filename}"
    save_path = upload_dir / safe_name

    file_bytes = await file.read()

    def _write_file():
        with save_path.open("wb") as buffer:
            buffer.write(file_bytes)

    await run_in_threadpool(_write_file)
    size_bytes = await run_in_threadpool(lambda: save_path.stat().st_size)

    return schemas.FileUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        saved_path=str(save_path),
        owner_id=owner_id,
    )
