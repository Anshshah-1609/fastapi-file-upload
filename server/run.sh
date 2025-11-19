#!/bin/bash
# Run script that ensures Poetry virtual environment is used

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first."
    echo "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
poetry install

# Run the application using Poetry's virtual environment
echo "Starting FastAPI application..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

