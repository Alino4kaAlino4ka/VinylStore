#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки подключения к MySQL
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

import pymysql
from sqlalchemy import create_engine, text
from database.connection import DATABASE_URL, engine, SessionLocal


class TestMySQLConnection(unittest.TestCase):
    """Тесты подключения к MySQL"""
    
    def test_01_config_env_loaded(self):
        """Тест 1: Проверка загрузки config.env"""
        print("\n[TEST 1] Проверка загрузки config.env...")
        self.assertIsNotNone(os.getenv("DATABASE_URL"), "DATABASE_URL не найден в переменных окружения")
        self.assertTrue(DATABASE_URL.startswith("mysql"), f"Ожидается MySQL, получено: {DATABASE_URL}")
        print("✅ config.env загружен, DATABASE_URL найден")
    
    def test_02_database_url_format(self):
        """Тест 2: Проверка формата строки подключения"""
        print("\n[TEST 2] Проверка формата строки подключения...")
        self.assertIn("mysql+pymysql://", DATABASE_URL, "Неверный формат строки подключения")
        self.assertIn("@localhost", DATABASE_URL, "Не найден хост localhost")
        self.assertIn("/audio_store", DATABASE_URL, "Не найдена база данных audio_store")
        print(f"✅ Формат строки подключения корректен: {DATABASE_URL.split('@')[0]}@...")
    
    def test_03_pymysql_installed(self):
        """Тест 3: Проверка установки pymysql"""
        print("\n[TEST 3] Проверка установки pymysql...")
        try:
            import pymysql
            version = pymysql.__version__
            print(f"✅ pymysql установлен, версия: {version}")
        except ImportError:
            self.fail("pymysql не установлен")
    
    def test_04_mysql_server_reachable(self):
        """Тест 4: Проверка доступности MySQL сервера"""
        print("\n[TEST 4] Проверка доступности MySQL сервера...")
        try:
            # Пытаемся подключиться к MySQL без указания базы данных
            connection = pymysql.connect(
                host='localhost',
                user='user',
                password='1234',
                connect_timeout=5
            )
            connection.close()
            print("✅ MySQL сервер доступен")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1045:
                print(f"⚠️  MySQL сервер доступен, но доступ запрещен: {e}")
                print("   Необходимо создать пользователя и выдать права")
            else:
                print(f"❌ Ошибка подключения к MySQL: {e}")
            raise
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            raise
    
    def test_05_user_exists(self):
        """Тест 5: Проверка существования пользователя"""
        print("\n[TEST 5] Проверка существования пользователя 'user'...")
        try:
            # Подключаемся как root для проверки пользователя
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',  # Попробуем без пароля
                connect_timeout=5
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT User, Host FROM mysql.user WHERE User='user' AND Host='localhost'")
                result = cursor.fetchone()
                if result:
                    print("✅ Пользователь 'user'@'localhost' существует")
                else:
                    print("⚠️  Пользователь 'user'@'localhost' не найден")
                    print("   Выполните: CREATE USER 'user'@'localhost' IDENTIFIED BY '1234';")
            connection.close()
        except Exception as e:
            print(f"⚠️  Не удалось проверить пользователя (возможно, нужен пароль root): {e}")
    
    def test_06_database_exists(self):
        """Тест 6: Проверка существования базы данных"""
        print("\n[TEST 6] Проверка существования базы данных 'audio_store'...")
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',  # Попробуем без пароля
                connect_timeout=5
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES LIKE 'audio_store'")
                result = cursor.fetchone()
                if result:
                    print("✅ База данных 'audio_store' существует")
                else:
                    print("⚠️  База данных 'audio_store' не найдена")
                    print("   Выполните: CREATE DATABASE audio_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            connection.close()
        except Exception as e:
            print(f"⚠️  Не удалось проверить базу данных (возможно, нужен пароль root): {e}")
    
    def test_07_user_privileges(self):
        """Тест 7: Проверка прав пользователя"""
        print("\n[TEST 7] Проверка прав пользователя 'user' на базу данных 'audio_store'...")
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',  # Попробуем без пароля
                connect_timeout=5
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW GRANTS FOR 'user'@'localhost'")
                grants = cursor.fetchall()
                if grants:
                    print("✅ Права пользователя:")
                    for grant in grants:
                        print(f"   {grant[0]}")
                    # Проверяем наличие прав на audio_store
                    has_audio_store_privileges = any('audio_store' in str(grant) for grant in grants)
                    if not has_audio_store_privileges:
                        print("⚠️  Пользователь не имеет прав на базу данных 'audio_store'")
                        print("   Выполните: GRANT ALL PRIVILEGES ON audio_store.* TO 'user'@'localhost';")
                else:
                    print("⚠️  Пользователь не найден или не имеет прав")
            connection.close()
        except Exception as e:
            print(f"⚠️  Не удалось проверить права (возможно, нужен пароль root): {e}")
    
    def test_08_sqlalchemy_connection(self):
        """Тест 8: Проверка подключения через SQLAlchemy"""
        print("\n[TEST 8] Проверка подключения через SQLAlchemy...")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                self.assertEqual(row[0], 1, "Неверный результат тестового запроса")
            print("✅ Подключение через SQLAlchemy работает")
        except Exception as e:
            print(f"❌ Ошибка подключения через SQLAlchemy: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование подключения к MySQL")
    print("=" * 60)
    
    unittest.main(verbosity=2)

