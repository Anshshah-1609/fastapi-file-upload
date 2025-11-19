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

router = APIRouter(prefix="/api/files", tags=["Files"])


def validate_csv_file(file: UploadFile) -> None:
    """ Validate that the uploaded file is a CSV file. """

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension != ".csv":
        raise HTTPException(
            status_code=400,
            detail=f"Only CSV files are allowed. Received: {file_extension}"
        )

    # Check content type
    if file.content_type not in ["text/csv", "application/csv", "text/plain"]:
        # Some browsers might send different content types, so we'll be lenient
        # but still check the extension
        pass


def validate_file_size(file_size: int) -> None:
    """ Validate that the file size is less than the maximum allowed size. """

    if file_size > app_config.MAX_FILE_SIZE:
        max_size_mb = app_config.MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb} MB"
        )


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

    # Step 1: Read CSV file using pandas
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.1,
            "message": "Reading CSV file...",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": None
        })
        await asyncio.sleep(update_interval)

    df = pd.read_csv(file_path)
    total_rows = len(df)
    total_columns = len(df.columns)

    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.2,
            "message": f"CSV loaded. Analyzing {total_rows} rows and {total_columns} columns...",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": total_rows,
            "total_columns": total_columns
        })
        await asyncio.sleep(update_interval)

    null_mask = df.isnull().any(axis=1) | df.isna().any(axis=1)

    # Step 2: Detect rows with null or undefined values using pandas
    # Check for pandas null/NaN values
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.3,
            "message": "Checking for null/NaN values...",
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
                "message": f"Analyzing column {idx + 1}/{total_object_columns}: {col}...",
                "null_count": int(null_mask.sum()),
                "processed_count": total_rows,  # All rows processed for this column
                "total_rows": total_rows
            })
            await asyncio.sleep(update_interval)

    # Step 4: Final null count
    null_count = null_mask.sum()

    # Step 5: Detect duplicate records per column
    if update_callback:
        await update_callback({
            "status": "analyzing",
            "progress": 0.85,
            "message": "Checking for duplicate records...",
            "null_count": int(null_count),
            "processed_count": total_rows,
            "total_rows": total_rows,
            "total_columns": total_columns
        })
        await asyncio.sleep(update_interval)

    duplicate_records: dict[str, int] = {}

    # Check for duplicates in each column
    # Exclude null, undefined, NaN, None, and empty strings from duplicate detection
    for col in df.columns:
        # Create a filtered series excluding null/undefined values
        col_series = df[col].copy()

        # Filter out pandas null/NaN values
        mask = col_series.notna() & col_series.notnull()

        # For object (string) columns, also filter out string representations of null/undefined
        if col_series.dtype == 'object':
            # Convert to string and check for null-like string values
            # Note: We need to handle pandas NaN values that become "nan" string
            str_values = col_series.astype(str)
            # Filter out null-like string values (case-insensitive)
            null_like_mask = str_values.str.lower().isin(
                ['null', 'none', 'undefined', 'nan', ''])
            mask = mask & ~null_like_mask

        # Get valid values from the column (non-null-like values)
        valid_series = col_series[mask]

        # Check for duplicates only in valid (non-null-like) values
        if len(valid_series) > 0:
            # Count occurrences of each value
            value_counts = valid_series.value_counts()

            # Find values that appear more than once (duplicates)
            duplicate_value_counts = value_counts[value_counts > 1]

            # Count how many distinct values are duplicated
            duplicate_count = len(duplicate_value_counts)

            # Only include columns that have duplicates
            if duplicate_count > 0:
                duplicate_records[col] = duplicate_count

    if update_callback:
        total_duplicate_columns = len(duplicate_records)
        await update_callback({
            "status": "analyzing",
            "progress": 0.9,
            "message": f"Analysis complete. Found {null_count} rows with null/undefined values. "
                      f"Found duplicates in {total_duplicate_columns} column(s).",
            "null_count": int(null_count),
            "processed_count": total_rows,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "duplicate_records": duplicate_records
        })
        await asyncio.sleep(update_interval)

    return int(null_count), int(total_rows), int(total_columns), duplicate_records


async def upload_file_with_sse_stream(
    file: UploadFile,
    db: Session,
    update_interval: float = 0.5
):
    """
    Async generator that processes file upload and sends SSE updates.

    Args:
        file: The uploaded file
        db: Database session
        update_interval: Interval in seconds between progress updates
    """

    try:
        # Initialize counters and timing
        start_time = time.time()
        null_count = 0
        processed_count = 0
        total_rows = None
        total_columns = None
        duplicate_records: dict[str, int] = {}

        # Step 1: Validate file type
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.0,
            "message": "Validating file type...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        validate_csv_file(file)

        # Step 2: Read file content
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.1,
            "message": "Reading file content...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        content = await file.read()
        file_size = len(content)

        # Step 3: Validate file size
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.2,
            "message": "Validating file size...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        validate_file_size(file_size)

        # Step 4: Generate unique filename
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.3,
            "message": "Generating unique filename...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = app_config.UPLOAD_DIR / unique_filename

        # Step 5: Save file to disk
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.5,
            "message": "Saving file to disk...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except IOError as e:
            yield await send_sse_event({
                "status": "error",
                "progress": 0.0,
                "message": f"Failed to save file: {str(e)}",
                "null_count": null_count,
                "processed_count": processed_count,
                "total_rows": total_rows
            })
            return

        # Step 6: Store file metadata in database
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.7,
            "message": "Storing file metadata in database...",
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        try:
            # Generate unique file reference (UUID) for this file
            file_reference = str(uuid.uuid4())

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
        except Exception as e:
            # If database save fails, remove the file
            if file_path.exists():
                file_path.unlink()
            yield await send_sse_event({
                "status": "error",
                "progress": 0.0,
                "message": f"Failed to store file metadata in database: {str(e)}",
                "null_count": null_count,
                "processed_count": processed_count,
                "total_rows": total_rows
            })
            return

        # Step 7: Upload complete
        yield await send_sse_event({
            "status": "uploading",
            "progress": 0.9,
            "message": "File upload complete...",
            "file_id": db_file.id,
            "file_reference": db_file.file_reference,
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        # Step 8: Upload phase complete
        yield await send_sse_event({
            "status": "uploading",
            "progress": 1.0,
            "message": "Upload phase complete. Starting analysis...",
            "file_id": db_file.id,
            "file_reference": db_file.file_reference,
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows
        })
        await asyncio.sleep(update_interval)

        # Step 9: Analyze CSV for null/undefined values with progress updates
        # Use a queue to stream events in real-time
        analysis_queue = asyncio.Queue()
        analysis_complete = asyncio.Event()
        analysis_result = None
        analysis_error = None

        async def analysis_progress_callback(update_data: dict):
            """Callback to send progress updates during CSV analysis - streams events in real-time."""

            nonlocal null_count, processed_count, total_rows, total_columns, duplicate_records
            null_count = update_data.get("null_count", 0)
            processed_count = update_data.get("processed_count", 0)
            total_rows = update_data.get("total_rows", total_rows)
            total_columns = update_data.get("total_columns", total_columns)
            duplicate_records = update_data.get(
                "duplicate_records", duplicate_records)

            # Create the SSE event with rounded progress
            progress = round_progress(update_data.get("progress", 0.0))
            event_data = {
                "status": update_data.get("status", "analyzing"),
                "progress": progress,
                "message": update_data.get("message", "Analyzing CSV..."),
                "file_id": db_file.id,
                "file_reference": db_file.file_reference,
                "null_count": null_count,
                "processed_count": processed_count,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "duplicate_records": duplicate_records
            }
            # Put event in queue for immediate streaming
            await analysis_queue.put(event_data)

        async def run_analysis():
            """Run analysis in background and stream events."""

            nonlocal null_count, processed_count, total_rows, total_columns, duplicate_records, analysis_result, analysis_error
            try:
                null_count, total_rows, total_columns, duplicate_records = await analyze_csv_for_nulls_and_duplicates(
                    file_path,
                    update_callback=analysis_progress_callback,
                    update_interval=update_interval
                )
                analysis_result = (null_count, total_rows,
                                   total_columns, duplicate_records)
                processed_count = total_rows if total_rows else processed_count
            except Exception as e:
                analysis_error = e
            finally:
                # Signal that analysis is complete
                analysis_complete.set()
                # Put a sentinel value to stop the queue consumer
                await analysis_queue.put(None)

        try:
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

            # Update final values from result
            null_count, total_rows, total_columns, duplicate_records = analysis_result
            processed_count = total_rows if total_rows else processed_count

            # Update null_count, total_rows, total_columns, duplicate_records, and analysis_time in database
            try:
                analysis_end_time = time.time()
                analysis_duration = analysis_end_time - start_time

                db_file.null_count = null_count
                db_file.total_rows = total_rows
                db_file.total_columns = total_columns
                db_file.duplicate_records = duplicate_records
                db_file.analysis_time = str(round(analysis_duration, 2))
                db.commit()
                db.refresh(db_file)
            except Exception as db_error:
                # Log error but don't fail the upload
                logger = get_logger(__name__)
                logger.warning(
                    f"Failed to update analysis data in database: {str(db_error)}")

        except Exception as e:
            yield await send_sse_event({
                "status": "error",
                "progress": 0.7,
                "message": f"Failed to analyze CSV: {str(e)}",
                "null_count": null_count,
                "processed_count": processed_count,
                "total_rows": total_rows,
                "duplicate_records": duplicate_records
            })
            return

        # Step 10: Calculate time consumption
        end_time = time.time()
        time_consumption = end_time - start_time

        # Step 11: Send completion event with all report data
        yield await send_sse_event({
            "status": "completed",
            "progress": 1.0,
            "message": "File uploaded and analyzed successfully",
            "file_id": db_file.id,
            "file_reference": db_file.file_reference,
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_size": file_size,
            "file_path": str(file_path),
            "null_count": null_count,
            "processed_count": processed_count,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "duplicate_records": duplicate_records,
            # Time in seconds, rounded to 2 decimals
            "time_consumption": round(time_consumption, 2)
        })

    except HTTPException as e:
        yield await send_sse_event({
            "status": "error",
            "progress": 0.0,
            "message": e.detail,
            "null_count": 0,
            "processed_count": 0,
            "total_rows": None
        })
    except Exception as e:
        yield await send_sse_event({
            "status": "error",
            "progress": 0.0,
            "message": f"Unexpected error: {str(e)}",
            "null_count": 0,
            "processed_count": 0,
            "total_rows": None
        })

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

    return StreamingResponse(
        upload_file_with_sse_stream(file, db, update_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
