import os
from typing import Optional, List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EarthSage AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip().lower()
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg://earthsage_user:earthsage_password@postgres:5439/earthsage"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "1800"))
    
    # CORS & Security
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    SHOW_DOCS: bool = os.getenv("SHOW_DOCS", "true").strip().lower() in ("true", "1", "yes")

    # NASA POWER Endpoint (Public API - No authentication token required)
    NASA_POWER_BASE_URL: str = os.getenv(
        "NASA_POWER_BASE_URL",
        "https://power.larc.nasa.gov/api/temporal/monthly/point"
    )
    NASA_POWER_TIMEOUT: float = float(os.getenv("NASA_POWER_TIMEOUT", "30.0"))

    # AI / Gemini Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "none").strip().lower()
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    # JWT & Authentication
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "earthsage-jwt-secret-key-development-mode-2026-secure-random"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    AUTH_COOKIE_SECURE: bool = os.getenv("AUTH_COOKIE_SECURE", "false").strip().lower() in ("true", "1", "yes")
    AUTH_COOKIE_SAMESITE: str = os.getenv("AUTH_COOKIE_SAMESITE", "lax").strip().lower()
    AUTH_COOKIE_NAME: str = "earthsage_refresh_token"

    model_config = ConfigDict(env_file=".env", extra="allow")

    def get_cors_origins(self) -> List[str]:
        raw = self.CORS_ORIGINS.strip()
        default_dev = [
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:8020",
            "http://127.0.0.1:8020",
        ]
        if not raw or raw == "*":
            return default_dev
        parsed = [o.strip() for o in raw.split(",") if o.strip()]
        # Merge defaults for local accessibility
        for d in default_dev:
            if d not in parsed:
                parsed.append(d)
        return parsed

settings = Settings()
