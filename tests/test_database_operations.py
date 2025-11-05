#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки операций с базой данных
"""

import os
import sys
import unittest
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
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

from sqlalchemy import text
from database.connection import engine, SessionLocal, init_db
from database.models import Base, Artist, Category, VinylRecord


class TestDatabaseOperations(unittest.TestCase):
    """Тесты операций с базой данных"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        print("\n" + "=" * 60)
        print("Настройка тестов базы данных")
        print("=" * 60)
        try:
            # Проверяем подключение
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Подключение к базе данных установлено")
        except Exception as e:
            print(f"❌ Не удалось подключиться к базе данных: {e}")
            raise
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.db = SessionLocal()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()
    
    def test_09_tables_exist(self):
        """Тест 9: Проверка существования таблиц"""
        print("\n[TEST 9] Проверка существования таблиц...")
        try:
            with engine.connect() as conn:
                # Проверяем наличие основных таблиц
                tables = ['artists', 'categories', 'vinyl_records', 'vinyl_record_categories']
                for table in tables:
                    result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                    exists = result.fetchone() is not None
                    if exists:
                        print(f"✅ Таблица '{table}' существует")
                    else:
                        print(f"⚠️  Таблица '{table}' не найдена")
                        print("   Запустите: python init_db.py")
        except Exception as e:
            print(f"❌ Ошибка при проверке таблиц: {e}")
            raise
    
    def test_10_create_artist(self):
        """Тест 10: Создание записи артиста"""
        print("\n[TEST 10] Тест создания артиста...")
        try:
            # Проверяем, существует ли уже тестовый артист
            existing = self.db.query(Artist).filter_by(name="Test Artist").first()
            if existing:
                self.db.delete(existing)
                self.db.commit()
            
            artist = Artist(name="Test Artist")
            self.db.add(artist)
            self.db.commit()
            
            # Проверяем, что артист создан
            created = self.db.query(Artist).filter_by(name="Test Artist").first()
            self.assertIsNotNone(created, "Артист не был создан")
            self.assertEqual(created.name, "Test Artist")
            
            # Удаляем тестового артиста
            self.db.delete(created)
            self.db.commit()
            
            print("✅ Создание артиста работает корректно")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Ошибка при создании артиста: {e}")
            raise
    
    def test_11_create_category(self):
        """Тест 11: Создание категории"""
        print("\n[TEST 11] Тест создания категории...")
        try:
            # Проверяем, существует ли уже тестовая категория
            existing = self.db.query(Category).filter_by(name="Test Category").first()
            if existing:
                self.db.delete(existing)
                self.db.commit()
            
            category = Category(name="Test Category")
            self.db.add(category)
            self.db.commit()
            
            # Проверяем, что категория создана
            created = self.db.query(Category).filter_by(name="Test Category").first()
            self.assertIsNotNone(created, "Категория не была создана")
            self.assertEqual(created.name, "Test Category")
            
            # Удаляем тестовую категорию
            self.db.delete(created)
            self.db.commit()
            
            print("✅ Создание категории работает корректно")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Ошибка при создании категории: {e}")
            raise
    
    def test_12_create_vinyl_record(self):
        """Тест 12: Создание виниловой пластинки"""
        print("\n[TEST 12] Тест создания виниловой пластинки...")
        try:
            # Создаем тестового артиста и категорию
            artist = Artist(name="Test Artist for Vinyl")
            category = Category(name="Test Category for Vinyl")
            self.db.add(artist)
            self.db.add(category)
            self.db.commit()
            
            # Создаем пластинку
            vinyl = VinylRecord(
                title="Test Vinyl",
                description="Test Description",
                price=19.99,
                artist_id=artist.id,
                categories=[category]
            )
            self.db.add(vinyl)
            self.db.commit()
            
            # Проверяем, что пластинка создана
            created = self.db.query(VinylRecord).filter_by(title="Test Vinyl").first()
            self.assertIsNotNone(created, "Пластинка не была создана")
            self.assertEqual(created.title, "Test Vinyl")
            self.assertEqual(len(created.categories), 1)
            
            # Удаляем тестовые данные
            self.db.delete(created)
            self.db.delete(artist)
            self.db.delete(category)
            self.db.commit()
            
            print("✅ Создание виниловой пластинки работает корректно")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Ошибка при создании пластинки: {e}")
            raise
    
    def test_13_query_operations(self):
        """Тест 13: Проверка операций запросов"""
        print("\n[TEST 13] Тест операций запросов...")
        try:
            # Проверяем количество записей
            artist_count = self.db.query(Artist).count()
            category_count = self.db.query(Category).count()
            vinyl_count = self.db.query(VinylRecord).count()
            
            print(f"   Артистов в БД: {artist_count}")
            print(f"   Категорий в БД: {category_count}")
            print(f"   Пластинок в БД: {vinyl_count}")
            
            print("✅ Операции запросов работают корректно")
        except Exception as e:
            print(f"❌ Ошибка при выполнении запросов: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование операций с базой данных")
    print("=" * 60)
    
    unittest.main(verbosity=2)

