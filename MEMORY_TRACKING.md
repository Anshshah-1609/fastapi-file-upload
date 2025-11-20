# Memory Tracking Documentation

## Overview

This document explains how memory consumption is tracked during the CSV file upload and analysis process. The memory tracking system monitors the peak RAM usage specifically during the CSV analysis phase to help understand resource requirements and optimize performance.

## What is Being Tracked?

### Process-Specific Memory (RSS)

The memory tracking system measures **Resident Set Size (RSS)** of the **current Python process only**. This includes:

- **Included:**

  - Memory used by the current FastAPI application process
  - Memory allocated for CSV data processing (pandas DataFrames, chunks)
  - Memory used by Python objects, libraries, and dependencies during analysis
  - Memory used by the analysis algorithms (null detection, duplicate detection)

- **NOT Included:**
  - Memory used by other API endpoints or concurrent requests
  - Memory used by other processes on the system
  - Memory used by the database server (PostgreSQL)
  - Memory used by the web server (Uvicorn/Gunicorn workers)
  - System-level memory (kernel, buffers, cache)
  - Memory used by the frontend application

### Memory Measurement Method

The system uses `psutil.Process(os.getpid()).memory_info().rss` to get the RSS (Resident Set Size) of the current process:

```python
def get_current_memory_mb() -> float:
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
```

**RSS (Resident Set Size)** represents the amount of physical RAM currently being used by the process, excluding swapped-out memory.

## When is Memory Tracked?

Memory tracking occurs **only during the CSV analysis phase**, not during the entire upload process:

### Upload Process Phases:

1. **Phase 1: File Validation and Reading** ❌ _No memory tracking_

   - File type validation
   - File content reading
   - File size validation

2. **Phase 2: File Saving** ❌ _No memory tracking_

   - Generating unique filename
   - Saving file to disk

3. **Phase 3: Database Storage** ❌ _No memory tracking_

   - Storing file metadata in database

4. **Phase 4: Upload Complete Notification** ❌ _No memory tracking_

   - Sending upload completion event

5. **Phase 5: CSV Analysis** ✅ **Memory tracking active**

   - Reading CSV file structure
   - Processing chunks for null detection
   - Processing chunks for duplicate detection
   - Generating analysis results

6. **Phase 6: Completion Event** ❌ _No memory tracking_
   - Sending final completion event

### Memory Tracking Timeline

```
Upload Start
    │
    ├─ Phase 1: Validation ❌
    ├─ Phase 2: Save to Disk ❌
    ├─ Phase 3: Database Storage ❌
    ├─ Phase 4: Upload Complete ❌
    │
    ├─ Phase 5: CSV Analysis ✅ MEMORY TRACKING STARTS
    │   │
    │   ├─ Initial memory snapshot
    │   ├─ Background memory monitor (checks every 100ms)
    │   ├─ Memory checks in progress callbacks
    │   ├─ Final memory check
    │   │
    │   └─ Peak memory recorded ✅ MEMORY TRACKING ENDS
    │
    └─ Phase 6: Completion ❌
```

## How Memory Tracking Works

### 1. Initial Memory Snapshot

When the analysis phase begins, the system captures the initial memory usage:

```python
initial_memory = get_current_memory_mb()
peak_memory_mb = initial_memory
```

### 2. Background Memory Monitoring

A background task continuously monitors memory usage every 100ms:

```python
async def monitor_memory():
    nonlocal peak_memory_mb
    while True:
        await asyncio.sleep(0.1)  # Check every 100ms
        current_memory = get_current_memory_mb()
        peak_memory_mb = max(peak_memory_mb, current_memory)
```

### 3. Progress Callback Memory Checks

During analysis progress updates, memory is also checked:

```python
# Track memory usage during analysis
current_memory = get_current_memory_mb()
peak_memory_mb = max(peak_memory_mb, current_memory)
```

### 4. Final Memory Check

After analysis completes, a final memory check is performed:

```python
final_memory = get_current_memory_mb()
peak_memory_mb = max(peak_memory_mb, final_memory)
```

### 5. Peak Memory Storage

The peak memory value is stored in the database:

```python
db_file.memory_usage_mb = str(round(peak_memory_mb, 2))
```

## Memory Tracking Scope

### ✅ What is Included

- **Current Process Memory**: Only the memory used by the FastAPI process handling the upload request
- **Analysis Operations**: Memory used during CSV reading, null detection, and duplicate detection
- **Pandas Operations**: Memory used by pandas DataFrames during chunked processing
- **Python Objects**: Memory used by Python objects, dictionaries, sets created during analysis
- **Library Memory**: Memory used by imported libraries (pandas, psutil, etc.) during analysis

### ❌ What is NOT Included

- **Other API Requests**: Memory used by concurrent requests to other endpoints
- **Other Processes**: Memory used by database server, web server workers, or system processes
- **System Memory**: Kernel memory, buffers, cache, or other system-level memory
- **Frontend Memory**: Memory used by the React frontend application
- **Database Memory**: Memory used by PostgreSQL for query execution
- **Upload Phase Memory**: Memory used during file reading and saving (before analysis starts)

## Technical Details

### Memory Measurement Frequency

- **Background Monitor**: Checks every 100ms during analysis
- **Progress Callbacks**: Checks on each progress update (varies based on chunk processing)
- **Final Check**: Once at the end of analysis

### Memory Accuracy

- **Precision**: Memory values are rounded to 2 decimal places (MB)
- **Measurement Method**: RSS (Resident Set Size) - physical RAM used
- **Unit**: Megabytes (MB)
- **Timing**: Peak memory is the maximum value observed during the entire analysis phase

### Memory Tracking Limitations

1. **Process-Specific**: Only tracks the current process, not system-wide memory
2. **Analysis Phase Only**: Does not track memory during file upload phases
3. **Sampling Rate**: 100ms intervals may miss very brief memory spikes
4. **Python Overhead**: Includes Python interpreter and library overhead
5. **Garbage Collection**: Memory may be freed by Python's garbage collector between measurements

## Example Memory Usage Flow

```
Time    | Phase              | Memory (MB) | Notes
--------|--------------------|-------------|------------------
0.0s    | Upload Start       | 150.0       | Baseline
0.5s    | File Validation    | 152.0       | Not tracked
1.0s    | File Reading       | 180.0       | Not tracked
1.5s    | Save to Disk       | 182.0       | Not tracked
2.0s    | Database Storage   | 183.0       | Not tracked
2.5s    | Analysis Start ✅  | 185.0       | Tracking starts
3.0s    | Reading CSV        | 200.0       | Tracked
3.5s    | Chunk 1 Processing | 250.0       | Tracked
4.0s    | Chunk 2 Processing | 280.0       | Tracked (peak)
4.5s    | Chunk 3 Processing | 275.0       | Tracked
5.0s    | Duplicate Detection| 270.0       | Tracked
5.5s    | Analysis Complete  | 190.0       | Final check
6.0s    | Completion Event   | 188.0       | Tracking ends
--------|--------------------|-------------|------------------
Peak Memory: 280.0 MB (recorded at 4.0s during chunk processing)
```

## Database Storage

The peak memory usage is stored in the `files` table:

- **Column**: `memory_usage_mb`
- **Type**: `String(20)` (stored as string to preserve precision)
- **Format**: Decimal number with 2 decimal places (e.g., "280.45")
- **Unit**: Megabytes (MB)

## API Response

The memory usage is included in the CSV report API response:

```json
{
  "file_id": 123,
  "original_filename": "data.csv",
  "memory_usage_mb": "280.45",
  "time_consumption": "3.50",
  ...
}
```

## Best Practices

1. **Interpretation**: The memory value represents peak usage during analysis only
2. **Comparison**: Compare memory usage across different file sizes to understand scaling
3. **Optimization**: Use memory usage data to optimize chunk sizes and processing algorithms
4. **Monitoring**: Track memory usage trends to identify memory leaks or optimization opportunities
5. **Resource Planning**: Use peak memory values to plan server resources and capacity

## Troubleshooting

### Memory Value is 0.0

- Check if `psutil` is properly installed
- Verify the analysis phase completed successfully
- Check logs for memory tracking errors

### Memory Value Seems Low

- Remember: Only process-specific memory is tracked
- System memory, database memory, and other processes are not included
- Memory is only tracked during analysis, not during upload

### Memory Value Seems High

- Large CSV files will naturally use more memory
- Chunk size affects memory usage (default: 100,000 rows per chunk)
- Multiple concurrent requests may share process memory

## Future Enhancements

Potential improvements to memory tracking:

1. **Full Upload Tracking**: Track memory during all upload phases
2. **System Memory**: Option to track system-wide memory usage
3. **Memory Breakdown**: Track memory by operation (reading, null detection, duplicates)
4. **Memory Profiling**: Detailed memory profiling with memory_profiler
5. **Real-time Monitoring**: Stream memory usage in SSE events during analysis

## References

- [psutil Documentation](https://psutil.readthedocs.io/)
- [RSS vs VSZ Memory](https://en.wikipedia.org/wiki/Resident_set_size)
- [Python Memory Management](https://docs.python.org/3/c-api/memory.html)
