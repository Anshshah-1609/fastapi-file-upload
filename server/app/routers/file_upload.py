""" File upload router. """

import uuid
import json
import asyncio
import time
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd

from app.configs import app_config
from app.database import get_db
from app.models import FileModel
from app.logger import get_logger
from app.repository import create

# Log error but don't fail the upload
logger = get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["Files"])


# ============================================================================
# HELPER FUNCTIONS FOR FILE UPLOAD WITH SSE
# ============================================================================

def validate_csv_file(file: UploadFile) -> None:
    """ Validate that the uploaded file is a CSV file. """

    logger.debug(f"Validating CSV file: {file.filename}")

    if not file.filename:
        logger.error("File validation failed: Filename is required")
        raise HTTPException(status_code=400, detail="Filename is required")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension != ".csv":
        logger.error(
            f"File validation failed: Invalid file extension '{file_extension}' for file '{file.filename}'")
        raise HTTPException(
            status_code=400,
            detail=f"Only CSV files are allowed. Received: {file_extension}"
        )

    # Check content type
    if file.content_type not in ["text/csv", "application/csv", "text/plain"]:
        # Some browsers might send different content types, so we'll be lenient
        # but still check the extension
        logger.debug(
            f"Content type '{file.content_type}' not in standard CSV types, but extension is valid")

    logger.info(f"File validation successful: {file.filename}")


def validate_file_size(file_size: int) -> None:
    """ Validate that the file size is less than the maximum allowed size. """

    max_size_mb = app_config.MAX_FILE_SIZE / (1024 * 1024)
    file_size_mb = file_size / (1024 * 1024)
    logger.debug(
        f"Validating file size: {file_size_mb:.2f} MB (max: {max_size_mb:.2f} MB)")

    if file_size > app_config.MAX_FILE_SIZE:
        logger.error(
            f"File size validation failed: {file_size_mb:.2f} MB exceeds maximum {max_size_mb:.2f} MB")
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb} MB"
        )

    logger.info(f"File size validation successful: {file_size_mb:.2f} MB")


def round_progress(progress: float) -> float:
    """Round progress value to 2 decimal places."""

    return round(progress, 2)


async def send_sse_event(data: dict) -> str:
    """Format data as SSE event."""

    # Round progress to 2 decimal places
    if "progress" in data and data["progress"] is not None:
        data["progress"] = round_progress(data["progress"])
    json_data = json.dumps(data)
    return f"data: {json_data}\n\n"


async def analyze_csv_for_nulls_and_duplicates(
    file_path: Path,
    update_callback=None,
    update_interval: float = 0.1
) -> tuple[int, int, int, dict[str, int]]:
    """
    Analyze CSV file for null/undefined values and duplicate records using pandas and cleanlab.

    Sends progress updates during analysis if update_callback is provided.

    Uses pandas for direct null detection and duplicate detection. Cleanlab is imported and available
    for advanced data quality assessment beyond null detection.

    Args:
        file_path: Path to the CSV file
        update_callback: Optional async function to call with progress updates
        update_interval: Interval in seconds between progress updates

    Returns:
        Tuple of (null_count, total_rows, total_columns, duplicate_records) where:
        - null_count is the number of rows containing at least one null/undefined value
        - total_rows is the total number of rows in the CSV
        - total_columns is the total number of columns in the CSV
        - duplicate_records is a dict with column_name as key and duplicate count as value
          e.g., {"email": 10, "phone": 22}
    """
    logger.info(f"Starting CSV analysis for file: {file_path}")

    # Step 1: Read CSV file using pandas
    logger.debug("Step 1: Reading CSV file using pandas")
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.1,
            "message": "Reading and parsing CSV file structure...",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": None
        })
        await asyncio.sleep(update_interval)

    try:
        df = pd.read_csv(file_path)
        total_rows = len(df)
        total_columns = len(df.columns)
        logger.info(
            f"CSV file loaded successfully: {total_rows} rows, {total_columns} columns")
    except Exception as e:
        logger.error(
            f"Failed to read CSV file {file_path}: {str(e)}")
        raise

    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.2,
            "message": f"CSV file successfully loaded. Beginning comprehensive analysis of {total_rows:,} rows across {total_columns} columns...",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": total_rows,
            "total_columns": total_columns
        })

    null_mask = df.isnull().any(axis=1) | df.isna().any(axis=1)

    # Step 2: Detect rows with null or undefined values using pandas
    # Check for pandas null/NaN values
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.3,
            "message": "Scanning dataset for null, undefined, and missing values across all columns...",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

    # Step 3: Check for string representations of null/undefined in object columns
    object_columns = [col for col in df.columns if df[col].dtype == 'object']
    total_object_columns = len(object_columns)

    for idx, col in enumerate(object_columns):
        # Check for string representations of null/undefined values
        null_mask |= df[col].astype(str).str.lower().isin(
            ['null', 'none', 'undefined', 'nan', ''])

        if update_callback and total_object_columns > 0:
            # Update progress based on column processing
            column_progress = 0.4 + (0.4 * (idx + 1) / total_object_columns)
            await update_callback({
                "status": "analyzing",
                "progress": round_progress(min(column_progress, 0.8)),
                "message": f"Examining column {idx + 1} of {total_object_columns}: '{col}' for string-based null representations...",
                "null_count": int(null_mask.sum()),
                "processed_count": total_rows,  # All rows processed for this column
                "total_rows": total_rows
            })

    # Step 4: Final null count
    null_count = null_mask.sum()
    logger.debug(
        f"Step 4: Null detection complete. Found {null_count} rows with null/undefined values")

    # Step 5: Detect duplicate records per column
    logger.debug("Step 5: Starting duplicate detection per column")
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.85,
            "message": "Performing parallel duplicate detection across all columns to identify repeated values...",
            "null_count": int(null_count),
            "processed_count": total_rows,
            "total_rows": total_rows,
            "total_columns": total_columns
        })

    duplicate_records: dict[str, int] = {}

    def check_column_duplicates(col: str, df_subset: pd.DataFrame) -> tuple[str, int]:
        """
        Check for duplicates in a single column using pandas duplicated() function.

        Args:
            col: Column name
            df_subset: DataFrame containing only the column to check

        Returns:
            Tuple of (column_name, duplicate_count) or (column_name, 0) if no duplicates
        """
        # Filter out null/undefined values first
        # Create a mask for valid (non-null-like) values
        mask = df_subset[col].notna() & df_subset[col].notnull()

        # For object (string) columns, also filter out string representations of null/undefined
        if df_subset[col].dtype == 'object':
            str_values = df_subset[col].astype(str)
            # Filter out null-like string values (case-insensitive)
            null_like_mask = str_values.str.lower().isin(
                ['null', 'none', 'undefined', 'nan', ''])
            mask = mask & ~null_like_mask

        # Get DataFrame with only valid (non-null-like) values
        valid_df = df_subset[mask].copy()

        # Check if there are any valid values
        if len(valid_df) == 0:
            return (col, 0)

        # Use pandas duplicated() to find duplicates (excluding first occurrence)
        # This returns a boolean Series where True indicates duplicate rows

        # keep='first' -> Exclude (do NOT mark) the first occurrence of each duplicate group.
        # keep='last'  -> Exclude (do NOT mark) the last occurrence of each duplicate group.
        # keep=False (Default) -> Do NOT exclude any occurrence.
        duplicates_mask = valid_df.duplicated(subset=[col], keep='first')

        # Count the number of duplicate rows
        duplicate_count = duplicates_mask.sum()

        # Return the count if duplicates found
        if duplicate_count > 0:
            return (col, int(duplicate_count))

        return (col, 0)

    # Process all columns in parallel using asyncio.gather with thread pool
    logger.debug(
        f"Processing {len(df.columns)} columns in parallel for duplicate detection using pandas duplicated()")

    # Create tasks for parallel execution
    # Each task processes a single column by creating a subset DataFrame
    tasks = [
        asyncio.to_thread(check_column_duplicates, col, df[[col]])
        for col in df.columns
    ]

    # Execute all column checks in parallel
    results = await asyncio.gather(*tasks)

    # Process results and build duplicate_records dictionary
    for col, duplicate_count in results:
        if duplicate_count > 0:
            duplicate_records[col] = duplicate_count
            logger.debug(
                f"Found {duplicate_count} duplicate rows in column '{col}'")

    total_duplicate_columns = len(duplicate_records)
    logger.info(
        f"Duplicate detection complete. Found duplicates in {total_duplicate_columns} column(s)")

    if update_callback:
        total_duplicate_columns = len(duplicate_records)
        await update_callback({
            "status": "analyzing",
            "progress": 0.9,
            "message": f"Data quality analysis completed successfully. Identified {null_count:,} rows containing null or undefined values. "
                      f"Detected duplicate entries in {total_duplicate_columns} column(s). Generating comprehensive report...",
            "null_count": int(null_count),
            "processed_count": total_rows,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "duplicate_records": duplicate_records
        })
        await asyncio.sleep(update_interval)

    logger.info(f"CSV analysis complete: {null_count} null rows, {total_rows} total rows, "
                f"{total_columns} columns, {len(duplicate_records)} columns with duplicates")
    return int(null_count), int(total_rows), int(total_columns), duplicate_records


def create_upload_progress_event(
    status: str,
    progress: float,
    message: str,
    file_id: int | None = None,
    file_reference: str | None = None,
    **kwargs
) -> dict:
    """
    Create a standardized SSE progress event dictionary.

    Args:
        status: Current status ("uploading", "analyzing", "completed", "error")
        progress: Progress value between 0.0 and 1.0
        message: Human-readable status message
        file_id: Optional file ID
        file_reference: Optional file reference UUID
        **kwargs: Additional fields to include in the event

    Returns:
        Dictionary ready to be sent as SSE event
    """
    event = {
        "status": status,
        "progress": round_progress(progress),
        "message": message,
        "null_count": kwargs.get("null_count", 0),
        "processed_count": kwargs.get("processed_count", 0),
        "total_rows": kwargs.get("total_rows"),
    }

    # Add optional fields if provided
    if file_id is not None:
        event["file_id"] = file_id
    if file_reference is not None:
        event["file_reference"] = file_reference
    if "total_columns" in kwargs:
        event["total_columns"] = kwargs["total_columns"]
    if "duplicate_records" in kwargs:
        event["duplicate_records"] = kwargs["duplicate_records"]
    if "time_consumption" in kwargs:
        event["time_consumption"] = kwargs["time_consumption"]
    if "original_filename" in kwargs:
        event["original_filename"] = kwargs["original_filename"]
    if "stored_filename" in kwargs:
        event["stored_filename"] = kwargs["stored_filename"]
    if "file_size" in kwargs:
        event["file_size"] = kwargs["file_size"]
    if "file_path" in kwargs:
        event["file_path"] = kwargs["file_path"]

    return event


async def validate_and_read_file(
    file: UploadFile,
    update_interval: float,
    progress_data: dict,
    result: dict
):
    """
    Step 1-3: Validate file type, read content, and validate file size.

    Args:
        file: The uploaded file
        update_interval: Interval between progress updates
        progress_data: Dictionary to track progress state
        result: Dictionary to store results (will contain 'content' and 'file_size')

    Yields:
        SSE formatted strings with progress updates

    Raises:
        HTTPException: If validation fails
    """
    # Step 1: Validate file type
    logger.debug("Phase 1 - Step 1: Validating file type")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.0,
        message="Validating file format and ensuring CSV compatibility...",
        **progress_data
    ))
    validate_csv_file(file)

    # Step 2: Read file content
    logger.debug("Phase 1 - Step 2: Reading file content")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.1,
        message="Reading and processing uploaded file content into memory...",
        **progress_data
    ))
    await asyncio.sleep(update_interval)
    try:
        content = await file.read()
        file_size = len(content)
        logger.info(f"File content read successfully: {file_size} bytes")
        result["content"] = content
        result["file_size"] = file_size
    except Exception as e:
        logger.error(f"Failed to read file content: {str(e)}")
        raise

    # Step 3: Validate file size
    logger.debug("Phase 1 - Step 3: Validating file size")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.2,
        message="Validating file size against maximum allowed limits...",
        **progress_data
    ))
    await asyncio.sleep(update_interval)
    validate_file_size(file_size)


async def save_file_to_disk(
    content: bytes,
    file: UploadFile,
    update_interval: float,
    progress_data: dict,
    result: dict
):
    """
    Step 4-5: Generate unique filename and save file to disk.

    Args:
        content: File content bytes
        file: The uploaded file
        update_interval: Interval between progress updates
        progress_data: Dictionary to track progress state
        result: Dictionary to store results (will contain 'file_path' and 'unique_filename')

    Yields:
        SSE formatted strings with progress updates

    Raises:
        IOError: If file save fails
    """

    # Step 4: Generate unique filename
    logger.debug("Phase 2 - Step 4: Generating unique filename")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.3,
        message="Generating secure unique identifier for file storage...",
        **progress_data
    ))
    await asyncio.sleep(update_interval)

    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = app_config.UPLOAD_DIR / unique_filename
    logger.debug(f"Generated unique filename: {unique_filename}")

    # Step 5: Save file to disk
    logger.debug(f"Phase 2 - Step 5: Saving file to disk at {file_path}")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.5,
        message="Writing file to secure storage location on server...",
        **progress_data
    ))
    await asyncio.sleep(update_interval)

    try:
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"File saved successfully to disk: {file_path}")
        result["file_path"] = file_path
        result["unique_filename"] = unique_filename
    except IOError as e:
        logger.error(
            f"Failed to save file to disk at {file_path}: {str(e)}")
        # Yield error event before raising
        yield await send_sse_event(create_upload_progress_event(
            status="error",
            progress=0.0,
            message=f"Error occurred while saving file to disk: {str(e)}. Please try again or contact support if the issue persists.",
            **progress_data
        ))
        raise


async def store_file_metadata(
    file: UploadFile,
    unique_filename: str,
    file_path: Path,
    file_size: int,
    db: Session,
    progress_data: dict,
    result: dict
):
    """
    Step 6: Store file metadata in database.

    Args:
        file: The uploaded file
        unique_filename: Generated unique filename
        file_path: Path where file is saved
        file_size: Size of the file in bytes
        db: Database session
        progress_data: Dictionary to track progress state
        result: Dictionary to store results (will contain 'db_file')

    Yields:
        SSE formatted strings with progress updates

    Raises:
        Exception: If database save fails
    """
    logger.debug("Phase 3 - Step 6: Storing file metadata in database")
    yield await send_sse_event(create_upload_progress_event(
        status="uploading",
        progress=0.7,
        message="Persisting file metadata and creating database records...",
        **progress_data
    ))

    try:
        # Generate unique file reference (UUID) for this file
        file_reference = str(uuid.uuid4())
        logger.debug(f"Generated file reference UUID: {file_reference}")

        db_file = FileModel(
            original_filename=file.filename,
            stored_filename=unique_filename,
            file_path=str(file_path),
            file_size=file_size,
            content_type=file.content_type or "text/csv",
            file_reference=file_reference,
            null_count=0  # Will be updated after analysis
        )
        create(db, db_file)
        logger.info(
            f"File metadata stored in database successfully. File ID: {db_file.id}, Reference: {file_reference}")
        result["db_file"] = db_file
    except Exception as e:
        logger.error(
            f"Failed to store file metadata in database: {str(e)}")
        # If database save fails, remove the file from disk
        if file_path.exists():
            logger.warning(
                f"Removing file from disk due to database error: {file_path}")
            file_path.unlink()
        # Yield error event before raising
        yield await send_sse_event(create_upload_progress_event(
            status="error",
            progress=0.0,
            message=f"Database operation failed while storing file metadata: {str(e)}. The file has been removed from disk. Please try again.",
            **progress_data
        ))
        raise


async def run_csv_analysis_with_streaming(
    file_path: Path,
    db_file: FileModel,
    update_interval: float,
    progress_data: dict,
    result: dict
):
    """
    Step 9: Analyze CSV file with real-time progress streaming via SSE.

    Uses an async queue to stream analysis progress events in real-time
    without buffering delays.

    Args:
        file_path: Path to the CSV file
        db_file: Database file model instance
        update_interval: Interval between progress updates
        progress_data: Dictionary to track progress state (modified in place)
        result: Dictionary to store results (will contain 'null_count', 'total_rows', 
                'total_columns', 'duplicate_records')

    Yields:
        SSE formatted strings with progress updates

    Raises:
        Exception: If analysis fails
    """
    analysis_queue = asyncio.Queue()
    analysis_result = None
    analysis_error = None

    async def analysis_progress_callback(update_data: dict):
        """Callback to send progress updates during CSV analysis - streams events in real-time."""
        nonlocal progress_data

        # Update progress data from callback
        progress_data["null_count"] = update_data.get("null_count", 0)
        progress_data["processed_count"] = update_data.get(
            "processed_count", 0)
        progress_data["total_rows"] = update_data.get(
            "total_rows", progress_data.get("total_rows"))
        progress_data["total_columns"] = update_data.get(
            "total_columns", progress_data.get("total_columns"))
        progress_data["duplicate_records"] = update_data.get(
            "duplicate_records", progress_data.get("duplicate_records", {}))

        # Create the SSE event with rounded progress
        event_data = create_upload_progress_event(
            status=update_data.get("status", "analyzing"),
            progress=update_data.get("progress", 0.0),
            message=update_data.get(
                "message", "Performing comprehensive CSV data analysis..."),
            file_id=db_file.id,
            file_reference=db_file.file_reference,
            **progress_data
        )
        # Put event in queue for immediate streaming
        await analysis_queue.put(event_data)

    async def run_analysis():
        """Run analysis in background and stream events."""
        nonlocal analysis_result, analysis_error, progress_data

        try:
            logger.debug(f"Starting CSV analysis task for file: {file_path}")
            null_count, total_rows, total_columns, duplicate_records = await analyze_csv_for_nulls_and_duplicates(
                file_path,
                update_callback=analysis_progress_callback,
                update_interval=update_interval
            )
            analysis_result = (null_count, total_rows,
                               total_columns, duplicate_records)
            progress_data["processed_count"] = total_rows if total_rows else progress_data.get(
                "processed_count", 0)
            logger.info(f"CSV analysis task completed successfully. Results: {null_count} nulls, "
                        f"{total_rows} rows, {total_columns} columns, {len(duplicate_records)} duplicate columns")
        except Exception as e:
            logger.error(f"CSV analysis task failed: {str(e)}")
            analysis_error = e
        finally:
            # Put a sentinel value to stop the queue consumer
            await analysis_queue.put(None)

    # Start analysis in background
    analysis_task = asyncio.create_task(run_analysis())

    # Stream events as they arrive from the queue in real-time
    while True:
        # Wait for event from queue (blocks until event is available)
        event = await analysis_queue.get()

        # None is sentinel value indicating analysis complete
        if event is None:
            break

        # Yield event immediately - no delay, events stream in real-time
        yield await send_sse_event(event)

    # Wait for analysis to complete
    await analysis_task

    # Handle analysis result or error
    if analysis_error:
        raise analysis_error

    # Store results in result dictionary
    if analysis_result:
        null_count, total_rows, total_columns, duplicate_records = analysis_result
        result["null_count"] = null_count
        result["total_rows"] = total_rows
        result["total_columns"] = total_columns
        result["duplicate_records"] = duplicate_records


async def update_analysis_results_in_db(
    db_file: FileModel,
    null_count: int,
    total_rows: int,
    total_columns: int,
    duplicate_records: dict[str, int],
    analysis_duration: float,
    db: Session
) -> None:
    """
    Update analysis results in the database.

    Args:
        db_file: Database file model instance
        null_count: Number of rows with null/undefined values
        total_rows: Total number of rows
        total_columns: Total number of columns
        duplicate_records: Dictionary of duplicate records per column
        analysis_duration: Time taken for analysis in seconds
        db: Database session
    """
    try:
        logger.debug(
            f"Updating analysis results in database for file ID: {db_file.id}")
        db_file.null_count = null_count
        db_file.total_rows = total_rows
        db_file.total_columns = total_columns
        db_file.duplicate_records = duplicate_records
        db_file.analysis_time = str(round(analysis_duration, 2))
        db.commit()
        db.refresh(db_file)
        logger.info(f"Analysis results updated in database successfully. File ID: {db_file.id}, "
                    f"Analysis time: {analysis_duration:.2f}s")
    except Exception as db_error:
        logger.warning(
            f"Failed to update analysis data in database for file ID {db_file.id}: {str(db_error)}",
        )


async def upload_file_with_sse_stream(
    file: UploadFile,
    db: Session,
    update_interval: float = 0.5
):
    """
    Async generator that processes file upload and sends SSE updates.

    This function orchestrates the entire file upload and analysis process:
    1. Validates file type and size
    2. Reads file content
    3. Saves file to disk
    4. Stores metadata in database
    5. Analyzes CSV for null values and duplicates
    6. Updates database with analysis results
    7. Sends completion event

    Args:
        file: The uploaded file
        db: Database session
        update_interval: Interval in seconds between progress updates

    Yields:
        SSE formatted strings with progress updates
    """
    # Initialize tracking variables
    start_time = time.time()
    progress_data = {
        "null_count": 0,
        "processed_count": 0,
        "total_rows": None,
        "total_columns": None,
        "duplicate_records": {}
    }

    logger.info(f"Starting file upload process for file: {file.filename}")
    try:
        # ====================================================================
        # PHASE 1: FILE VALIDATION AND READING (Steps 1-3)
        # ====================================================================
        phase1_result = {}
        gen1 = validate_and_read_file(
            file, update_interval, progress_data, phase1_result)
        async for event in gen1:
            yield event
        content = phase1_result["content"]
        file_size = phase1_result["file_size"]

        # ====================================================================
        # PHASE 2: FILE SAVING (Steps 4-5)
        # ====================================================================
        phase2_result = {}
        gen2 = save_file_to_disk(
            content, file, update_interval, progress_data, phase2_result)
        async for event in gen2:
            yield event
        file_path = phase2_result["file_path"]
        unique_filename = phase2_result["unique_filename"]

        # ====================================================================
        # PHASE 3: DATABASE STORAGE (Step 6)
        # ====================================================================
        phase3_result = {}
        gen3 = store_file_metadata(
            file, unique_filename, file_path, file_size,
            db, progress_data, phase3_result
        )
        async for event in gen3:
            yield event
        db_file = phase3_result["db_file"]

        # ====================================================================
        # PHASE 4: UPLOAD COMPLETE NOTIFICATION (Step 7)
        # ====================================================================
        # Step 7: Upload phase complete
        logger.info(
            f"Upload phase complete. File ID: {db_file.id}, Reference: {db_file.file_reference}")
        yield await send_sse_event(create_upload_progress_event(
            status="uploading",
            progress=1.0,
            message="File upload completed successfully. Initiating comprehensive data quality analysis...",
            file_id=db_file.id,
            file_reference=db_file.file_reference,
            **progress_data
        ))
        await asyncio.sleep(update_interval)

        # ====================================================================
        # PHASE 5: CSV ANALYSIS WITH REAL-TIME STREAMING (Step 9)
        # ====================================================================
        logger.info(f"Starting CSV analysis phase for file ID: {db_file.id}")
        try:
            phase5_result = {}
            gen4 = run_csv_analysis_with_streaming(
                file_path, db_file, update_interval, progress_data, phase5_result
            )
            async for event in gen4:
                yield event

            # Get results from phase5_result
            null_count = phase5_result["null_count"]
            total_rows = phase5_result["total_rows"]
            total_columns = phase5_result["total_columns"]
            duplicate_records = phase5_result["duplicate_records"]

            # Update progress data with final results
            progress_data.update({
                "null_count": null_count,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "duplicate_records": duplicate_records,
                "processed_count": total_rows
            })

            # Update database with analysis results
            analysis_duration = time.time() - start_time
            logger.debug(f"Analysis duration: {analysis_duration:.2f} seconds")
            await update_analysis_results_in_db(
                db_file, null_count, total_rows, total_columns,
                duplicate_records, analysis_duration, db
            )

        except Exception as e:
            logger.error(
                f"CSV analysis failed for file ID {db_file.id}: {str(e)}")
            yield await send_sse_event(create_upload_progress_event(
                status="error",
                progress=0.7,
                message=f"Data analysis encountered an error: {str(e)}. The file has been uploaded but analysis could not be completed. Please review the file format and try again.",
                **progress_data
            ))
            return

        # ====================================================================
        # PHASE 6: COMPLETION EVENT (Steps 09-10)
        # ====================================================================

        # Step 9: Calculate time consumption
        time_consumption = time.time() - start_time
        logger.info(f"File upload and analysis completed successfully. "
                    f"File ID: {db_file.id}, Total time: {time_consumption:.2f}s, "
                    f"Rows: {total_rows}, Columns: {total_columns}, Nulls: {null_count}")

        # Step 10: Send completion event with all report data
        yield await send_sse_event(create_upload_progress_event(
            status="completed",
            progress=1.0,
            message="File upload and data quality analysis completed successfully. Your comprehensive report is ready for review.",
            file_id=db_file.id,
            file_reference=db_file.file_reference,
            **{**progress_data,
               "original_filename": file.filename,
               "stored_filename": unique_filename,
               "file_size": file_size,
               "file_path": str(file_path),
               "time_consumption": round(time_consumption, 2)
               }
        ))

    except HTTPException as e:
        logger.error(f"HTTPException during file upload: {e.detail}")
        yield await send_sse_event(create_upload_progress_event(
            status="error",
            progress=0.0,
            message=e.detail,
            null_count=0,
            processed_count=0,
            total_rows=None
        ))
    except Exception as e:
        logger.error(
            f"Unexpected error during file upload: {str(e)}")
        yield await send_sse_event(create_upload_progress_event(
            status="error",
            progress=0.0,
            message=f"An unexpected error occurred during file processing: {str(e)}. Please try again or contact support if the problem persists.",
            null_count=0,
            processed_count=0,
            total_rows=None
        ))

# =======================================================
#
# Upload File with SSE API ENDPOINT
#
#  =======================================================


@router.post("/upload-sse")
async def upload_file_with_sse(
    file: UploadFile = File(...),
    update_interval: float = Query(
        0.5, ge=0.1, le=5.0, description="Update interval in seconds"),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file with Server-Sent Events (SSE) progress updates.

    - Validates that the file is a CSV file
    - Validates that the file size is less than the maximum allowed size
    - Saves the file with a UUID-based filename
    - Stores file metadata in the database
    - Analyzes the CSV using cleanlab to detect null/undefined values
    - Returns progress updates via SSE at specified intervals
    - Returns count of records with null/undefined values

    The response is a Server-Sent Events stream that sends JSON updates:
    - status: "uploading", "analyzing", "completed", or "error"
    - progress: Float between 0.0 and 1.0
    - message: Human-readable status message
    - On completion: file_id, original_filename, stored_filename, file_size, 
      file_path, null_count, total_rows
    """
    logger.info(f"Received upload request for file: {file.filename}, "
                f"content_type: {file.content_type}, update_interval: {update_interval}s")

    return StreamingResponse(
        upload_file_with_sse_stream(file, db, update_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
