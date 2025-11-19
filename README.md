# File Upload and Management System

A full-stack application for uploading, managing, and viewing CSV files. Built with FastAPI (Python) backend and React (TypeScript) frontend.

## Features

- 📤 **CSV File Upload**: Drag-and-drop or click to upload CSV files
- 📋 **File Management**: View, search, and manage uploaded files
- 🔍 **Search Functionality**: Search files by filename
- 📄 **Pagination**: Efficient file listing with pagination support
- 📊 **File Details**: View detailed information about each uploaded file
- 💾 **Database Storage**: PostgreSQL database for file metadata
- 🎨 **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## Tech Stack

### Backend

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **Uvicorn** - ASGI server
- **Poetry** - Dependency management

### Frontend

- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **React Dropzone** - File upload component

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm/yarn
- PostgreSQL database
- Poetry (for Python dependency management)

## Installation

### Backend Setup

1. Navigate to the server directory:

```bash
cd server
```

2. Install dependencies using Poetry:

```bash
poetry install
```

**Important:** This project uses Poetry for dependency management. All packages are installed in Poetry's virtual environment (`.venv`). Always use `poetry run` or activate the Poetry shell to ensure you're using the correct Python environment.

4. Create a `.env` file in the `server/app` directory with the following variables:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760
DEBUG=True
```

### Frontend Setup

1. Navigate to the client directory:

```bash
cd client
```

2. Install dependencies:

```bash
yarn install
# or
npm install
```

## Running the Application

### Start the Backend

From the `server` directory, you have several options:

**Option 1: Using the run script (Recommended)**

```bash
./run.sh
# or
python run.py
```

**Option 2: Using Poetry directly**

```bash
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: Using Poetry run (without activating shell)**

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

### Start the Frontend

From the `client` directory:

```bash
yarn dev
# or
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
file-upload-and-fixes/
├── server/                 # Backend application
│   ├── app/
│   │   ├── configs/        # Application configuration
│   │   ├── database/       # Database connection and setup
│   │   ├── logger/         # Logging configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repository/     # Data access layer
│   │   ├── routers/        # API routes
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── main.py         # FastAPI application entry point
│   ├── uploads/            # Uploaded files storage
│   └── pyproject.toml      # Python dependencies
│
└── client/                 # Frontend application
    ├── src/
    │   ├── components/     # React components
    │   ├── hooks/          # Custom React hooks
    │   ├── lib/            # Utility functions and API client
    │   └── App.tsx         # Main application component
    └── package.json        # Node.js dependencies
```

## API Endpoints

### File Upload

- `POST /api/files/upload` - Upload a CSV file
  - Request: Multipart form data with file
  - Response: File metadata including ID, filename, size, etc.

### File Listing

- `GET /api/files/` - List all files with pagination
  - Query Parameters:
    - `page` (int): Page number (default: 1)
    - `limit` (int): Items per page (default: 10, max: 100)
    - `search` (string): Search term for filename filtering

### File Details

- `GET /api/files/{file_id}` - Get file details by ID
  - Response: Complete file metadata

## Database Schema

The application uses a `files` table with the following structure:

- `id` (Integer, Primary Key)
- `original_filename` (String, 255) - Original filename from upload
- `stored_filename` (String, 255, Unique) - UUID-based stored filename
- `file_path` (String, 500) - Full path to stored file
- `file_size` (BigInteger) - File size in bytes
- `content_type` (String, 100) - MIME type
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

## Adding New Python Packages

**Important:** Always use Poetry to add new packages. This ensures packages are installed in the correct virtual environment and `pyproject.toml` is updated automatically.

### Using the Helper Script (Recommended)

```bash
cd server
./add_package.sh <package_name> [version_constraint]
```

Examples:

```bash
./add_package.sh requests
./add_package.sh pandas ">=2.0.0,<3.0.0"
```

### Using Poetry Directly

```bash
cd server
poetry add <package_name>
# or with version constraint
poetry add "<package_name>>=2.0.0,<3.0.0"
```

After adding a package, Poetry will:

- Install it in the virtual environment (`.venv`)
- Update `pyproject.toml`
- Update `poetry.lock`
- The helper script also updates `requirements.txt`

**Never install packages directly with `pip install`** - always use Poetry to maintain consistency.

## Development Notes

- The database tables are automatically created on application startup using `sync_database()`
- File uploads are validated for:
  - File type (must be CSV)
  - File size (default max: 10MB, configurable)
- Uploaded files are stored with UUID-based filenames to prevent conflicts
- The application uses SQLAlchemy ORM with a repository pattern for data access
- **Always use Poetry's virtual environment** - packages are installed in `.venv`, not system Python

## Environment Variables

| Variable          | Description                            | Default                 |
| ----------------- | -------------------------------------- | ----------------------- |
| `DB_HOST`         | PostgreSQL host                        | Required                |
| `DB_PORT`         | PostgreSQL port                        | Required                |
| `DB_NAME`         | Database name                          | Required                |
| `DB_USER`         | Database user                          | Required                |
| `DB_PASSWORD`     | Database password                      | Required                |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` |
| `UPLOAD_FOLDER`   | Directory for uploaded files           | `uploads`               |
| `MAX_FILE_SIZE`   | Maximum file size in bytes             | `10485760` (10MB)       |
| `DEBUG`           | Enable debug mode                      | `False`                 |

## License

This project is open source and available for educational purposes.

## Author

Ansh Shah
