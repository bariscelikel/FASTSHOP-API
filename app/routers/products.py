from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Category, Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Ürünler"])
SessionDep = Annotated[Session, Depends(get_session)]


def _get_product_or_404(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    return product


def _ensure_category_exists(session: Session, category_id: int) -> None:
    if session.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Ürün kategorisi bulunamadı.")


def _ensure_slug_available(
    session: Session, slug: str, exclude_id: int | None = None
) -> None:
    statement = select(Product).where(Product.slug == slug)
    if exclude_id is not None:
        statement = statement.where(Product.id != exclude_id)
    if session.exec(statement).first() is not None:
        raise HTTPException(status_code=409, detail="Bu ürün kısa adı zaten kullanılıyor.")


@router.get(
    "",
    response_model=list[ProductRead],
    summary="Ürünleri listele",
    description="Ürünleri sayfalama parametreleriyle listeler.",
)
def list_products(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="En fazla döndürülecek kayıt sayısı.")] = 20,
    offset: Annotated[int, Query(ge=0, description="Atlanacak kayıt sayısı.")] = 0,
) -> list[Product]:
    return list(
        session.exec(select(Product).order_by(Product.id).offset(offset).limit(limit)).all()
    )


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ürün oluştur",
    description="Mevcut bir kategoriye bağlı yeni bir ürün oluşturur.",
)
def create_product(payload: ProductCreate, session: SessionDep) -> Product:
    _ensure_category_exists(session, payload.category_id)
    _ensure_slug_available(session, payload.slug)
    product = Product.model_validate(payload)
    session.add(product)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Ürün kaydı oluşturulamadı; kısa ad kullanılıyor olabilir."
        ) from error
    session.refresh(product)
    return product


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Ürün ayrıntısını getir",
    description="Kimliğe göre tek bir ürünü getirir.",
)
def get_product(product_id: int, session: SessionDep) -> Product:
    return _get_product_or_404(session, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Ürünü güncelle",
    description="Bir ürünün tüm düzenlenebilir alanlarını günceller.",
)
def update_product(
    product_id: int, payload: ProductUpdate, session: SessionDep
) -> Product:
    product = _get_product_or_404(session, product_id)
    _ensure_category_exists(session, payload.category_id)
    _ensure_slug_available(session, payload.slug, exclude_id=product_id)
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    session.add(product)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Ürün güncellenemedi; kısa ad kullanılıyor olabilir."
        ) from error
    session.refresh(product)
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ürünü sil",
    description="Bir ürünü kalıcı olarak siler.",
)
def delete_product(product_id: int, session: SessionDep) -> Response:
    product = _get_product_or_404(session, product_id)
    session.delete(product)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
