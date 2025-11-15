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
    DATABASE_USER: str = "worky_user"
    DATABASE_PASSWORD: str = "worky_password"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3007", "http://localhost:3000", "http://localhost:8007"]
    
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
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
