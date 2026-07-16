import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Article, Source
from app.fetcher.extractor import extract_article_text

logger = logging.getLogger(__name__)


async def enrich_pending_articles(db: Session) -> int:
    """
    Fetches full text for articles that only have a summary.
    Runs after each RSS fetch cycle and on its own schedule.
    Fails closed: a failed scrape leaves the article as-is.
    Returns the number of articles successfully enriched.
    """
    if not settings.enable_article_scraping:
        return 0

    # Find articles with no full content yet, joining to source for scraping_allowed check
    candidates = (
        db.query(Article)
        .join(Source, Article.source_id == Source.id)
        .filter(Article.content.is_(None))
        .filter(Source.scraping_allowed.is_(True))
        .order_by(Article.published_at.desc())
        .limit(settings.enrich_batch_size)
        .all()
    )

    enriched = 0
    for article in candidates:
        try:
            text = await extract_article_text(article.link)
            if text:
                article.content = text
                article.content_source = "scraped"
                enriched += 1
        except Exception as exc:
            logger.warning("Enrichment failed for article %s: %s", article.id, exc)

    if enriched:
        db.commit()
        logger.info("Enriched %d articles", enriched)

    return enriched
