"""
Chat completions endpoint router.
"""

import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse
)
from app.auth import verify_api_key
from app.config import model_registry
from app.services.llm_client import llm_client
from app.services.logging_service import logging_service


router = APIRouter(prefix="/v1", tags=["chat"])


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    responses={
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Create a chat completion using the specified model.
    
    This endpoint is OpenAI-compatible and can be used as a drop-in replacement
    for OpenAI's chat completions API.
    
    **Supported Models:**
    - `llama-7b`: Fast, efficient 7B parameter model
    - `gpt-4-mini`: Balanced model with good reasoning
    - `gemini-flash`: Advanced model with strong reasoning
    
    **Example Request:**
    ```json
    {
        "model": "llama-7b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    ```
    """
    request_id = f"req-{uuid.uuid4().hex[:12]}"
    start_time = time.time()
    
    # Validate model
    if not model_registry.is_valid_model(request.model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model: {request.model}. Available models: {', '.join(model_registry.list_models().keys())}"
        )
    
    # Log request
    logging_service.log_request(
        request_id=request_id,
        endpoint="/v1/chat/completions",
        model=request.model,
        api_key=api_key,
        metadata=request.metadata
    )
    
    try:
        # Call LLM
        response = await llm_client.chat_completion(
            model_id=request.model,
            messages=request.messages,
            max_tokens=request.max_tokens or 512,
            temperature=request.temperature or 0.7,
            top_p=request.top_p or 0.95,
            stream=request.stream or False
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Get backend model name
        model_config = model_registry.get_model(request.model)
        backend_model = model_config['model_name']
        
        # Log completion
        logging_service.log_completion(
            request_id=request_id,
            model=request.model,
            backend_model=backend_model,
            latency_ms=latency_ms,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            status='success',
            metadata=request.metadata
        )
        
        return response
        
    except Exception as e:
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log error
        logging_service.log_completion(
            request_id=request_id,
            model=request.model,
            backend_model=model_registry.get_model(request.model)['model_name'],
            latency_ms=latency_ms,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            status='error',
            error=str(e),
            metadata=request.metadata
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating completion: {str(e)}"
        )
