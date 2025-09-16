"""
Central exception handling for K12 LMS API.
Provides consistent error responses with request IDs and proper logging.
"""

import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class APIException(Exception):
    """Base API exception with request ID support."""
    
    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning(
        f"HTTP Exception - ID: {request_id} | "
        f"Status: {exc.status_code} | "
        f"Detail: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "request_id": request_id
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions with detailed error information."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning(
        f"Validation Error - ID: {request_id} | "
        f"Errors: {exc.errors()}"
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": "Request validation failed",
            "errors": exc.errors(),
            "request_id": request_id
        }
    )

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"API Exception - ID: {request_id} | "
        f"Status: {exc.status_code} | "
        f"Message: {exc.message}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
            "request_id": request_id
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions with proper logging."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the full stack trace
    logger.error(
        f"Unhandled Exception - ID: {request_id} | "
        f"Type: {type(exc).__name__} | "
        f"Message: {str(exc)} | "
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "request_id": request_id
        }
    )

def setup_exception_handlers(app):
    """Set up all exception handlers for the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
