import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = {".csv"}
ALLOWED_CONTENT_TYPES = {"text/csv", "application/vnd.ms-excel"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def validate_upload_file(file: UploadFile, file_bytes: bytes) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid content type for CSV upload")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")


def get_raw_upload_dir(project_root: Path) -> Path:
    return project_root / "uploads" / "raw"


def build_safe_filename(original_name: str) -> str:
    return f"{uuid.uuid4()}_{original_name}"

