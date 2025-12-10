"""
Batch generation endpoints router.
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    BatchGenerationRequest,
    BatchSubmissionResponse,
    BatchStatusResponse,
    BatchTaskResult,
    ErrorResponse,
    UsageInfo
)
from app.auth import verify_api_key
from app.config import model_registry
from app.services.batch_service import batch_service
from app.services.logging_service import logging_service


router = APIRouter(prefix="/v1/batch", tags=["batch"])


@router.post(
    "/generate",
    response_model=BatchSubmissionResponse,
    responses={
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def submit_batch_generation(
    request: BatchGenerationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit a batch generation job for asynchronous processing.
    
    This endpoint accepts multiple generation tasks and processes them in the background.
    Use the returned `job_id` to check status and retrieve results.
    
    **Example Request:**
    ```json
    {
        "model": "llama-7b",
        "tasks": [
            {
                "id": "task-1",
                "messages": [
                    {"role": "system", "content": "Generate synthetic profiles."},
                    {"role": "user", "content": "Create a fitness client profile."}
                ]
            },
            {
                "id": "task-2",
                "messages": [
                    {"role": "system", "content": "Generate synthetic profiles."},
                    {"role": "user", "content": "Create a patient profile."}
                ]
            }
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    ```
    """
    # Validate model
    if not model_registry.is_valid_model(request.model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model: {request.model}"
        )
    
    # Submit job
    job_id = batch_service.submit_batch_job(
        model_id=request.model,
        tasks=[{"id": task.id, "messages": task.messages} for task in request.tasks],
        max_tokens=request.max_tokens or 512,
        temperature=request.temperature or 0.7,
        top_p=request.top_p or 0.95,
        metadata=request.batch_metadata
    )
    
    # Log submission
    logging_service.log_batch_job(
        job_id=job_id,
        event='submitted',
        model=request.model,
        task_count=len(request.tasks),
        status='queued',
        metadata=request.batch_metadata
    )
    
    return BatchSubmissionResponse(
        job_id=job_id,
        status='queued',
        submitted_at=int(time.time()),
        task_count=len(request.tasks)
    )


@router.get(
    "/{job_id}",
    response_model=BatchStatusResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    }
)
async def get_batch_status(
    job_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get the status of a batch generation job.
    
    Returns the current status and results (if completed) for the specified job.
    
    **Job Statuses:**
    - `queued`: Job is waiting to be processed
    - `processing`: Job is currently being processed
    - `completed`: Job has finished successfully
    - `failed`: Job encountered an error
    """
    job_data = batch_service.get_job_status(job_id)
    
    if not job_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    # Convert results to proper schema
    results = None
    if job_data.get('results'):
        results = [
            BatchTaskResult(
                id=r['id'],
                output=r['output'],
                usage=UsageInfo(**r['usage']),
                error=r.get('error')
            )
            for r in job_data['results']
        ]
    
    return BatchStatusResponse(
        job_id=job_data['job_id'],
        status=job_data['status'],
        submitted_at=job_data['submitted_at'],
        started_at=job_data.get('started_at'),
        completed_at=job_data.get('completed_at'),
        task_count=job_data['task_count'],
        completed_count=job_data.get('completed_count', 0),
        failed_count=job_data.get('failed_count', 0),
        results=results,
        error=job_data.get('error')
    )
