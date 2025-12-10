"""
Batch job management service using Redis queue.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List
from redis import Redis
from app.config import settings


class BatchService:
    """Service for managing batch generation jobs."""
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis not available: {e}")
            print("Batch operations will use in-memory storage (not production-ready)")
            self.redis_client = None
            self._in_memory_jobs: Dict[str, Dict[str, Any]] = {}
    
    def submit_batch_job(
        self,
        model_id: str,
        tasks: List[Dict[str, Any]],
        max_tokens: int,
        temperature: float,
        top_p: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a new batch job.
        
        Args:
            model_id: Model to use for generation
            tasks: List of generation tasks
            max_tokens: Maximum tokens per task
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            metadata: Optional job metadata
            
        Returns:
            Job ID
        """
        job_id = f"batch-{uuid.uuid4().hex[:12]}"
        submitted_at = int(time.time())
        
        job_data = {
            'job_id': job_id,
            'status': 'queued',
            'model_id': model_id,
            'tasks': tasks,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'metadata': metadata or {},
            'submitted_at': submitted_at,
            'started_at': None,
            'completed_at': None,
            'task_count': len(tasks),
            'completed_count': 0,
            'failed_count': 0,
            'results': None,
            'error': None
        }
        
        if self.redis_client:
            # Store job data in Redis
            self.redis_client.set(
                f"job:{job_id}",
                json.dumps(job_data),
                ex=86400  # Expire after 24 hours
            )
            # Add to queue
            self.redis_client.lpush('batch_queue', job_id)
        else:
            # In-memory fallback
            self._in_memory_jobs[job_id] = job_data
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a batch job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data or None if not found
        """
        if self.redis_client:
            job_data_str = self.redis_client.get(f"job:{job_id}")
            if job_data_str:
                return json.loads(job_data_str)
        else:
            return self._in_memory_jobs.get(job_id)
        
        return None
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        results: Optional[List[Dict[str, Any]]] = None,
        error: Optional[str] = None
    ):
        """
        Update the status of a batch job.
        
        Args:
            job_id: Job identifier
            status: New status
            results: Job results (if completed)
            error: Error message (if failed)
        """
        job_data = self.get_job_status(job_id)
        if not job_data:
            return
        
        job_data['status'] = status
        
        if status == 'processing' and not job_data['started_at']:
            job_data['started_at'] = int(time.time())
        
        if status in ['completed', 'failed']:
            job_data['completed_at'] = int(time.time())
        
        if results:
            job_data['results'] = results
            job_data['completed_count'] = sum(1 for r in results if not r.get('error'))
            job_data['failed_count'] = sum(1 for r in results if r.get('error'))
        
        if error:
            job_data['error'] = error
        
        if self.redis_client:
            self.redis_client.set(
                f"job:{job_id}",
                json.dumps(job_data),
                ex=86400
            )
        else:
            self._in_memory_jobs[job_id] = job_data
    
    def get_next_job(self) -> Optional[str]:
        """
        Get the next job from the queue.
        
        Returns:
            Job ID or None if queue is empty
        """
        if self.redis_client:
            job_id = self.redis_client.rpop('batch_queue')
            return job_id
        else:
            # In-memory fallback: find first queued job
            for job_id, job_data in self._in_memory_jobs.items():
                if job_data['status'] == 'queued':
                    return job_id
            return None


# Global batch service instance
batch_service = BatchService()
