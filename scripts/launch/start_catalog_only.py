#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для запуска только catalog сервиса
"""
import subprocess
import sys
from pathlib import Path

def main():
    base_path = Path(__file__).parent
    service_path = base_path / "services" / "catalog"
    
    print("=" * 60)
    print("Запуск Catalog сервиса на порту 8000")
    print("=" * 60)
    print(f"Директория: {service_path}")
    print("\nНажмите Ctrl+C для остановки\n")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, cwd=service_path)
    except KeyboardInterrupt:
        print("\n\nОстановка сервиса...")
    except Exception as e:
        print(f"\nОшибка: {e}")

if __name__ == "__main__":
    main()

