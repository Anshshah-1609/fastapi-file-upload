import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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

function App() {
  console.log("App component rendered");

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-8 px-4 max-w-6xl">
          <div className="space-y-8">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                CSV File Upload
              </h1>
              <p className="text-muted-foreground mt-2">
                Upload and manage your CSV files
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-4">Upload CSV File</h2>
                <CSVDropzone />
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-4">Uploaded Files</h2>
                <FileListTable />
              </div>
            </div>
          </div>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
