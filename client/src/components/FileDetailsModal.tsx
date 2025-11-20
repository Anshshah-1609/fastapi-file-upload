import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  FileText,
  Hash,
  FileType,
  File,
  HardDrive,
  Folder,
  Calendar,
  Clock,
  Database,
  AlertCircle,
  Loader2,
  Table2,
} from "lucide-react";
import { formatDateTime } from "@/lib/date-utils";
import type { FileResponse } from "@/lib/api";
import { formatFileSize } from "@/lib/utils";
import { useGetFilePreview } from "@/hooks/useGetFilePreview";

interface FileDetailsModalProps {
  file: FileResponse;
  onClose: () => void;
}

export const FileDetailsModal = ({ file, onClose }: FileDetailsModalProps) => {
  const {
    data: previewData,
    isLoading: isLoadingPreview,
    isError: isPreviewError,
  } = useGetFilePreview(file.id, !!file);

  return (
    <Dialog open={!!file} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <DialogClose className="h-6 w-6" onClick={onClose} />
        <DialogHeader className="pb-4 border-b">
          <DialogTitle className="flex items-center gap-3 text-2xl">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              <FileText className="h-6 w-6" />
            </div>
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              File Details & Preview
            </span>
          </DialogTitle>
          <DialogDescription className="text-base mt-2">
            Complete information about the uploaded file and CSV data preview
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* File Details Section */}
          <div className="relative rounded-xl border bg-gradient-to-br from-slate-50 to-blue-50/50 p-6 shadow-sm max-w-5xl">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-200/20 to-purple-200/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <File className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-slate-900">
                  File Information
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-blue-100">
                    <Hash className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      File ID
                    </label>
                    <p className="text-sm font-semibold mt-1 break-words text-slate-900">
                      {file.id}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-purple-100">
                    <FileType className="h-4 w-4 text-purple-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      Content Type
                    </label>
                    <p className="text-sm font-semibold mt-1 break-words text-slate-900">
                      {file.content_type}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-green-100">
                    <FileText className="h-4 w-4 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      Original Filename
                    </label>
                    <p className="text-sm font-semibold mt-1 break-words text-slate-900">
                      {file.original_filename}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-indigo-100">
                    <File className="h-4 w-4 text-indigo-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      Stored Filename
                    </label>
                    <p className="text-sm font-semibold mt-1 break-words text-slate-900">
                      {file.stored_filename}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-orange-100">
                    <HardDrive className="h-4 w-4 text-orange-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      File Size
                    </label>
                    <p className="text-sm font-semibold mt-1 text-slate-900">
                      {formatFileSize(file.file_size)}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-teal-100">
                    <Folder className="h-4 w-4 text-teal-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      File Path
                    </label>
                    <p className="text-xs font-semibold mt-1 break-words text-slate-900">
                      {file.file_path}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-emerald-100">
                    <Calendar className="h-4 w-4 text-emerald-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      Created At
                    </label>
                    <p className="text-sm font-semibold mt-1 text-slate-900">
                      {formatDateTime(file.created_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 backdrop-blur-sm">
                  <div className="p-2 rounded-md bg-amber-100">
                    <Clock className="h-4 w-4 text-amber-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      Updated At
                    </label>
                    <p className="text-sm font-semibold mt-1 text-slate-900">
                      {formatDateTime(file.updated_at)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CSV Preview Section */}
          <div className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-slate-50 to-purple-50/50 px-4 py-6 shadow-sm max-w-5xl">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-200/20 to-pink-200/20 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <Database className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-slate-900">
                  CSV Data Preview
                </h3>
                {previewData && (
                  <span className="text-sm font-normal text-slate-500 ml-2">
                    (Showing first {previewData.preview_count} of{" "}
                    {previewData.total_rows} records)
                  </span>
                )}
              </div>

              {isLoadingPreview && (
                <div className="flex flex-col items-center justify-center p-12">
                  <Loader2 className="h-8 w-8 animate-spin text-purple-600 mb-3" />
                  <p className="text-sm text-slate-600">
                    Loading preview data...
                  </p>
                </div>
              )}

              {isPreviewError && (
                <div className="flex flex-col items-center justify-center p-8 rounded-lg bg-destructive/10 border border-destructive/20">
                  <AlertCircle className="h-8 w-8 text-destructive mb-3" />
                  <p className="font-medium text-destructive mb-1">
                    Failed to load CSV preview
                  </p>
                  <p className="text-sm text-destructive/80 text-center">
                    The file may be corrupted or in an unsupported format.
                  </p>
                </div>
              )}

              {previewData && previewData.records.length > 0 && (
                <div className="rounded-lg border border-slate-200 overflow-x-auto bg-white shadow-sm w-full max-w-full">
                  <Table
                    style={{ minWidth: "max-content", width: "max-content" }}
                  >
                    <TableHeader>
                      <TableRow className="bg-slate-50 hover:bg-slate-50">
                        {previewData.columns.map((column) => (
                          <TableHead
                            key={column}
                            className="font-semibold whitespace-nowrap text-slate-700"
                          >
                            <div className="flex items-center gap-2">
                              <Table2 className="h-3.5 w-3.5 text-purple-600" />
                              {column}
                            </div>
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {previewData.records.map((record, index) => (
                        <TableRow
                          key={index}
                          className="hover:bg-slate-50/50 border-b border-slate-100"
                        >
                          {previewData.columns.map((column) => (
                            <TableCell
                              key={column}
                              className="max-w-[200px] truncate whitespace-nowrap text-slate-700"
                            >
                              {record[column] !== null &&
                              record[column] !== undefined ? (
                                String(record[column])
                              ) : (
                                <span className="text-slate-400 italic">
                                  (empty)
                                </span>
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              {previewData && previewData.records.length === 0 && (
                <div className="flex flex-col items-center justify-center p-12 rounded-lg bg-slate-100/50 border border-slate-200">
                  <Database className="h-10 w-10 text-slate-400 mb-3" />
                  <p className="text-sm font-medium text-slate-600">
                    No data available in this CSV file.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
