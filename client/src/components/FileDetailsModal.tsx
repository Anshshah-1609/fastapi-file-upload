import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { formatDateTimeWithSeconds } from "@/lib/date-utils";
import type { FileResponse } from "@/lib/api";

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

interface FileDetailsModalProps {
  file: FileResponse;
  onClose: () => void;
}

export function FileDetailsModal({ file, onClose }: FileDetailsModalProps) {
  return (
    <Dialog open={!!file} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>File Details</DialogTitle>
          <DialogDescription>
            Complete information about the uploaded file
          </DialogDescription>
        </DialogHeader>
        <DialogClose onClick={onClose} />

        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                File ID
              </label>
              <p className="text-sm font-medium mt-1">{file.id}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Content Type
              </label>
              <p className="text-sm font-medium mt-1">{file.content_type}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Original Filename
              </label>
              <p className="text-sm font-medium mt-1 break-words">
                {file.original_filename}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Stored Filename
              </label>
              <p className="text-sm font-medium mt-1 break-words">
                {file.stored_filename}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                File Size
              </label>
              <p className="text-sm font-medium mt-1">
                {formatFileSize(file.file_size)}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                File Path
              </label>
              <p className="text-sm font-medium mt-1 break-words">
                {file.file_path}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Created At
              </label>
              <p className="text-sm font-medium mt-1">
                {formatDateTimeWithSeconds(file.created_at)}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Updated At
              </label>
              <p className="text-sm font-medium mt-1">
                {formatDateTimeWithSeconds(file.updated_at)}
              </p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
