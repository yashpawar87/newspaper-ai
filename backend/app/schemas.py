from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    sort_order: int


class CategoryCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    sort_order: int = 0


class SourceCreate(BaseModel):
    category_slug: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    feed_url: str = Field(min_length=1)
    weight: float = 1.0
    is_active: bool = True


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_slug: str
    name: str
    feed_url: str
    weight: float
    is_active: bool
    scraping_allowed: bool
    last_fetched_at: datetime | None
    last_success_at: datetime | None
    failure_count: int
    last_error: str | None


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None
    content: str | None
    content_source: str | None
    link: str
    image_url: str | None
    source_name: str
    category_slug: str
    published_at: datetime | None
    click_count: int
    rank_score: float
    is_pinned: bool


class ArticlesResponse(BaseModel):
    articles: list[ArticleOut]
    page: int
    total: int
