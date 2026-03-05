from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

# Header name used in requests: "X-API-KEY"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    """
    Dependency to validate the API Key in the request header.
    """
    if api_key_header == settings.API_KEY:
        return api_key_header
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": {
                "status_code": 403,
                "type": "unauthorized",
                "message": "Invalid or missing API Key. Please provide X-API-KEY header."
            }
        }
    )
