#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска всех сервисов и тестов
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    """Запускает сервисы и затем тесты"""
    print("🚀 Запуск сервисов и тестов...")
    print("=" * 60)
    
    # Запускаем сервисы
    print("\n1️⃣ Запуск сервисов...")
    base_path = Path(__file__).parent.parent
    services_script = base_path / "start_services_final.py"
    
    if not services_script.exists():
        print(f"❌ Файл {services_script} не найден!")
        return False
    
    # Запускаем сервисы в фоне
    print(f"   Запуск: {services_script}")
    process = subprocess.Popen(
        [sys.executable, str(services_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(base_path)
    )
    
    # Ждем запуска сервисов
    print("\n2️⃣ Ожидание запуска сервисов (30 секунд)...")
    time.sleep(30)
    
    # Запускаем тесты
    print("\n3️⃣ Запуск тестов...")
    test_script = Path(__file__).parent / "test_all_services.py"
    
    result = subprocess.run(
        [sys.executable, str(test_script)],
        cwd=str(base_path)
    )
    
    # Останавливаем сервисы
    print("\n4️⃣ Остановка сервисов...")
    try:
        process.terminate()
        process.wait(timeout=5)
    except:
        process.kill()
    
    return result.returncode == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

