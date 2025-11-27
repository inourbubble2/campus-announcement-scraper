from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://root:password@localhost:5432/scraper"
    WEBHOOK_BASE_URL: str = "http://localhost:8081"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
