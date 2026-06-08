import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Local AI Bank Statement Converter"
    API_V1_STR: str = "/api"
    
    # Security
    # In production, change this secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-local-ai-bank-converter-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for ease of local desktop use
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    MAX_FILE_SIZE_MB: int = 150  # Handles large PDF bank statements
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "tiff", "bmp"]
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # OCR Settings
    TESSERACT_CMD: Optional[str] = os.getenv("TESSERACT_CMD", None)  # path to tesseract.exe on Windows if needed
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
