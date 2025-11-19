import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fileApi } from "@/lib/api";

export const useFiles = ({
  page = 1,
  limit = 10,
  search = "",
}: {
  page?: number;
  limit?: number;
  search?: string;
}) => {
  return useQuery({
    queryKey: ["files", page, limit, search],
    queryFn: () => fileApi.getFiles({ page, limit, search }),
  });
};

export const useUploadFile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: fileApi.uploadFile,
    onSuccess: () => {
      // Invalidate and refetch files list
      queryClient.invalidateQueries({ queryKey: ["files"] });
    },
  });
};
