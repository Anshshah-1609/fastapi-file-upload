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
  file_reference: string | null;
  null_count?: number | null;
  total_rows?: number | null;
  total_columns?: number | null;
  analysis_time?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CSVReportResponse {
  file_id: number;
  original_filename: string;
  file_size: number;
  total_records: number;
  total_columns: number;
  null_records: number;
  duplicate_records?: Record<string, number> | null;
  time_consumption: string;
  created_at: string;
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

export interface SSEUploadProgress {
  status: "uploading" | "analyzing" | "completed" | "error";
  progress: number; // 0.0 to 1.0
  message: string;
  file_id?: number;
  file_reference?: string;
  original_filename?: string;
  stored_filename?: string;
  file_size?: number;
  file_path?: string;
  null_count?: number;
  processed_count?: number;
  total_rows?: number;
  total_columns?: number;
  time_consumption?: number;
}

export interface CSVPreviewResponse {
  file_id: number;
  columns: string[];
  records: Record<string, string | null>[];
  total_rows: number;
  preview_count: number;
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

  getFileReportByReference: async (
    fileReference: string
  ): Promise<CSVReportResponse> => {
    const response = await api.get<CSVReportResponse>(
      `/api/files/reference/${fileReference}/report`
    );
    return response.data;
  },

  getFilePreview: async (
    fileId: number,
    limit: number = 10
  ): Promise<CSVPreviewResponse> => {
    const response = await api.get<CSVPreviewResponse>(
      `/api/files/${fileId}/preview`,
      {
        params: { limit },
      }
    );
    return response.data;
  },

  deleteFile: async (
    fileId: number
  ): Promise<{
    message: string;
    file_id: number;
    original_filename: string;
    stored_filename: string;
  }> => {
    const response = await api.delete<{
      message: string;
      file_id: number;
      original_filename: string;
      stored_filename: string;
    }>(`/api/files/${fileId}`);
    return response.data;
  },

  uploadFileWithSSE: async (
    file: File,
    updateInterval: number = 0.5,
    onProgress: (progress: SSEUploadProgress) => void
  ): Promise<SSEUploadProgress> => {
    const formData = new FormData();
    formData.append("file", file);

    const url = `${API_BASE_URL}/api/files/upload-sse?update_interval=${updateInterval}`;

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let lastEvent: SSEUploadProgress | null = null;

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.substring(6)) as SSEUploadProgress;
            lastEvent = data;
            onProgress(data);

            if (data.status === "completed") {
              return data;
            } else if (data.status === "error") {
              throw new Error(data.message);
            }
          } catch (e) {
            // Ignore JSON parse errors for incomplete chunks
            if (
              e instanceof Error &&
              e.message !== "Unexpected end of JSON input"
            ) {
              throw e;
            }
          }
        }
      }
    }

    // Process remaining buffer
    if (buffer.startsWith("data: ")) {
      const data = JSON.parse(buffer.substring(6)) as SSEUploadProgress;
      lastEvent = data;
      onProgress(data);

      if (data.status === "completed") {
        return data;
      } else if (data.status === "error") {
        throw new Error(data.message);
      }
    }

    if (lastEvent) {
      return lastEvent;
    }

    throw new Error("Upload completed without final event");
  },
};
