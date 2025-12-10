"""
Background worker for processing batch generation jobs.
"""

import asyncio
import time
from app.services.batch_service import batch_service
from app.services.llm_client import llm_client
from app.services.logging_service import logging_service


async def process_batch_job(job_id: str):
    """
    Process a single batch job.
    
    Args:
        job_id: Job identifier to process
    """
    job_data = batch_service.get_job_status(job_id)
    
    if not job_data:
        logging_service.logger.error(f"Job not found: {job_id}")
        return
    
    # Update status to processing
    batch_service.update_job_status(job_id, 'processing')
    
    logging_service.log_batch_job(
        job_id=job_id,
        event='started',
        model=job_data['model_id'],
        task_count=job_data['task_count'],
        status='processing',
        metadata=job_data.get('metadata')
    )
    
    try:
        # Process all tasks
        results = await llm_client.batch_chat_completion(
            model_id=job_data['model_id'],
            tasks=job_data['tasks'],
            max_tokens=job_data['max_tokens'],
            temperature=job_data['temperature'],
            top_p=job_data['top_p']
        )
        
        # Update job with results
        batch_service.update_job_status(
            job_id=job_id,
            status='completed',
            results=results
        )
        
        logging_service.log_batch_job(
            job_id=job_id,
            event='completed',
            model=job_data['model_id'],
            task_count=job_data['task_count'],
            status='completed',
            completed_count=sum(1 for r in results if not r.get('error')),
            failed_count=sum(1 for r in results if r.get('error')),
            metadata=job_data.get('metadata')
        )
        
    except Exception as e:
        error_msg = str(e)
        batch_service.update_job_status(
            job_id=job_id,
            status='failed',
            error=error_msg
        )
        
        logging_service.log_batch_job(
            job_id=job_id,
            event='failed',
            model=job_data['model_id'],
            task_count=job_data['task_count'],
            status='failed',
            error=error_msg,
            metadata=job_data.get('metadata')
        )


async def worker_loop():
    """
    Main worker loop that processes batch jobs from the queue.
    """
    logging_service.logger.info("Batch worker started")
    
    while True:
        try:
            # Get next job from queue
            job_id = batch_service.get_next_job()
            
            if job_id:
                logging_service.logger.info(f"Processing job: {job_id}")
                await process_batch_job(job_id)
            else:
                # No jobs in queue, wait before checking again
                await asyncio.sleep(5)
                
        except Exception as e:
            logging_service.logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    # Run the worker
    asyncio.run(worker_loop())
