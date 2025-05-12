import os
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "medical_store.db"
    
    # Application settings
    APP_NAME: str = "Medical Store Management System"
    DEBUG: bool = True
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_config(self) -> Dict[str, Any]:
        return {
            "database_url": self.DATABASE_URL,
            "debug": self.DEBUG
        }

    def get_app_config(self) -> Dict[str, Any]:
        return {
            "app_name": self.APP_NAME,
            "debug": self.DEBUG,
            "secret_key": self.SECRET_KEY,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES
        }

    def get_storage_config(self) -> Dict[str, Any]:
        return {
            "upload_dir": self.UPLOAD_DIR,
            "max_upload_size": self.MAX_UPLOAD_SIZE
        }

    def get_logging_config(self) -> Dict[str, Any]:
        return {
            "log_level": self.LOG_LEVEL,
            "log_dir": self.LOG_DIR
        }

# Create settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
