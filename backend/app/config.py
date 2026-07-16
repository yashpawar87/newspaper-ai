from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/newspaper"
    allowed_origins: str = "http://localhost:3000"
    fetch_interval_minutes: int = 15
    scraper_user_agent: str = "DailyDigestBot/1.0 (+https://example.com/bot; contact: you@example.com)"
    seed_on_startup: bool = True
    anthropic_api_key: str = ""
    admin_token: str = ""

    @property
    def sqlalchemy_database_url(self) -> str:
        # Some hosted Postgres providers still expose postgres:// URLs.
        # SQLAlchemy expects the postgresql:// dialect name.
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql://", 1)
        return self.database_url

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
