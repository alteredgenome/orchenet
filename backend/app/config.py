"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    # Relative path from backend/ to data/ directory
    database_url: str = "sqlite:///../data/orchenet.db"

    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_key_header: str = "X-API-Key"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 4

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"

    # SSH Configuration
    ssh_timeout: int = 30
    ssh_max_connections: int = 10
    ssh_connect_timeout: int = 15

    # Task Processor
    task_poll_interval: int = 10
    task_max_retries: int = 3

    # Agent communication
    agent_check_in_interval: int = 60  # seconds
    agent_timeout: int = 300  # seconds

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/orchenet.log"

    # UniFi Controller Defaults
    unifi_site: str = "default"
    unifi_verify_ssl: bool = False

    # Redis (optional)
    redis_url: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env


settings = Settings()
