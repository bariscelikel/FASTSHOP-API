from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Category, Product
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Kategoriler"])
SessionDep = Annotated[Session, Depends(get_session)]


def _get_category_or_404(session: Session, category_id: int) -> Category:
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı.")
    return category


def _ensure_slug_available(
    session: Session, slug: str, exclude_id: int | None = None
) -> None:
    statement = select(Category).where(Category.slug == slug)
    if exclude_id is not None:
        statement = statement.where(Category.id != exclude_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(status_code=409, detail="Bu kategori kısa adı zaten kullanılıyor.")


@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Kategorileri listele",
    description="Kategorileri sayfalama parametreleriyle listeler.",
)
def list_categories(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="En fazla döndürülecek kayıt sayısı.")] = 20,
    offset: Annotated[int, Query(ge=0, description="Atlanacak kayıt sayısı.")] = 0,
) -> list[Category]:
    return list(
        session.exec(select(Category).order_by(Category.id).offset(offset).limit(limit)).all()
    )


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Kategori oluştur",
    description="Yeni bir ürün kategorisi oluşturur.",
)
def create_category(payload: CategoryCreate, session: SessionDep) -> Category:
    _ensure_slug_available(session, payload.slug)
    category = Category.model_validate(payload)
    session.add(category)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Bu kategori kısa adı zaten kullanılıyor."
        ) from error
    session.refresh(category)
    return category


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Kategori ayrıntısını getir",
    description="Kimliğe göre tek bir kategoriyi getirir.",
)
def get_category(category_id: int, session: SessionDep) -> Category:
    return _get_category_or_404(session, category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Kategoriyi güncelle",
    description="Bir kategorinin adını ve kısa adını tamamen günceller.",
)
def update_category(
    category_id: int, payload: CategoryUpdate, session: SessionDep
) -> Category:
    category = _get_category_or_404(session, category_id)
    _ensure_slug_available(session, payload.slug, exclude_id=category_id)
    category.name = payload.name
    category.slug = payload.slug
    session.add(category)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Bu kategori kısa adı zaten kullanılıyor."
        ) from error
    session.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kategoriyi sil",
    description="Ürünü olmayan bir kategoriyi siler.",
)
def delete_category(category_id: int, session: SessionDep) -> Response:
    category = _get_category_or_404(session, category_id)
    product = session.exec(
        select(Product).where(Product.category_id == category_id).limit(1)
    ).first()
    if product is not None:
        raise HTTPException(
            status_code=409,
            detail="Ürün içeren kategori silinemez. Önce kategorideki ürünleri silin veya taşıyın.",
        )
    session.delete(category)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
