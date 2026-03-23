from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://finautomation:finautomation@localhost:5432/finautomation"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-to-a-random-string"
    UPLOAD_DIR: str = "./uploads"
    MULTILOGIN_API_URL: str = "http://localhost:35000/api/v2"
    SCHEDULE_START_HOUR: int = 9
    SCHEDULE_END_HOUR: int = 21
    DAILY_JOBS_MIN: int = 2
    DAILY_JOBS_MAX: int = 3
    CAMPAIGN_DURATION_DAYS: int = 30

    class Config:
        env_file = ".env"

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def upload_path(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
