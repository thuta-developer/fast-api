from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    app_name : str = "FastAPI Project"
    app_env : Literal["development", "staging", "production"] = "development"
    debug : bool = False
    api_v1_prefix : str = "/api/v1"
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    database_url: str = Field(default="sqlite+aiosqlite:///./sql_app.db")
    
    secret_key : str = Field(default="HOhyhDPTW5XcQInmqQyYhI66BwCOD2hpRj34FfFDHA")
    algorithm : str = "HS256"
    access_token_expire_minutes : int = 30
    
    
    cors_origins: str = Field(default="", validation_alias="CORS_ORIGINS")
    
    # cors_origins: str = Field(default="CORS_ORIGINS")
    
    
    # For postgresql
    # @field_validator("database_url", mode="before")
    # @classmethod
    # def validate_database_url(cls, value: str) -> str:
    #     url = str(value)
    #     if url.startswith("postgresql://"):
    #         return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    #     if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
    #         return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    #     return url
    
    @property
    def cors_origin_list(self) -> list[str]:
        return [origins.strip() for origins in self.cors_origins.split(",") if origins.strip()]
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()

