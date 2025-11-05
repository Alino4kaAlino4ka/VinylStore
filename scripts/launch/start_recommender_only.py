#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для запуска только recommender сервиса для отладки
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    base_path = Path(__file__).parent
    service_path = base_path / "services" / "recommender"
    
    # Переменные окружения
    # ВАЖНО: API ключ должен быть установлен в config.env или переменных окружения системы
    # НЕ храните API ключи в коде!
    env = os.environ.copy()
    
    # Предупреждение, если ключ не найден
    if "OPENROUTER_API_KEY" not in env:
        print("WARNING: OPENROUTER_API_KEY не найден в переменных окружения!")
        print("Убедитесь, что config.env существует и содержит OPENROUTER_API_KEY")
    
    print("=" * 60)
    print("Запуск Recommender сервиса на порту 8004")
    print("=" * 60)
    print(f"Директория: {service_path}")
    print(f"Python: {sys.executable}")
    print("=" * 60)
    print("\nНажмите Ctrl+C для остановки\n")
    
    # Команда для запуска
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8004",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, cwd=service_path, env=env)
    except KeyboardInterrupt:
        print("\n\nОстановка сервиса...")
    except Exception as e:
        print(f"\nОшибка: {e}")

if __name__ == "__main__":
    main()

