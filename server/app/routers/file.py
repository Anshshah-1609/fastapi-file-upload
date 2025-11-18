""" File upload router. """

import uuid
import math
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.configs import app_config
from app.database import get_db
from app.models import FileModel
from app import schemas
from app.repository import get_all, get_by_id, create, remove

router = APIRouter(prefix="/api/files", tags=["Files"])


def validate_csv_file(file: UploadFile) -> None:
    """ Validate that the uploaded file is a CSV file. """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension != ".csv":
        raise HTTPException(
            status_code=400,
            detail=f"Only CSV files are allowed. Received: {file_extension}"
        )

    # Check content type
    if file.content_type not in ["text/csv", "application/csv", "text/plain"]:
        # Some browsers might send different content types, so we'll be lenient
        # but still check the extension
        pass


def validate_file_size(file_size: int) -> None:
    """ Validate that the file size is less than the maximum allowed size. """
    if file_size > app_config.MAX_FILE_SIZE:
        max_size_mb = app_config.MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb} MB"
        )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file to the server.

    - Validates that the file is a CSV file
    - Validates that the file size is less than 10 MB
    - Saves the file with a UUID-based filename
    - Stores file metadata in the database
    """
    # Validate file type
    validate_csv_file(file)

    # Read file content to get size
    content = await file.read()
    file_size = len(content)

    # Validate file size
    validate_file_size(file_size)

    # Generate unique filename with UUID
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = app_config.UPLOAD_DIR / unique_filename

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except IOError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # Store file metadata in database using repository
    try:
        db_file = FileModel(
            original_filename=file.filename,
            stored_filename=unique_filename,
            file_path=str(file_path),
            file_size=file_size,
            content_type=file.content_type or "text/csv"
        )
        create(db, db_file)
    except Exception as e:
        # If database save fails, remove the file
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store file metadata in database: {str(e)}"
        )

    return {
        "message": "File uploaded successfully",
        "file_id": db_file.id,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_size": file_size,
        "file_path": str(file_path)
    }


@router.get("/", response_model=schemas.FileListResponse)
def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query("", description="Search term for filename"),
    db: Session = Depends(get_db)
):
    """
    List all files with pagination and optional search.

    - Supports pagination with page and limit parameters
    - Supports searching by original filename (case-insensitive)
    - Returns file list with pagination metadata
    """
    query_params = schemas.FileQueryParams(
        page=page, limit=limit, search=search)
    files, total = get_all(db, query_params)

    total_pages = math.ceil(total / limit) if total > 0 else 0

    return schemas.FileListResponse(
        files=[schemas.FileResponse.model_validate(file) for file in files],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{file_id}", response_model=schemas.FileResponse)
def get_file_by_id(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Get file details by ID.

    - Returns complete file metadata including original filename, stored filename,
      file path, size, content type, and timestamps
    - Returns 404 if file not found
    """
    file = get_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with ID {file_id} not found"
        )

    return schemas.FileResponse.model_validate(file)
