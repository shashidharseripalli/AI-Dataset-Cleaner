from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/download", tags=["download"])


def _processed_files_dir() -> Path:
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "cleaned" / "processed_files"


def _resolve_cleaned_file(file_path: str) -> Path:
    cleaned_dir = _processed_files_dir().resolve()
    requested_path = Path(file_path.strip().strip("'\""))

    if not requested_path.is_absolute():
        requested_path = cleaned_dir / requested_path

    resolved_path = requested_path.resolve()

    if cleaned_dir not in resolved_path.parents and resolved_path != cleaned_dir:
        raise HTTPException(status_code=400, detail="File must be inside cleaned/processed_files")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="Cleaned file not found")
    if not resolved_path.is_file():
        raise HTTPException(status_code=400, detail="Requested path is not a file")
    if resolved_path.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV downloads are supported")

    return resolved_path


@router.get("/cleaned")
async def download_cleaned_file(file_path: str = Query(..., description="Cleaned CSV path or filename")):
    cleaned_file = _resolve_cleaned_file(file_path)
    return FileResponse(
        path=cleaned_file,
        media_type="text/csv",
        filename=cleaned_file.name,
    )


@router.get("/cleaned/{filename}")
async def download_cleaned_file_by_name(filename: str):
    cleaned_file = _resolve_cleaned_file(filename)
    return FileResponse(
        path=cleaned_file,
        media_type="text/csv",
        filename=cleaned_file.name,
    )
