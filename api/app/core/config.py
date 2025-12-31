from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Worky API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5437
    DATABASE_NAME: str = "worky"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Can be comma-separated string or list
    CORS_ORIGINS: str = "http://localhost:3007,http://localhost:3008,http://localhost:3000,http://localhost:8007"
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS_ORIGINS string into list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        elif isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return []
    
    # External Services
    GITHUB_TOKEN: Optional[str] = None
    GITLAB_TOKEN: Optional[str] = None
    BITBUCKET_TOKEN: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOKI_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    ENVIRONMENT: str = "development"
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # or "azure", "anthropic", "local"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1000
    LLM_TIMEOUT: int = 30
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_PASSWORD: Optional[str] = None
    
    # Chat Configuration
    CHAT_RATE_LIMIT_PER_MINUTE: int = 60
    CHAT_RATE_LIMIT_PER_HOUR: int = 1000
    CHAT_SESSION_TTL_MINUTES: int = 30
    CHAT_MAX_QUERY_LENGTH: int = 2000
    CHAT_MAX_CONTEXT_MESSAGES: int = 10
    CHAT_ENABLE_VECTOR_SEARCH: bool = False
    CHAT_ENABLE_ACTIONS: bool = True
    CHAT_ENABLE_AUDIT_LOGGING: bool = True
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
