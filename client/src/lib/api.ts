import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface FileResponse {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_path: string;
  file_size: number;
  content_type: string;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  files: FileResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface UploadResponse {
  message: string;
  file_id: number;
  original_filename: string;
  stored_filename: string;
  file_size: number;
  file_path: string;
}

export const fileApi = {
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post<UploadResponse>(
      "/api/files/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  getFiles: async ({
    page = 1,
    limit = 10,
    search = "",
  }: {
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<FileListResponse> => {
    const response = await api.get<FileListResponse>("/api/files/", {
      params: { page, limit, search },
    });
    return response.data;
  },

  getFileById: async (fileId: number): Promise<FileResponse> => {
    const response = await api.get<FileResponse>(`/api/files/${fileId}`);
    return response.data;
  },
};
