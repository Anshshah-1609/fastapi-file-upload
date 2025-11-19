import {
  FileText,
  Clock,
  Database,
  AlertTriangle,
  CheckCircle2,
  Copy,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { formatDateTime, formatTime } from "@/lib/date-utils";
import { formatFileSize } from "@/lib/utils";
import { useGetFileByReference } from "@/hooks/useGetFileByReference";
import { CountUp } from "./ui/countUp";

interface CSVReportModalProps {
  fileReference: string;
  onClose: () => void;
}

export const CSVReportModal = ({
  fileReference,
  onClose,
}: CSVReportModalProps) => {
  const {
    data: report,
    isLoading,
    isError,
    error,
  } = useGetFileByReference(fileReference);

  const isOpen = !!fileReference;

  if (!isOpen || !report) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogClose className="h-6 w-6" onClick={onClose} />
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            CSV Analysis Report
          </DialogTitle>
          <DialogDescription>
            Comprehensive analysis report for the uploaded CSV file
          </DialogDescription>
        </DialogHeader>

        {isLoading && (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        )}

        {isError && (
          <div className="p-4 rounded-md bg-destructive/10 text-destructive">
            <p className="font-medium">Failed to load report</p>
            <p className="text-sm mt-1">
              {error instanceof Error
                ? error.message
                : "An error occurred while loading the report"}
            </p>
          </div>
        )}

        {report && (
          <div className="space-y-6 py-4">
            {/* Header Section */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-2">File Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    File Name
                  </label>
                  <p className="text-sm font-medium mt-1 break-words">
                    {report.original_filename}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    File Size
                  </label>
                  <p className="text-sm font-medium mt-1">
                    {formatFileSize(report.file_size)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Uploaded At
                  </label>
                  <p className="text-sm font-medium mt-1">
                    {formatDateTime(report.created_at)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    File ID
                  </label>
                  <p className="text-sm font-medium mt-1">#{report.file_id}</p>
                </div>
              </div>
            </div>

            {/* Statistics Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Analysis Statistics</h3>
              <div className="grid grid-cols-2 gap-4">
                {/* Total Records */}
                <div className="p-4 rounded-lg border bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="h-4 w-4 text-primary" />
                    <label className="text-sm font-medium text-muted-foreground">
                      Total Records
                    </label>
                  </div>
                  <p className="text-2xl font-bold">
                    <CountUp targetNumber={report.total_records} />
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Total number of rows in the CSV
                  </p>
                </div>

                {/* Total Columns */}
                <div className="p-4 rounded-lg border bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="h-4 w-4 text-primary" />
                    <label className="text-sm font-medium text-muted-foreground">
                      Total Columns
                    </label>
                  </div>
                  <p className="text-2xl font-bold">
                    <CountUp targetNumber={report.total_columns} />
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Number of columns in the CSV
                  </p>
                </div>

                {/* Null Records */}
                <div className="p-4 rounded-lg border bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    {report.null_records > 0 ? (
                      <AlertTriangle className="h-4 w-4 text-orange-500" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    )}
                    <label className="text-sm font-medium text-muted-foreground">
                      Missing Values
                    </label>
                  </div>
                  <p
                    className={`text-2xl font-bold ${
                      report.null_records > 0
                        ? "text-orange-600 dark:text-orange-400"
                        : "text-green-600 dark:text-green-400"
                    }`}
                  >
                    <CountUp targetNumber={report.null_records} />
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {report.null_records > 0
                      ? `Rows containing null/undefined values`
                      : `No null values found`}
                  </p>
                </div>

                {/* Time Consumption */}
                <div className="p-4 rounded-lg border bg-card">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-primary" />
                    <label className="text-sm font-medium text-muted-foreground">
                      Processing Time
                    </label>
                  </div>
                  <p className="text-2xl font-bold">
                    {report.time_consumption} seconds
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Time taken to analyze the file
                  </p>
                </div>
              </div>
            </div>

            {/* Duplicate Records Section */}
            {report.duplicate_records &&
              Object.keys(report.duplicate_records).length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">
                    Duplicate Records by Column
                  </h3>
                  <div className="p-4 rounded-lg border bg-card">
                    <p className="text-sm text-muted-foreground mb-4">
                      The following columns contain duplicate values. The count
                      represents the number of duplicate records found in each
                      column.
                    </p>
                    <div className="space-y-3">
                      {Object.entries(report.duplicate_records)
                        .sort(([, a], [, b]) => b - a) // Sort by count descending
                        .map(([columnName, count]) => (
                          <div
                            key={columnName}
                            className="flex items-center justify-between p-3 rounded-md border bg-muted/30 hover:bg-muted/50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <div className="p-2 rounded-md bg-orange-500/10">
                                <Copy className="h-4 w-4 text-orange-500" />
                              </div>
                              <div>
                                <p className="text-sm font-semibold">
                                  {columnName}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  Column with duplicate values
                                </p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-xl font-bold text-orange-600 dark:text-orange-400">
                                <CountUp targetNumber={count} />
                              </p>
                              <p className="text-xs text-muted-foreground">
                                duplicate record{count !== 1 ? "s" : ""}
                              </p>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}

            {/* Summary Section */}
            <div className="p-4 rounded-lg border bg-muted/50">
              <h4 className="text-sm font-semibold mb-2">Summary</h4>
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>
                  • The CSV file contains&nbsp;
                  <strong>
                    <CountUp targetNumber={report.total_records} />
                  </strong>
                  &nbsp; records across&nbsp;
                  <strong>
                    <CountUp targetNumber={report.total_columns} />
                  </strong>
                  &nbsp; columns.
                </p>
                <p>
                  • Analysis found&nbsp;
                  <strong>
                    <CountUp targetNumber={report.null_records} />
                  </strong>
                  &nbsp; record(s) with null or undefined values.
                </p>
                {report.duplicate_records &&
                  Object.keys(report.duplicate_records).length > 0 && (
                    <p>
                      • Found duplicate values in&nbsp;
                      <strong>
                        <CountUp
                          targetNumber={
                            Object.keys(report.duplicate_records).length
                          }
                        />
                      </strong>
                      &nbsp; column(s) with a total of&nbsp;
                      <strong>
                        <CountUp
                          targetNumber={Object.values(
                            report.duplicate_records
                          ).reduce((sum, count) => sum + count, 0)}
                        />
                      </strong>
                      &nbsp; duplicate record(s).
                    </p>
                  )}
                <p>
                  • The analysis completed in&nbsp;
                  <strong>{formatTime(report.time_consumption)}</strong>.
                </p>
                {report.null_records === 0 &&
                  (!report.duplicate_records ||
                    Object.keys(report.duplicate_records).length === 0) && (
                    <p className="text-green-600 dark:text-green-400 font-medium mt-2">
                      ✓ No data quality issues detected.
                    </p>
                  )}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
