#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт для запуска микросервисов с эмодзи
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# Настройка кодировки для корректного отображения русских символов
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class SimpleMicroserviceManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
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
        
    def start_service(self, name, port, path, env_vars=None):
        """Запустить сервис"""
        try:
            print(f"🚀 Запуск микросервиса {name}...")
            
            # Подготовка переменных окружения
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Команда для запуска сервиса
            cmd = [
                sys.executable, "-c", 
                f"from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port={port}, reload=True)"
            ]
            
            # Запуск процесса
            process = subprocess.Popen(
                cmd,
                cwd=self.base_path / path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            self.processes.append({
                'name': name,
                'process': process,
                'port': port
            })
            
            print(f"✅ Микросервис {name} запущен на порту {port}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска {name}: {e}")
            return False
    
    def start_all_services(self):
        """Запустить все сервисы"""
        print("🚀 Запуск микросервисов...")
        
        # Запуск сервисов
        self.start_service("auth", 8001, "services/auth")
        self.start_service("catalog", 8002, "services/catalog")
        self.start_service("cart", 8004, "services/cart")
        self.start_service("orders", 8003, "services/orders")
        self.start_service("recommender", 8005, "services/recommender", None)  # OPENROUTER_API_KEY из config.env
        self.start_service("web", 8000, "src")
        
        return True
    
    def wait_for_services(self, timeout=10):
        """Ожидание запуска сервисов"""
        print("⏳ Ожидание запуска сервисов...")
        time.sleep(timeout)
        print("❌ Таймаут ожидания запуска сервисов")
        return False
    
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
    
    def run_tests(self):
        """Запустить тесты сервисов"""
        print("\n🧪 Запуск тестов...")
        
        # Простые тесты
        test_results = []
        
        # Тест каталога
        try:
            import requests
            response = requests.get("http://127.0.0.1:8002/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Тест каталога: PASSED")
                test_results.append(True)
            else:
                print("❌ Тест каталога: FAILED")
                test_results.append(False)
        except:
            print("❌ Тест каталога: FAILED")
            test_results.append(False)
        
        # Тест корзины
        try:
            response = requests.get("http://127.0.0.1:8004/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Тест корзины: PASSED")
                test_results.append(True)
            else:
                print("❌ Тест корзины: FAILED")
                test_results.append(False)
        except:
            print("❌ Тест корзины: FAILED")
            test_results.append(False)
        
        # Тест заказов
        try:
            response = requests.get("http://127.0.0.1:8003/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Тест заказов: PASSED")
                test_results.append(True)
            else:
                print("❌ Тест заказов: FAILED")
                test_results.append(False)
        except:
            print("❌ Тест заказов: FAILED")
            test_results.append(False)
        
        # Тест рекомендаций
        try:
            response = requests.get("http://127.0.0.1:8005/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Тест рекомендаций: PASSED")
                test_results.append(True)
            else:
                print("❌ Тест рекомендаций: FAILED")
                test_results.append(False)
        except:
            print("❌ Тест рекомендаций: FAILED")
            test_results.append(False)
        
        print("🧪 Тесты завершены!")
        return test_results

def main():
    """Главная функция"""
    manager = SimpleMicroserviceManager()
    
    try:
        # Запуск всех сервисов
        if manager.start_all_services():
            # Ожидание запуска сервисов
            manager.wait_for_services()
            
            # Запуск тестов
            manager.run_tests()
            
            # Остановка сервисов
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
