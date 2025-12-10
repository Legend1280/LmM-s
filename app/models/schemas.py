"""
Pydantic models for API request and response schemas.
OpenAI-compatible format for easy integration.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Chat Completion Schemas
# ============================================================================

class Message(BaseModel):
    """A single message in a conversation."""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """Request schema for chat completions endpoint."""
    model: str = Field(..., description="Model identifier (e.g., 'llama-7b', 'gpt-4-mini', 'gemini-flash')")
    messages: List[Message] = Field(..., description="List of conversation messages")
    max_tokens: Optional[int] = Field(512, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for logging")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "llama-7b",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_tokens": 512,
                "temperature": 0.7,
                "metadata": {"request_id": "req-123", "source": "web-app"}
            }
        }


class UsageInfo(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatChoice(BaseModel):
    """A single chat completion choice."""
    index: int
    message: Message
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Response schema for chat completions endpoint."""
    id: str
    model: str
    created: int
    choices: List[ChatChoice]
    usage: UsageInfo

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-abc123",
                "model": "llama-7b",
                "created": 1733830400,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "The capital of France is Paris."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 25,
                    "completion_tokens": 8,
                    "total_tokens": 33
                }
            }
        }


# ============================================================================
# Batch Generation Schemas
# ============================================================================

class BatchTask(BaseModel):
    """A single task in a batch generation request."""
    id: str = Field(..., description="Unique identifier for this task")
    messages: List[Message] = Field(..., description="Conversation messages for this task")


class BatchGenerationRequest(BaseModel):
    """Request schema for batch generation endpoint."""
    model: str = Field(..., description="Model identifier")
    tasks: List[BatchTask] = Field(..., description="List of generation tasks")
    max_tokens: Optional[int] = Field(512, description="Maximum tokens per task")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    batch_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata for the entire batch")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "llama-7b",
                "tasks": [
                    {
                        "id": "task-1",
                        "messages": [
                            {"role": "system", "content": "Generate synthetic user profiles."},
                            {"role": "user", "content": "Create a fitness client profile."}
                        ]
                    },
                    {
                        "id": "task-2",
                        "messages": [
                            {"role": "system", "content": "Generate synthetic user profiles."},
                            {"role": "user", "content": "Create a cardiology patient profile."}
                        ]
                    }
                ],
                "max_tokens": 512,
                "temperature": 0.7,
                "batch_metadata": {"project": "synthetic_data_v1"}
            }
        }


class BatchSubmissionResponse(BaseModel):
    """Response when a batch job is submitted."""
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    submitted_at: int
    task_count: int


class BatchTaskResult(BaseModel):
    """Result for a single task in a batch."""
    id: str
    output: str
    usage: UsageInfo
    error: Optional[str] = None


class BatchStatusResponse(BaseModel):
    """Response for batch job status check."""
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    submitted_at: int
    started_at: Optional[int] = None
    completed_at: Optional[int] = None
    task_count: int
    completed_count: int
    failed_count: int
    results: Optional[List[BatchTaskResult]] = None
    error: Optional[str] = None


# ============================================================================
# Model Information Schemas
# ============================================================================

class ModelInfo(BaseModel):
    """Information about an available model."""
    id: str
    display_name: str
    description: str
    tier: str
    max_tokens: int
    supports_streaming: bool


class ModelsListResponse(BaseModel):
    """Response listing all available models."""
    models: List[ModelInfo]


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
