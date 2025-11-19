import { fileApi } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export const useGetFileByReference = (fileReference: string) => {
  const {
    data: report,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["file-report", fileReference],
    queryFn: () => {
      if (fileReference) {
        return fileApi.getFileReportByReference(fileReference);
      }

      return null;
    },
    enabled: !!fileReference,
  });

  return {
    data: report,
    isLoading,
    isError,
    error,
  };
};
