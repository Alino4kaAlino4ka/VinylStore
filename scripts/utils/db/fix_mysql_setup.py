#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для диагностики и помощи в настройке MySQL
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корень проекта в PYTHONPATH для импорта модулей
# Корень проекта - на 4 уровня выше от scripts/utils/db/fix_mysql_setup.py
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

import pymysql

def check_mysql_setup():
    """Проверка и помощь в настройке MySQL"""
    print("=" * 60)
    print("Диагностика и настройка MySQL")
    print("=" * 60)
    
    issues = []
    fixes = []
    
    # 1. Проверка подключения к MySQL серверу
    print("\n[1] Проверка доступности MySQL сервера...")
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',  # Попробуем без пароля
            connect_timeout=5
        )
        print("✅ MySQL сервер доступен")
        root_connection = connection
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print("⚠️  Требуется пароль root для проверки")
            root_password = input("Введите пароль root MySQL (или Enter для пропуска): ").strip()
            if root_password:
                try:
                    root_connection = pymysql.connect(
                        host='localhost',
                        user='root',
                        password=root_password,
                        connect_timeout=5
                    )
                    print("✅ Подключение к MySQL как root успешно")
                except Exception as e2:
                    print(f"❌ Не удалось подключиться как root: {e2}")
                    print("   Продолжаем проверку без доступа root...")
                    root_connection = None
            else:
                root_connection = None
        else:
            print(f"❌ Ошибка подключения: {e}")
            issues.append("MySQL сервер недоступен или не запущен")
            root_connection = None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        issues.append("Ошибка подключения к MySQL")
        root_connection = None
    
    # 2. Проверка пользователя
    print("\n[2] Проверка пользователя 'user'@'localhost'...")
    if root_connection:
        try:
            with root_connection.cursor() as cursor:
                cursor.execute("SELECT User, Host FROM mysql.user WHERE User='user' AND Host='localhost'")
                result = cursor.fetchone()
                if result:
                    print("✅ Пользователь 'user'@'localhost' существует")
                else:
                    print("❌ Пользователь 'user'@'localhost' не найден")
                    issues.append("Пользователь 'user'@'localhost' не существует")
                    fixes.append("CREATE USER 'user'@'localhost' IDENTIFIED BY '1234';")
        except Exception as e:
            print(f"⚠️  Ошибка при проверке пользователя: {e}")
    else:
        print("⚠️  Пропущено (нет доступа root)")
    
    # 3. Проверка базы данных
    print("\n[3] Проверка базы данных 'audio_store'...")
    if root_connection:
        try:
            with root_connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES LIKE 'audio_store'")
                result = cursor.fetchone()
                if result:
                    print("✅ База данных 'audio_store' существует")
                else:
                    print("❌ База данных 'audio_store' не найдена")
                    issues.append("База данных 'audio_store' не существует")
                    fixes.append("CREATE DATABASE audio_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        except Exception as e:
            print(f"⚠️  Ошибка при проверке базы данных: {e}")
    else:
        print("⚠️  Пропущено (нет доступа root)")
    
    # 4. Проверка прав
    print("\n[4] Проверка прав пользователя...")
    if root_connection:
        try:
            with root_connection.cursor() as cursor:
                cursor.execute("SHOW GRANTS FOR 'user'@'localhost'")
                grants = cursor.fetchall()
                if grants:
                    has_audio_store = any('audio_store' in str(grant[0]) for grant in grants)
                    if has_audio_store:
                        print("✅ Пользователь имеет права на 'audio_store'")
                    else:
                        print("❌ Пользователь не имеет прав на 'audio_store'")
                        issues.append("Пользователь не имеет прав на базу данных")
                        fixes.append("GRANT ALL PRIVILEGES ON audio_store.* TO 'user'@'localhost';")
                        fixes.append("FLUSH PRIVILEGES;")
                else:
                    print("❌ Пользователь не найден или не имеет прав")
        except Exception as e:
            print(f"⚠️  Ошибка при проверке прав: {e}")
    else:
        print("⚠️  Пропущено (нет доступа root)")
    
    # 5. Проверка подключения с учетными данными из config
    print("\n[5] Проверка подключения с учетными данными из config.env...")
    try:
        connection = pymysql.connect(
            host='localhost',
            user='user',
            password='1234',
            database='audio_store',
            connect_timeout=5
        )
        print("✅ Подключение с учетными данными из config.env работает!")
        connection.close()
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1045:
            print("❌ Доступ запрещен для пользователя 'user'@'localhost'")
            issues.append("Ошибка доступа: Access denied")
        elif e.args[0] == 1049:
            print("❌ База данных 'audio_store' не существует")
            issues.append("База данных не существует")
        else:
            print(f"❌ Ошибка подключения: {e}")
            issues.append(f"Ошибка подключения: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        issues.append(f"Ошибка: {e}")
    
    # Закрываем соединение root, если открыто
    if root_connection:
        root_connection.close()
    
    # Вывод результатов
    print("\n" + "=" * 60)
    if not issues:
        print("✅ Все проверки пройдены успешно!")
        print("   MySQL настроен корректно.")
        return True
    else:
        print("❌ Найдены проблемы:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        if fixes:
            print("\n📝 SQL команды для исправления:")
            print("   Выполните их в MySQL (mysql -u root -p):")
            print()
            for fix in fixes:
                print(f"   {fix}")
            
            print("\n   Или используйте готовый скрипт:")
            print("   mysql -u root -p < database/create_mysql_database.sql")
        
        return False


if __name__ == "__main__":
    success = check_mysql_setup()
    sys.exit(0 if success else 1)

