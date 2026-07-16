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
        # Normalise postgres:// -> postgresql:// first (some providers use the old name).
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        # Switch to the pg8000 dialect (pure-Python, no libpq required).
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+pg8000://", 1)
        return url

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
