import { useQuery } from "@tanstack/react-query";
import { fileApi } from "@/lib/api";

export const useGetFilePreview = (
  fileId: number | null,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ["file-preview", fileId],
    queryFn: () => {
      if (!fileId) throw new Error("File ID is required");
      return fileApi.getFilePreview(fileId, 10);
    },
    enabled: enabled && fileId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
