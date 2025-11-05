#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для резервного копирования базы данных MySQL
Поддерживает автоматическое создание бэкапов с датой и временем
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
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
# Корень проекта - на 4 уровня выше от scripts/utils/db/backup_db.py
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

def parse_database_url(database_url):
    """Парсит DATABASE_URL и возвращает компоненты"""
    if not database_url.startswith("mysql"):
        return None
    
    # Формат: mysql+pymysql://user:password@host/database_name
    try:
        url_part = database_url.replace("mysql+pymysql://", "").replace("mysql://", "")
        if "@" in url_part:
            auth_part, rest = url_part.split("@", 1)
            user, password = auth_part.split(":", 1)
            if "/" in rest:
                host_part, database = rest.split("/", 1)
                host = host_part.split(":")[0] if ":" in host_part else host_part
                port = host_part.split(":")[1] if ":" in host_part else "3306"
            else:
                host = rest
                port = "3306"
                database = None
        else:
            return None
        
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    except Exception as e:
        print(f"❌ Ошибка парсинга DATABASE_URL: {e}")
        return None

def create_backup(backup_dir=None, keep_days=30):
    """
    Создает резервную копию базы данных
    
    Args:
        backup_dir: Директория для сохранения бэкапов (по умолчанию: project_root/backups)
        keep_days: Количество дней для хранения старых бэкапов (по умолчанию: 30)
    """
    print("=" * 60)
    print("🗄️  Резервное копирование базы данных")
    print("=" * 60)
    
    # Получаем DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("❌ DATABASE_URL не найден в config.env")
        return False
    
    # Парсим DATABASE_URL
    db_info = parse_database_url(database_url)
    if not db_info:
        print("❌ Не удалось распарсить DATABASE_URL")
        print(f"   DATABASE_URL должен быть в формате: mysql+pymysql://user:password@host/database")
        return False
    
    if not db_info['database']:
        print("❌ Имя базы данных не указано в DATABASE_URL")
        return False
    
    # Определяем директорию для бэкапов
    if not backup_dir:
        backup_dir = project_root / 'backups'
    else:
        backup_dir = Path(backup_dir)
    
    # Создаем директорию для бэкапов, если её нет
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Директория для бэкапов: {backup_dir}")
    
    # Формируем имя файла бэкапа
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"audio_store_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    print(f"📦 База данных: {db_info['database']}")
    print(f"🖥️  Хост: {db_info['host']}:{db_info['port']}")
    print(f"👤 Пользователь: {db_info['user']}")
    print("-" * 60)
    
    # Проверяем наличие mysqldump
    try:
        result = subprocess.run(
            ["mysqldump", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise FileNotFoundError
        print(f"✅ mysqldump найден: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ mysqldump не найден в PATH")
        print("   Установите MySQL Client Tools или добавьте mysqldump в PATH")
        return False
    
    # Создаем бэкап
    print(f"🔄 Создание бэкапа: {backup_filename}")
    try:
        cmd = [
            "mysqldump",
            f"--host={db_info['host']}",
            f"--port={db_info['port']}",
            f"--user={db_info['user']}",
            f"--password={db_info['password']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            db_info['database']
        ]
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 минут максимум
            )
        
        if result.returncode != 0:
            print(f"❌ Ошибка при создании бэкапа:")
            print(result.stderr)
            if backup_path.exists():
                backup_path.unlink()
            return False
        
        # Проверяем размер файла
        file_size = backup_path.stat().st_size
        if file_size == 0:
            print("❌ Бэкап создан, но файл пуст!")
            backup_path.unlink()
            return False
        
        print(f"✅ Бэкап успешно создан!")
        print(f"   Файл: {backup_path}")
        print(f"   Размер: {file_size / 1024 / 1024:.2f} MB")
        
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при создании бэкапа (превышено 5 минут)")
        if backup_path.exists():
            backup_path.unlink()
        return False
    except Exception as e:
        print(f"❌ Ошибка при создании бэкапа: {e}")
        if backup_path.exists():
            backup_path.unlink()
        return False
    
    # Удаляем старые бэкапы (старше keep_days дней)
    if keep_days > 0:
        print(f"🧹 Очистка старых бэкапов (старше {keep_days} дней)...")
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            for backup_file in backup_dir.glob("audio_store_backup_*.sql"):
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"✅ Удалено старых бэкапов: {deleted_count}")
            else:
                print("✅ Старые бэкапы не найдены")
        except Exception as e:
            print(f"⚠️  Предупреждение при очистке старых бэкапов: {e}")
    
    print("-" * 60)
    print("✅ Резервное копирование завершено успешно!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Резервное копирование базы данных MySQL')
    parser.add_argument(
        '--backup-dir',
        type=str,
        help='Директория для сохранения бэкапов (по умолчанию: project_root/backups)'
    )
    parser.add_argument(
        '--keep-days',
        type=int,
        default=30,
        help='Количество дней для хранения старых бэкапов (по умолчанию: 30)'
    )
    
    args = parser.parse_args()
    
    success = create_backup(
        backup_dir=args.backup_dir,
        keep_days=args.keep_days
    )
    
    sys.exit(0 if success else 1)

