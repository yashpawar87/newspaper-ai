from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.models import Article, Category
from app.db.session import get_db
from app.fetcher.ranking import compute_rank_score
from app.schemas import ArticleOut, ArticlesResponse

router = APIRouter()
ARTICLE_LOOKBACK_DAYS = 7


def _to_article_out(article: Article) -> ArticleOut:
    return ArticleOut(
        id=article.id,
        title=article.title,
        summary=article.summary,
        content=article.content,
        content_source=article.content_source,
        link=article.link,
        image_url=article.image_url,
        source_name=article.source.name if article.source else "",
        category_slug=article.category.slug if article.category else "",
        published_at=article.published_at,
        click_count=article.click_count,
        rank_score=article.rank_score,
        is_pinned=article.is_pinned,
    )


@router.get("/articles", response_model=ArticlesResponse)
def list_articles(
    category: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=ARTICLE_LOOKBACK_DAYS)
    cat = db.query(Category).filter(Category.slug == category).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Unknown category")

    query = (
        db.query(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Article.category_id == cat.id)
        .filter(Article.published_at >= cutoff)
        .order_by(Article.rank_score.desc())
    )

    total = query.count()
    articles = query.offset((page - 1) * limit).limit(limit).all()

    return ArticlesResponse(
        articles=[_to_article_out(a) for a in articles],
        page=page,
        total=total,
    )


@router.get("/trending", response_model=list[ArticleOut])
def trending(limit: int = Query(10, ge=1, le=30), db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=ARTICLE_LOOKBACK_DAYS)
    articles = (
        db.query(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Article.published_at >= cutoff)
        .order_by(Article.rank_score.desc())
        .limit(limit)
        .all()
    )
    return [_to_article_out(a) for a in articles]


@router.get("/articles/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = (
        db.query(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _to_article_out(article)


@router.post("/articles/{article_id}/click", status_code=204)
def register_click(article_id: int, db: Session = Depends(get_db)):
    article = (
        db.query(Article)
        .options(joinedload(Article.source))
        .filter(Article.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.click_count += 1
    article.rank_score = compute_rank_score(article, article.source.weight if article.source else 1.0)
    db.commit()
