"""Application settings loaded from .env"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# resolve project root by walking up from this file's location
ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Load and validate settings from the .env file"""

    # Database connection parameters
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Secret key to create and verify JWT tokens
    SECRET_KEY: str

    @property
    def database_url(self) -> str:
        """Build full database connection URL"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # tell BaseSettings which .env file to read and where its located
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
    )


# singleton model instance to be imported and used across the app
settings = Settings()