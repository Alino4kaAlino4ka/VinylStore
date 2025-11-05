#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перезапуска сервиса каталога
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def kill_process_on_port(port):
    """Убить процесс на указанном порту"""
    try:
        # Windows
        if sys.platform == "win32":
            # Найти PID процесса на порту
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", pid],
                                capture_output=True,
                                check=False
                            )
                            print(f"✅ Остановлен процесс {pid} на порту {port}")
                            return True
                        except:
                            pass
        else:
            # Linux/Mac
            subprocess.run(
                ["lsof", "-ti", f":{port}", "|", "xargs", "kill", "-9"],
                shell=True,
                capture_output=True
            )
        return True
    except Exception as e:
        print(f"⚠️  Не удалось остановить процесс: {e}")
        return False

def start_catalog_service():
    """Запустить сервис каталога"""
    base_path = Path(__file__).parent
    catalog_path = base_path / "services" / "catalog"
    
    if not catalog_path.exists():
        print(f"❌ Путь {catalog_path} не существует!")
        return False
    
    # Команда для запуска
    python_code = """
from main import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000, reload=False)
"""
    
    try:
        if sys.platform == "win32":
            # Windows - запуск в новом окне
            cmd = [
                "cmd", "/c", "start", "Catalog Service",
                "cmd", "/k",
                f"cd /d {catalog_path} && python -c \"{python_code.replace(chr(10), ' ')}\""
            ]
            subprocess.Popen(cmd, shell=False)
        else:
            # Linux/Mac
            cmd = [
                sys.executable, "-c",
                python_code
            ]
            subprocess.Popen(cmd, cwd=catalog_path)
        
        print("✅ Сервис каталога запущен")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False

def main():
    print("🔄 Перезапуск сервиса каталога...")
    
    # Остановить существующий процесс
    print("🛑 Остановка текущего сервиса...")
    kill_process_on_port(8000)
    
    # Подождать
    print("⏳ Ожидание 2 секунды...")
    time.sleep(2)
    
    # Запустить новый процесс
    print("🚀 Запуск нового сервиса...")
    start_catalog_service()
    
    # Подождать и проверить
    print("⏳ Ожидание 3 секунды для запуска...")
    time.sleep(3)
    
    # Проверить статус
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Сервис каталога успешно перезапущен и работает!")
            
            # Проверить, что новые URL используются
            response = requests.get("http://localhost:8000/api/v1/products", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('products'):
                    first_product = data['products'][0]
                    cover_url = first_product.get('cover_url', '')
                    if 'placeholder.com' in cover_url:
                        print(f"✅ Новые URL изображений активны: {cover_url[:50]}...")
                    else:
                        print(f"⚠️  Старый URL все еще используется: {cover_url[:50]}...")
        else:
            print("⚠️  Сервис запущен, но health check не прошел")
    except Exception as e:
        print(f"⚠️  Не удалось проверить статус: {e}")
        print("   Проверьте вручную: http://localhost:8000/health")

if __name__ == "__main__":
    main()


