# app/config.py - FIXED VERSION
from pydantic_settings import BaseSettings  # CHANGED THIS LINE
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart OPS API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str  # Service role key for backend
    SUPABASE_JWT_SECRET: str
    
    # Security
    SECRET_KEY: str  # For additional JWT operations if needed
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    #Gmail
    GMAIL_USER: str
    GMAIL_PASSWORD: str

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # REMOVED the "and" - that was a typo!