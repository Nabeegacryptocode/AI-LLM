"""
Configuration management for IBM Docs LLM API
"""
from pydantic_settings import BaseSettings
from typing import List
import json
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_KEY: str
    ALLOWED_ORIGINS: str = '["*"]'
    
    # LLM Settings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # Vector DB Settings
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "ibm-docs"
    PINECONE_CLOUD: str = "aws"  # Cloud provider for Pinecone serverless
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    
    # RAG Settings
    TOP_K_RESULTS: int = 5
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    MIN_RELEVANCE_SCORE: float = 0.3
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./ibm_docs_llm.db"
    
    # Web Search Settings
    WEB_SEARCH_ENABLED: bool = True
    
    # Google Discovery Engine Settings
    GOOGLE_PROJECT_ID: str = "783867443498"
    GOOGLE_DISCOVERY_LOCATION: str = "global"
    GOOGLE_DISCOVERY_COLLECTION_ID: str = "default_collection"
    GOOGLE_DISCOVERY_ENGINE_ID: str = "fahm-llm_1779380839747"
    GOOGLE_DISCOVERY_SERVING_CONFIG: str = "default_search"
    USE_DISCOVERY_ENGINE: bool = True
    
    # Google Cloud Authentication (for production)
    GOOGLE_APPLICATION_CREDENTIALS: str = ""  # Path to service account JSON key
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from JSON string to list"""
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except json.JSONDecodeError:
            return ["*"]
    
    class Config:
        # Look for .env in backend directory
        env_file = os.path.join(Path(__file__).parent.parent, ".env")
        case_sensitive = True


# Global settings instance
settings = Settings()

# Made with Bob
