from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import API_DESCRIPTION, API_TITLE, API_VERSION
from app.db.session import create_db_and_tables
from app.routers import categories, products


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=[
        {"name": "Kategoriler", "description": "Ürün kategorilerini yönetin."},
        {"name": "Ürünler", "description": "E-ticaret ürünlerini yönetin."},
    ],
    lifespan=lifespan,
)

app.include_router(categories.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
