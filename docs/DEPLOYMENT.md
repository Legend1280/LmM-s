# Deployment Guide

This guide covers deploying the LLM Gateway API to production environments.

## Prerequisites

Before deploying, ensure you have the following:

- A server with Python 3.8+ installed
- Docker and Docker Compose (for containerized deployment)
- Redis server (for batch job processing)
- PostgreSQL database (optional, for persistent logging)
- Access to LLM backend services (Llama, GPT, Gemini)

## Deployment Options

### Option 1: Direct Python Deployment

This is the simplest deployment method, suitable for small-scale production or development environments.

#### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Legend1280/LmM-s.git
cd LmM-s

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure Environment

```bash
# Copy and edit the environment file
cp .env.example .env
nano .env
```

Set the following critical variables:

- `API_KEYS`: Comma-separated list of valid API keys
- `LLAMA_API_URL`: URL to your Llama model server
- `GEMINI_API_URL`: URL to your Gemini model server
- `OPENAI_API_KEY`: Your OpenAI API key
- `REDIS_HOST`: Redis server hostname
- `DATABASE_URL`: PostgreSQL connection string (optional)

#### Step 3: Start Services

```bash
# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# In a separate terminal, start the batch worker
python workers/batch_worker.py
```

#### Step 4: Configure Reverse Proxy

For production, use Nginx or Apache as a reverse proxy:

**Nginx Configuration Example:**

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Docker Deployment

Docker provides a more isolated and reproducible deployment environment.

#### Step 1: Create Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Step 2: Create Docker Compose File

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEYS=${API_KEYS}
      - LLAMA_API_URL=${LLAMA_API_URL}
      - GEMINI_API_URL=${GEMINI_API_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

  worker:
    build: .
    command: python workers/batch_worker.py
    environment:
      - API_KEYS=${API_KEYS}
      - LLAMA_API_URL=${LLAMA_API_URL}
      - GEMINI_API_URL=${GEMINI_API_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_HOST=redis
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

#### Step 3: Deploy

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Considerations

### Security

1. **Use HTTPS**: Always deploy behind a reverse proxy with SSL/TLS certificates.
2. **Rotate API Keys**: Regularly rotate your API keys and use strong, random values.
3. **Rate Limiting**: Implement rate limiting at the reverse proxy level.
4. **Firewall Rules**: Restrict access to the API server and Redis to trusted networks.

### Monitoring

1. **Health Checks**: Use the `/health` endpoint for monitoring.
2. **Log Aggregation**: Send logs to a centralized logging system (e.g., ELK, Splunk).
3. **Metrics**: Track request latency, token usage, and error rates.
4. **Alerts**: Set up alerts for high error rates or service downtime.

### Scaling

1. **Horizontal Scaling**: Run multiple instances of the gateway behind a load balancer.
2. **Redis Cluster**: Use Redis Cluster for high-availability batch processing.
3. **Database Connection Pooling**: Configure connection pooling for PostgreSQL.
4. **Model Server Scaling**: Scale your LLM backend servers based on demand.

## Troubleshooting

### Common Issues

**Issue: API returns 401 Unauthorized**

- Check that the `Authorization` header is correctly formatted.
- Verify that the API key is in the `API_KEYS` environment variable.

**Issue: Batch jobs are not processing**

- Ensure the batch worker is running.
- Check Redis connectivity.
- Review worker logs for errors.

**Issue: High latency**

- Check network connectivity to model backends.
- Monitor model server resource usage.
- Consider caching frequently requested completions.

## Support

For additional support, please open an issue on the [GitHub repository](https://github.com/Legend1280/LmM-s/issues).
