import os

API_TITLE = "FastShop Ürün Servisi"
API_DESCRIPTION = (
    "FastShop e-ticaret kataloğu için kategori ve ürün yönetim API'si. "
    "Tüm kaynak uç noktaları `/api/v1` altında sunulur."
)
API_VERSION = "1.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastshop.db")
