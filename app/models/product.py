from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    slug: str = Field(max_length=120, unique=True, index=True)
    description: str | None = None
    price: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    stock_quantity: int = Field(ge=0)
    category_id: int = Field(foreign_key="category.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
