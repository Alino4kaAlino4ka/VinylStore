#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест Cart Service для проверки проблемы с товарами
"""

import requests
import json
import sys
import io

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_cart_service():
    """Тестирует Cart Service с товарами 8 и 14"""
    
    # URL Cart Service
    cart_url = "http://127.0.0.1:8005/api/v1/cart/calculate"
    
    # Тестовые данные
    test_data = {
        "product_ids": ["8", "14"]
    }
    
    print("🧪 Тестирование Cart Service...")
    print(f"URL: {cart_url}")
    print(f"Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем запрос
        response = requests.post(
            cart_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('items'):
                print(f"✅ Найдено товаров: {len(data['items'])}")
                for item in data['items']:
                    print(f"   - {item.get('id')}: {item.get('title')} - {item.get('price')}₽")
            else:
                print("❌ Товары не найдены в ответе")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cart Service недоступен (порт 8005)")
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_catalog_service():
    """Тестирует Catalog Service"""
    
    catalog_url = "http://127.0.0.1:8000/api/v1/products"
    
    print("\n🧪 Тестирование Catalog Service...")
    print(f"URL: {catalog_url}")
    
    try:
        response = requests.get(catalog_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ Найдено товаров в каталоге: {len(products)}")
            
            # Ищем товары с ID 8 и 14
            for product in products:
                if str(product.get('id')) in ['8', '14']:
                    print(f"   - ID {product.get('id')}: {product.get('name')} - {product.get('price')}₽")
        else:
            print(f"❌ Ошибка Catalog Service: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Catalog Service недоступен (порт 8000)")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🔍 Тестирование сервисов магазина виниловых пластинок")
    print("=" * 50)
    
    test_catalog_service()
    test_cart_service()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено")
