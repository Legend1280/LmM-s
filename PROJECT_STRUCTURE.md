# LLM Gateway API - Project Structure

## Overview

This project provides a unified API gateway for accessing multiple large language models through a single, stable interface. The architecture follows a modular, isolated design that allows easy integration with other software systems.

## Architecture Components

### 1. LLM Gateway Service
- **Language**: Python with FastAPI
- **Responsibilities**:
  - Expose unified HTTP API endpoints
  - Validate requests and handle authentication
  - Route requests to appropriate model backends
  - Log usage and errors
  - Handle both synchronous and asynchronous batch operations

### 2. Model Backends
The gateway supports three model tiers:
- **Small Model**: Llama 7B (fast, efficient)
- **Medium Model**: GPT-4 Mini (balanced performance)
- **Large Model**: Gemini 2.5 Flash (advanced reasoning)

### 3. Job Queue & Worker (for batch operations)
- Redis-backed queue for async batch processing
- Worker process for handling background jobs
- Results storage and retrieval

## Directory Structure

```
LmM-s/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and model registry
│   ├── auth.py                 # API key authentication
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models for requests/responses
│   │   └── registry.py         # Model routing configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat completions endpoint
│   │   └── batch.py            # Batch generation endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py       # LLM backend client adapters
│   │   ├── batch_service.py    # Batch job management
│   │   └── logging_service.py  # Usage logging
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Utility functions
├── workers/
│   ├── __init__.py
│   └── batch_worker.py         # Background worker for batch jobs
├── tests/
│   ├── __init__.py
│   ├── test_chat.py
│   └── test_batch.py
├── config/
│   └── models.yaml             # Model routing configuration
├── examples/
│   ├── simple_chat.py          # Basic usage example
│   ├── batch_generation.py     # Batch processing example
│   └── integration_example.py  # Integration with other systems
├── docs/
│   ├── API.md                  # API documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── INTEGRATION.md          # Integration guide
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore
├── README.md
└── LICENSE
```

## API Endpoints

### Synchronous Chat Completions
- `POST /v1/chat/completions` - Single chat completion request
- OpenAI-compatible API format for easy integration

### Asynchronous Batch Generation
- `POST /v1/batch/generate` - Submit batch job
- `GET /v1/batch/{job_id}` - Check batch job status
- `GET /v1/batch/{job_id}/results` - Retrieve batch results

### Health & Status
- `GET /health` - Service health check
- `GET /v1/models` - List available models

## Model Configuration

Models are configured in `config/models.yaml`:

```yaml
models:
  llama-7b:
    display_name: "Llama 7B"
    backend_type: "openai_compatible"
    base_url: "${LLAMA_API_URL}"
    model_name: "llama-7b-instruct"
    max_tokens: 2048
    tier: "small"
  
  gpt-4-mini:
    display_name: "GPT-4 Mini"
    backend_type: "openai"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-4-mini"
    max_tokens: 4096
    tier: "medium"
  
  gemini-2.5-flash:
    display_name: "Gemini 2.5 Flash"
    backend_type: "openai_compatible"
    base_url: "${GEMINI_API_URL}"
    model_name: "gemini-2.5-flash"
    max_tokens: 8192
    tier: "large"
```

## Authentication

API key-based authentication:
- Header: `Authorization: Bearer <API_KEY>`
- Keys stored in environment variables or database
- Rate limiting per API key

## Logging & Observability

Per-request logging includes:
- `request_id` - Unique identifier
- `model` - Logical model name
- `backend_model` - Physical model name
- `timestamps` - Start, end, latency
- `token_usage` - Prompt and completion tokens
- `status` - Success/error codes
- `metadata` - Custom request metadata

## Design Principles

1. **Modular**: Each component is isolated and independently testable
2. **Non-destructive**: Changes don't break existing integrations
3. **Real connections**: Uses actual model APIs, not mocks
4. **Easy to edit**: Clear structure and well-documented code
5. **Stable contracts**: External API remains consistent while internal implementations can change
