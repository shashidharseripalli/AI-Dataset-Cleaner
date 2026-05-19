from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.database import crud, db, schemas
from backend.services import file_service

router = APIRouter(prefix="/datasets", tags=["uploads"])


@router.post("/upload", response_model=schemas.FileUploadResponse)
async def upload_dataset_file(
    owner_id: int = Form(...),
    dataset_name: str | None = Form(None),
    description: str | None = Form(None),
    file: UploadFile = File(...),
    db_session: Session = Depends(db.get_db),
):
    owner = await run_in_threadpool(crud.get_user, db_session, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")

    file_bytes = await file.read()
    file_service.validate_upload_file(file, file_bytes)

    project_root = Path(__file__).resolve().parent.parent.parent
    upload_dir = file_service.get_raw_upload_dir(project_root)
    await run_in_threadpool(lambda: upload_dir.mkdir(parents=True, exist_ok=True))

    safe_name = file_service.build_safe_filename(file.filename)
    save_path = upload_dir / safe_name

    def _write_file():
        with save_path.open("wb") as buffer:
            buffer.write(file_bytes)

    await run_in_threadpool(_write_file)
    size_bytes = await run_in_threadpool(lambda: save_path.stat().st_size)
    inferred_name = Path(file.filename).stem
    dataset_input = schemas.DatasetCreate(
        name=dataset_name or inferred_name,
        description=description,
        owner_id=owner_id,
    )
    db_dataset = await run_in_threadpool(crud.create_dataset, db_session, dataset_input)
    if not db_dataset:
        raise HTTPException(status_code=500, detail="Could not store dataset metadata")

    return schemas.FileUploadResponse(
        dataset_id=db_dataset.id,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        saved_path=str(save_path),
        owner_id=owner_id,
    )
