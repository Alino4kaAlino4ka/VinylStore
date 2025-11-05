#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная версия скрипта для запуска микросервисов
С эмодзи и тестами, как на скриншоте
"""

import os
import sys
import time
import subprocess
import signal
import requests
from pathlib import Path

# Настройка кодировки для корректного отображения русских символов
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class MicroserviceManager:
    def __init__(self):
        # Корень проекта - на 2 уровня выше от scripts/launch/
        self.base_path = Path(__file__).parent.parent.parent
        self.processes = []
        self.running = True
        self.stopped = False  # Флаг для отслеживания остановки
        
        # Настройка обработчика сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        print(f"\n🛑 Получен сигнал остановки...")
        self.running = False
        # Не вызываем stop_all_services() здесь, это сделает finally блок
        
    def start_service(self, name, port, path, env_vars=None):
        """Запустить сервис"""
        try:
            print(f"🚀 Запуск микросервиса {name}...")
            
            # Проверяем, что директория существует
            service_path = self.base_path / path
            if not service_path.exists():
                print(f"❌ Директория {service_path} не существует!")
                return False
            
            # Проверяем наличие main.py
            main_file = service_path / "main.py"
            if not main_file.exists():
                print(f"❌ Файл {main_file} не найден!")
                return False
            
            # Подготовка переменных окружения
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Команда для запуска сервиса
            # Добавляем настройку кодировки для Windows
            python_code = f"""
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
uvicorn.run(app, host='127.0.0.1', port={port}, reload=False)
"""
            cmd = [
                sys.executable, "-c", 
                python_code
            ]
            
            # Создаем файлы для логов
            log_dir = self.base_path / "logs"
            log_dir.mkdir(exist_ok=True)
            stdout_file = log_dir / f"{name}_stdout.log"
            stderr_file = log_dir / f"{name}_stderr.log"
            
            # Запуск процесса с логированием в файлы
            try:
                with open(stdout_file, 'w', encoding='utf-8') as stdout_f, \
                     open(stderr_file, 'w', encoding='utf-8') as stderr_f:
                    process = subprocess.Popen(
                        cmd,
                        cwd=service_path,
                        env=env,
                        stdout=stdout_f,
                        stderr=stderr_f,
                        text=True,
                        encoding='utf-8',
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
                    )
                
                # Небольшая задержка для проверки, что процесс не упал сразу
                time.sleep(0.5)
                
                # Проверяем, что процесс еще работает
                if process.poll() is not None:
                    # Процесс уже завершился - читаем ошибки
                    try:
                        with open(stderr_file, 'r', encoding='utf-8') as f:
                            error_output = f.read()
                        if error_output:
                            print(f"❌ {name} упал при запуске. Ошибка:\n{error_output[:500]}")
                        else:
                            print(f"❌ {name} завершился сразу после запуска (код: {process.returncode})")
                    except:
                        print(f"❌ {name} завершился сразу после запуска")
                    return False
                
                self.processes.append({
                    'name': name,
                    'process': process,
                    'port': port,
                    'stdout_file': stdout_file,
                    'stderr_file': stderr_file
                })
                
                print(f"✅ Микросервис {name} запущен на порту {port} (PID: {process.pid})")
                print(f"   Логи: {stdout_file.name}, {stderr_file.name}")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка при запуске процесса {name}: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Ошибка запуска {name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_all_services(self):
        """Запустить все сервисы"""
        print("🚀 Запуск микросервисов...")
        print("   Логи сервисов будут сохранены в папку logs/\n")
        
        # Запуск сервисов с согласованными портами и задержками
        services_started = []
        
        services = [
            ("catalog", 8000, "services/catalog", None),
            ("auth", 8001, "services/auth", None),
            ("orders", 8010, "services/orders", None),
            ("users", 8011, "services/users", None),
            ("prompts-manager", 8007, "services/prompts-manager", None),  # Должен запускаться до recommender
            ("recommender", 8012, "services/recommender", None),  # OPENROUTER_API_KEY загружается из config.env
            ("cart", 8005, "services/cart", None),
        ]
        
        for name, port, path, env_vars in services:
            if self.start_service(name, port, path, env_vars):
                services_started.append(name)
                time.sleep(1)  # Задержка между запусками
            else:
                print(f"⚠️  Пропущен сервис {name} из-за ошибки запуска")
        
        if len(services_started) > 0:
            print(f"\n✅ Успешно запущено сервисов: {len(services_started)}/{len(services)}")
            print(f"   Запущенные: {', '.join(services_started)}")
            return True
        else:
            print("\n❌ Не удалось запустить ни одного сервиса!")
            return False
    
    def check_service_health(self, name, port):
        """Проверка здоровья конкретного сервиса"""
        endpoints = [
            f"http://127.0.0.1:{port}/health",
            f"http://127.0.0.1:{port}/docs",
            f"http://127.0.0.1:{port}/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=2)
                if response.status_code in [200, 307, 308]:  # 307/308 - редиректы тоже OK
                    return True
            except:
                continue
        return False
    
    def wait_for_services_ready(self, timeout=60):
        """Ожидание готовности сервисов"""
        print("⏳ Ожидание запуска сервисов...")
        
        # Даем сервисам время на начальную загрузку
        print("   Даем сервисам 5 секунд на начальную загрузку...")
        time.sleep(5)
        
        start_time = time.time()
        ready_services = set()
        last_status_time = start_time
        
        while time.time() - start_time < timeout:
            for proc_info in self.processes:
                if proc_info['name'] not in ready_services:
                    if self.check_service_health(proc_info['name'], proc_info['port']):
                        ready_services.add(proc_info['name'])
                        print(f"✅ {proc_info['name']} готов к работе (порт {proc_info['port']})")
            
            # Показываем прогресс каждые 5 секунд
            if time.time() - last_status_time >= 5:
                elapsed = int(time.time() - start_time)
                print(f"   Прогресс: {len(ready_services)}/{len(self.processes)} сервисов готовы (прошло {elapsed}с)...")
                last_status_time = time.time()
            
            if len(ready_services) == len(self.processes):
                print("✅ Все сервисы готовы к работе!")
                return True
                
            time.sleep(2)
        
        print(f"⚠️  Таймаут ожидания запуска сервисов. Готово: {len(ready_services)}/{len(self.processes)}")
        
        # Проверяем, какие сервисы не готовы
        not_ready = [p['name'] for p in self.processes if p['name'] not in ready_services]
        if not_ready:
            print(f"   Не готовые сервисы: {', '.join(not_ready)}")
            # Показываем логи неготовых сервисов
            for name in not_ready:
                for proc_info in self.processes:
                    if proc_info['name'] == name:
                        # Проверяем, не упал ли процесс
                        if proc_info['process'].poll() is not None:
                            print(f"\n   ⚠️  {name} упал (код: {proc_info['process'].returncode})")
                            self.show_service_logs(name, lines=5)
                        break
        
        if len(ready_services) > 0:
            print("   Часть сервисов запущена, продолжаем работу...")
            return True
        return False
    
    def run_tests(self):
        """Запустить тесты сервисов"""
        print("\n🧪 Запуск тестов...")
        
        # Тест каталога
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест каталога: PASSED")
            else:
                print("❌ Тест каталога: FAILED")
        except:
            print("❌ Тест каталога: FAILED")
        
        # Тест аутентификации
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест аутентификации: PASSED")
            else:
                print("❌ Тест аутентификации: FAILED")
        except:
            print("❌ Тест аутентификации: FAILED")
        
        # Тест заказов
        try:
            response = requests.get("http://127.0.0.1:8010/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест заказов: PASSED")
            else:
                print("❌ Тест заказов: FAILED")
        except:
            print("❌ Тест заказов: FAILED")
        
        # Тест пользователей
        try:
            response = requests.get("http://127.0.0.1:8011/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест пользователей: PASSED")
            else:
                print("❌ Тест пользователей: FAILED")
        except:
            print("❌ Тест пользователей: FAILED")
        
        # Тест рекомендаций
        try:
            response = requests.get("http://127.0.0.1:8012/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест рекомендаций: PASSED")
            else:
                print("❌ Тест рекомендаций: FAILED")
        except:
            print("❌ Тест рекомендаций: FAILED")
        
        # Тест корзины
        try:
            response = requests.get("http://127.0.0.1:8005/health", timeout=3)
            if response.status_code == 200:
                print("✅ Тест корзины: PASSED")
            else:
                print("❌ Тест корзины: FAILED")
        except:
            print("❌ Тест корзины: FAILED")
        
        # Тест prompts-manager
        try:
            response = requests.get("http://127.0.0.1:8007/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and data.get("service") == "prompts-manager":
                    print("✅ Тест prompts-manager: PASSED")
                else:
                    print("❌ Тест prompts-manager: FAILED (неверный ответ)")
            else:
                print("❌ Тест prompts-manager: FAILED")
        except Exception as e:
            print(f"❌ Тест prompts-manager: FAILED ({str(e)})")
        
        print("🧪 Тесты завершены!")
    
    def show_service_logs(self, name, lines=10):
        """Показать последние строки логов сервиса"""
        for proc_info in self.processes:
            if proc_info['name'] == name:
                stderr_file = proc_info.get('stderr_file')
                if stderr_file and stderr_file.exists():
                    try:
                        with open(stderr_file, 'r', encoding='utf-8') as f:
                            log_lines = f.readlines()
                            if log_lines:
                                print(f"\nПоследние {min(lines, len(log_lines))} строк stderr для {name}:")
                                print("".join(log_lines[-lines:]))
                    except:
                        pass
                break
    
    def stop_all_services(self):
        """Остановить все сервисы"""
        if self.stopped:
            return  # Уже остановлено
        
        self.stopped = True
        print("🛑 Остановка сервисов...")
        
        for proc_info in self.processes:
            try:
                # Проверяем, работает ли процесс
                if proc_info['process'].poll() is None:
                    # Процесс еще работает - останавливаем
                    if sys.platform == "win32":
                        # На Windows используем taskkill для принудительного завершения
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc_info['process'].pid)], 
                                     capture_output=True)
                    else:
                        proc_info['process'].terminate()
                        try:
                            proc_info['process'].wait(timeout=5)
                        except:
                            proc_info['process'].kill()
                    print(f"✅ {proc_info['name']} остановлен")
                # Если процесс уже остановлен, просто пропускаем без сообщения
            except Exception as e:
                print(f"⚠️  Ошибка при остановке {proc_info['name']}: {e}")

def main():
    """Главная функция"""
    manager = MicroserviceManager()
    
    try:
        # Запуск всех сервисов
        if manager.start_all_services():
            # Ожидание готовности сервисов
            if manager.wait_for_services_ready():
                # Запуск тестов
                manager.run_tests()
                
                print("\n✅ Все сервисы запущены и работают!")
                print("   Нажмите Ctrl+C для остановки сервисов\n")
                
                # Мониторинг сервисов до прерывания
                try:
                    while manager.running:
                        time.sleep(5)
                        # Проверяем, что процессы еще работают
                        for proc_info in manager.processes:
                            if proc_info['process'].poll() is not None:
                                return_code = proc_info['process'].returncode
                                print(f"⚠️  {proc_info['name']} остановлен неожиданно (код: {return_code})")
                                manager.show_service_logs(proc_info['name'], lines=10)
                except KeyboardInterrupt:
                    pass
            else:
                print("⚠️  Не все сервисы готовы, но продолжаем работу...")
                print("   Нажмите Ctrl+C для остановки сервисов\n")
                
                # Все равно продолжаем работу, просто мониторим
                try:
                    while manager.running:
                        time.sleep(5)
                except KeyboardInterrupt:
                    pass
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if not manager.stopped:
            manager.stop_all_services()
        print("✅ Все сервисы остановлены.")

if __name__ == "__main__":
    main()
