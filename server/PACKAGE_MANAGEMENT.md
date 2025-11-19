# Package Management Guide

## Problem Fixed

Previously, when new packages were added to `pyproject.toml`, they weren't available when running the application because:

1. Packages were installed in Poetry's virtual environment (`.venv`)
2. The application was running with system Python instead of Poetry's Python
3. There was no clear process for adding new packages

## Solution

### 1. Fixed `pyproject.toml`

- Converted to proper Poetry format
- Set `package-mode = false` (since this is an application, not a library)
- Fixed README path reference

### 2. Created Helper Scripts

#### `run.sh` / `run.py`

- Automatically uses Poetry's virtual environment
- Installs dependencies if needed
- Runs the application correctly

#### `add_package.sh`

- Helper script to add new packages
- Automatically updates `requirements.txt`
- Ensures packages are installed in the correct environment

### 3. Updated Documentation

- Added clear instructions in README.md
- Documented multiple ways to run the application
- Added package management section

## How to Add New Packages

### Method 1: Using Helper Script (Recommended)

```bash
cd server
./add_package.sh <package_name> [version_constraint]
```

Example:

```bash
./add_package.sh requests
./add_package.sh pandas ">=2.0.0,<3.0.0"
```

### Method 2: Using Poetry Directly

```bash
cd server
poetry add <package_name>
```

Then manually update requirements.txt:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## How to Run the Application

### Method 1: Using Run Script (Recommended)

```bash
cd server
./run.sh
# or
python run.py
```

### Method 2: Using Poetry Shell

```bash
cd server
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Using Poetry Run

```bash
cd server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Important Notes

1. **Never use `pip install` directly** - Always use Poetry
2. **Always use `poetry run` or activate Poetry shell** - This ensures you're using the correct Python environment
3. **Packages are installed in `.venv`** - Not in system Python
4. **After adding packages, restart the application** - To load new modules

## Verification

To verify packages are installed correctly:

```bash
cd server
poetry run python -c "import pandas; print('✓ Working')"
```

To check which Python is being used:

```bash
cd server
poetry run python -c "import sys; print(sys.executable)"
```

This should show: `/path/to/server/.venv/bin/python`
