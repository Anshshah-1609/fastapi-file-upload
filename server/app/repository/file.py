"""Repository module for blog database operations."""

from __future__ import annotations

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
    files = query.offset(skip).limit(query_params.limit).all()

    return files, total


def get_by_id(db: Session, file_id: int):
    """Get a file by its ID."""
    return db.query(models.FileModel).filter(models.FileModel.id == file_id).first()


def create(db: Session, file: models.FileModel):
    """Create a new file."""
    db.add(file)
    db.commit()
    db.refresh(file)


def remove(db: Session, file_id: int):
    """Remove a file by its ID."""

    file = get_by_id(db, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    db.delete(file)
    db.commit()
    return file
