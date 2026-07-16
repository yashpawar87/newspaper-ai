from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db.models import Category, Source
from app.db.session import get_db
from app.fetcher.scheduler import run_fetch_cycle
from app.schemas import CategoryCreate, CategoryOut, SourceCreate, SourceOut

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if settings.admin_token and x_admin_token != settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )


def _source_out(source: Source) -> SourceOut:
    return SourceOut(
        id=source.id,
        category_slug=source.category.slug if source.category else "",
        name=source.name,
        feed_url=source.feed_url,
        weight=source.weight,
        is_active=source.is_active,
        scraping_allowed=source.scraping_allowed,
        last_fetched_at=source.last_fetched_at,
        last_success_at=source.last_success_at,
        failure_count=source.failure_count,
        last_error=source.last_error,
    )


@router.post(
    "/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_token)],
)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category slug already exists")

    category = Category(
        slug=payload.slug,
        name=payload.name,
        sort_order=payload.sort_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get(
    "/sources",
    response_model=list[SourceOut],
    dependencies=[Depends(require_admin_token)],
)
def list_sources(db: Session = Depends(get_db)):
    sources = (
        db.query(Source)
        .options(joinedload(Source.category))
        .order_by(Source.name, Source.feed_url)
        .all()
    )
    return [_source_out(source) for source in sources]


@router.post(
    "/sources",
    response_model=SourceOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_token)],
)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.slug == payload.category_slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Unknown category")

    existing = db.query(Source).filter(Source.feed_url == payload.feed_url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Source feed URL already exists")

    source = Source(
        category_id=category.id,
        name=payload.name,
        feed_url=payload.feed_url,
        weight=payload.weight,
        is_active=payload.is_active,
        scraping_allowed=False,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    source.category = category
    return _source_out(source)


@router.post("/fetch", dependencies=[Depends(require_admin_token)])
async def fetch_now():
    return await run_fetch_cycle()
