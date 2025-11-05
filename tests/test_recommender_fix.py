#!/usr/bin/env python3
"""
Тест исправленного сервиса рекомендаций
"""
import asyncio
import httpx
import json
import os

async def test_catalog_connection():
    """Тестирует подключение к каталогу"""
    print("🔍 Тестируем подключение к каталогу...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/api/v1/products")
            print(f"Статус каталога: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Структура ответа: {type(data)}")
                print(f"Ключи: {list(data.keys()) if isinstance(data, dict) else 'Не словарь'}")
                
                if isinstance(data, dict) and "products" in data:
                    products = data["products"]
                    print(f"Количество продуктов: {len(products)}")
                    if products:
                        print(f"Пример продукта: {products[0]}")
                        return True
                else:
                    print("❌ Неожиданная структура ответа каталога")
                    return False
            else:
                print(f"❌ Ошибка каталога: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к каталогу: {e}")
        return False

async def test_recommender_service():
    """Тестирует сервис рекомендаций"""
    print("\n🤖 Тестируем сервис рекомендаций...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Проверяем health
            response = await client.get("http://127.0.0.1:8004/health")
            print(f"Health статус: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"Health данные: {health_data}")
                
                # Тестируем генерацию рекомендаций
                test_request = {
                    "user_preferences": "Люблю классическую литературу",
                    "max_recommendations": 2,
                    "model": "gpt-4"
                }
                
                print("Отправляем запрос на генерацию рекомендаций...")
                response = await client.post(
                    "http://127.0.0.1:8004/api/v1/recommendations/generate",
                    json=test_request,
                    timeout=30
                )
                
                print(f"Статус генерации: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Рекомендации успешно сгенерированы!")
                    print(f"Уверенность: {data.get('confidence_score', 0) * 100:.1f}%")
                    print(f"Количество рекомендаций: {len(data.get('recommendations', []))}")
                    return True
                else:
                    error_text = await response.aread()
                    print(f"❌ Ошибка генерации: {response.status_code}")
                    print(f"Детали: {error_text.decode()}")
                    return False
            else:
                print(f"❌ Сервис рекомендаций недоступен: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка тестирования рекомендаций: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование исправленного сервиса рекомендаций\n")
    
    # Тест 1: Каталог
    catalog_ok = await test_catalog_connection()
    
    # Тест 2: Рекомендации
    recommender_ok = await test_recommender_service()
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   Каталог: {'✅ РАБОТАЕТ' if catalog_ok else '❌ НЕ РАБОТАЕТ'}")
    print(f"   Рекомендации: {'✅ РАБОТАЕТ' if recommender_ok else '❌ НЕ РАБОТАЕТ'}")
    
    if catalog_ok and recommender_ok:
        print("\n🎉 Все исправления работают корректно!")
        return 0
    else:
        print("\n⚠️ Есть проблемы, требующие внимания")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
