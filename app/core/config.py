"""
Application configuration using Pydantic Settings.

All configuration values can be overridden via environment variables.
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="WirelessAgent Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(
        default="5G Network Slicing Resource Allocation Backend Service",
        description="Application description"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")

    # CORS settings
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

    # LLM API settings
    llm_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek/OpenAI API key"
    )
    llm_base_url: str = Field(
        default="https://api.deepseek.com",
        description="LLM API base URL"
    )
    llm_model: str = Field(
        default="deepseek-chat",
        description="LLM model name"
    )
    llm_temperature: float = Field(
        default=0.0,
        description="LLM temperature"
    )

    # Knowledge base settings
    knowledge_base_path: Optional[str] = Field(
        default=None,
        description="Path to knowledge base file"
    )

    # Ray tracing data settings
    ray_tracing_data_path: str = Field(
        default="./ray_tracing_results.csv",
        description="Path to ray tracing results CSV"
    )

    # Network slice configuration
    embb_total_capacity: int = Field(default=90, description="eMBB total capacity (MHz)")
    urllc_total_capacity: int = Field(default=30, description="URLLC total capacity (MHz)")
    mmtc_total_capacity: int = Field(default=10, description="mMTC total capacity (MHz)")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format (json or console)"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate logging level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper


class DevelopmentSettings(Settings):
    """Development environment settings."""

    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = True
    log_level: str = "DEBUG"
    log_format: str = "console"


class TestingSettings(Settings):
    """Testing environment settings."""

    model_config = SettingsConfigDict(
        env_file=".env.testing",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = False
    log_level: str = "DEBUG"
    log_format: str = "console"

    # Use test-specific capacities
    embb_total_capacity: int = 90
    urllc_total_capacity: int = 30
    mmtc_total_capacity: int = 10


class ProductionSettings(Settings):
    """Production environment settings."""

    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS should be restrictive in production
    cors_origins: List[str] = Field(
        default=[],
        description="Allowed CORS origins (must be explicitly set in production)"
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate that CORS origins are not wildcard in production."""
        if v == ["*"] or "*" in v:
            raise ValueError(
                "Wildcard (*) is not allowed for CORS_ORIGINS in production. "
                "Please specify explicit origins."
            )
        if not v:
            raise ValueError(
                "CORS_ORIGINS must be explicitly set in production. "
                "Please specify allowed origins."
            )
        return v

    @field_validator("llm_api_key")
    @classmethod
    def validate_llm_api_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate that LLM API key is set in production."""
        if not v:
            raise ValueError(
                "LLM_API_KEY must be set in production environment."
            )
        return v


# Environment to settings class mapping
SETTINGS_MAP = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}


def get_settings(env: str | None = None) -> Settings:
    """Get settings instance for the specified environment.

    Args:
        env: Environment name (development, testing, production).
             If None, uses ENV environment variable or defaults to 'development'.

    Returns:
        Settings: Application settings instance for the specified environment.

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        'WirelessAgent Backend'
        >>> dev_settings = get_settings("development")
        >>> print(dev_settings.debug)
        True
    """
    env = env or os.getenv("ENV", "development")
    settings_class = SETTINGS_MAP.get(env.lower(), Settings)
    return settings_class()


@lru_cache()
def get_cached_settings() -> Settings:
    """Get cached settings instance.

    This function caches the settings instance to avoid
    repeated environment variable lookups.

    Returns:
        Settings: Cached application settings instance.
    """
    return get_settings()


# Export all settings classes and functions
__all__ = [
    "Settings",
    "DevelopmentSettings",
    "TestingSettings",
    "ProductionSettings",
    "SETTINGS_MAP",
    "get_settings",
    "get_cached_settings",
]
