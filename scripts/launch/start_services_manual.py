#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ручной запуск всех сервисов
"""

import subprocess
import time
import os
import sys

def start_service(name, port, path, env_vars=None):
    """Запустить сервис в отдельном процессе"""
    print(f"🚀 Запуск {name} на порту {port}...")
    
    # Подготовка переменных окружения
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        # Запуск процесса
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=path,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        print(f"✅ {name} запущен (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска {name}: {e}")
        return None

def main():
    """Главная функция"""
    print("🚀 Ручной запуск всех сервисов...")
    
    processes = []
    
    # Запуск сервисов
    services = [
        ("Каталог", 8000, "services/catalog", None),
        ("Аутентификация", 8001, "services/auth", None),
        ("Заказы", 8003, "services/orders", None),
        ("Пользователи", 8006, "services/users", None),
        ("Менеджер промптов", 8007, "services/prompts-manager", None),
        ("Рекомендации", 8004, "services/recommender", None),  # OPENROUTER_API_KEY загружается из config.env
        ("Корзина", 8005, "services/cart", None),
    ]
    
    for name, port, path, env_vars in services:
        process = start_service(name, port, path, env_vars)
        if process:
            processes.append((name, process))
        time.sleep(2)
    
    print(f"\n✅ Запущено {len(processes)} сервисов")
    print("\nСервисы:")
    for name, process in processes:
        print(f"  - {name}: PID {process.pid}")
    
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        # Ожидание
        while True:
            time.sleep(5)
            # Проверка, что процессы еще работают
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} остановлен неожиданно")
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        for name, process in processes:
            try:
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                 capture_output=True)
                else:
                    process.terminate()
                print(f"✅ {name} остановлен")
            except:
                pass
        print("✅ Все сервисы остановлены")

if __name__ == "__main__":
    main()

