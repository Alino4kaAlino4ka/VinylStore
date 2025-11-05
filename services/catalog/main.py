from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
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
    title="Catalog Service API",
    description="API для управления каталогом товаров и админ-панелью.",
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
class Artist(BaseModel):
    id: int
    name: str

class Product(BaseModel):
    id: int
    name: str
    artist: str
    artist_id: Optional[int] = None
    description: str
    price: float
    cover_url: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    artist_id: Optional[int] = None
    artist_name: Optional[str] = None
    description: str
    price: float
    cover_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    artist_id: Optional[int] = None
    artist_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cover_url: Optional[str] = None

# Хранилище данных (в реальном приложении это была бы база данных)
artists = [
    Artist(id=1, name="The Beatles"),
    Artist(id=2, name="Pink Floyd"),
    Artist(id=3, name="Led Zeppelin"),
    Artist(id=4, name="Queen"),
    Artist(id=5, name="The Rolling Stones"),
    Artist(id=6, name="The Doors"),
    Artist(id=7, name="AC/DC"),
    Artist(id=8, name="Black Sabbath"),
    Artist(id=9, name="David Bowie"),
    Artist(id=10, name="Bob Dylan"),
    Artist(id=11, name="The Who"),
    Artist(id=12, name="Deep Purple"),
    Artist(id=13, name="Jimi Hendrix"),
    Artist(id=14, name="The Clash"),
    # Советские исполнители
    Artist(id=15, name="Сергей Рахманинов"),
    Artist(id=16, name="Аквариум"),
    Artist(id=17, name="Кино"),
    Artist(id=18, name="ДДТ"),
    Artist(id=19, name="Алиса"),
    Artist(id=20, name="Наутилус Помпилиус"),
    Artist(id=21, name="Земляне"),
    Artist(id=22, name="Машина Времени"),
    Artist(id=23, name="Воскресение"),
    Artist(id=24, name="Сплин"),
    Artist(id=25, name="Разные исполнители")
]

# Используем реальные обложки альбомов из открытых источников
products = [
    # The Beatles
    Product(
        id=1,
        name="Abbey Road",
        artist="The Beatles",
        artist_id=1,
        description="Легендарный альбом The Beatles 1969 года с культовой обложкой",
        price=3500.0,
        cover_url="https://avatars.mds.yandex.net/i?id=91bd9f5e4a38ad9380572f77fe800e9e29847bc9-4642926-images-thumbs&n=13"
    ),
    Product(
        id=2,
        name="Sgt. Pepper's Lonely Hearts Club Band",
        artist="The Beatles",
        artist_id=1,
        description="Революционный альбом 1967 года, один из величайших в истории музыки",
        price=3800.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/5/50/Sgt._Pepper%27s_Lonely_Hearts_Club_Band.jpg"
    ),
    Product(
        id=3,
        name="The White Album",
        artist="The Beatles",
        artist_id=1,
        description="Двойной альбом 1968 года с разнообразными музыкальными стилями",
        price=4200.0,
        cover_url="https://avatars.mds.yandex.net/i?id=1413c9b506b88090a9df3a55bc34f7525651290b31bff652-5709707-images-thumbs&n=13"
    ),
    Product(
        id=4,
        name="Revolver",
        artist="The Beatles",
        artist_id=1,
        description="Новаторский альбом 1966 года с экспериментальными звуками",
        price=3400.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/e/ec/Revolver_%28album_cover%29.jpg"
    ),
    
    # Pink Floyd
    Product(
        id=5,
        name="The Dark Side of the Moon",
        artist="Pink Floyd",
        artist_id=2,
        description="Культовый альбом Pink Floyd 1973 года с призмой на обложке",
        price=4000.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/3/3b/Dark_Side_of_the_Moon.png"
    ),
    Product(
        id=6,
        name="The Wall",
        artist="Pink Floyd",
        artist_id=2,
        description="Концептуальный двойной альбом 1979 года о изоляции и стенах",
        price=4800.0,
        cover_url="https://avatars.mds.yandex.net/i?id=a50d345f4e05a17e5257f8850847193a0974f46c-5178729-images-thumbs&n=13"
    ),
    Product(
        id=7,
        name="Wish You Were Here",
        artist="Pink Floyd",
        artist_id=2,
        description="Альбом 1975 года, посвященный бывшему участнику группы",
        price=3600.0,
        cover_url="https://avatars.mds.yandex.net/i?id=f1367efa02d08458f2a3191274d601517098d04b-9215166-images-thumbs&n=13"
    ),
    
    # Led Zeppelin
    Product(
        id=8,
        name="Led Zeppelin IV",
        artist="Led Zeppelin",
        artist_id=3,
        description="Четвертый студийный альбом 1971 года, один из величайших рок-альбомов",
        price=3800.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/2/26/Led_Zeppelin_-_Led_Zeppelin_IV.jpg"
    ),
    Product(
        id=9,
        name="Physical Graffiti",
        artist="Led Zeppelin",
        artist_id=3,
        description="Двойной альбом 1975 года с разнообразными композициями",
        price=4200.0,
        cover_url="https://avatars.mds.yandex.net/i?id=06a7175cfde99b2e2f0f05f092628ff13ed01e2a-10639895-images-thumbs&n=13"
    ),
    
    # Queen
    Product(
        id=10,
        name="A Night at the Opera",
        artist="Queen",
        artist_id=4,
        description="Великолепный альбом 1975 года с легендарной композицией Bohemian Rhapsody",
        price=3600.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/4/4d/Queen_A_Night_At_The_Opera.png"
    ),
    Product(
        id=11,
        name="News of the World",
        artist="Queen",
        artist_id=4,
        description="Альбом 1977 года с хитами We Will Rock You и We Are the Champions",
        price=3500.0,
        cover_url="https://avatars.mds.yandex.net/i?id=519a31f8796ca2835ee588795ed6fe2013f6a4ea-5234915-images-thumbs&n=13"
    ),
    
    
    # The Doors
    Product(
        id=14,
        name="The Doors",
        artist="The Doors",
        artist_id=6,
        description="Дебютный альбом 1967 года с легендарной композицией Light My Fire",
        price=3300.0,
        cover_url="https://avatars.mds.yandex.net/i?id=73f53eff85fd68e6149cefb6293ca38f49918b6c-5239568-images-thumbs&n=13"
    ),
    
    # AC/DC
    Product(
        id=15,
        name="Back in Black",
        artist="AC/DC",
        artist_id=7,
        description="Культовый альбом 1980 года, один из самых продаваемых в истории",
        price=3600.0,
        cover_url="https://avatars.mds.yandex.net/i?id=1e14b6d0ae134845f078a8776e357e8038cc5827-6432328-images-thumbs&n=13"
    ),
    
    # Black Sabbath
    Product(
        id=16,
        name="Paranoid",
        artist="Black Sabbath",
        artist_id=8,
        description="Второй студийный альбом 1970 года, классика хеви-метала",
        price=3400.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/6/64/Black_Sabbath_-_Paranoid.jpg"
    ),
    
    # David Bowie
    Product(
        id=17,
        name="The Rise and Fall of Ziggy Stardust",
        artist="David Bowie",
        artist_id=9,
        description="Концептуальный альбом 1972 года, один из величайших в рок-музыке",
        price=3800.0,
        cover_url="https://avatars.mds.yandex.net/i?id=f57e1e457105395cd86ddab8ca51845a523d751a-5233020-images-thumbs&n=13"
    ),
    
    # Bob Dylan
    Product(
        id=18,
        name="Highway 61 Revisited",
        artist="Bob Dylan",
        artist_id=10,
        description="Шестой студийный альбом 1965 года, поворотный момент в карьере",
        price=3500.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/9/95/Bob_Dylan_-_Highway_61_Revisited.jpg"
    ),
    
    # The Who
    Product(
        id=19,
        name="Tommy",
        artist="The Who",
        artist_id=11,
        description="Рок-опера 1969 года, первый успешный альбом в этом жанре",
        price=4000.0,
        cover_url="https://avatars.mds.yandex.net/i?id=6a863b780d205ba739bffa7c6aab923d73a9ac08-5331459-images-thumbs&n=13"
    ),
    
    # Deep Purple
    Product(
        id=20,
        name="Machine Head",
        artist="Deep Purple",
        artist_id=12,
        description="Шестой студийный альбом 1972 года с хитам Smoke on the Water",
        price=3600.0,
        cover_url="https://avatars.mds.yandex.net/i?id=e59aad9de98d3a17cda1e7dc52a3d7e1db2fe395-8494072-images-thumbs&n=13"
    ),
    
    # Jimi Hendrix
    Product(
        id=21,
        name="Are You Experienced",
        artist="Jimi Hendrix",
        artist_id=13,
        description="Дебютный альбом 1967 года, революция в гитарной музыке",
        price=3600.0,
        cover_url="https://avatars.mds.yandex.net/i?id=08aa8e158506bcecfb8650c312e22bdbea643fad-4872191-images-thumbs&n=13"
    ),
    
    # The Clash
    Product(
        id=22,
        name="London Calling",
        artist="The Clash",
        artist_id=14,
        description="Третий студийный альбом 1979 года, классика панк-рока",
        price=3900.0,
        cover_url="https://upload.wikimedia.org/wikipedia/en/0/00/TheClashLondonCallingalbumcover.jpg"
    ),
    
    # Советские пластинки
    # Классическая музыка
    Product(
        id=23,
        name="С. Рахманинов. Колокола",
        artist="Сергей Рахманинов",
        artist_id=15,
        description="Виниловая пластинка фирмы «Мелодия», СССР, 1980-е годы. Состояние: отличное. Редкая запись произведений великого русского композитора.",
        price=3500.0,
        cover_url="https://avatars.mds.yandex.net/i?id=cb1678edcbd01a10a9c0ca8030dc7b49ad8e8c8b-5287637-images-thumbs&n=13"
    ),
    Product(
        id=24,
        name="Пьесы для органа",
        artist="Разные исполнители",
        artist_id=25,
        description="Виниловая пластинка фирмы «Мелодия», СССР. Классические произведения для органа. Состояние: хорошее.",
        price=2800.0,
        cover_url="https://avatars.mds.yandex.net/i?id=3578ce28a38e0113dc59b37ef34a050914c074ff-7762396-images-thumbs&n=13"
    ),
    
    # Советский рок
    Product(
        id=25,
        name="Чёрная роза — эмблема печали",
        artist="Аквариум",
        artist_id=16,
        description="Легендарный альбом группы Аквариум, СССР. Один из самых известных альбомов советского рока. Редкая пластинка в хорошем состоянии.",
        price=4000.0,
        cover_url="https://avatars.mds.yandex.net/i?id=5266e1b6baecdaec9966ad87e28b6cdafd113e61-5424538-images-thumbs&n=13"
    ),
    Product(
        id=26,
        name="Антология Советской Песни Для Школьников. Пластинка 2",
        artist="Разные исполнители",
        artist_id=25,
        description="Виниловая пластинка фирмы «Мелодия», СССР. Коллекция советских песен для школьников. Состояние: хорошее.",
        price=650.0,
        cover_url="https://cdn1.ozone.ru/s3/multimedia-1-v/c600/7048041583.jpg"
    ),
    
    # Дополнительные популярные советские пластинки
    Product(
        id=27,
        name="Начальник Камчатки",
        artist="Кино",
        artist_id=17,
        description="Культовый альбом группы Кино, СССР, 1984 год. Редкая пластинка советского рока. Состояние: отличное.",
        price=4500.0,
        cover_url="https://avatars.mds.yandex.net/i?id=1c695561f9ca0e099db4ec43ef843726ae149730-4327459-images-thumbs&n=13"
    ),
    Product(
        id=28,
        name="Это всё",
        artist="Кино",
        artist_id=17,
        description="Альбом группы Кино, СССР, 1990 год. Один из последних альбомов группы. Редкая пластинка.",
        price=5000.0,
        cover_url="https://avatars.mds.yandex.net/i?id=ef558975a408d8849b5f8bf388abef9c8171bb88-12829626-images-thumbs&n=13"
    ),
    Product(
        id=29,
        name="Чёрный пёс Петербург",
        artist="ДДТ",
        artist_id=18,
        description="Легендарный альбом группы ДДТ, СССР, 1988 год. Редкая пластинка в коллекционном состоянии.",
        price=4200.0,
        cover_url="https://avatars.mds.yandex.net/i?id=bad8e76417424baeb1479a4fac119ec3f0ef6756-16452655-images-thumbs&n=13"
    ),
    Product(
        id=31,
        name="Разлука",
        artist="Наутилус Помпилиус",
        artist_id=20,
        description="Культовый альбом группы Наутилус Помпилиус, СССР, 1986 год. Редкая пластинка.",
        price=4000.0,
        cover_url="https://avatars.mds.yandex.net/i?id=93c8c7dc43ebaad7504a2a907080f5e4b06d976b-4590689-images-thumbs&n=13"
    ),
    Product(
        id=32,
        name="Земляне",
        artist="Земляне",
        artist_id=21,
        description="Виниловая пластинка группы Земляне, СССР, 1980-е годы. Популярные советские хиты.",
        price=2500.0,
        cover_url="https://avatars.mds.yandex.net/i?id=91053324e43c3b83f516ae6ee077521dbf2a21fe-12985844-images-thumbs&n=13"
    ),
    Product(
        id=35,
        name="Пыльная Быль",
        artist="Сплин",
        artist_id=24,
        description="Ранний альбом группы Сплин, СССР, конец 1980-х. Редкая пластинка.",
        price=3200.0,
        cover_url="https://i.scdn.co/image/ab67616d0000b2737483596e721f026e4d86a95e"
    ),
    Product(
        id=36,
        name="Танцы на крыше",
        artist="Кино",
        artist_id=17,
        description="Альбом группы Кино, СССР, 1988 год. Один из самых популярных альбомов группы.",
        price=4800.0,
        cover_url="https://avatars.mds.yandex.net/i?id=adc39d2c7349658f8a09a2bc9bf6bcda2808e91c-4238413-images-thumbs&n=13"
    ),
    Product(
        id=37,
        name="Группа крови",
        artist="Кино",
        artist_id=17,
        description="Культовый альбом группы Кино, СССР, 1988 год. Легендарная пластинка советского рока.",
        price=5500.0,
        cover_url="https://shop-zrec.ru/wp-content/uploads/2023/01/6535892210.jpg"
    ),
    Product(
        id=38,
        name="Аквариум",
        artist="Аквариум",
        artist_id=16,
        description="Ранний альбом группы Аквариум, СССР, 1981 год. Редкая коллекционная пластинка.",
        price=4200.0,
        cover_url="https://is1-ssl.mzstatic.com/image/thumb/Music126/v4/e7/88/bc/e788bc4c-810a-bd24-cc0b-498f7520fc7a/cover.jpg/1380x1380bb.webp"
    ),
    Product(
        id=39,
        name="Дети Гор",
        artist="Аквариум",
        artist_id=16,
        description="Альбом группы Аквариум, СССР, 1985 год. Классика советского рока.",
        price=3800.0,
        cover_url="https://avatars.mds.yandex.net/i?id=0189d310ade02fd058a4cd02da346e73ea121f32-5292008-images-thumbs&n=13"
    ),
    Product(
        id=40,
        name="Радио Африка",
        artist="Аквариум",
        artist_id=16,
        description="Альбом группы Аквариум, СССР, 1983 год. Редкая пластинка в хорошем состоянии.",
        price=4000.0,
        cover_url="https://avatars.mds.yandex.net/i?id=15128ee64b0c58116fdfc8f7d14c9ffd050cb345-10385132-images-thumbs&n=13"
    ),
    Product(
        id=41,
        name="Время Любить",
        artist="ДДТ",
        artist_id=18,
        description="Альбом группы ДДТ, СССР, 1987 год. Классика советского рока.",
        price=3600.0,
        cover_url="https://avatars.mds.yandex.net/i?id=13335a5385122e20c8addced7d009e5b57112aad-10574297-images-thumbs&n=13"
    ),
    Product(
        id=42,
        name="Я получил эту роль",
        artist="ДДТ",
        artist_id=18,
        description="Альбом группы ДДТ, СССР, 1987 год. Редкая пластинка.",
        price=3900.0,
        cover_url="https://avatars.dzeninfra.ru/get-zen_doc/9662522/pub_6437cc9033a671351e2bec76_6437f73fe9b3ec6cf29fdd21/scale_1200"
    )
]

# Эндпоинты для админ-панели
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/admin/products", tags=["Admin"])
def get_all_products():
    """Получает все товары для админ-панели."""
    return {"products": products}

@app.get("/api/v1/admin/products/{product_id}", tags=["Admin"])
def get_product(product_id: str):
    """Получает конкретный товар по ID."""
    product = next((p for p in products if str(p.id) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/v1/admin/products", tags=["Admin"])
def create_product(product_data: ProductCreate):
    """Создает новый товар."""
    # Определяем исполнителя
    artist_name = product_data.artist_name
    if not artist_name and product_data.artist_id:
        artist = next((a for a in artists if a.id == product_data.artist_id), None)
        artist_name = artist.name if artist else f"Исполнитель {product_data.artist_id}"
    elif not artist_name:
        artist_name = "Неизвестный исполнитель"
    
    # Создаем новый товар
    new_id = max([p.id for p in products if isinstance(p.id, int)], default=0) + 1
    new_product = Product(
        id=new_id,
        name=product_data.name,
        artist=artist_name,
        artist_id=product_data.artist_id,
        description=product_data.description,
        price=product_data.price,
        cover_url=product_data.cover_url
    )
    
    products.append(new_product)
    return new_product

@app.put("/api/v1/admin/products/{product_id}", tags=["Admin"])
def update_product(product_id: str, product_data: ProductUpdate):
    """Обновляет существующий товар."""
    product = next((p for p in products if str(p.id) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Обновляем поля
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.cover_url is not None:
        product.cover_url = product_data.cover_url
    
    # Обновляем исполнителя
    if product_data.artist_name:
        product.artist = product_data.artist_name
    elif product_data.artist_id:
        artist = next((a for a in artists if a.id == product_data.artist_id), None)
        if artist:
            product.artist = artist.name
            product.artist_id = product_data.artist_id
    
    return product

@app.delete("/api/v1/admin/products/{product_id}", tags=["Admin"])
def delete_product(product_id: str):
    """Удаляет товар."""
    global products
    product = next((p for p in products if str(p.id) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    products = [p for p in products if str(p.id) != str(product_id)]
    return {"message": "Product deleted successfully"}

@app.get("/api/v1/admin/artists", tags=["Admin"])
def get_all_artists():
    """Получает всех исполнителей."""
    return {"artists": artists}

# Эндпоинты для публичного каталога
@app.get("/api/v1/products", tags=["Public"])
def get_products():
    """Получает все товары для публичного каталога."""
    return {"products": products}

@app.get("/api/v1/products/{product_id}", tags=["Public"])
def get_public_product(product_id: str):
    """Получает конкретный товар для публичного каталога."""
    product = next((p for p in products if str(p.id) == str(product_id)), None) 
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

