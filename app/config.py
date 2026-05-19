import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: str = Field(default="your-email@gmail.com")
    SMTP_PASSWORD: str = Field(default="your-app-specific-password")
    SMTP_USE_TLS: bool = Field(default=True)
    SMTP_USE_SSL: bool = Field(default=False)
    
    DEFAULT_FROM_EMAIL: str = Field(default="your-email@gmail.com")
    API_KEY: str = Field(default="pointnest-secure-email-key-2026")

settings = Settings()
