"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "sqlite:///./orchenet.db"

    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Agent communication
    agent_check_in_interval: int = 60  # seconds
    agent_timeout: int = 300  # seconds

    class Config:
        env_file = ".env"


settings = Settings()
