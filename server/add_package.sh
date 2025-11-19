#!/bin/bash
# Helper script to add new Python packages using Poetry
# Usage: ./add_package.sh <package_name> [version_constraint]
# Example: ./add_package.sh pandas ">=2.0.0,<3.0.0"

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <package_name> [version_constraint]"
    echo "Example: $0 pandas '>=2.0.0,<3.0.0'"
    echo "Example: $0 requests"
    exit 1
fi

PACKAGE_NAME="$1"
VERSION="${2:-}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first."
    exit 1
fi

echo "Adding package: $PACKAGE_NAME${VERSION:+ ($VERSION)}"

# Add the package using Poetry
if [ -n "$VERSION" ]; then
    poetry add "${PACKAGE_NAME}${VERSION}"
else
    poetry add "$PACKAGE_NAME"
fi

# Update requirements.txt
echo "Updating requirements.txt..."
poetry export -f requirements.txt --output requirements.txt --without-hashes

echo "✓ Package $PACKAGE_NAME added successfully!"
echo "✓ Dependencies installed in Poetry virtual environment"
echo "✓ requirements.txt updated"

