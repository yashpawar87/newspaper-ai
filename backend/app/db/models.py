from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    sources: Mapped[list["Source"]] = relationship(back_populates="category")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    feed_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Reserved for a future summarization/enrichment pipeline. v1 does not
    # scrape full source pages; teaser-only feeds stay teaser-only.
    scraping_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)

    category: Mapped["Category"] = relationship(back_populates="sources")


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("idx_articles_category_rank", "category_id", "rank_score"),
        Index("idx_articles_published", "published_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    guid: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    # "feed" when content came from the RSS feed's content:encoded field.
    # "ai_summary" is reserved for a future summarization pipeline.
    content_source: Mapped[str | None] = mapped_column(String(20))
    link: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    rank_score: Mapped[float] = mapped_column(Float, default=0)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped["Source"] = relationship()
    category: Mapped["Category"] = relationship()
