#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая проверка статуса сервисов
"""
import requests
import sys

services = {
    "Catalog": "http://127.0.0.1:8000",
    "Auth": "http://127.0.0.1:8001",
    "Orders": "http://127.0.0.1:8010",
    "Users": "http://127.0.0.1:8011",
    "Recommender": "http://127.0.0.1:8012",
    "Cart": "http://127.0.0.1:8005",
}

def check_service(name, url):
    """Проверка статуса сервиса"""
    endpoints = [
        f"{url}/health",
        f"{url}/docs",
        f"{url}/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code in [200, 307, 308]:
                print(f"✓ {name}: OK ({response.status_code}) - {endpoint}")
                return True
        except:
            continue
    
    print(f"✗ {name}: NOT AVAILABLE")
    return False

def main():
    print("=" * 60)
    print("Проверка статуса сервисов")
    print("=" * 60)
    
    results = {}
    for name, url in services.items():
        results[name] = check_service(name, url)
    
    print("\n" + "=" * 60)
    print("Результаты:")
    available = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Доступно: {available}/{total}")
    
    if available == total:
        print("✓ Все сервисы работают!")
        return 0
    else:
        print("✗ Некоторые сервисы недоступны")
        print("\nНедоступные сервисы:")
        for name, status in results.items():
            if not status:
                print(f"  - {name}")
        print("\nЗапустите сервисы: python start_services_final.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())

