# FastShop API

FastAPI, SQLModel ve SQLite kullanan ürün/kategori servisi.

## Docker ile çalıştırma

Docker Engine veya Docker Desktop çalışır durumdayken proje kökünde:

```bash
docker build -t fastshop-api .
docker run --detach --name fastshop-api --publish 8000:8000 --volume fastshop-data:/data fastshop-api
```

API belgeleri <http://localhost:8000/docs> adresindedir. Konteynerin sağlık
durumunu `docker ps` ile kontrol edebilirsiniz.

Veritabanı, `fastshop-data` adlı Docker volume'unda `/data/fastshop.db` olarak
saklanır; konteyner yeniden oluşturulsa da volume silinmediği sürece veriler
korunur. Konteyner root olmayan `fastshop` kullanıcısıyla çalışır.

Docker Compose ile build edip başlatmak için:

```bash
docker compose up --build --detach
```

Durdurmak için `docker compose down` kullanın. Veritabanı volume'unu da silmek
isterseniz `docker compose down --volumes` çalıştırın; bu işlem kalıcı verileri
siler.
