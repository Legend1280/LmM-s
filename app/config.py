"""
Configuration management and model registry.
Loads model configurations from YAML and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Configuration
    api_title: str = "LLM Gateway API"
    api_version: str = "1.0.0"
    api_description: str = "Unified API for accessing multiple large language models"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Authentication
    api_keys: str = Field(default="", description="Comma-separated list of valid API keys")
    
    # Model Backend URLs
    llama_api_url: Optional[str] = Field(None, env="LLAMA_API_URL")
    gemini_api_url: Optional[str] = Field(None, env="GEMINI_API_URL")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Redis Configuration (for batch jobs)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Database Configuration (for logging)
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ModelConfig:
    """Model configuration and registry."""
    
    def __init__(self, config_path: str = "config/models.yaml"):
        self.config_path = Path(config_path)
        self.models: Dict[str, Any] = {}
        self.defaults: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load model configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Model config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.models = config.get('models', {})
        self.defaults = config.get('defaults', {})
        
        # Substitute environment variables in URLs
        for model_id, model_config in self.models.items():
            if 'base_url' in model_config:
                base_url = model_config['base_url']
                if base_url.startswith('${') and base_url.endswith('}'):
                    env_var = base_url[2:-1]
                    model_config['base_url'] = os.getenv(env_var, '')
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific model."""
        return self.models.get(model_id)
    
    def list_models(self) -> Dict[str, Any]:
        """List all available models."""
        return self.models
    
    def is_valid_model(self, model_id: str) -> bool:
        """Check if a model ID is valid."""
        return model_id in self.models
    
    def get_default(self, key: str, default: Any = None) -> Any:
        """Get a default configuration value."""
        return self.defaults.get(key, default)


# Global instances
settings = Settings()
model_registry = ModelConfig()


def get_api_keys() -> list[str]:
    """Get list of valid API keys from settings."""
    if not settings.api_keys:
        return []
    return [key.strip() for key in settings.api_keys.split(',') if key.strip()]
