from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Ürün adı.")
    slug: str = Field(min_length=1, max_length=120, description="Benzersiz URL kısa adı.")
    description: str | None = Field(default=None, description="Ürün açıklaması.")
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2, description="Ürün fiyatı.")
    stock_quantity: int = Field(ge=0, description="Stok adedi.")
    category_id: int = Field(gt=0, description="Ürünün bağlı olduğu kategori kimliği.")


class ProductUpdate(ProductCreate):
    pass


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Ürünün benzersiz kimliği.")
    name: str = Field(description="Ürün adı.")
    slug: str = Field(description="Ürün URL kısa adı.")
    description: str | None = Field(description="Ürün açıklaması.")
    price: Decimal = Field(description="Ürün fiyatı.")
    stock_quantity: int = Field(description="Stok adedi.")
    category_id: int = Field(description="Ürünün bağlı olduğu kategori kimliği.")
    created_at: datetime = Field(description="Ürünün oluşturulma zamanı (UTC).")
