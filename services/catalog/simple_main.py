from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple Catalog Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/admin/products")
def get_products():
    return {
        "products": [
            {
                "id": 1,
                "name": "Игра престолов",
                "author": "Джордж Р.Р. Мартин",
                "author_id": 1,
                "description": "Эпическая сага о борьбе за властью в Вестеросе",
                "price": 29.99,
                "cover_url": "https://cdn.litres.ru/pub/c/cover_415/248812.webpl"
            },
            {
                "id": 2,
                "name": "Гарри Поттер и философский камень",
                "author": "Дж.К. Роулинг",
                "author_id": 2,
                "description": "Первая книга о юном волшебнике",
                "price": 24.99,
                "cover_url": "https://example.com/harry-potter.jpg"
            },
            {
                "id": 3,
                "name": "Властелин колец",
                "author": "Дж.Р.Р. Толкин",
                "author_id": 3,
                "description": "Эпическая трилогия о кольце всевластья",
                "price": 39.99,
                "cover_url": "https://example.com/lotr.jpg"
            }
        ]
    }

@app.post("/api/v1/admin/products")
def create_product(product_data: dict):
    return {
        "id": 4,
        "name": product_data.get("name", "Новый товар"),
        "author": product_data.get("author_name", "Неизвестный автор"),
        "description": product_data.get("description", ""),
        "price": product_data.get("price", 0),
        "cover_url": product_data.get("cover_url", "")
    }

@app.put("/api/v1/admin/products/{product_id}")
def update_product(product_id: str, product_data: dict):
    return {
        "id": int(product_id),
        "name": product_data.get("name", "Обновленный товар"),
        "author": product_data.get("author_name", "Неизвестный автор"),
        "description": product_data.get("description", ""),
        "price": product_data.get("price", 0),
        "cover_url": product_data.get("cover_url", "")
    }

@app.delete("/api/v1/admin/products/{product_id}")
def delete_product(product_id: str):
    return {"message": "Product deleted successfully"}
