import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.db.models import Source
from app.db.session import SessionLocal
from app.fetcher.enrich import enrich_pending_articles
from app.fetcher.parser import fetch_source
from app.fetcher.ranking import recompute_rankings

logger = logging.getLogger(__name__)

_fetch_lock = asyncio.Lock()


async def run_fetch_cycle() -> dict:
    if _fetch_lock.locked():
        logger.info("Fetch cycle already running, skipping this tick")
        return {"status": "skipped", "reason": "fetch cycle already running"}
    async with _fetch_lock:
        db = SessionLocal()
        try:
            sources = db.query(Source).filter(Source.is_active.is_(True)).all()
            source_results = []
            inserted_total = 0
            for source in sources:
                inserted_count = await fetch_source(source, db)
                inserted_total += inserted_count
                source_results.append(
                    {
                        "id": source.id,
                        "name": source.name,
                        "feed_url": source.feed_url,
                        "inserted": inserted_count,
                        "failure_count": source.failure_count,
                        "last_error": source.last_error,
                    }
                )
            recompute_rankings(db)
            enriched = await enrich_pending_articles(db)
            return {
                "status": "ok",
                "source_count": len(sources),
                "inserted": inserted_total,
                "enriched": enriched,
                "sources": source_results,
            }
        finally:
            db.close()


async def run_enrich_cycle() -> None:
    db = SessionLocal()
    try:
        await enrich_pending_articles(db)
    finally:
        db.close()


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_fetch_cycle,
        IntervalTrigger(minutes=settings.fetch_interval_minutes),
        id="fetch_feeds",
        next_run_time=None,  # first run kicked off manually on startup, see main.py
    )
    scheduler.add_job(
        run_enrich_cycle,
        IntervalTrigger(minutes=settings.enrich_interval_minutes),
        id="enrich_articles",
        next_run_time=None,  # enrichment runs after first fetch cycle completes
    )
    scheduler.start()
    return scheduler
