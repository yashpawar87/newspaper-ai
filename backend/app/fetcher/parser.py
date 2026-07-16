from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Article, Source


def _clean_html(raw: str | None, max_length: int = 320) -> str | None:
    if not raw:
        return None
    text = BeautifulSoup(raw, "html.parser").get_text(separator=" ").strip()
    text = " ".join(text.split())
    if not text:
        return None
    if len(text) > max_length:
        text = text[:max_length].rstrip() + "…"
    return text


def _extract_feed_content(entry) -> str | None:
    """
    Pulls the feed's own content:encoded / Atom content field when the
    publisher included it — this is full text the publisher chose to put
    in the feed, distinct from anything scraped separately.
    """
    content_list = entry.get("content")
    if content_list:
        raw = content_list[0].get("value")
        text = BeautifulSoup(raw, "html.parser").get_text(separator="\n\n").strip() if raw else None
        return text or None
    return None


async def _extract_image(entry, article_url: str) -> str | None:
    media_content = entry.get("media_content")
    if media_content:
        url = media_content[0].get("url")
        if url:
            return url

    media_thumbnail = entry.get("media_thumbnail")
    if media_thumbnail:
        url = media_thumbnail[0].get("url")
        if url:
            return url

    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and link.get("type", "").startswith("image"):
            return link.get("href")

    # Last resort: scrape og:image from the article page. One extra HTTP
    # call per article missing a feed image, so only reached when the
    # cheaper options above all miss.
    try:
        async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": settings.scraper_user_agent}) as client:
            resp = await client.get(article_url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
    except Exception:
        pass

    return None


def _parse_published(entry) -> datetime:
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


async def fetch_source(source: Source, db: Session) -> int:
    """
    Fetches one source's feed, inserts any new articles. Never raises —
    failures are recorded on the source row so the scheduler can move on
    to the next source and surface unhealthy feeds via /health.
    """
    source.last_fetched_at = datetime.now(timezone.utc)

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": settings.scraper_user_agent},
            follow_redirects=True,
        ) as client:
            resp = await client.get(source.feed_url)
            resp.raise_for_status()
        parsed = feedparser.parse(resp.text)
        if not parsed.entries:
            raise ValueError("Feed returned no entries")
    except Exception as exc:
        source.failure_count = (source.failure_count or 0) + 1
        source.last_error = str(exc)[:500]
        db.commit()
        return 0

    inserted_count = 0
    seen_guids: set[str] = set()
    for entry in parsed.entries:
        guid = entry.get("id") or entry.get("link")
        if not guid or guid in seen_guids:
            continue
        seen_guids.add(guid)

        exists = db.query(Article.id).filter(Article.guid == guid).first()
        if exists:
            continue

        link = entry.get("link", "")
        title = entry.get("title", "").strip()
        if not link or not title:
            continue

        image_url = await _extract_image(entry, link)
        feed_content = _extract_feed_content(entry)

        article = Article(
            source_id=source.id,
            category_id=source.category_id,
            guid=guid,
            title=title,
            summary=_clean_html(entry.get("summary")),
            content=feed_content,
            content_source="feed" if feed_content else None,
            link=link,
            image_url=image_url,
            published_at=_parse_published(entry),
        )
        db.add(article)
        inserted_count += 1

    source.failure_count = 0
    source.last_success_at = datetime.now(timezone.utc)
    source.last_error = None
    db.commit()
    return inserted_count
