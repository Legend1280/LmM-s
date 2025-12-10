# Quick Start Guide

Get up and running with the LLM Gateway API in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Legend1280/LmM-s.git
cd LmM-s
```

### Step 2: Install Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred text editor
```

**Minimum required configuration:**

```env
# For development, you can leave this empty (no authentication)
API_KEYS=""

# Add your OpenAI API key (required for GPT-4 Mini)
OPENAI_API_KEY="sk-your-openai-key-here"

# Optional: Add other model backend URLs
LLAMA_API_URL="http://localhost:8001/v1"
GEMINI_API_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
```

### Step 4: Start the Server

```bash
# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## Test the API

### Option 1: Using the Interactive Documentation

Open your browser and navigate to:

`http://localhost:8000/docs`

This will show you the interactive API documentation where you can test all endpoints directly.

### Option 2: Using curl

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "gpt-4-mini",
  "messages": [
    {"role": "user", "content": "Hello! What can you do?"}
  ]
}'
```

### Option 3: Using Python

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # Not required if API_KEYS is empty in .env
)

response = client.chat.completions.create(
    model="gpt-4-mini",
    messages=[
        {"role": "user", "content": "Hello! What can you do?"}
    ]
)

print(response.choices[0].message.content)
```

## Next Steps

- **Add Authentication**: Set `API_KEYS` in your `.env` file to enable authentication
- **Configure More Models**: Add Llama and Gemini endpoints in the `.env` file
- **Enable Batch Processing**: Install and configure Redis for async batch jobs
- **Read the Documentation**: Check out the [full documentation](docs/) for advanced features

## Common Issues

**Issue: ModuleNotFoundError**

Make sure you've activated your virtual environment and installed all dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: Connection refused to model backend**

Check that your model backend URLs in `.env` are correct and the services are running.

**Issue: OpenAI API errors**

Verify that your `OPENAI_API_KEY` is valid and has sufficient credits.

## Support

For more help, see:

- [Full Documentation](README.md)
- [API Reference](docs/API.md)
- [Integration Guide](docs/INTEGRATION.md)
- [GitHub Issues](https://github.com/Legend1280/LmM-s/issues)
