from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import Category
from app.db.session import get_db
from app.schemas import CategoryOut

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order).all()
