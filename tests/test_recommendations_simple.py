#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работы рекомендаций
"""

import requests
import json
import sys
import io

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_recommendations():
    """Тестирует сервис рекомендаций"""
    
    # URL сервиса рекомендаций
    rec_url = "http://127.0.0.1:8004/api/v1/recommendations/generate"
    
    # Тестовые данные
    test_data = {
        "user_preferences": "Люблю классический рок и прогрессивный рок",
        "max_recommendations": 3
    }
    
    print("🧪 Тестирование сервиса рекомендаций...")
    print(f"URL: {rec_url}")
    print(f"Данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем запрос
        response = requests.post(
            rec_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('recommendations'):
                print(f"✅ Найдено рекомендаций: {len(data['recommendations'])}")
                for i, rec in enumerate(data['recommendations']):
                    print(f"   {i+1}. {rec.get('name', 'Неизвестная пластинка')} - {rec.get('artist', 'Неизвестный исполнитель')}")
            else:
                print("❌ Рекомендации не найдены в ответе")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервис рекомендаций недоступен (порт 8004)")
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_catalog():
    """Тестирует сервис каталога"""
    
    # URL сервиса каталога
    catalog_url = "http://127.0.0.1:8000/api/v1/products"
    
    print("\n🧪 Тестирование сервиса каталога...")
    print(f"URL: {catalog_url}")
    
    try:
        # Отправляем запрос
        response = requests.get(catalog_url, timeout=10)
        
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('products'):
                print(f"✅ Найдено продуктов: {len(data['products'])}")
            else:
                print("❌ Продукты не найдены в ответе")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервис каталога недоступен (порт 8000)")
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов...")
    test_catalog()
    test_recommendations()
    print("\n✅ Тесты завершены!")
