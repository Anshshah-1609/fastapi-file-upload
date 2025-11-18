import {
  useCallback,
  useState,
  useEffect,
  useRef,
  startTransition,
} from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUploadFile } from "@/hooks/useFiles";
import { cn } from "@/lib/utils";

export const CSVDropzone = () => {
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const uploadFile = useUploadFile();
  const prevSuccessRef = useRef(false);

  // Show success message and hide it after 3 seconds
  useEffect(() => {
    const wasSuccess = prevSuccessRef.current;
    const isSuccess = uploadFile.isSuccess;

    // Only trigger when success transitions from false to true
    if (isSuccess && !wasSuccess) {
      startTransition(() => {
        setShowSuccess(true);
      });
      const timer = setTimeout(() => {
        setShowSuccess(false);
      }, 3000);

      prevSuccessRef.current = isSuccess;

      return () => {
        clearTimeout(timer);
      };
    }

    prevSuccessRef.current = isSuccess;
  }, [uploadFile.isSuccess]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setError(null);
      setShowSuccess(false);

      if (acceptedFiles.length === 0) {
        setError("No file selected");
        return;
      }

      const file = acceptedFiles[0];

      // Validate file extension
      if (!file.name.toLowerCase().endsWith(".csv")) {
        setError("Only CSV files are allowed");
        return;
      }

      try {
        await uploadFile.mutateAsync(file);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || "Failed to upload file");
      }
    },
    [uploadFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".csv"],
    },
    maxFiles: 1,
    onDropRejected: (fileRejections) => {
      if (fileRejections.length > 0) {
        const rejection = fileRejections[0];
        if (rejection.errors.some((e) => e.code === "file-invalid-type")) {
          setError("Only CSV files are allowed");
        } else {
          setError("File rejected. Please try again.");
        }
      }
    },
  });

  return (
    <div className="w-full space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50",
          uploadFile.isPending && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} disabled={uploadFile.isPending} />
        <div className="flex flex-col items-center justify-center gap-4">
          {uploadFile.isPending ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
              <p className="text-sm text-muted-foreground">Uploading...</p>
            </>
          ) : (
            <>
              <div className="rounded-full bg-primary/10 p-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">
                  {isDragActive
                    ? "Drop the CSV file here"
                    : "Drag & drop a CSV file here, or click to select"}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Only CSV files are accepted
                </p>
              </div>
              <Button type="button" variant="outline" size="sm">
                <FileText className="h-4 w-4" />
                Select CSV File
              </Button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {showSuccess && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-green-500/10 text-green-600 dark:text-green-400 text-sm">
          <FileText className="h-4 w-4" />
          <span>File uploaded successfully!</span>
        </div>
      )}
    </div>
  );
};
