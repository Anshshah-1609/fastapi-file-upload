import { useState } from "react";
import { Eye, ChevronLeft, ChevronRight, FileText, Trash2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useFiles } from "@/hooks/useFiles";
import { useDeleteFile } from "@/hooks/useDeletefile";
import { formatDateTime } from "@/lib/date-utils";
import type { FileResponse } from "@/lib/api";
import { FileDetailsModal } from "./FileDetailsModal";
import { CSVReportModal } from "./CSVReportModal";
import { DeleteFileDialog } from "./DeleteFileDialog";
import { formatFileSize } from "@/lib/utils";
import { toast } from "sonner";

export const FileListTable = () => {
  const [page, setPage] = useState(1);
  const [selectedFile, setSelectedFile] = useState<FileResponse | null>(null);
  const [reportFileReference, setReportFileReference] = useState<string | null>(
    null
  );
  const [fileToDelete, setFileToDelete] = useState<FileResponse | null>(null);
  const limit = 10;

  const { data, isLoading, isError } = useFiles({ page, limit });
  const deleteFile = useDeleteFile();

  const handleDeleteClick = (file: FileResponse) => {
    setFileToDelete(file);
  };

  const handleDeleteConfirm = async () => {
    if (!fileToDelete) return;

    try {
      await deleteFile.mutateAsync(fileToDelete.id);
      toast.success("File deleted successfully", {
        description: `${fileToDelete.original_filename} has been permanently deleted.`,
      });
      setFileToDelete(null);
    } catch (error) {
      toast.error("Failed to delete file", {
        description:
          error instanceof Error
            ? error.message
            : "An error occurred while deleting the file.",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center p-8 text-destructive">
        Failed to load files. Please try again.
      </div>
    );
  }

  if (!data || data.files.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        No files uploaded yet. Upload a CSV file to get started.
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Original Filename</TableHead>
              <TableHead>File Size</TableHead>
              <TableHead>Content Type</TableHead>
              <TableHead>Uploaded At</TableHead>
              <TableHead className="text-center">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.files.map((file) => (
              <TableRow key={file.id}>
                <TableCell className="font-medium">
                  {file.original_filename}
                </TableCell>
                <TableCell>{formatFileSize(file.file_size)}</TableCell>
                <TableCell>{file.content_type}</TableCell>
                <TableCell>{formatDateTime(file.created_at)}</TableCell>
                <TableCell className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    {file.total_rows !== null &&
                      file.total_rows !== undefined && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() =>
                            setReportFileReference(file.file_reference)
                          }
                          title="View CSV Report"
                        >
                          <FileText className="h-4 w-4" />
                          <span className="sr-only">View report</span>
                        </Button>
                      )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSelectedFile(file)}
                      title="View file details"
                    >
                      <Eye className="h-4 w-4" />
                      <span className="sr-only">View details</span>
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteClick(file)}
                      title="Delete file"
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                      <span className="sr-only">Delete file</span>
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {data.total_pages > 1 && (
        <div className="flex items-center justify-between px-2 py-4">
          <div className="text-sm text-muted-foreground">
            Showing {(page - 1) * limit + 1} to{" "}
            {Math.min(page * limit, data.total)} of {data.total} files
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <div className="text-sm">
              Page {page} of {data.total_pages}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
              disabled={page === data.total_pages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {selectedFile && (
        <FileDetailsModal
          file={selectedFile}
          onClose={() => setSelectedFile(null)}
        />
      )}

      {reportFileReference && (
        <CSVReportModal
          fileReference={reportFileReference}
          onClose={() => setReportFileReference(null)}
        />
      )}

      {fileToDelete && (
        <DeleteFileDialog
          file={fileToDelete}
          isOpen={!!fileToDelete}
          onClose={() => setFileToDelete(null)}
          onConfirm={handleDeleteConfirm}
          isDeleting={deleteFile.isPending}
        />
      )}
    </>
  );
};
