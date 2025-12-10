"""
LLM Gateway API - Main application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings, model_registry
from app.routers import chat, batch
from app.models.schemas import ModelInfo, ModelsListResponse


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(batch.router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
        "timestamp": int(time.time())
    }


@app.get("/v1/models", response_model=ModelsListResponse)
async def list_models():
    """
    List all available models.
    
    Returns information about all models that can be used with this API.
    """
    models = model_registry.list_models()
    
    model_list = [
        ModelInfo(
            id=model_id,
            display_name=config['display_name'],
            description=config['description'],
            tier=config['tier'],
            max_tokens=config['max_tokens'],
            supports_streaming=config.get('supports_streaming', False)
        )
        for model_id, config in models.items()
    ]
    
    return ModelsListResponse(models=model_list)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "health": "/health",
        "models": "/v1/models"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
