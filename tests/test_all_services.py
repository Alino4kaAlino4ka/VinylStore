#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный тест всех сервисов системы
"""

import requests
import json
import time
import sys
import io

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_service(service_name, port, endpoint="/health", method="GET", data=None, timeout=None):
    """Тестирует отдельный сервис"""
    url = f"http://127.0.0.1:{port}{endpoint}"
    
    print(f"\n🧪 Тестирование {service_name} (порт {port})...")
    print(f"URL: {url}")
    
    # Устанавливаем таймаут по умолчанию
    if timeout is None:
        timeout = 90 if method == "POST" and "recommendations" in endpoint else (30 if method == "POST" else 10)
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        print(f"📡 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ {service_name}: PASSED")
            if response.content:
                try:
                    data = response.json()
                    print(f"📦 Ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"📦 Ответ: {response.text[:200]}...")
            return True
        else:
            print(f"❌ {service_name}: FAILED - {response.status_code}")
            print(f"Ошибка: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name}: FAILED - Сервис недоступен")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {service_name}: FAILED - Таймаут")
        return False
    except Exception as e:
        print(f"❌ {service_name}: FAILED - {e}")
        return False

def test_catalog_products():
    """Тестирует получение продуктов из каталога"""
    return test_service("Каталог (продукты)", 8000, "/api/v1/products")

def test_recommendations():
    """Тестирует генерацию рекомендаций"""
    data = {
        "user_preferences": "classic rock and progressive rock",
        "max_recommendations": 3
    }
    return test_service("Рекомендации", 8004, "/api/v1/recommendations/generate", "POST", data, timeout=120)

def test_cart_calculation():
    """Тестирует расчет корзины"""
    data = {
        "product_ids": ["1", "2", "3"]
    }
    return test_service("Корзина (расчет)", 8005, "/api/v1/cart/calculate", "POST", data)

def test_orders():
    """Тестирует получение списка заказов"""
    return test_service("Заказы", 8002, "/api/v1/orders", "GET")  # Исправлено с 8003 на 8002

def test_users():
    """Тестирует получение пользователей"""
    return test_service("Пользователи", 8003, "/api/v1/users")  # Исправлено с 8006 на 8003

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск комплексного тестирования всех сервисов...")
    print("=" * 60)
    
    # Проверяем доступность сервисов перед тестированием
    print("\n⏳ Проверка доступности сервисов...")
    services_to_check = [
        ("Каталог", 8000),
        ("Аутентификация", 8001),
        ("Заказы", 8002),
        ("Пользователи", 8003),
        ("Рекомендации", 8004),
        ("Корзина", 8005)
    ]
    
    available_services = []
    for service_name, port in services_to_check:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                available_services.append(service_name)
                print(f"✅ {service_name} доступен")
            else:
                print(f"⚠️  {service_name} отвечает с кодом {response.status_code}")
        except:
            print(f"❌ {service_name} недоступен (порт {port})")
    
    if len(available_services) < len(services_to_check):
        print(f"\n⚠️  ВНИМАНИЕ: Только {len(available_services)}/{len(services_to_check)} сервисов доступны!")
        print("   Убедитесь, что все сервисы запущены: python start_services_final.py")
        print("   Продолжаем тестирование доступных сервисов...\n")
    
    results = {}
    
    # Тест здоровья сервисов
    print("\n📋 ТЕСТ 1: Проверка здоровья сервисов")
    print("-" * 40)
    
    services = [
        ("Каталог", 8000),
        ("Аутентификация", 8001),
        ("Заказы", 8010),  # Обновлен порт
        ("Пользователи", 8011),  # Обновлен порт
        ("Рекомендации", 8012),  # Обновлен порт
        ("Корзина", 8005),
        ("Prompts Manager", 8007)
    ]
    
    for service_name, port in services:
        results[f"{service_name}_health"] = test_service(service_name, port)
    
    # Тест функциональности
    print("\n📋 ТЕСТ 2: Проверка функциональности")
    print("-" * 40)
    
    results["catalog_products"] = test_catalog_products()
    results["recommendations"] = test_recommendations()
    results["cart_calculation"] = test_cart_calculation()
    results["orders"] = test_orders()
    results["users"] = test_users()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    print(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Детальные результаты:")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} тестов провалено")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

