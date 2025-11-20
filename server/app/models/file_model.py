""" File model for database storage. """

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, TypeDecorator, Text

from app.database.connection import Base


class JSONEncodedDict(TypeDecorator):
    """Custom type for storing JSON as Text in PostgreSQL."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class FileModel(Base):
    """ Model for storing file metadata. """

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), unique=True,
                             nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    content_type = Column(String(100), nullable=False)
    # UUID reference for updates
    file_reference = Column(String(36), unique=True, nullable=True, index=True)
    # Count of rows with null/undefined values
    null_count = Column(Integer, nullable=True, default=0)
    # Total number of rows in the CSV
    total_rows = Column(Integer, nullable=True)
    # Total number of columns in the CSV
    total_columns = Column(Integer, nullable=True)
    # Analysis time in seconds
    # Store as string to preserve precision
    analysis_time = Column(String(20), nullable=True)
    # Peak memory usage during analysis in MB
    # Store as string to preserve precision
    memory_usage_mb = Column(String(20), nullable=True)
    # Duplicate records count per column
    # Format: {"column_name": count, ...} e.g., {"email": 10, "phone": 22}
    duplicate_records = Column(JSONEncodedDict, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<FileModel(id={self.id}, original_filename='{self.original_filename}', stored_filename='{self.stored_filename}', file_reference='{self.file_reference}')>"
