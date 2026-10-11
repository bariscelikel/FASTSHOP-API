from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Kategori adı.")
    slug: str = Field(min_length=1, max_length=120, description="Benzersiz URL kısa adı.")


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Yeni kategori adı.")
    slug: str = Field(min_length=1, max_length=120, description="Yeni benzersiz URL kısa adı.")


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Kategorinin benzersiz kimliği.")
    name: str = Field(description="Kategori adı.")
    slug: str = Field(description="Kategori URL kısa adı.")
