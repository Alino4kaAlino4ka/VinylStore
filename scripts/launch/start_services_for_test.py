#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт для запуска catalog и recommender для тестирования
"""

import subprocess
import sys
import time
from pathlib import Path

def start_service(name, port, path):
    """Запустить сервис в отдельном окне"""
    base_path = Path(__file__).parent
    service_path = base_path / path
    
    cmd = [
        sys.executable, "-c",
        f"from main import app; import uvicorn; print('Starting {name} on port {port}...'); uvicorn.run(app, host='127.0.0.1', port={port})"
    ]
    
    if sys.platform == "win32":
        # Запуск в отдельном окне cmd
        subprocess.Popen(
            ["start", "cmd", "/k"] + cmd,
            cwd=str(service_path),
            shell=True
        )
    else:
        subprocess.Popen(cmd, cwd=str(service_path))
    
    print(f"✅ {name} запускается на порту {port}...")

def main():
    print("🚀 Запуск catalog и recommender для тестирования...\n")
    
    # Запуск catalog
    start_service("Catalog Service", 8000, "services/catalog")
    time.sleep(2)
    
    # Запус recommender
    start_service("Recommender Service", 8004, "services/recommender")
    time.sleep(2)
    
    print("\n✅ Сервисы запущены!")
    print("📝 Catalog API: http://127.0.0.1:8000")
    print("📝 Recommender API: http://127.0.0.1:8004")
    print("\n⏳ Подождите 5-10 секунд для полной инициализации...")
    print("🌐 Затем откройте: tests/test_ai_description_generator.html\n")

if __name__ == "__main__":
    main()
