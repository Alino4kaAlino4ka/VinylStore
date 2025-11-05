from sqlalchemy.orm import Session
from . import models

def create_more_examples(db: Session):
    """
    Наполняет базу данных дополнительным набором данных.
    """
    # Проверка, чтобы не создавать дубликаты
    if db.query(models.Artist).count() > 5:
        print("Дополнительные данные уже существуют.")
        return

    print("Добавление расширенного набора данных...")

    # --- Исполнители ---
    artists = [
        models.Artist(name="The Beatles"),
        models.Artist(name="Pink Floyd"),
        models.Artist(name="Led Zeppelin"),
        models.Artist(name="Queen"),
    ]
    db.add_all(artists)
    db.commit()

    # --- Категории (жанры) ---
    categories = [
        models.Category(name="Рок"),
        models.Category(name="Поп"),
        models.Category(name="Прогрессив-рок"),
        models.Category(name="Классический рок"),
    ]
    db.add_all(categories)
    db.commit()
    
    # --- Получение объектов для связывания ---
    beatles = db.query(models.Artist).filter_by(name="The Beatles").one()
    pink_floyd = db.query(models.Artist).filter_by(name="Pink Floyd").one()
    led_zeppelin = db.query(models.Artist).filter_by(name="Led Zeppelin").one()
    queen = db.query(models.Artist).filter_by(name="Queen").one()

    rock_cat = db.query(models.Category).filter_by(name="Рок").one()
    pop_cat = db.query(models.Category).filter_by(name="Поп").one()
    prog_rock_cat = db.query(models.Category).filter_by(name="Прогрессив-рок").one()
    classic_rock_cat = db.query(models.Category).filter_by(name="Классический рок").one()

    # --- Виниловые пластинки ---
    vinyl_records = [
        models.VinylRecord(
            title="Abbey Road",
            description="Легендарный альбом The Beatles 1969 года.",
            price=29.99,
            artist_id=beatles.id,
            categories=[rock_cat, pop_cat]
        ),
        models.VinylRecord(
            title="The Dark Side of the Moon",
            description="Культовый альбом Pink Floyd 1973 года.",
            price=34.99,
            artist_id=pink_floyd.id,
            categories=[prog_rock_cat, classic_rock_cat]
        ),
        models.VinylRecord(
            title="Led Zeppelin IV",
            description="Четвертый студийный альбом Led Zeppelin 1971 года.",
            price=32.99,
            artist_id=led_zeppelin.id,
            categories=[rock_cat, classic_rock_cat]
        ),
        models.VinylRecord(
            title="A Night at the Opera",
            description="Великолепный альбом Queen 1975 года.",
            price=31.99,
            artist_id=queen.id,
            categories=[rock_cat, pop_cat]
        ),
    ]
    db.add_all(vinyl_records)
    db.commit()
    
    print("Расширенный набор данных успешно добавлен.")

if __name__ == "__main__":
    from .connection import SessionLocal
    db_session = SessionLocal()
    try:
        create_more_examples(db_session)
    finally:
        db_session.close()
