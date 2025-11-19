"""Repository module for blog database operations."""

from __future__ import annotations
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.logger import get_logger

logger = get_logger(__name__)


def get_all(db: Session, query_params: schemas.FileQueryParams):
    """Get all files with optional search by filename."""
    skip = (query_params.page - 1) * query_params.limit
    query = db.query(models.FileModel)

    # Add search filter if search term is provided
    if query_params.search:
        query = query.filter(models.FileModel.original_filename.ilike(
            f"%{query_params.search}%"))

    total = query.count()
    files = query.order_by(models.FileModel.id.desc()).offset(
        skip).limit(query_params.limit).all()

    return files, total


def get_by_id(db: Session, file_id: int):
    """Get a file by its ID."""
    return db.query(models.FileModel).filter(models.FileModel.id == file_id).first()


def create(db: Session, file: models.FileModel):
    """Create a new file."""
    db.add(file)
    db.commit()
    db.refresh(file)


def remove(db: Session, file_id: int, delete_file_from_disk: bool = True):
    """
    Remove a file by its ID.

    Args:
        db: Database session
        file_id: ID of the file to remove
        delete_file_from_disk: If True, also delete the file from disk

    Returns:
        The deleted file model

    Raises:
        HTTPException: If file not found
    """
    file = get_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Delete file from disk if requested
    if delete_file_from_disk and file.file_path:
        try:
            file_path = Path(file.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file from disk: {file_path}")
            else:
                logger.warning(f"File not found on disk: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file from disk: {str(e)}")
            # Continue with database deletion even if file deletion fails

    # Delete from database
    db.delete(file)
    db.commit()
    return file


def get_by_reference(db: Session, file_reference: str):
    """Get a file by its reference (UUID)."""
    return db.query(models.FileModel).filter(
        models.FileModel.file_reference == file_reference
    ).first()


def update_null_count(db: Session, file_reference: str, null_count: int):
    """Update null_count for a file using its reference."""
    file = get_by_reference(db, file_reference)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with reference '{file_reference}' not found"
        )
    file.null_count = null_count
    db.commit()
    db.refresh(file)
    return file


def update_null_count_by_id(db: Session, file_id: int, null_count: int):
    """Update null_count for a file using its ID."""
    file = get_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found"
        )
    file.null_count = null_count
    db.commit()
    db.refresh(file)
    return file
