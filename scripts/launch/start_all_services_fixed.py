#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный скрипт для запуска всех микросервисов
Согласованы все порты и эндпоинты
"""

import os
import sys
import time
import subprocess
import threading
import requests
import signal
from pathlib import Path

# Настройка кодировки для корректного отображения русских символов
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class MicroserviceManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.services = []
        self.processes = []
        self.running = True
        
        # Настройка обработчика сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        print(f"\n🛑 Получен сигнал остановки...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)
        
    def add_service(self, name, port, path, env_vars=None, health_endpoint="/health"):
        """Добавить сервис для запуска"""
        service_info = {
            'name': name,
            'port': port,
            'path': self.base_path / path,
            'env_vars': env_vars or {},
            'health_endpoint': health_endpoint
        }
        self.services.append(service_info)
        
    def check_service_health(self, port, endpoint="/health"):
        """Проверить готовность сервиса"""
        try:
            response = requests.get(f"http://127.0.0.1:{port}{endpoint}", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def start_service(self, service_info):
        """Запустить отдельный сервис"""
        try:
            print(f"🚀 Запуск микросервиса {service_info['name']}...")
            
            # Подготовка переменных окружения
            env = os.environ.copy()
            env.update(service_info['env_vars'])
            
            # Команда для запуска сервиса
            cmd = [
                sys.executable, "-c", 
                f"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port={service_info['port']}, reload=True)"
            ]
            
            # Запуск процесса
            process = subprocess.Popen(
                cmd,
                cwd=service_info['path'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # Даем процессу время на запуск и проверяем ошибки
            time.sleep(3)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ {service_info['name']} завершился с ошибкой:")
                if stderr:
                    print(f"Ошибка: {stderr[:200]}...")
                return False
            
            self.processes.append({
                'name': service_info['name'],
                'process': process,
                'port': service_info['port'],
                'health_endpoint': service_info['health_endpoint']
            })
            
            print(f"✅ Микросервис {service_info['name']} запущен на порту {service_info['port']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска {service_info['name']}: {e}")
            return False
    
    def start_all_services(self):
        """Запустить все сервисы"""
        print("🚀 Запуск микросервисов...")
        
        # Настройка сервисов с согласованными портами
        self.add_service("catalog", 8000, "services/catalog", health_endpoint="/health")
        self.add_service("auth", 8001, "services/auth", health_endpoint="/health")
        self.add_service("orders", 8002, "services/orders", health_endpoint="/health")
        self.add_service("users", 8003, "services/users", health_endpoint="/health")
        self.add_service("prompts-manager", 8007, "services/prompts-manager", health_endpoint="/health")
        self.add_service("recommender", 8004, "services/recommender", None, health_endpoint="/health")  # OPENROUTER_API_KEY из config.env
        self.add_service("cart", 8005, "services/cart", health_endpoint="/health")
        
        # Запуск сервисов
        for service in self.services:
            self.start_service(service)
            time.sleep(2)  # Увеличенная задержка между запусками
        
        return True
    
    def wait_for_services_ready(self, timeout=90):
        """Ожидание готовности всех сервисов"""
        print("⏳ Ожидание запуска сервисов...")
        
        start_time = time.time()
        ready_services = set()
        
        while time.time() - start_time < timeout:
            for proc_info in self.processes:
                if proc_info['name'] not in ready_services:
                    if self.check_service_health(proc_info['port'], proc_info['health_endpoint']):
                        ready_services.add(proc_info['name'])
                        print(f"✅ {proc_info['name']} готов к работе")
            
            if len(ready_services) == len(self.processes):
                print("✅ Все сервисы готовы к работе!")
                return True
                
            time.sleep(3)
        
        print(f"❌ Таймаут ожидания запуска сервисов. Готово: {len(ready_services)}/{len(self.processes)}")
        return len(ready_services) > 0
    
    def monitor_services(self):
        """Мониторинг состояния сервисов"""
        print("\nМониторинг сервисов (Ctrl+C для остановки)...")
        try:
            while self.running:
                time.sleep(10)
                for proc_info in self.processes:
                    if proc_info['process'].poll() is not None:
                        print(f"⚠️  {proc_info['name']} остановлен неожиданно")
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервисов...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """Остановить все сервисы"""
        print("🛑 Остановка сервисов...")
        for proc_info in self.processes:
            try:
                if sys.platform == "win32":
                    # На Windows используем taskkill для принудительного завершения
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc_info['process'].pid)], 
                                 capture_output=True)
                else:
                    proc_info['process'].terminate()
                print(f"✅ {proc_info['name']} остановлен")
            except:
                pass
    
    def check_services_status(self):
        """Проверить статус сервисов"""
        print("\nСтатус сервисов:")
        for proc_info in self.processes:
            status = "работает" if proc_info['process'].poll() is None else "остановлен"
            print(f"- {proc_info['name']}: {status}")
    
    def run_quick_test(self):
        """Быстрый тест основных сервисов"""
        print("\n🧪 Быстрый тест сервисов...")
        
        # Тест каталога
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Каталог: OK")
            else:
                print("❌ Каталог: FAILED")
        except:
            print("❌ Каталог: FAILED")
        
        # Тест рекомендаций
        try:
            response = requests.get("http://127.0.0.1:8004/health", timeout=5)
            if response.status_code == 200:
                print("✅ Рекомендации: OK")
            else:
                print("❌ Рекомендации: FAILED")
        except:
            print("❌ Рекомендации: FAILED")
        
        # Тест корзины
        try:
            response = requests.get("http://127.0.0.1:8005/health", timeout=5)
            if response.status_code == 200:
                print("✅ Корзина: OK")
            else:
                print("❌ Корзина: FAILED")
        except:
            print("❌ Корзина: FAILED")
        
        print("🧪 Быстрый тест завершен!")

def main():
    """Главная функция"""
    manager = MicroserviceManager()
    
    try:
        # Запуск всех сервисов
        if manager.start_all_services():
            # Ожидание готовности сервисов
            if manager.wait_for_services_ready():
                # Быстрый тест
                manager.run_quick_test()
                
                # Проверка статуса
                manager.check_services_status()
                
                # Мониторинг
                manager.monitor_services()
            else:
                print("❌ Не удалось запустить все сервисы")
                manager.stop_all_services()
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        manager.stop_all_services()
        print("✅ Все сервисы остановлены.")

if __name__ == "__main__":
    main()

