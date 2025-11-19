""" Routers for the application. """

from .file import router as file_router
from .file_upload import router as file_upload_router

__all__ = ["file_router", "file_upload_router"]
