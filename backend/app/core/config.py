from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    database_url: str = "sqlite:///./k12.db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
