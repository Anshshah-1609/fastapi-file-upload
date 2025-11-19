#!/usr/bin/env python3
"""
Run script that ensures the application uses Poetry's virtual environment.
This script automatically uses Poetry's Python interpreter.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the FastAPI application using Poetry."""
    script_dir = Path(__file__).parent

    # Check if Poetry is installed
    try:
        subprocess.run(
            ["poetry", "--version"],
            check=True,
            capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Poetry is not installed. Please install Poetry first.")
        print("Visit: https://python-poetry.org/docs/#installation")
        sys.exit(1)

    # Install dependencies if needed
    print("Checking dependencies...")
    subprocess.run(
        ["poetry", "install"],
        cwd=script_dir,
        check=True
    )

    # Run the application using Poetry's virtual environment
    print("Starting FastAPI application...")
    subprocess.run(
        [
            "poetry", "run", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ],
        cwd=script_dir,
        check=True
    )


if __name__ == "__main__":
    main()
