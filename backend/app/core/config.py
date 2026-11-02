import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusHelp RAG Chatbot"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost",
        "*"
    ]
    
    # Database
    # Default to SQLite for zero-config plug-and-play, supports PostgreSQL in Docker/production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR / 'campushelp.db'}"
    )
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "campushelp_super_secure_jwt_secret_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ADMIN_DEFAULT_EMAIL: str = "admin@campushelp.edu"
    ADMIN_DEFAULT_PASSWORD: str = "Admin@CampusHelp2026!"
    
    # Qdrant Vector Database
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL", None)
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "campus_documents")
    # If True or Qdrant server unreachable, use local path or in-memory client
    QDRANT_LOCAL_PATH: str = str(BASE_DIR / "qdrant_storage")
    
    # RAG Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")  # "openai" or "mock"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION: int = 1536
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = 0.2
    
    # Ingestion & Retrieval Configuration
    CHUNK_SIZE: int = 500  # in characters / tokens
    CHUNK_OVERLAP: int = 50
    TOP_K_CANDIDATES: int = 10
    RERANK_TOP_K: int = 4
    
    # File Storage
    UPLOAD_DIRECTORY: str = str(UPLOAD_DIR)
    MAX_FILE_SIZE_MB: int = 20
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()
