"""
Configuration management for K12 LMS API.
Validates environment variables and provides sensible defaults.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    """Application settings with environment variable validation."""
    
    def __init__(self):
        self._validate_and_set_defaults()
    
    def _validate_and_set_defaults(self):
        """Validate critical environment variables and set defaults."""
        missing_vars = []
        
        # Critical variables that must be set
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            missing_vars.append("SECRET_KEY")
            logger.warning("SECRET_KEY not set, using default (NOT FOR PRODUCTION)")
            self.SECRET_KEY = "default-secret-key-change-in-production"
        
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
            logger.warning("DATABASE_URL not set, using default SQLite")
            self.DATABASE_URL = "sqlite:///./k12_lms.db"
        
        # Optional variables with defaults
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.SHORT_ANSWER_PASS_THRESHOLD = float(os.getenv("SHORT_ANSWER_PASS_THRESHOLD", "0.7"))
        # Allow multiple origins for development
        allowed_origins = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000,http://localhost:3001")
        self.ALLOWED_ORIGIN = [origin.strip() for origin in allowed_origins.split(",")]
        self.API_VERSION = os.getenv("API_VERSION", "1.0.0")
        self.BUILD_TIME = os.getenv("BUILD_TIME", "unknown")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        # Log missing critical variables
        if missing_vars:
            logger.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
            logger.error("Please set these variables in your .env file or environment")
        
        # Log configuration summary
        logger.info("Configuration loaded:")
        logger.info(f"  Environment: {self.ENVIRONMENT}")
        logger.info(f"  API Version: {self.API_VERSION}")
        logger.info(f"  Database: {self.DATABASE_URL.split('://')[0]}://[hidden]")
        logger.info(f"  Allowed Origin: {self.ALLOWED_ORIGIN}")
        logger.info(f"  Embedding Model: {self.EMBEDDING_MODEL}")
        logger.info(f"  Pass Threshold: {self.SHORT_ANSWER_PASS_THRESHOLD}")

# Global settings instance
settings = Settings()