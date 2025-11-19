import {
  useCallback,
  useState,
  useEffect,
  useRef,
  startTransition,
} from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle, CheckCircle2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUploadFileWithSSE } from "@/hooks/useUploadFileWithSSE";
import { cn } from "@/lib/utils";
import { CSVReportModal } from "./CSVReportModal";
import { CountUp } from "./ui/countUp";
import { toast } from "sonner";

export const CSVDropzone = () => {
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [reportFileReference, setReportFileReference] = useState<string | null>(
    null
  );
  const uploadFileWithSSE = useUploadFileWithSSE();
  const prevSuccessRef = useRef(false);
  const prevFileReferenceRef = useRef<string | null>(null);

  // Show success message, open report, and show toast when upload completes
  useEffect(() => {
    const wasSuccess = prevSuccessRef.current;
    const progress = uploadFileWithSSE.progress;
    const isSuccess =
      progress?.status === "completed" && !uploadFileWithSSE.isUploading;

    // Only trigger when success transitions from false to true
    if (isSuccess && !wasSuccess && progress?.file_reference) {
      const fileReference = progress.file_reference;
      const originalFilename = progress.original_filename || "the file";

      // Show success toast
      toast.success("File uploaded and analyzed successfully", {
        description: `${originalFilename} has been processed and analyzed.`,
      });

      // Auto-open report modal using file_reference
      if (fileReference && fileReference !== prevFileReferenceRef.current) {
        prevFileReferenceRef.current = fileReference;
        // Use setTimeout to defer state update and avoid synchronous setState
        setTimeout(() => {
          setReportFileReference(fileReference);
        }, 0);
      }

      // Clear selected file on successful upload
      setTimeout(() => {
        setSelectedFile(null);
      }, 0);

      // Show success message
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
  }, [
    uploadFileWithSSE.progress?.status,
    uploadFileWithSSE.isUploading,
    uploadFileWithSSE.progress,
  ]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
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

    // Store the selected file instead of uploading immediately
    setSelectedFile(file);
  }, []);

  const handleUploadNow = useCallback(async () => {
    if (!selectedFile) return;

    setError(null);
    setShowSuccess(false);
    uploadFileWithSSE.reset();

    try {
      await uploadFileWithSSE.upload(selectedFile);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || "Failed to upload file");
      }
    }
  }, [selectedFile, uploadFileWithSSE]);

  const handleClearSelection = useCallback(() => {
    setSelectedFile(null);
    setError(null);
    setShowSuccess(false);
    uploadFileWithSSE.reset();
  }, [uploadFileWithSSE]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".csv"],
    },
    maxFiles: 1,
    disabled: uploadFileWithSSE.isUploading || !!selectedFile,
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

  const progress = uploadFileWithSSE.progress;
  const progressPercentage = progress ? Math.round(progress.progress * 100) : 0;
  const isUploading = uploadFileWithSSE.isUploading;
  const isCompleted = progress?.status === "completed";
  const isError = progress?.status === "error";

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="w-full space-y-4">
      {!selectedFile && !isUploading && (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center gap-4">
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
          </div>
        </div>
      )}

      {/* Selected File Preview */}
      {selectedFile && !isUploading && (
        <div className="border rounded-lg p-4 bg-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearSelection}
              >
                <X className="h-4 w-4 mr-1" />
                Clear Selection
              </Button>
              <Button variant="default" size="sm" onClick={handleUploadNow}>
                <Upload className="h-4 w-4 mr-1" />
                Upload Now
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Uploading State */}
      {isUploading && (
        <div className="border-2 border-dashed rounded-lg p-8 text-center">
          <div className="flex flex-col items-center justify-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            <p className="text-sm text-muted-foreground">
              {progress?.message || "Processing..."}
            </p>
          </div>
        </div>
      )}

      {/* Progress Bar and Statistics */}
      {isUploading && progress && (
        <div className="space-y-3 p-4 border rounded-lg bg-muted/50">
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium">
                {progress.status === "uploading"
                  ? "Uploading..."
                  : progress.status === "analyzing"
                  ? "Analyzing CSV..."
                  : "Processing..."}
              </span>
              <span className="text-muted-foreground">
                {progressPercentage}%
              </span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2.5">
              <div
                className={cn(
                  "h-2.5 rounded-full transition-all duration-300",
                  isError
                    ? "bg-destructive"
                    : isCompleted
                    ? "bg-green-500"
                    : "bg-primary"
                )}
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>

          {/* Statistics */}
          {progress.status === "analyzing" && (
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Records Checked</p>
                <p className="font-semibold">
                  {progress.processed_count?.toLocaleString() || 0}
                  {progress.total_rows
                    ? ` / ${progress.total_rows.toLocaleString()}`
                    : ""}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Missing Values</p>
                <p className="font-semibold text-orange-600 dark:text-orange-400">
                  <CountUp targetNumber={progress.null_count || 0} />
                </p>
              </div>
            </div>
          )}

          {progress.status === "completed" && (
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Total Records</p>
                <p className="font-semibold">
                  {progress.total_rows?.toLocaleString() || 0}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Missing Values</p>
                <p className="font-semibold text-orange-600 dark:text-orange-400">
                  <CountUp targetNumber={progress.null_count || 0} />
                </p>
              </div>
            </div>
          )}

          {progress.message && (
            <p className="text-sm text-muted-foreground">{progress.message}</p>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          <AlertCircle className="h-4 w-4" />
          <p className="text-sm text-red-500">{error}</p>
        </div>
      )}

      {showSuccess && (
        <div className="flex items-center justify-between gap-2 p-3 rounded-md bg-green-500/10 text-green-600 dark:text-green-400 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>File uploaded and analyzed successfully!</span>
            {progress?.null_count !== undefined && (
              <span className="ml-2">
                Found {progress.null_count} record(s) with null/undefined
                values.
              </span>
            )}
          </div>
          {progress?.file_reference && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setReportFileReference(progress.file_reference!)}
              className="h-7 text-xs"
            >
              <FileText className="h-3 w-3 mr-1" />
              View Report
            </Button>
          )}
        </div>
      )}

      {reportFileReference && (
        <CSVReportModal
          fileReference={reportFileReference}
          onClose={() => setReportFileReference(null)}
        />
      )}
    </div>
  );
};
