import {
  FileText,
  Clock,
  Database,
  AlertTriangle,
  CheckCircle2,
  Copy,
  File,
  HardDrive,
  Calendar,
  Hash,
  BarChart3,
  TrendingUp,
  Shield,
  XCircle,
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
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogClose className="h-6 w-6" onClick={onClose} />
        <DialogHeader className="pb-4 border-b">
          <DialogTitle className="flex items-center gap-3 text-2xl">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              <BarChart3 className="h-6 w-6" />
            </div>
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              CSV Analysis Report
            </span>
          </DialogTitle>
          <DialogDescription className="text-base mt-2">
            Comprehensive data quality analysis and insights
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
            <div className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-slate-50 to-blue-50/50 dark:from-slate-900 dark:to-blue-950/30 p-6 shadow-sm">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-200/20 to-purple-200/20 rounded-full blur-3xl" />
              <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                  <File className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                    File Information
                  </h3>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-2 rounded-md bg-blue-100 dark:bg-blue-900/30">
                      <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        File Name
                      </label>
                      <p className="text-sm font-semibold mt-1 break-words text-slate-900 dark:text-slate-100">
                        {report.original_filename}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-2 rounded-md bg-purple-100 dark:bg-purple-900/30">
                      <HardDrive className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        File Size
                      </label>
                      <p className="text-sm font-semibold mt-1 text-slate-900 dark:text-slate-100">
                        {formatFileSize(report.file_size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-2 rounded-md bg-green-100 dark:bg-green-900/30">
                      <Calendar className="h-4 w-4 text-green-600 dark:text-green-400" />
                    </div>
                    <div className="flex-1">
                      <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        Uploaded At
                      </label>
                      <p className="text-sm font-semibold mt-1 text-slate-900 dark:text-slate-100">
                        {formatDateTime(report.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-2 rounded-md bg-orange-100 dark:bg-orange-900/30">
                      <Hash className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                    </div>
                    <div className="flex-1">
                      <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        File ID
                      </label>
                      <p className="text-sm font-semibold mt-1 text-slate-900 dark:text-slate-100">
                        #{report.file_id}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Statistics Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Analysis Statistics
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {/* Total Records */}
                <div className="group relative overflow-hidden rounded-xl border-2 border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 p-5 shadow-sm hover:shadow-md transition-all duration-300">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-blue-200/20 dark:bg-blue-800/20 rounded-full blur-2xl" />
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2.5 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg">
                        <Database className="h-5 w-5" />
                      </div>
                      <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                        Total Records
                      </label>
                    </div>
                    <p className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-1">
                      <CountUp targetNumber={report.total_records} />
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      Total number of rows in the CSV
                    </p>
                  </div>
                </div>

                {/* Total Columns */}
                <div className="group relative overflow-hidden rounded-xl border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 p-5 shadow-sm hover:shadow-md transition-all duration-300">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-purple-200/20 dark:bg-purple-800/20 rounded-full blur-2xl" />
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2.5 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 text-white shadow-lg">
                        <FileText className="h-5 w-5" />
                      </div>
                      <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                        Total Columns
                      </label>
                    </div>
                    <p className="text-3xl font-bold text-purple-700 dark:text-purple-300 mb-1">
                      <CountUp targetNumber={report.total_columns} />
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      Number of columns in the CSV
                    </p>
                  </div>
                </div>

                {/* Null Records */}
                <div
                  className={`group relative overflow-hidden rounded-xl border-2 p-5 shadow-sm hover:shadow-md transition-all duration-300 ${
                    report.null_records > 0
                      ? "border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/30 dark:to-red-950/30"
                      : "border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30"
                  }`}
                >
                  <div
                    className={`absolute top-0 right-0 w-20 h-20 rounded-full blur-2xl ${
                      report.null_records > 0
                        ? "bg-orange-200/20 dark:bg-orange-800/20"
                        : "bg-green-200/20 dark:bg-green-800/20"
                    }`}
                  />
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-3">
                      <div
                        className={`p-2.5 rounded-lg text-white shadow-lg ${
                          report.null_records > 0
                            ? "bg-gradient-to-br from-orange-500 to-red-600"
                            : "bg-gradient-to-br from-green-500 to-emerald-600"
                        }`}
                      >
                        {report.null_records > 0 ? (
                          <XCircle className="h-5 w-5" />
                        ) : (
                          <Shield className="h-5 w-5" />
                        )}
                      </div>
                      <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                        Missing Values
                      </label>
                    </div>
                    <p
                      className={`text-3xl font-bold mb-1 ${
                        report.null_records > 0
                          ? "text-orange-700 dark:text-orange-300"
                          : "text-green-700 dark:text-green-300"
                      }`}
                    >
                      <CountUp targetNumber={report.null_records} />
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {report.null_records > 0
                        ? `Rows containing null/undefined values`
                        : `No null values found`}
                    </p>
                  </div>
                </div>

                {/* Time Consumption */}
                <div className="group relative overflow-hidden rounded-xl border-2 border-cyan-200 dark:border-cyan-800 bg-gradient-to-br from-cyan-50 to-teal-50 dark:from-cyan-950/30 dark:to-teal-950/30 p-5 shadow-sm hover:shadow-md transition-all duration-300">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-200/20 dark:bg-cyan-800/20 rounded-full blur-2xl" />
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2.5 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 text-white shadow-lg">
                        <Clock className="h-5 w-5" />
                      </div>
                      <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                        Processing Time
                      </label>
                    </div>
                    <p className="text-3xl font-bold text-cyan-700 dark:text-cyan-300 mb-1">
                      {report.time_consumption} seconds
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      Time taken to analyze the file
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Duplicate Records Section */}
            {report.duplicate_records &&
              Object.keys(report.duplicate_records).length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Copy className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                      Duplicate Records by Column
                    </h3>
                  </div>
                  <div className="relative overflow-hidden rounded-xl border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-950/20 dark:to-orange-950/20 p-5 shadow-sm">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-200/10 dark:bg-amber-800/10 rounded-full blur-3xl" />
                    <div className="relative">
                      <div className="flex items-start gap-2 mb-4 p-3 rounded-lg bg-amber-100/50 dark:bg-amber-900/20 border border-amber-200/50 dark:border-amber-800/50">
                        <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-amber-900 dark:text-amber-200">
                          The following columns contain duplicate values. The
                          count represents the number of duplicate records found
                          in each column.
                        </p>
                      </div>
                      <div className="space-y-3">
                        {Object.entries(report.duplicate_records)
                          .sort(([, a], [, b]) => b - a) // Sort by count descending
                          .map(([columnName, count], index) => (
                            <div
                              key={columnName}
                              className="flex items-center justify-between p-4 rounded-lg border-2 border-amber-200/50 dark:border-amber-800/50 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm hover:border-amber-300 dark:hover:border-amber-700 hover:shadow-md transition-all duration-200"
                            >
                              <div className="flex items-center gap-4">
                                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 text-white font-bold text-sm shadow-md">
                                  {index + 1}
                                </div>
                                <div className="p-2.5 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                                  <Copy className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                                </div>
                                <div>
                                  <p className="text-sm font-bold text-slate-900 dark:text-slate-100">
                                    {columnName}
                                  </p>
                                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                    Column with duplicate values
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-2xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 dark:from-amber-400 dark:to-orange-400 bg-clip-text text-transparent">
                                  <CountUp targetNumber={count} />
                                </p>
                                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                                  duplicate record{count !== 1 ? "s" : ""}
                                </p>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

            {/* Summary Section */}
            <div className="relative overflow-hidden rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 dark:from-slate-900 dark:via-blue-950/20 dark:to-purple-950/20 p-6 shadow-lg">
              <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-200/20 to-purple-200/20 dark:from-blue-800/10 dark:to-purple-800/10 rounded-full blur-3xl" />
              <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                    <BarChart3 className="h-4 w-4" />
                  </div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">
                    Executive Summary
                  </h4>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-1.5 rounded bg-blue-100 dark:bg-blue-900/30 mt-0.5">
                      <Database className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 flex-1">
                      The CSV file contains&nbsp;
                      <strong className="text-blue-700 dark:text-blue-300 font-bold">
                        <CountUp targetNumber={report.total_records} />
                      </strong>
                      &nbsp; records across&nbsp;
                      <strong className="text-purple-700 dark:text-purple-300 font-bold">
                        <CountUp targetNumber={report.total_columns} />
                      </strong>
                      &nbsp; columns.
                    </p>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-1.5 rounded bg-orange-100 dark:bg-orange-900/30 mt-0.5">
                      <AlertTriangle className="h-3.5 w-3.5 text-orange-600 dark:text-orange-400" />
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 flex-1">
                      Analysis found&nbsp;
                      <strong className="text-orange-700 dark:text-orange-300 font-bold">
                        <CountUp targetNumber={report.null_records} />
                      </strong>
                      &nbsp; record(s) with null or undefined values.
                    </p>
                  </div>
                  {report.duplicate_records &&
                    Object.keys(report.duplicate_records).length > 0 && (
                      <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                        <div className="p-1.5 rounded bg-amber-100 dark:bg-amber-900/30 mt-0.5">
                          <Copy className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                        </div>
                        <p className="text-slate-700 dark:text-slate-300 flex-1">
                          Found duplicate values in&nbsp;
                          <strong className="text-amber-700 dark:text-amber-300 font-bold">
                            <CountUp
                              targetNumber={
                                Object.keys(report.duplicate_records).length
                              }
                            />
                          </strong>
                          &nbsp; column(s) with a total of&nbsp;
                          <strong className="text-amber-700 dark:text-amber-300 font-bold">
                            <CountUp
                              targetNumber={Object.values(
                                report.duplicate_records
                              ).reduce((sum, count) => sum + count, 0)}
                            />
                          </strong>
                          &nbsp; duplicate record(s).
                        </p>
                      </div>
                    )}
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
                    <div className="p-1.5 rounded bg-cyan-100 dark:bg-cyan-900/30 mt-0.5">
                      <Clock className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 flex-1">
                      The analysis completed in&nbsp;
                      <strong className="text-cyan-700 dark:text-cyan-300 font-bold">
                        {formatTime(report.time_consumption)}
                      </strong>
                      .
                    </p>
                  </div>
                  {report.null_records === 0 &&
                    (!report.duplicate_records ||
                      Object.keys(report.duplicate_records).length === 0) && (
                      <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border-2 border-green-200 dark:border-green-800">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                          <p className="text-green-800 dark:text-green-300 font-semibold">
                            ✓ No data quality issues detected. Your data is
                            clean!
                          </p>
                        </div>
                      </div>
                    )}
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
