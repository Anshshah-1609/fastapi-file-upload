# File Upload Frontend

A React frontend application for uploading and managing CSV files, built with:

- **React** + **TypeScript** + **Vite**
- **TanStack Query** for API state management
- **shadcn/ui** for UI components
- **TailwindCSS** for styling
- **react-dropzone** for file uploads

## Features

- 📤 CSV file upload with drag & drop support
- 📋 File list table with pagination
- 👁️ View file details in a modal
- ✅ File validation (CSV only)
- 🎨 Modern, responsive UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update the API base URL in `.env` if your backend runs on a different port:
```
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

## API Endpoints

The frontend expects the following API endpoints:

- `POST /api/files/upload` - Upload a CSV file
- `GET /api/files/` - List files with pagination (query params: `page`, `limit`, `search`)
- `GET /api/files/{file_id}` - Get file details by ID

## Build

To build for production:
```bash
npm run build
```

The built files will be in the `dist` directory.
