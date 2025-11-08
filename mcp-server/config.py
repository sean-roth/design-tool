"""Configuration management for MCP Server."""

from pydantic_settings import BaseSettings
from typing import Dict, Any
import json
from pathlib import Path


class PenPotSettings(BaseSettings):
    """PenPot connection settings."""
    url: str = "http://localhost:9001"
    plugin_endpoint: str = "/plugin/api"
    timeout: int = 30


class ServerSettings(BaseSettings):
    """MCP Server settings."""
    host: str = "0.0.0.0"
    port: int = 3000
    log_level: str = "INFO"
    cors_origins: list[str] = ["*"]


class ProjectConfig:
    """Project-specific configuration (brand colors, typography, etc)."""

    def __init__(self, config_path: str = "projects.json"):
        self.config_path = Path(config_path)
        self.projects: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load project configurations from JSON file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.projects = json.load(f)
        else:
            # Default configuration
            self.projects = {
                "compel-english": {
                    "brand_colors": {
                        "primary": "#FF5733",
                        "secondary": "#2e3434",
                        "accent": "#FFC300"
                    },
                    "typography": {
                        "heading": "Inter",
                        "body": "Open Sans"
                    },
                    "spacing": {
                        "unit": 8  # 8px base unit
                    }
                }
            }
            self.save()

    def save(self):
        """Save project configurations to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def get_project(self, project_name: str) -> Dict[str, Any]:
        """Get configuration for specific project."""
        return self.projects.get(project_name, {})


class Settings(BaseSettings):
    """Main application settings."""
    penpot: PenPotSettings = PenPotSettings()
    server: ServerSettings = ServerSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


# Global settings instance
settings = Settings()
project_config = ProjectConfig()
