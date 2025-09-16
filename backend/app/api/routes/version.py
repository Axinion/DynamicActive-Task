"""
Version endpoint for K12 LMS API.
Returns version and build time information.
"""

import os
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
async def get_version():
    """Get API version and build information."""
    return {
        "version": os.getenv("API_VERSION", "1.0.0"),
        "buildTime": os.getenv("BUILD_TIME", datetime.now().isoformat()),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
