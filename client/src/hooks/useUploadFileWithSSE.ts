import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { fileApi, type SSEUploadProgress } from "@/lib/api";

export const useUploadFileWithSSE = () => {
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState<SSEUploadProgress | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const upload = useCallback(
    async (file: File, updateInterval: number = 0.5) => {
      setIsUploading(true);
      setProgress(null);

      try {
        const result = await fileApi.uploadFileWithSSE(
          file,
          updateInterval,
          (progressData) => {
            setProgress(progressData);
          }
        );

        // Invalidate and refetch files list on success
        if (result.status === "completed") {
          queryClient.invalidateQueries({ queryKey: ["files"] });
        }

        return result;
      } finally {
        setIsUploading(false);
      }
    },
    [queryClient]
  );

  const reset = useCallback(() => {
    setProgress(null);
    setIsUploading(false);
  }, []);

  return { upload, progress, isUploading, reset };
};
