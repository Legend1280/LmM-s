# LLM Gateway API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An OpenAI-compatible API gateway for accessing multiple large language models through a single, unified interface. This project provides a stable, modular, and easy-to-maintain wrapper for Llama, GPT, Gemini, and other models.

## Features

- **Unified API**: Access multiple LLMs with a single, consistent API.
- **OpenAI-Compatible**: Drop-in replacement for OpenAI's Python client and other compatible tools.
- **Model Routing**: Map logical model names (e.g., `reasoning-small`) to different backends without client-side changes.
- **Synchronous & Asynchronous API**: Supports both real-time chat completions and async batch generation for large workloads.
- **Authentication**: Secure your API with API key authentication.
- **Logging & Observability**: Detailed logging of requests, responses, latency, and token usage.
- **Modular Architecture**: Clean, decoupled design makes it easy to extend and maintain.

## Supported Models

This gateway is pre-configured to support three tiers of models:

| Tier   | Model Name        | Description                                |
|--------|-------------------|--------------------------------------------|
| Small  | Llama 7B          | Fast and efficient for general tasks       |
| Medium | GPT-4 Mini        | Balanced performance and reasoning         |
| Large  | Gemini 2.5 Flash  | Advanced reasoning and multimodal capabilities |

Adding new models is as simple as updating a YAML configuration file.

## High-Level Architecture

The system consists of three main components:

1.  **LLM Gateway Service**: A FastAPI application that exposes the public API, handles authentication, and routes requests.
2.  **Model Servers**: One or more backend servers that host the actual LLMs (e.g., vLLM, TGI, Ollama).
3.  **Job Queue & Worker**: A Redis-backed queue and a Python worker for processing asynchronous batch jobs.

For a detailed breakdown, see the [Project Structure](PROJECT_STRUCTURE.md) document.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for Redis and model servers)
- An OpenAI API key (if using GPT models)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Legend1280/LmM-s.git
    cd LmM-s
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**

    Copy the example environment file and fill in your details.

    ```bash
    cp .env.example .env
    ```

    Edit `.env` to add your API keys and backend URLs:

    ```env
    # Your secret API keys for the gateway
    API_KEYS="your-secret-key-1,your-secret-key-2"

    # Backend model endpoints
    LLAMA_API_URL="http://localhost:8001/v1"
    GEMINI_API_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
    OPENAI_API_KEY="sk-your-openai-key"

    # Redis (optional)
    REDIS_HOST="localhost"
    ```

### Running the Application

1.  **Start the FastAPI server:**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

2.  **Start the batch worker (in a separate terminal):**

    ```bash
    python workers/batch_worker.py
    ```

3.  **Access the API documentation:**

    The interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Usage

You can interact with the API using any HTTP client or the OpenAI Python library.

### Using `curl`

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your-secret-key-1" \
-d 
  "model": "llama-7b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ]
}
```

### Using the OpenAI Python Client

See the [examples/](examples/) directory for detailed Python scripts.

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-secret-key-1"
)

response = client.chat.completions.create(
    model="llama-7b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

## Documentation

- **[API Reference](docs/API.md)**: Detailed documentation for all API endpoints.
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Instructions for deploying the gateway to production.
- **[Integration Guide](docs/INTEGRATION.md)**: Tips for integrating the gateway with your applications.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
