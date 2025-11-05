"""
Тест для генерации описания виниловой пластинки через оркестратор
"""
import asyncio
import httpx
import json
import time

async def test_description_generation():
    """Тестирует весь процесс генерации описания"""
    base_url = "http://127.0.0.1:8004"
    catalog_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("Тест генерации описания виниловой пластинки")
    print("=" * 60)
    
    # Шаг 0: Проверка доступности сервисов
    print("\n[Шаг 0] Проверка доступности сервисов...")
    services_ok = True
    
    # Проверяем recommender
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/health")
            print(f"✅ Recommender service (порт 8004): {resp.status_code}")
            if resp.status_code == 200:
                health_data = resp.json()
                print(f"   Статус: {health_data.get('status', 'unknown')}")
    except httpx.ConnectError:
        print(f"❌ Recommender service (порт 8004): НЕ ДОСТУПЕН")
        print("   Запустите сервис: python start_services_final.py")
        services_ok = False
    except Exception as e:
        print(f"❌ Recommender service (порт 8004): Ошибка - {type(e).__name__}: {e}")
        services_ok = False
    
    # Проверяем catalog
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{catalog_url}/api/v1/products")
            print(f"✅ Catalog service (порт 8000): {resp.status_code}")
    except httpx.ConnectError:
        print(f"❌ Catalog service (порт 8000): НЕ ДОСТУПЕН")
        print("   Запустите сервис: python start_services_final.py")
        services_ok = False
    except Exception as e:
        print(f"❌ Catalog service (порт 8000): Ошибка - {type(e).__name__}: {e}")
        services_ok = False
    
    if not services_ok:
        print("\n⚠️  Не все сервисы доступны. Запустите их перед тестированием.")
        print("   Команда: python start_services_final.py")
        return
    
    # Шаг 1: Получаем список продуктов
    print("\n[Шаг 1] Получаем список продуктов...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{catalog_url}/api/v1/products")
            products = resp.json()
            if "products" in products and len(products["products"]) > 0:
                product_id = products["products"][0]["id"]
                print(f"✅ Найден продукт с ID: {product_id}")
                print(f"   Название: {products['products'][0]['name']}")
            else:
                print("❌ Нет продуктов в каталоге")
                return
    except Exception as e:
        print(f"❌ Ошибка получения продуктов: {e}")
        return
    
    # Шаг 2: Тестируем генерацию описания
    print(f"\n[Шаг 2] Генерируем описание для продукта ID={product_id}...")
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Отправляем запрос
            print("   Отправка запроса к оркестратору...")
            response = await client.post(
                f"{base_url}/api/v1/recommendations/generate-description/{product_id}"
            )
            
            elapsed = time.time() - start_time
            print(f"   Время выполнения: {elapsed:.2f} секунд")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Успешно!")
                print(f"   Product ID: {data.get('product_id')}")
                print(f"   Success: {data.get('success')}")
                print(f"   Message: {data.get('message')}")
                print(f"   Description: {data.get('generated_description', '')[:200]}...")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        print(f"❌ Таймаут после {elapsed:.2f} секунд")
        print("   Проверьте:")
        print("   - Подключение к OpenRouter API")
        print("   - Скорость интернета")
        print("   - Настройки OPENROUTER_API_KEY в config.env")
    except httpx.ConnectError:
        elapsed = time.time() - start_time
        print(f"❌ Ошибка подключения после {elapsed:.2f} секунд")
        print("   Убедитесь, что сервис recommender запущен на порту 8004")
    except httpx.HTTPStatusError as e:
        elapsed = time.time() - start_time
        print(f"❌ HTTP ошибка после {elapsed:.2f} секунд: {e.response.status_code}")
        try:
            error_data = e.response.json()
            print(f"   Детали: {error_data.get('detail', error_data)}")
        except:
            print(f"   Ответ: {e.response.text[:200]}")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Ошибка после {elapsed:.2f} секунд: {e}")
        print(f"   Тип ошибки: {type(e).__name__}")
        import traceback
        print(f"   Детали: {traceback.format_exc()[:300]}")
    
    print("\n" + "=" * 60)
    print("Тест завершен")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_description_generation())

