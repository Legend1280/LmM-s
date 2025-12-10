"""
Logging service for tracking API usage and performance.
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logging API requests and usage."""
    
    def __init__(self):
        self.logger = logger
    
    def log_request(
        self,
        request_id: str,
        endpoint: str,
        model: str,
        api_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an incoming API request.
        
        Args:
            request_id: Unique request identifier
            endpoint: API endpoint being called
            model: Model being requested
            api_key: API key used (masked)
            metadata: Additional request metadata
        """
        log_data = {
            'event': 'request_received',
            'request_id': request_id,
            'endpoint': endpoint,
            'model': model,
            'api_key': self._mask_api_key(api_key) if api_key else None,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_completion(
        self,
        request_id: str,
        model: str,
        backend_model: str,
        latency_ms: float,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        status: str = 'success',
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a completed API request.
        
        Args:
            request_id: Unique request identifier
            model: Logical model name
            backend_model: Physical backend model name
            latency_ms: Request latency in milliseconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total tokens used
            status: Request status (success/error)
            error: Error message if failed
            metadata: Additional metadata
        """
        log_data = {
            'event': 'request_completed',
            'request_id': request_id,
            'model': model,
            'backend_model': backend_model,
            'latency_ms': round(latency_ms, 2),
            'tokens': {
                'prompt': prompt_tokens,
                'completion': completion_tokens,
                'total': total_tokens
            },
            'status': status,
            'error': error,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if status == 'success':
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))
    
    def log_batch_job(
        self,
        job_id: str,
        event: str,
        model: str,
        task_count: int,
        status: Optional[str] = None,
        completed_count: Optional[int] = None,
        failed_count: Optional[int] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a batch job event.
        
        Args:
            job_id: Batch job identifier
            event: Event type (submitted/started/completed/failed)
            model: Model being used
            task_count: Number of tasks in batch
            status: Current job status
            completed_count: Number of completed tasks
            failed_count: Number of failed tasks
            error: Error message if failed
            metadata: Additional metadata
        """
        log_data = {
            'event': f'batch_{event}',
            'job_id': job_id,
            'model': model,
            'task_count': task_count,
            'status': status,
            'completed_count': completed_count,
            'failed_count': failed_count,
            'error': error,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(json.dumps(log_data))
    
    @staticmethod
    def _mask_api_key(api_key: str) -> str:
        """Mask API key for logging (show only last 4 characters)."""
        if len(api_key) <= 4:
            return "****"
        return f"****{api_key[-4:]}"


# Global logging service instance
logging_service = LoggingService()
