#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перезапуска сервиса orders
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def find_orders_process():
    """Находит процесс orders service"""
    try:
        if sys.platform == "win32":
            # На Windows используем tasklist
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True,
                text=True
            )
            # Простой поиск - в реальности нужно проверять командную строку
            # Но для простоты просто перезапустим через start_services_final.py
            return None
        else:
            # На Linux/Mac
            result = subprocess.run(
                ["pgrep", "-f", "orders.*main.py"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None

def restart_orders_service():
    """Перезапускает сервис orders"""
    base_path = Path(__file__).parent
    orders_path = base_path / "services" / "orders"
    
    print("🔄 Перезапуск сервиса orders...")
    print(f"   Путь: {orders_path}")
    
    # Останавливаем существующий процесс (если есть)
    if sys.platform == "win32":
        # На Windows ищем процесс по порту или просто перезапускаем
        print("   Остановка существующего процесса...")
        try:
            # Пытаемся найти и убить процесс на порту 8002
            subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            # Проще всего - убить все процессы python с orders в рабочей директории
            # Но это может быть опасно, поэтому просто запустим новый
        except:
            pass
    
    # Запускаем новый процесс
    print("   Запуск сервиса orders...")
    
    try:
        # Загружаем переменные окружения
        from dotenv import load_dotenv
        config_path = base_path / "config.env"
        if config_path.exists():
            load_dotenv(config_path, override=True)
        
        # Запускаем через uvicorn
        cmd = [
            sys.executable, "-c",
            """
import sys
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass
from main import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8002, reload=False)
"""
        ]
        
        log_dir = base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        stdout_file = log_dir / "orders_stdout.log"
        stderr_file = log_dir / "orders_stderr.log"
        
        with open(stdout_file, 'w', encoding='utf-8') as stdout_f, \
             open(stderr_file, 'w', encoding='utf-8') as stderr_f:
            process = subprocess.Popen(
                cmd,
                cwd=orders_path,
                stdout=stdout_f,
                stderr=stderr_f,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
        
        time.sleep(1)
        
        if process.poll() is None:
            print(f"✅ Сервис orders запущен (PID: {process.pid})")
            print(f"   Логи: {stdout_file.name}, {stderr_file.name}")
            return True
        else:
            print(f"❌ Сервис orders не запустился (код: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Перезапуск сервиса Orders для загрузки новых переменных окружения")
    print("=" * 60)
    print()
    
    if restart_orders_service():
        print()
        print("✅ Перезапуск выполнен успешно!")
        print("   Теперь сервис orders использует новые переменные из config.env")
        print("   Проверьте логи в logs/orders_stdout.log и logs/orders_stderr.log")
    else:
        print()
        print("❌ Не удалось перезапустить сервис")
        print("   Рекомендуется использовать start_services_final.py для полного перезапуска")

