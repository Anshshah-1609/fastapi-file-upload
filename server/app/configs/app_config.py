""" Application configuration from environment variables. """

import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class AppConfig:
    """ Application configuration class. """

    def __init__(self) -> None:
        """ Initialize the application configuration. """

        root_dir = Path(__file__).parent.parent
        env_path = root_dir / ".env"

        # Only load .env file if it exists (for local development)
        # In production, environment variables should be set directly by the deployment platform
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
        else:
            # Try to load from current directory as fallback
            load_dotenv(override=False)

        # Database configuration
        self.DB_HOST = self.get_os("DB_HOST")
        self.DB_PORT = int(self.get_os("DB_PORT"))
        self.DB_NAME = self.get_os("DB_NAME")
        self.DB_USER = self.get_os("DB_USER")
        self.DB_PASSWORD = self.get_os("DB_PASSWORD")
        self.ALLOWED_ORIGINS = self.get_os_optional(
            "ALLOWED_ORIGINS", "http://localhost:3000").split(",")

        # File upload configuration
        self.UPLOAD_FOLDER: str = self.get_os_optional(
            "UPLOAD_FOLDER", "uploads")

        # Create upload directory if it doesn't exist
        self.UPLOAD_DIR = Path(self.UPLOAD_FOLDER)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        self.MAX_FILE_SIZE: int = int(self.get_os_optional(
            "MAX_FILE_SIZE", "10485760"))  # 10 MB in bytes

        # Application configuration
        self.DEBUG: bool = self.get_os_optional(
            "DEBUG", "False").lower() == "true"

    @staticmethod
    def get_os(key: str) -> str:
        """Get an environment variable. Raises an error if not found.

        Args:
            key: The environment variable key

        Returns:
            The environment variable value

        Raises:
            ValueError: If the environment variable is not set
        """
        value = os.getenv(key)
        if value is None:
            error_msg = f"Environment variable '{key}' is not set"
            raise ValueError(error_msg)
        return value

    @staticmethod
    def get_os_optional(key: str, default: str | None = None) -> str:
        """Get an environment variable with an optional default value.

        Args:
            key: The environment variable key
            default: Optional default value if the key is not found

        Returns:
            The environment variable value or the default value
        """
        return os.getenv(key, default) if default is not None else os.getenv(key, "")


# Create a singleton instance
app_config = AppConfig()
