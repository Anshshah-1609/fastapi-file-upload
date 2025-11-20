""" Pydantic schemas for request/response validation. """

from datetime import datetime
from typing import Dict
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
    file_reference: str | None = None
    null_count: int | None = None
    total_rows: int | None = None
    total_columns: int | None = None
    analysis_time: str | None = None  # Time in seconds as string
    # Format: {"column_name": count}
    duplicate_records: Dict[str, int] | None = None
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


class FileUploadProgressResponse(BaseModel):
    """Response schema for file upload progress via SSE."""
    status: str  # "uploading", "analyzing", "completed", "error"
    progress: float  # 0.0 to 1.0
    message: str
    file_id: int | None = None
    file_reference: str | None = None  # UUID reference for updating null_count
    original_filename: str | None = None
    stored_filename: str | None = None
    file_size: int | None = None
    file_path: str | None = None
    null_count: int | None = None  # Count of rows with null/undefined values
    processed_count: int | None = None  # Number of rows processed so far
    total_rows: int | None = None  # Total number of rows in CSV
    total_columns: int | None = None  # Total number of columns in CSV
    # Duplicate counts per column
    duplicate_records: Dict[str, int] | None = None
    time_consumption: float | None = None  # Time taken in seconds


class UpdateNullCountRequest(BaseModel):
    """Request schema for updating null_count."""
    null_count: int


class UpdateNullCountResponse(BaseModel):
    """Response schema for null_count update."""
    message: str
    file_id: int
    file_reference: str
    null_count: int


class CSVReportResponse(BaseModel):
    """Response schema for CSV analysis report."""
    file_id: int
    original_filename: str
    file_size: int
    total_records: int
    total_columns: int
    null_records: int
    # Format: {"column_name": count}
    duplicate_records: Dict[str, int] | None = None
    time_consumption: str  # Time in seconds as string
    created_at: datetime


class CSVPreviewResponse(BaseModel):
    """Response schema for CSV preview (first 10 records)."""
    file_id: int
    columns: list[str]  # Column names
    records: list[Dict[str, str | None]]  # First 10 records as dictionaries
    total_rows: int  # Total number of rows in the CSV
    preview_count: int  # Number of records in preview (max 10)
