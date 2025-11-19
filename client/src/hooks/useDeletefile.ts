import { fileApi } from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";

export const useDeleteFile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: fileApi.deleteFile,
    onSuccess: () => {
      // Invalidate and refetch files list
      queryClient.invalidateQueries({ queryKey: ["files"] });
    },
  });
};
