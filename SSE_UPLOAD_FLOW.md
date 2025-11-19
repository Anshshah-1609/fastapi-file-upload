# SSE File Upload & Null/Undefined Value Check Flow Diagram

## Complete Flow: CSV Upload with Real-Time SSE Progress Updates

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLIENT INITIATES UPLOAD                              │
│                    POST /api/files/upload-sse                               │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: VALIDATE FILE TYPE                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                        │   │
│  │   status: "uploading",                                              │   │
│  │   progress: 0.0,                                                    │   │
│  │   message: "Validating file type...",                               │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Check file extension (.csv)                                             │
│  • Validate content type                                                   │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: READ FILE CONTENT                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                        │   │
│  │   status: "uploading",                                              │   │
│  │   progress: 0.1,                                                    │   │
│  │   message: "Reading file content...",                               │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Read entire file content into memory                                    │
│  • Calculate file_size                                                     │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: VALIDATE FILE SIZE                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "uploading",                                               │   │
│  │   progress: 0.2,                                                    │   │
│  │   message: "Validating file size...",                                │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Check if file_size <= MAX_FILE_SIZE (default: 10MB)                      │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: GENERATE UNIQUE FILENAME                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                        │   │
│  │   status: "uploading",                                              │   │
│  │   progress: 0.3,                                                    │   │
│  │   message: "Generating unique filename...",                         │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Generate UUID for stored_filename                                       │
│  • Format: {uuid}.csv                                                      │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: SAVE FILE TO DISK                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                        │   │
│  │   status: "uploading",                                              │   │
│  │   progress: 0.5,                                                    │   │
│  │   message: "Saving file to disk...",                                │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Write file content to UPLOAD_DIR/{uuid}.csv                             │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 6: STORE FILE METADATA IN DATABASE                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                        │   │
│  │   status: "uploading",                                              │   │
│  │   progress: 0.7,                                                    │   │
│  │   message: "Storing file metadata in database...",                  │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Generate file_reference (UUID)                                          │
│  • Create FileModel record with:                                           │
│    - original_filename                                                     │
│    - stored_filename                                                       │
│    - file_path                                                             │
│    - file_size                                                             │
│    - content_type                                                          │
│    - file_reference (UUID)                                                 │
│    - null_count = 0 (initial)                                              │
│  • Commit to database                                                      │
└───────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: UPLOAD COMPLETE                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "uploading",                                               │   │
│  │   progress: 0.9,                                                    │   │
│  │   message: "File upload complete...",                                │   │
│  │   file_id: <id>,                                                    │   │
│  │   file_reference: "<uuid>",                                         │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 8: UPLOAD PHASE COMPLETE                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "uploading",                                               │   │
│  │   progress: 1.0,                                                    │   │
│  │   message: "Upload phase complete. Starting analysis...",           │   │
│  │   file_id: <id>,                                                    │   │
│  │   file_reference: "<uuid>",                                         │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: null                                                  │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 9: START CSV ANALYSIS (REAL-TIME STREAMING)               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Create asyncio.Queue for real-time event streaming                 │   │
│  │ • Start analysis_task in background                                  │   │
│  │ • Stream events immediately as they're generated                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                  │
                ▼                                  ▼
┌───────────────────────────────┐  ┌──────────────────────────────────────────┐
│   ANALYSIS TASK (Background)  │  │   EVENT STREAMING (Real-Time)            │
│                               │  │                                          │
│   ┌───────────────────────┐  │  │   ┌──────────────────────────────────┐  │
│   │ analyze_csv_for_nulls()│  │  │   │ while True:                       │  │
│   │                        │  │  │   │   event = await queue.get()      │  │
│   │ 1. Read CSV            │  │  │   │   yield send_sse_event(event)     │  │
│   │ 2. Detect nulls       │  │  │   │                                    │  │
│   │ 3. Check columns      │  │  │   └──────────────────────────────────┘  │
│   │ 4. Count results      │  │  │                                          │
│   └───────────────────────┘  │  │                                          │
│           │                   │  │                                          │
│           │ (puts events)     │  │                                          │
│           └──────────────────┼──┘                                          │
│                               │                                              │
└───────────────────────────────┴──────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              ANALYSIS SUB-STEPS (Events Streamed in Real-Time)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                  │
                ▼                                  ▼
┌───────────────────────────────┐  ┌──────────────────────────────────────────┐
│  A9.1: Reading CSV File       │  │  A9.2: CSV Loaded                          │
│  ┌─────────────────────────┐ │  │  ┌────────────────────────────────────┐  │
│  │ SSE Event: {             │ │  │  │ SSE Event: {                        │  │
│  │   status: "analyzing",   │ │  │  │   status: "analyzing",              │  │
│  │   progress: 0.1,         │ │  │  │   progress: 0.2,                   │  │
│  │   message: "Reading...", │ │  │  │   message: "CSV loaded. Analyzing │  │
│  │   null_count: 0,         │ │  │  │            {total_rows} rows...",   │  │
│  │   processed_count: 0,    │ │  │  │   total_rows: <count>,              │  │
│  │   total_rows: null       │ │  │  │   total_columns: <count>,           │  │
│  │ }                        │ │  │  │   null_count: 0,                    │  │
│  └─────────────────────────┘ │  │  │   processed_count: 0                  │  │
│  • pd.read_csv(file_path)   │  │  │ }                                      │  │
│  • Calculate total_rows      │  │  └────────────────────────────────────┘  │
│  • Calculate total_columns   │  │  • Display row/column counts              │
└───────────────────────────────┘  └──────────────────────────────────────────┘
                │                                  │
                └────────────────┬─────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  A9.3: Checking for Null/NaN Values                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "analyzing",                                               │   │
│  │   progress: 0.3,                                                    │   │
│  │   message: "Checking for null/NaN values...",                       │   │
│  │   null_count: 0,                                                    │   │
│  │   processed_count: 0,                                               │   │
│  │   total_rows: <count>,                                              │   │
│  │   total_columns: <count>                                            │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • df.isnull().any(axis=1) | df.isna().any(axis=1)                          │
│  • Create null_mask for pandas null/NaN values                               │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  A9.4: Analyzing Object Columns (String Representations)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ For each object column:                                              │   │
│  │                                                                       │   │
│  │ SSE Event: {                                                         │   │
│  │   status: "analyzing",                                               │   │
│  │   progress: 0.4 - 0.8 (incremental),                                │   │
│  │   message: "Analyzing column {idx}/{total}: {col_name}...",         │   │
│  │   null_count: <incremental_count>,                                  │   │
│  │   processed_count: <total_rows>,                                    │   │
│  │   total_rows: <count>,                                              │   │
│  │   total_columns: <count>                                            │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Check for string representations: 'null', 'none', 'undefined', 'nan', ''│
│  • Update null_mask incrementally                                           │
│  • Progress: 0.4 + (0.4 * (idx + 1) / total_columns)                        │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  A9.5: Analysis Complete                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "analyzing",                                               │   │
│  │   progress: 0.9,                                                    │   │
│  │   message: "Analysis complete. Found {null_count} rows...",        │   │
│  │   null_count: <final_count>,                                        │   │
│  │   processed_count: <total_rows>,                                    │   │
│  │   total_rows: <count>,                                              │   │
│  │   total_columns: <count>                                            │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Calculate final null_count = null_mask.sum()                             │
│  • Return (null_count, total_rows, total_columns)                            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 10: UPDATE DATABASE WITH ANALYSIS RESULTS                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Calculate analysis_duration = end_time - start_time                │   │
│  │ • Update FileModel record:                                           │   │
│  │   - null_count = <calculated_count>                                  │   │
│  │   - total_rows = <count>                                             │   │
│  │   - total_columns = <count>                                         │   │
│  │   - analysis_time = str(round(analysis_duration, 2))                  │   │
│  │ • Commit to database                                                 │   │
│  │ • Refresh db_file object                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 11: SEND COMPLETION EVENT                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SSE Event: {                                                         │   │
│  │   status: "completed",                                              │   │
│  │   progress: 1.0,                                                    │   │
│  │   message: "File uploaded and analyzed successfully",                │   │
│  │   file_id: <id>,                                                    │   │
│  │   file_reference: "<uuid>",                                         │   │
│  │   original_filename: "<name>",                                     │   │
│  │   stored_filename: "<uuid>.csv",                                   │   │
│  │   file_size: <bytes>,                                              │   │
│  │   file_path: "<path>",                                             │   │
│  │   null_count: <final_count>,                                       │   │
│  │   processed_count: <total_rows>,                                   │   │
│  │   total_rows: <count>,                                             │   │
│  │   total_columns: <count>,                                          │   │
│  │   time_consumption: <seconds>                                      │   │
│  │ }                                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT RECEIVES COMPLETION                         │
│                    • Display final results                                  │
│                    • Show null_count, total_rows, time_consumption          │
│                    • Enable report download/view                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### Real-Time Streaming

- **No Delays**: Events stream immediately as they're generated
- **Queue-Based**: Uses `asyncio.Queue` for real-time event delivery
- **Background Processing**: Analysis runs in background task while events stream

### Progress Tracking

- **Upload Phase**: 0.0 → 1.0 (10 steps)
- **Analysis Phase**: 0.1 → 0.9 (incremental based on columns)
- **All Progress Values**: Rounded to 2 decimal places

### Data Tracking

- **null_count**: Incrementally updated during analysis
- **processed_count**: Shows rows processed so far
- **total_rows**: Available after CSV is loaded
- **total_columns**: Available after CSV is loaded
- **time_consumption**: Calculated and included in completion event

### Database Updates

- **Initial**: File metadata stored with `null_count = 0`
- **After Analysis**: Updates `null_count`, `total_rows`, `total_columns`, `analysis_time`
- **Reference**: `file_reference` (UUID) available for future updates

## Error Handling

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERROR SCENARIOS                                     │
│                                                                              │
│  • Invalid file type → HTTPException 400                                    │
│  • File too large → HTTPException 400                                       │
│  • File save failure → SSE error event                                     │
│  • Database save failure → SSE error event + cleanup file                   │
│  • Analysis failure → SSE error event (file still saved)                    │
│  • Database update failure → Logged but doesn't fail upload                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

- **POST** `/api/files/upload-sse` - SSE upload with real-time progress
- **GET** `/api/files/{file_id}/report` - Get analysis report
- **PATCH** `/api/files/reference/{file_reference}/null-count` - Update null_count by reference
- **PATCH** `/api/files/{file_id}/null-count` - Update null_count by ID
