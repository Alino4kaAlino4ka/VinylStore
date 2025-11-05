#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заполнения базы данных начальными тестовыми данными
Поддерживает как SQLite, так и MySQL (настройки из config.env)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корень проекта в PYTHONPATH для импорта модулей
# Корень проекта - на 4 уровня выше от scripts/utils/db/seed_db.py
# (db -> utils -> scripts -> корень)
# Используем resolve() для получения абсолютного пути
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
config_paths = [
    project_root / 'config.env',
    Path.cwd() / 'config.env',
]
for config_path in config_paths:
    if config_path.exists():
        load_dotenv(config_path, override=False)
        break

from database.connection import SessionLocal, DATABASE_URL
from database.models import Artist, Category, VinylRecord

def seed_database():
    """
    Наполняет базу данных начальными тестовыми данными.
    Поддерживает MySQL и SQLite.
    """
    print("=" * 60)
    print("Заполнение базы данных начальными данными")
    print("=" * 60)
    
    # Определяем тип БД для информативного сообщения
    if DATABASE_URL.startswith("mysql"):
        db_type = "MySQL"
        print(f"Тип БД: {db_type}")
    elif DATABASE_URL.startswith("sqlite"):
        db_type = "SQLite"
        print(f"Тип БД: {db_type}")
    else:
        db_type = "Неизвестный"
        print(f"Тип БД: {db_type}")
    
    print("-" * 60)
    
    # Создаем сессию для работы с БД
    db = SessionLocal()

    try:
        # Проверяем, существуют ли уже данные, чтобы избежать дублирования
        existing_artist = db.query(Artist).filter_by(name="The Beatles").first()
        if existing_artist:
            print("⚠️  Тестовые данные уже существуют в базе данных.")
            print(f"   Найдено записей артистов: {db.query(Artist).count()}")
            print(f"   Найдено записей пластинок: {db.query(VinylRecord).count()}")
            return

        print("Начало наполнения базы данных тестовыми данными...")

        # 1. Создание исполнителя
        artist_beatles = Artist(name="The Beatles")
        db.add(artist_beatles)

        # 2. Создание категорий
        category_rock = Category(name="Рок")
        category_pop = Category(name="Поп")
        category_classic = Category(name="Классический рок")
        db.add_all([category_rock, category_pop, category_classic])
        
        # Важно сделать commit здесь, чтобы получить ID для исполнителя и категорий
        # SQLAlchemy достаточно умен, чтобы обработать это и без коммита,
        # но для ясности и надежности лучше зафиксировать транзакцию.
        db.commit()

        # 3. Создание виниловых пластинок и связывание с исполнителем и категориями
        
        # Пластинка "Abbey Road"
        abbey_road = VinylRecord(
            title="Abbey Road",
            description="Легендарный альбом The Beatles 1969 года с культовой обложкой.",
            price=29.99,
            artist_id=artist_beatles.id,
            categories=[category_rock, category_pop]
        )
        db.add(abbey_road)

        # Пластинка "Sgt. Pepper's Lonely Hearts Club Band"
        sgt_pepper = VinylRecord(
            title="Sgt. Pepper's Lonely Hearts Club Band",
            description="Революционный альбом 1967 года, один из величайших в истории музыки.",
            price=32.99,
            artist_id=artist_beatles.id,
            categories=[category_rock, category_pop]
        )
        db.add(sgt_pepper)

        # 4. Сохранение всех объектов в базу данных
        db.commit()

        print("-" * 60)
        print("✅ База данных успешно наполнена тестовыми данными!")
        print(f"   Создано артистов: {db.query(Artist).count()}")
        print(f"   Создано категорий: {db.query(Category).count()}")
        print(f"   Создано пластинок: {db.query(VinylRecord).count()}")

    except Exception as e:
        print("-" * 60)
        print(f"❌ Произошла ошибка при наполнении базы данных: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
