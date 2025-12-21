"""Application configuration.

Loaded from environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the application.

    For non-critical settings, default values are applied where an
    environment variable is not explicitly set.

    Attributes:
        DATABASE_URL: Connection string for the PostgreSQL database.
        SECRET_KEY: Secret key for cryptographic signing.
        ALGORITHM: JWT signing algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Token TTL.
        REDIS_URL: Connection string for Redis.
    """

    DATABASE_URL: str
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
