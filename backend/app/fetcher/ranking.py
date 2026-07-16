from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.models import Article, Source


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def compute_rank_score(article: Article, source_weight: float) -> float:
    now = datetime.now(timezone.utc)
    published = _as_utc(article.published_at) if article.published_at else now
    hours_since = max(0.0, (now - published).total_seconds() / 3600)

    recency_score = max(0.0, 100 - hours_since * 2)  # decays to 0 after ~50 hours
    score = (source_weight * 10) + recency_score + (article.click_count * 0.5)
    if article.is_pinned:
        score += 1000
    return score


def recompute_rankings(db: Session, lookback_hours: int = 72) -> None:
    cutoff = datetime.now(timezone.utc).timestamp() - lookback_hours * 3600
    articles = (
        db.query(Article)
        .join(Source, Article.source_id == Source.id)
        .filter(Article.published_at.isnot(None))
        .all()
    )

    for article in articles:
        published = article.published_at
        if published and _as_utc(published).timestamp() < cutoff:
            continue
        source_weight = article.source.weight if article.source else 1.0
        article.rank_score = compute_rank_score(article, source_weight)

    db.commit()
