# Integration Guide

This guide provides instructions for integrating the LLM Gateway API into your applications.

## Overview

The LLM Gateway API is designed to be OpenAI-compatible, making it easy to integrate with existing tools and libraries that support the OpenAI API format. This compatibility allows you to switch between the gateway and OpenAI's API with minimal code changes.

## Integration Methods

### Method 1: Using the OpenAI Python Client

The OpenAI Python client can be configured to use the LLM Gateway by changing the `base_url` parameter.

#### Installation

```bash
pip install openai python-dotenv
```

#### Basic Usage

```python
import openai

# Configure the client to use your gateway
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-api-key-here"
)

# Make a chat completion request
response = client.chat.completions.create(
    model="llama-7b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
)

print(response.choices[0].message.content)
```

### Method 2: Using HTTP Requests

You can integrate the gateway using any HTTP client library.

#### Python with `requests`

```python
import requests

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": "Bearer your-api-key-here",
    "Content-Type": "application/json"
}
payload = {
    "model": "llama-7b",
    "messages": [
        {"role": "user", "content": "What is machine learning?"}
    ]
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

#### JavaScript with `fetch`

```javascript
const url = "http://localhost:8000/v1/chat/completions";
const headers = {
    "Authorization": "Bearer your-api-key-here",
    "Content-Type": "application/json"
};
const payload = {
    model: "llama-7b",
    messages: [
        { role: "user", content: "What is machine learning?" }
    ]
};

fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => console.log(data.choices[0].message.content))
.catch(error => console.error("Error:", error));
```

### Method 3: Using LangChain

LangChain is a popular framework for building LLM applications. You can integrate the gateway by using the `ChatOpenAI` class with a custom base URL.

#### Installation

```bash
pip install langchain openai
```

#### Usage

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Initialize the chat model with your gateway
chat = ChatOpenAI(
    openai_api_base="http://localhost:8000/v1",
    openai_api_key="your-api-key-here",
    model_name="llama-7b"
)

# Create messages
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is machine learning?")
]

# Get response
response = chat(messages)
print(response.content)
```

## Model Selection

The gateway supports multiple models. Choose the appropriate model based on your use case:

| Model | Use Case | Strengths |
|-------|----------|-----------|
| `llama-7b` | General tasks, high throughput | Fast, efficient, good for simple queries |
| `gpt-4-mini` | Balanced reasoning | Good reasoning, moderate cost |
| `gemini-flash` | Complex reasoning | Advanced reasoning, multimodal support |

## Batch Processing

For processing large volumes of data, use the batch generation endpoint.

### Example: Generating Synthetic Data

```python
import requests
import time

url = "http://localhost:8000/v1/batch/generate"
headers = {
    "Authorization": "Bearer your-api-key-here",
    "Content-Type": "application/json"
}

# Submit batch job
payload = {
    "model": "llama-7b",
    "tasks": [
        {
            "id": f"task-{i}",
            "messages": [
                {"role": "system", "content": "Generate synthetic user profiles."},
                {"role": "user", "content": f"Create user profile #{i}"}
            ]
        }
        for i in range(100)  # Generate 100 profiles
    ],
    "max_tokens": 300
}

response = requests.post(url, json=payload, headers=headers)
job_id = response.json()["job_id"]

# Poll for completion
status_url = f"http://localhost:8000/v1/batch/{job_id}"
while True:
    status_response = requests.get(status_url, headers=headers)
    status_data = status_response.json()
    
    if status_data["status"] in ["completed", "failed"]:
        break
    
    time.sleep(5)

# Process results
if status_data["status"] == "completed":
    for result in status_data["results"]:
        print(f"Task {result['id']}: {result['output']}")
```

## Error Handling

Always implement proper error handling in your integration.

### Example Error Handling

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-api-key-here"
)

try:
    response = client.chat.completions.create(
        model="llama-7b",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

except openai.AuthenticationError:
    print("Authentication failed. Check your API key.")

except openai.APIError as e:
    print(f"API error occurred: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Use Environment Variables**: Store API keys and URLs in environment variables, not in code.
2. **Implement Retry Logic**: Add exponential backoff for transient errors.
3. **Cache Responses**: Cache frequently requested completions to reduce latency and costs.
4. **Monitor Usage**: Track token usage and costs to optimize your application.
5. **Handle Rate Limits**: Implement rate limiting on the client side to avoid overwhelming the gateway.

## Advanced Integration Patterns

### Pattern 1: Multi-Model Fallback

Use multiple models with fallback logic for reliability:

```python
def chat_with_fallback(messages, models=["llama-7b", "gpt-4-mini", "gemini-flash"]):
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue
    
    raise Exception("All models failed")
```

### Pattern 2: Streaming Responses

For long-form content, use streaming to improve user experience:

```python
response = client.chat.completions.create(
    model="llama-7b",
    messages=[{"role": "user", "content": "Write a long story."}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Support

For additional integration support, please refer to the [API Reference](API.md) or open an issue on the [GitHub repository](https://github.com/Legend1280/LmM-s/issues).
