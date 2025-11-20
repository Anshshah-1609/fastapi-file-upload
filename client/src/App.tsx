import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { Upload, Database, FileText } from "lucide-react";
import { CSVDropzone } from "@/components/CSVDropzone";
import { FileListTable } from "@/components/FileListTable";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30">
        <div className="container mx-auto py-8 px-4 max-w-6xl">
          <div className="space-y-8">
            {/* Header Section */}
            <div className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-white to-blue-50/50 shadow-lg p-8">
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-200/20 to-purple-200/20 rounded-full blur-3xl" />
              <div className="relative">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                    <Database className="h-8 w-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      CSV File Upload
                    </h1>
                    <p className="text-slate-600 mt-1.5 flex items-center gap-2">
                      <FileText className="h-4 w-4 text-slate-400" />
                      Upload and manage your CSV files with ease
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-8">
              {/* Upload Section */}
              <div className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-white to-slate-50/50 shadow-md p-6">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-100/30 to-purple-100/30 rounded-full blur-2xl" />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-blue-100">
                      <Upload className="h-5 w-5 text-blue-600" />
                    </div>
                    <h2 className="text-2xl font-semibold text-slate-900">
                      Upload CSV File
                    </h2>
                  </div>
                  <CSVDropzone />
                </div>
              </div>

              {/* Files List Section */}
              <div className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-white to-slate-50/50 shadow-md p-6">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-100/30 to-pink-100/30 rounded-full blur-2xl" />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-purple-100">
                      <FileText className="h-5 w-5 text-purple-600" />
                    </div>
                    <h2 className="text-2xl font-semibold text-slate-900">
                      Uploaded Files
                    </h2>
                  </div>
                  <FileListTable />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Toaster position="top-right" richColors />
    </QueryClientProvider>
  );
};

export default App;
