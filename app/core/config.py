"""Application configuration.

Sensitive values are loaded from environment variables; other settings
use defaults unless overridden.
"""

from typing import Literal

from pydantic import PostgresDsn, RedisDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the application.

    Attributes:
        PROJECT_NAME: Name of the application used for display and
            metadata.
        API_V1_STR: Base path for version 1 of the API.
        ENVIRONMENT: Runtime environment (local, staging, or
            production).
        SECRET_KEY: Secret key for JWT signing. Must be set via an
            environment variable.
        ALGORITHM: Algorithm used for JWT signing.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in
            minutes.
        POSTGRES_USER: PostgreSQL username.
        POSTGRES_PASSWORD: PostgreSQL user's password. Must be set via
            an environment variable.
        POSTGRES_HOST: Hostname or IP address of the PostgreSQL server.
        POSTGRES_PORT: PostgreSQL server port.
        POSTGRES_DB: Name of the PostgreSQL database.
        REDIS_HOST: Hostname or IP address of the Redis server.
        REDIS_PORT: Redis server port.
        REDIS_DB: Index of the Redis database.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "FastAPI Blog Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fastapi_blog"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """The PostgreSQL DSN constructed from components."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> RedisDsn:
        """The Redis DSN constructed from components."""
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=str(self.REDIS_DB),
        )


settings = Settings()
