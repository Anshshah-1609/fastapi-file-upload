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
from app.logger import get_logger
from app.repository import (
    get_all,
    get_by_id,
    get_by_reference,
    create,
    remove,
    update_null_count,
    update_null_count_by_id
)

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


@router.get("/reference/{file_reference}/report", response_model=schemas.CSVReportResponse)
def get_file_report_by_reference(
    file_reference: str,
    db: Session = Depends(get_db)
):
    """
    Get CSV analysis report for a file by reference (UUID).

    - Uses file_reference (UUID) to identify the file
    - Returns analysis report including time consumption, total records,
      file name, file size, total columns, null records, and duplicate records
    - Returns 404 if file not found
    - Returns 400 if file has not been analyzed yet
    """
    file = get_by_reference(db, file_reference)
    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File with reference '{file_reference}' not found"
        )

    # Check if file has been analyzed
    if file.null_count is None or file.total_rows is None or file.total_columns is None or file.analysis_time is None:
        raise HTTPException(
            status_code=400,
            detail="File has not been analyzed yet. Please upload the file with analysis enabled."
        )

    return schemas.CSVReportResponse(
        file_id=file.id,
        original_filename=file.original_filename,
        file_size=file.file_size,
        total_records=file.total_rows if file.total_rows is not None else 0,
        total_columns=file.total_columns if file.total_columns is not None else 0,
        null_records=file.null_count if file.null_count is not None else 0,
        duplicate_records=file.duplicate_records if file.duplicate_records else {},
        time_consumption=file.analysis_time,
        created_at=file.created_at
    )


# @router.patch("/reference/{file_reference}/null-count", response_model=schemas.UpdateNullCountResponse)
# def update_file_null_count(
#     file_reference: str,
#     request: schemas.UpdateNullCountRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Update null_count for a file using its reference (UUID).

#     - Uses file_reference (UUID) to identify the file
#     - Updates the null_count in the database
#     - Returns updated file information

#     This endpoint allows updating null_count without exposing the file ID.
#     """
#     file = update_null_count(db, file_reference, request.null_count)

#     return schemas.UpdateNullCountResponse(
#         message="Null count updated successfully",
#         file_id=file.id,
#         file_reference=file.file_reference,
#         null_count=file.null_count
#     )


# @router.patch("/{file_id}/null-count", response_model=schemas.UpdateNullCountResponse)
# def update_file_null_count_by_id(
#     file_id: int,
#     request: schemas.UpdateNullCountRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Update null_count for a file using its ID.

#     - Uses file_id to identify the file
#     - Updates the null_count in the database
#     - Returns updated file information
#     """
#     file = update_null_count_by_id(db, file_id, request.null_count)

#     return schemas.UpdateNullCountResponse(
#         message="Null count updated successfully",
#         file_id=file.id,
#         file_reference=file.file_reference or "",
#         null_count=file.null_count
#     )


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a file by its ID.

    - Deletes the file from the uploads folder (disk)
    - Deletes the file record from the database
    - Returns 404 if file not found
    - Returns success message on successful deletion

    Note: If file deletion from disk fails, the database record will still be deleted.
    """
    try:
        deleted_file = remove(db, file_id, delete_file_from_disk=True)

        return {
            "message": "File deleted successfully",
            "file_id": deleted_file.id,
            "original_filename": deleted_file.original_filename,
            "stored_filename": deleted_file.stored_filename
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 404)
        raise e
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
