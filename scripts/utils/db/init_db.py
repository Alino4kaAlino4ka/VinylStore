#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт инициализации базы данных
Создает все таблицы, определенные в моделях database.models
Поддерживает как SQLite, так и MySQL (настройки из config.env)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        else:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        pass

# Добавляем корень проекта в PYTHONPATH для импорта модулей
# Корень проекта - на 4 уровня выше от scripts/utils/db/init_db.py
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

from database.connection import init_db, DATABASE_URL

if __name__ == "__main__":
    print("=" * 60)
    print("Инициализация базы данных")
    print("=" * 60)
    
    # Определяем тип БД для информативного сообщения
    if DATABASE_URL.startswith("mysql"):
        db_type = "MySQL"
        print(f"Тип БД: {db_type}")
        print(f"Подключение: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    elif DATABASE_URL.startswith("sqlite"):
        db_type = "SQLite"
        print(f"Тип БД: {db_type}")
        print(f"Путь к файлу: {DATABASE_URL.split('///')[-1] if '///' in DATABASE_URL else 'по умолчанию'}")
    else:
        db_type = "Неизвестный"
        print(f"Тип БД: {db_type}")
    
    print("-" * 60)
    
    try:
        init_db()
        print("-" * 60)
        print("✅ Инициализация завершена успешно!")
    except Exception as e:
        print("-" * 60)
        print(f"❌ Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
