from sqlalchemy import text

from app.config import settings
from app.db import models  # noqa: F401 - registers SQLAlchemy models
from app.db.session import Base, SessionLocal, engine
from app.seed import seed_defaults


POSTGRES_COMPAT_MIGRATIONS = [
    "ALTER TABLE categories ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS weight DOUBLE PRECISION DEFAULT 1.0",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS scraping_allowed BOOLEAN DEFAULT FALSE",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_fetched_at TIMESTAMPTZ",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_success_at TIMESTAMPTZ",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0",
    "ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_error TEXT",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary TEXT",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS content TEXT",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS content_source VARCHAR(20)",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS image_url TEXT",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS fetched_at TIMESTAMPTZ DEFAULT now()",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS click_count INTEGER DEFAULT 0",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS rank_score DOUBLE PRECISION DEFAULT 0",
    "ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE",
    "CREATE INDEX IF NOT EXISTS idx_articles_category_rank ON articles(category_id, rank_score DESC)",
    "CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC)",
]


def apply_postgres_compat_migrations() -> None:
    with engine.begin() as conn:
        if conn.dialect.name != "postgresql":
            return
        for statement in POSTGRES_COMPAT_MIGRATIONS:
            conn.execute(text(statement))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    apply_postgres_compat_migrations()
    if not settings.seed_on_startup:
        return

    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()
