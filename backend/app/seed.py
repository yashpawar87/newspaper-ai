"""
Run once after the tables exist (`python -m app.seed`) to populate
categories and sources. `scraping_allowed` is intentionally left False
for every source here — flip it to True per source only after manually
checking that source's robots.txt and Terms of Service, per the v2 note
in CLAUDE.md section 12.
"""

from sqlalchemy.orm import Session

from app.db.models import Category, Source
from app.db.session import SessionLocal

CATEGORIES = [
    {"slug": "top-stories", "name": "Top Stories", "sort_order": 0},
    {"slug": "latest-stories", "name": "Latest Stories", "sort_order": 1},
    {"slug": "tech", "name": "Tech", "sort_order": 2},
    {"slug": "business", "name": "Business", "sort_order": 3},
    {"slug": "entertainment", "name": "Entertainment", "sort_order": 4},
    {"slug": "sports", "name": "Sports", "sort_order": 5},
]

SOURCES = [
    ("top-stories", "Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"),
    ("latest-stories", "Times of India", "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms"),
    ("sports", "Times of India", "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"),
    ("business", "Times of India", "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms"),
    ("entertainment", "Times of India", "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms"),
    ("tech", "Economic Times", "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms"),
]


def seed_defaults(db: Session) -> None:
    slug_to_category: dict[str, Category] = {}

    for cat_data in CATEGORIES:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if existing:
            existing.name = cat_data["name"]
            existing.sort_order = cat_data["sort_order"]
            slug_to_category[cat_data["slug"]] = existing
            continue
        category = Category(**cat_data)
        db.add(category)
        db.flush()
        slug_to_category[cat_data["slug"]] = category

    for slug, source_name, feed_url in SOURCES:
        existing = db.query(Source).filter(Source.feed_url == feed_url).first()
        if existing:
            existing.category_id = slug_to_category[slug].id
            existing.name = source_name
            continue
        existing = (
            db.query(Source)
            .filter(Source.category_id == slug_to_category[slug].id)
            .filter(Source.name == source_name)
            .first()
        )
        if existing:
            existing.feed_url = feed_url
            existing.is_active = True
            continue
        db.add(
            Source(
                category_id=slug_to_category[slug].id,
                name=source_name,
                feed_url=feed_url,
                weight=1.0,
                is_active=True,
                scraping_allowed=True,
            )
        )

    db.commit()


def seed() -> None:
    db = SessionLocal()
    try:
        seed_defaults(db)
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
