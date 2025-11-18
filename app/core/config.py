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
        DATABASE_URL (str): The connection string for the PostgreSQL
            database.
        SECRET_KEY (str): The secret key used for cryptographic signing.
        ALGORITHM (str): The algorithm used for JWT token signing.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The duration in minutes
            before an access token expires.
    """

    def __init__(self):
        """Initializes configuration settings from environment variables.

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


settings = Settings()
