""" File model for database storage. """

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger

from app.database.connection import Base


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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<FileModel(id={self.id}, original_filename='{self.original_filename}', stored_filename='{self.stored_filename}')>"
