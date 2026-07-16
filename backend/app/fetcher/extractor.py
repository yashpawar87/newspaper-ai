import httpx
import trafilatura

from app.config import settings
from app.fetcher.robots import is_scraping_allowed


async def extract_article_text(url: str) -> str | None:
    """
    Fetches a source article page and extracts the main body text,
    stripped of nav/ads/boilerplate. Returns None (rather than raising)
    on any failure — a missing scrape should never break the fetch
    pipeline, it just means that article stays teaser-only.

    Callers are responsible for checking `source.scraping_allowed` (the
    manual per-source ToS/robots.txt review) before calling this at all.
    This function additionally re-checks robots.txt live, since a site's
    policy can change after the manual review was done.
    """
    if not is_scraping_allowed(url, settings.scraper_user_agent):
        return None

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": settings.scraper_user_agent},
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError:
        return None

    text = trafilatura.extract(
        response.text,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    return text.strip() if text else None
