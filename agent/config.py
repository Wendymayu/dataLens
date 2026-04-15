"""Configuration management for DataLens"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database connection configuration"""
    name: str
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


class ModelConfig(BaseModel):
    """Model configuration"""
    provider: str = Field(..., description="Model provider: 'anthropic', 'qwen', 'zhipu', or 'openai-compatible'")
    model_name: str = Field(..., description="Model name/ID")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Base URL for OpenAI-compatible API (optional)")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096)


class AppConfig(BaseModel):
    """Application configuration"""
    model: ModelConfig
    databases: Dict[str, DatabaseConfig] = Field(default_factory=dict)
    current_database: Optional[str] = None
    use_mcp: bool = True  # Use MCP for database access (default: True)

    class Config:
        json_encoders = {DatabaseConfig: lambda v: v.model_dump()}


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from file or environment"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = json.load(f)
                return AppConfig(**data)

        # Load from environment variables
        model_config = ModelConfig(
            provider=os.getenv("MODEL_PROVIDER", "anthropic"),
            model_name=os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022"),
            api_key=os.getenv("API_KEY", ""),
        )
        return AppConfig(model=model_config)

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, "w") as f:
            json.dump(self.config.model_dump(), f, indent=2)

    def add_database(self, name: str, config: DatabaseConfig):
        """Add or update a database configuration"""
        self.config.databases[name] = config
        if not self.config.current_database:
            self.config.current_database = name
        self.save_config()

    def remove_database(self, name: str):
        """Remove a database configuration"""
        if name in self.config.databases:
            del self.config.databases[name]
            if self.config.current_database == name:
                self.config.current_database = (
                    next(iter(self.config.databases))
                    if self.config.databases else None
                )
            self.save_config()

    def get_database(self, name: Optional[str] = None) -> Optional[DatabaseConfig]:
        """Get database configuration by name or current"""
        db_name = name or self.config.current_database
        return self.config.databases.get(db_name)

    def set_current_database(self, name: str) -> bool:
        """Set current database"""
        if name in self.config.databases:
            self.config.current_database = name
            self.save_config()
            return True
        return False

    def list_databases(self) -> Dict[str, DatabaseConfig]:
        """List all database configurations"""
        return self.config.databases

    def update_model(self, provider: str, model_name: str, api_key: str, base_url: Optional[str] = None):
        """Update model configuration"""
        self.config.model = ModelConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )
        self.save_config()
