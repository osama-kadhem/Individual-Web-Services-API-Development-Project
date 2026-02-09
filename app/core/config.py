from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "IronMind Coach API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./ironmind.db"


settings = Settings()
