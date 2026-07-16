import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from app.api.admin import router as admin_router
from app.api.articles import router as articles_router
from app.api.categories import router as categories_router
from app.config import settings
from app.db.init_db import init_db
from app.db.models import Article, Source
from app.db.session import get_db
from app.fetcher.scheduler import run_fetch_cycle, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = start_scheduler()
    # Kick off one fetch immediately on boot rather than waiting for the
    # first interval tick, so a fresh deploy isn't empty for 15 minutes.
    asyncio.create_task(run_fetch_cycle())
    yield
    scheduler.shutdown()


app = FastAPI(title="RSS Newspaper API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(articles_router)
app.include_router(admin_router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    sources = (
        db.query(Source)
        .options(joinedload(Source.category))
        .order_by(Source.name, Source.feed_url)
        .all()
    )
    unhealthy = [source for source in sources if source.is_active and source.failure_count >= 5]
    article_count = db.query(Article.id).count()

    return {
        "status": "degraded" if unhealthy else "ok",
        "scheduler": {
            "rss_fetch_enabled": True,
            "fetch_interval_minutes": settings.fetch_interval_minutes,
        },
        "database": {
            "article_count": article_count,
            "source_count": len(sources),
        },
        "feeds": [
            {
                "id": source.id,
                "name": source.name,
                "category": source.category.slug if source.category else None,
                "feed_url": source.feed_url,
                "is_active": source.is_active,
                "last_fetched_at": source.last_fetched_at,
                "last_success_at": source.last_success_at,
                "failure_count": source.failure_count,
                "last_error": source.last_error,
                "healthy": source.failure_count < 5,
            }
            for source in sources
        ],
    }
