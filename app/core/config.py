"""Configuration settings for the application.

This module handles loading environment variables and defining the
application's configuration settings using a Settings class.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration settings.

    Attributes:
        DATABASE_URL: The connection string for the PostgreSQL database.
        SECRET_KEY: The secret key used for cryptographic signing.
        ALGORITHM: The algorithm used for JWT token signing.
        ACCESS_TOKEN_EXPIRE_MINUTES: The duration in minutes before an
            access token expires.
        REDIS_URL: Connection string for Redis (used by Celery).
    """

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str

    def __init__(self):
        """Initializes configuration settings.

        Settings are derived from environment variables. For
        non-critical settings, default values are applied where an
        environment variable is not explicitly set.

        Raises:
            ValueError: If the required environment variable
                DATABASE_URL or SECRET_KEY is not set.
        """
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable must be set")

        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set")

        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")

        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )

        self.REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


settings = Settings()
