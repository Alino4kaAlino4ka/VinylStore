#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт миграции данных из SQLite в MySQL
Переносит все данные из старых SQLite баз данных в новую MySQL базу данных
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Корень проекта - на 4 уровня выше от scripts/utils/db/migrate_sqlite_to_mysql.py
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

from database.models import (
    Base, Artist, Category, VinylRecord, Order, OrderItem, User, Prompt
)

# Пути к SQLite базам данных
SQLITE_DATABASES = [
    project_root / 'audio_store.db',
    project_root / 'services' / 'auth' / 'audio_store.db',
    project_root / 'services' / 'prompts-manager' / 'audio_store.db',
    project_root / 'services' / 'catalog' / 'audio_store.db',
]


def get_sqlite_session(db_path):
    """Получить сессию для SQLite базы данных"""
    if not db_path.exists():
        return None
    
    sqlite_url = f"sqlite:///{db_path}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()  # Возвращаем экземпляр сессии


def get_mysql_session():
    """Получить сессию для MySQL базы данных"""
    mysql_url = os.getenv("DATABASE_URL", "mysql+pymysql://user:1234@localhost/audio_store")
    if not mysql_url.startswith("mysql"):
        raise ValueError("DATABASE_URL должен указывать на MySQL")
    
    engine = create_engine(mysql_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()  # Возвращаем экземпляр сессии


def migrate_table(sqlite_db, mysql_db, model_class, table_name):
    """Миграция данных из одной таблицы"""
    print(f"\n  [Таблица: {table_name}]")
    
    # Получаем данные из SQLite
    sqlite_records = sqlite_db.query(model_class).all()
    
    if not sqlite_records:
        print(f"    ⚠️  Нет данных в SQLite")
        return 0
    
    print(f"    📥 Найдено записей в SQLite: {len(sqlite_records)}")
    
    # Проверяем, есть ли уже данные в MySQL
    existing_count = mysql_db.query(model_class).count()
    if existing_count > 0:
        print(f"    ⚠️  В MySQL уже есть {existing_count} записей")
        response = input(f"    Продолжить? (y/n, по умолчанию n): ").strip().lower()
        if response != 'y':
            print(f"    ⏭️  Пропущено")
            return 0
    
    migrated = 0
    skipped = 0
    
    for record in sqlite_records:
        try:
            # Создаем новый объект для MySQL
            if model_class == Artist:
                new_record = Artist(name=record.name)
            elif model_class == Category:
                new_record = Category(name=record.name)
            elif model_class == VinylRecord:
                # Сначала нужно найти или создать артиста
                artist = mysql_db.query(Artist).filter_by(name=record.artist.name).first()
                if not artist:
                    artist = Artist(name=record.artist.name)
                    mysql_db.add(artist)
                    mysql_db.flush()
                
                # Находим или создаем категории
                categories = []
                for cat in record.categories:
                    db_cat = mysql_db.query(Category).filter_by(name=cat.name).first()
                    if not db_cat:
                        db_cat = Category(name=cat.name)
                        mysql_db.add(db_cat)
                        mysql_db.flush()
                    categories.append(db_cat)
                
                new_record = VinylRecord(
                    title=record.title,
                    description=record.description,
                    price=record.price,
                    cover_image_url=record.cover_image_url,
                    artist_id=artist.id,
                    categories=categories
                )
            elif model_class == User:
                new_record = User(
                    email=record.email,
                    hashed_password=record.hashed_password
                )
            elif model_class == Prompt:
                new_record = Prompt(
                    id=record.id,
                    name=record.name,
                    template=record.template
                )
            elif model_class == Order:
                new_record = Order(
                    id=record.id,
                    created_at=record.created_at,
                    total_price=record.total_price
                )
            elif model_class == OrderItem:
                new_record = OrderItem(
                    id=record.id,
                    order_id=record.order_id,
                    vinyl_id=record.vinyl_id,
                    quantity=record.quantity,
                    price_at_purchase=record.price_at_purchase
                )
            else:
                print(f"    ⚠️  Неизвестный тип модели: {model_class}")
                continue
            
            mysql_db.add(new_record)
            migrated += 1
            
        except Exception as e:
            print(f"    ⚠️  Ошибка при миграции записи {record.id}: {e}")
            skipped += 1
            continue
    
    try:
        mysql_db.commit()
        print(f"    ✅ Перенесено: {migrated}, пропущено: {skipped}")
        return migrated
    except Exception as e:
        mysql_db.rollback()
        print(f"    ❌ Ошибка при сохранении: {e}")
        return 0


def migrate_database(sqlite_path, mysql_db):
    """Миграция данных из одной SQLite базы данных"""
    print(f"\n{'='*60}")
    print(f"Миграция из: {sqlite_path.name}")
    print(f"{'='*60}")
    
    sqlite_db = get_sqlite_session(sqlite_path)
    if not sqlite_db:
        print(f"⚠️  Файл {sqlite_path} не найден, пропускаем")
        return
    
    try:
        # Проверяем наличие таблиц в SQLite
        total_migrated = 0
        
        # 1. Artists
        if sqlite_db.query(Artist).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, Artist, "artists")
        
        # 2. Categories
        if sqlite_db.query(Category).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, Category, "categories")
        
        # 3. VinylRecords (нужно после Artists и Categories)
        if sqlite_db.query(VinylRecord).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, VinylRecord, "vinyl_records")
        
        # 4. Users
        if sqlite_db.query(User).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, User, "users")
        
        # 5. Prompts
        if sqlite_db.query(Prompt).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, Prompt, "prompts")
        
        # 6. Orders (нужно после создания всех остальных)
        if sqlite_db.query(Order).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, Order, "orders")
        
        # 7. OrderItems (нужно после Orders)
        if sqlite_db.query(OrderItem).count() > 0:
            total_migrated += migrate_table(sqlite_db, mysql_db, OrderItem, "order_items")
        
        print(f"\n✅ Всего перенесено записей из {sqlite_path.name}: {total_migrated}")
        
    except Exception as e:
        print(f"❌ Ошибка при миграции из {sqlite_path}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sqlite_db.close()


def main():
    """Основная функция миграции"""
    print("=" * 60)
    print("Миграция данных из SQLite в MySQL")
    print("=" * 60)
    
    # Проверяем подключение к MySQL
    print("\n[1] Проверка подключения к MySQL...")
    try:
        mysql_db = get_mysql_session()
        
        # Тестовый запрос
        mysql_db.execute(text("SELECT 1"))
        print("✅ Подключение к MySQL установлено")
    except Exception as e:
        print(f"❌ Ошибка подключения к MySQL: {e}")
        print("   Убедитесь, что MySQL настроен и DATABASE_URL в config.env корректен")
        return
    
    # Статистика перед миграцией
    print("\n[2] Статистика MySQL БД перед миграцией:")
    print(f"   Артистов: {mysql_db.query(Artist).count()}")
    print(f"   Категорий: {mysql_db.query(Category).count()}")
    print(f"   Пластинок: {mysql_db.query(VinylRecord).count()}")
    print(f"   Пользователей: {mysql_db.query(User).count()}")
    print(f"   Промптов: {mysql_db.query(Prompt).count()}")
    print(f"   Заказов: {mysql_db.query(Order).count()}")
    
    # Миграция из каждой SQLite базы
    print("\n[3] Начало миграции...")
    for sqlite_path in SQLITE_DATABASES:
        if sqlite_path.exists():
            migrate_database(sqlite_path, mysql_db)
        else:
            print(f"\n⚠️  Файл {sqlite_path} не найден, пропускаем")
    
    # Статистика после миграции
    print("\n" + "=" * 60)
    print("[4] Статистика MySQL БД после миграции:")
    print(f"   Артистов: {mysql_db.query(Artist).count()}")
    print(f"   Категорий: {mysql_db.query(Category).count()}")
    print(f"   Пластинок: {mysql_db.query(VinylRecord).count()}")
    print(f"   Пользователей: {mysql_db.query(User).count()}")
    print(f"   Промптов: {mysql_db.query(Prompt).count()}")
    print(f"   Заказов: {mysql_db.query(Order).count()}")
    print("=" * 60)
    
    mysql_db.close()
    print("\n✅ Миграция завершена!")


if __name__ == "__main__":
    main()

