from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
config_paths = [
    Path(__file__).parent.parent.parent / 'config.env',
    Path(__file__).parent.parent / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

# --- Приложение FastAPI ---
app = FastAPI(
    title="Cart API",
    description="Микросервис для валидации и расчета стоимости корзины.",
    version="1.0.0"
)

# Настройка CORS
# Для production укажите конкретные домены через переменную окружения ALLOWED_ORIGINS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins]
if "*" in allowed_origins and os.getenv("ENVIRONMENT", "development") == "production":
    print("WARNING: CORS настроен на allow_origins=['*'] в production! Это небезопасно!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class CartRequest(BaseModel):
    product_ids: List[str]

class CartItem(BaseModel):
    id: str
    title: str
    artist: str
    price: float
    image_url: str = None

class CartResponse(BaseModel):
    items: List[CartItem]
    total: float

# Моковые данные для товаров (используются только как fallback, основные данные берутся из Catalog Service)
# Обновлены на виниловые пластинки
MOCK_PRODUCTS = {
    "1": CartItem(
        id="1",
        title="Abbey Road",
        artist="The Beatles",
        price=29.99,
        image_url="https://i.scdn.co/image/ab67616d0000b273dcf4823e7b0b2934f2e45b8b"
    ),
    "2": CartItem(
        id="2",
        title="Sgt. Pepper's Lonely Hearts Club Band",
        artist="The Beatles",
        price=32.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "3": CartItem(
        id="3",
        title="The White Album",
        artist="The Beatles",
        price=39.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "4": CartItem(
        id="4",
        title="Revolver",
        artist="The Beatles",
        price=28.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "5": CartItem(
        id="5",
        title="The Dark Side of the Moon",
        artist="Pink Floyd",
        price=34.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "6": CartItem(
        id="6",
        title="The Wall",
        artist="Pink Floyd",
        price=44.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "7": CartItem(
        id="7",
        title="Wish You Were Here",
        artist="Pink Floyd",
        price=31.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "8": CartItem(
        id="8",
        title="Led Zeppelin IV",
        artist="Led Zeppelin",
        price=32.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "9": CartItem(
        id="9",
        title="Physical Graffiti",
        artist="Led Zeppelin",
        price=38.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "10": CartItem(
        id="10",
        title="A Night at the Opera",
        artist="Queen",
        price=31.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "11": CartItem(
        id="11",
        title="News of the World",
        artist="Queen",
        price=29.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "12": CartItem(
        id="12",
        title="Sticky Fingers",
        artist="The Rolling Stones",
        price=33.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "13": CartItem(
        id="13",
        title="Exile on Main St.",
        artist="The Rolling Stones",
        price=39.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "14": CartItem(
        id="14",
        title="The Doors",
        artist="The Doors",
        price=27.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "15": CartItem(
        id="15",
        title="Back in Black",
        artist="AC/DC",
        price=30.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "16": CartItem(
        id="16",
        title="Paranoid",
        artist="Black Sabbath",
        price=28.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "17": CartItem(
        id="17",
        title="The Rise and Fall of Ziggy Stardust",
        artist="David Bowie",
        price=32.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "18": CartItem(
        id="18",
        title="Highway 61 Revisited",
        artist="Bob Dylan",
        price=29.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "19": CartItem(
        id="19",
        title="Tommy",
        artist="The Who",
        price=35.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "20": CartItem(
        id="20",
        title="Machine Head",
        artist="Deep Purple",
        price=30.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "21": CartItem(
        id="21",
        title="Are You Experienced",
        artist="Jimi Hendrix",
        price=31.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    ),
    "22": CartItem(
        id="22",
        title="London Calling",
        artist="The Clash",
        price=33.99,
        image_url="https://i.scdn.co/image/ab67616d0000b2739c39ba8e4b4b4b4b4b4b4b4b"
    )
}

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/cart/calculate", tags=["Cart"])
def calculate_cart(request: CartRequest):
    """Рассчитывает стоимость корзины на основе переданных ID товаров."""
    items = []
    total = 0.0
    found_ids = []
    missing_ids = []
    
    print(f"Cart Service: получен запрос с ID товаров: {request.product_ids}")
    
    # Сначала пытаемся получить данные из Catalog Service
    catalog_url = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8000")
    
    try:
        # Получаем все товары из каталога
        catalog_response = requests.get(f"{catalog_url}/api/v1/products", timeout=5)
        if catalog_response.status_code == 200:
            catalog_data = catalog_response.json()
            catalog_products = catalog_data.get("products", [])
            
            # Создаем словарь для быстрого поиска
            catalog_dict = {str(p["id"]): p for p in catalog_products}
            
            for product_id in request.product_ids:
                product_id_str = str(product_id)
                if product_id_str in catalog_dict:
                    # Используем данные из каталога
                    product = catalog_dict[product_id_str]
                    item = CartItem(
                        id=product_id_str,
                        title=product.get("name") or product.get("title", ""),
                        artist=product.get("artist") or product.get("author", "Неизвестный исполнитель"),
                        price=product.get("price", 0.0),
                        image_url=product.get("cover_url") or product.get("cover_image_url") or product.get("image_url")
                    )
                    items.append(item)
                    total += item.price
                    found_ids.append(product_id)
                elif product_id_str in MOCK_PRODUCTS:
                    # Fallback на моковые данные
                    item = MOCK_PRODUCTS[product_id_str]
                    items.append(item)
                    total += item.price
                    found_ids.append(product_id)
                else:
                    missing_ids.append(product_id)
                    print(f"Cart Service: товар с ID '{product_id}' не найден")
        else:
            # Если не удалось получить из каталога, используем моки
            print(f"Cart Service: не удалось получить данные из Catalog Service (status: {catalog_response.status_code}), используем моковые данные")
            for product_id in request.product_ids:
                product_id_str = str(product_id)
                if product_id_str in MOCK_PRODUCTS:
                    item = MOCK_PRODUCTS[product_id_str]
                    items.append(item)
                    total += item.price
                    found_ids.append(product_id)
                else:
                    missing_ids.append(product_id)
    except Exception as e:
        # Если ошибка при обращении к каталогу, используем моки
        print(f"Cart Service: ошибка при обращении к Catalog Service: {e}, используем моковые данные")
        for product_id in request.product_ids:
            product_id_str = str(product_id)
            if product_id_str in MOCK_PRODUCTS:
                item = MOCK_PRODUCTS[product_id_str]
                items.append(item)
                total += item.price
                found_ids.append(product_id)
            else:
                missing_ids.append(product_id)
    
    print(f"Cart Service: найдено товаров: {len(found_ids)}, не найдено: {len(missing_ids)}")
    print(f"Cart Service: итоговая сумма: {total}")
    
    return CartResponse(items=items, total=total)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)  # Изменено с 8001 на 8005 для избежания конфликта с auth