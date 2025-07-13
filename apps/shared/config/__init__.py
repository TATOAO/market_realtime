"""
Configuration management for the stock monitor application.

This module provides a centralized configuration class using Pydantic Settings
to manage environment variables for various services including Futu API and TimescaleDB.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class manages all configuration settings for the stock monitor application,
    including database connections, API endpoints, and service configurations.
    """
    
    # Futu API Configuration
    futu_host: str = Field(default="127.0.0.1", description="Futu OpenD host address")
    futu_port: int = Field(default=11111, description="Futu OpenD port number")
    futu_quote_ctx_timeout: int = Field(default=15, description="Futu quote context timeout in seconds")
    
    # Database Configuration (TimescaleDB/PostgreSQL)
    database_host: str = Field(default="localhost", description="Database host address")
    database_port: int = Field(default=5432, description="Database port number")
    database_name: str = Field(default="futu_helper", description="Database name")
    database_username: str = Field(default="postgres", description="Database username")
    database_password: str = Field(default="", description="Database password")

    database_pool_min_size: int = Field(default=5, description="Database connection pool minimum size")
    database_pool_max_size: int = Field(default=20, description="Database connection pool maximum size")
    
    # Application Configuration
    app_name: str = Field(default="futu_helper", description="Application name")
    app_environment: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # External API Configuration
    external_api_timeout: int = Field(default=30, description="External API timeout in seconds")
    external_api_retry_attempts: int = Field(default=3, description="Number of retry attempts for external API calls")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")
    
    # WebSocket Configuration
    websocket_url: str = Field(default="ws://localhost:8002", description="WebSocket server URL")
    websocket_port: int = Field(default=8002, description="WebSocket server port")
    
    # Monitoring Configuration
    monitoring_interval: int = Field(default=60, description="Monitoring interval in seconds")
    alert_check_interval: int = Field(default=30, description="Alert check interval in seconds")
    monitoring_port: int = Field(default=8002, description="Monitoring port")
    
    @property
    def database_connection_string(self) -> str:
        """Get the database connection string."""
        if hasattr(self, '_database_url') and self._database_url:
            return self._database_url
        
        # Build connection string from individual components
        password_part = f":{self.database_password}" if self.database_password else ""
        return f"postgresql://{self.database_username}{password_part}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def database_url(self) -> str:
        """Get the database URL (alias for database_connection_string)."""
        return self.database_connection_string
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def futu_connection_info(self) -> dict:
        """
        Get Futu API connection information.
        
        Returns:
            dict: Futu connection parameters
        """
        return {
            "host": self.futu_host,
            "port": self.futu_port,
            "timeout": self.futu_quote_ctx_timeout
        }
    
    def validate_settings(self) -> None:
        """
        Validate critical settings and raise errors if invalid.
        
        Raises:
            ValueError: If required settings are missing or invalid
        """
        if not self.database_url and not all([self.database_host, self.database_name, self.database_username]):
            raise ValueError("Database configuration is incomplete. Either provide DATABASE_URL or all individual database settings.")
        
        if self.database_pool_min_size > self.database_pool_max_size:
            raise ValueError("Database pool min_size cannot be greater than max_size")
        
        if self.futu_port <= 0 or self.futu_port > 65535:
            raise ValueError("Invalid Futu port number. Must be between 1 and 65535")


# Global settings instance
settings = Settings()

# Validate settings on import
try:
    settings.validate_settings()
except ValueError as e:
    print(f"Configuration error: {e}")
    raise

# python -m shared.config.__init__
if __name__ == "__main__":
    print(settings.database_url)