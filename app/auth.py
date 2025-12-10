"""
API key authentication for the LLM Gateway.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.config import get_api_keys


security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        The API key if valid
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    api_keys = get_api_keys()
    
    # If no API keys are configured, allow all requests (development mode)
    if not api_keys:
        return "dev-mode"
    
    token = credentials.credentials
    
    if token not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def get_optional_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """
    Get API key if provided, but don't require it.
    Useful for optional authentication endpoints.
    """
    if credentials is None:
        return None
    
    api_keys = get_api_keys()
    if not api_keys:
        return "dev-mode"
    
    token = credentials.credentials
    if token in api_keys:
        return token
    
    return None
