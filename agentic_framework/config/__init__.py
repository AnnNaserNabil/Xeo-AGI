"""
Configuration module for the Xeo framework.

This module provides a centralized way to manage configuration settings
across the entire application.
"""
from typing import Any, Dict, Optional
from pydantic import BaseSettings, Field, validator
from pathlib import Path

class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application settings
    APP_NAME: str = "Xeo AI Framework"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Path settings
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / ".cache"
    
    # LLM settings
    DEFAULT_LLM_PROVIDER: str = "gemini"
    DEFAULT_LLM_MODEL: str = "gemini-2.0-flash"
    
    # Memory settings
    MAX_MEMORY_ITEMS: int = 1000
    MEMORY_EXPIRY_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        
    @validator('DATA_DIR', 'CACHE_DIR', pre=True)
    def ensure_dirs_exist(cls, v: Path) -> Path:
        """Ensure that directory paths exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings
