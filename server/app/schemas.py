""" Pydantic schemas for request/response validation. """

from datetime import datetime
from pydantic import BaseModel


class FileQueryParams(BaseModel):
    page: int = 1
    limit: int = 10
    search: str = ""


class FileResponse(BaseModel):
    """Response schema for file data."""
    id: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    content_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response schema for file list with pagination."""
    files: list[FileResponse]
    total: int
    page: int
    limit: int
    total_pages: int
