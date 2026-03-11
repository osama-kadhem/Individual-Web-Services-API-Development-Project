from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "IronMind Coach API"
    VERSION: str = "0.6.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./data/ironmind.db"
    API_KEY: str = "ironmind_secret_2026"
    
    # JWT Settings
    SECRET_KEY: str = "super_secret_ironmind_key_2026_leeds_com3011"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours


settings = Settings()
