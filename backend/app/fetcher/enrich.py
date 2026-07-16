from sqlalchemy.orm import Session


async def enrich_pending_articles(db: Session) -> int:
    """
    v1 intentionally does not scrape source article pages to backfill missing
    feed content. Teaser-only feed entries stay teaser-only and link out.
    """
    return 0
