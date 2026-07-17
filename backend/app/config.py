from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # watsonx Orchestrate
    wxo_instance_url: str = "https://your-instance.cloud.ibm.com"
    wxo_api_key: str = "your-wxo-api-key"
    wxo_model: str = "watsonx/ibm/granite-3-8b-instruct"

    # PostgreSQL
    database_url: str = "postgresql://commai:commai_secret@localhost:5432/commai"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    # MCP
    wxo_mcp_url: str = "https://developer.watson-orchestrate.ibm.com/mcp"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
