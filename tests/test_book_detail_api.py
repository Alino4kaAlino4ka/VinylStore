"""
Тесты для проверки API эндпоинта детальной информации о виниловой пластинке
для использования в vinyl-detail.js
"""

import requests
import json
import sys
import io

# Настройка кодировки для Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Конфигурация
API_BASE_URL = 'http://localhost:8000'
PRODUCTS_ENDPOINT = f'{API_BASE_URL}/api/v1/products'

def test_api_available():
    """Тест 1: Проверка доступности API"""
    print("\n🧪 Тест 1: Проверка доступности API")
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            print("✅ API сервис доступен")
            return True
        else:
            print(f"❌ API вернул статус {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API. Убедитесь, что сервис каталога запущен на порту 8000")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_get_vinyl_record_by_id(record_id=1):
    """Тест 2: Получение виниловой пластинки по ID"""
    print(f"\n🧪 Тест 2: Получение виниловой пластинки по ID={record_id}")
    try:
        response = requests.get(f'{PRODUCTS_ENDPOINT}/{record_id}', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Виниловая пластинка успешно получена")
            print(f"   Название: {data.get('name') or data.get('title', 'N/A')}")
            artist = data.get('artist', 'N/A')
            if isinstance(artist, dict):
                artist = artist.get('name', 'N/A')
            print(f"   Исполнитель: {artist}")
            print(f"   Цена: {data.get('price', 'N/A')}")
            return True, data
        elif response.status_code == 404:
            print(f"⚠️ Виниловая пластинка с ID={record_id} не найдена")
            return False, None
        else:
            print(f"❌ API вернул статус {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API")
        return False, None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False, None

def test_get_nonexistent_record():
    """Тест 3: Получение несуществующей виниловой пластинки"""
    print("\n🧪 Тест 3: Получение несуществующей виниловой пластинки (ID=99999)")
    try:
        response = requests.get(f'{PRODUCTS_ENDPOINT}/99999', timeout=5)
        
        if response.status_code == 404:
            print("✅ API корректно возвращает 404 для несуществующей виниловой пластинки")
            return True
        else:
            print(f"⚠️ Ожидался статус 404, получен {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_api_response_structure(record_id=1):
    """Тест 4: Проверка структуры ответа API"""
    print(f"\n🧪 Тест 4: Проверка структуры ответа для виниловой пластинки ID={record_id}")
    
    success, data = test_get_vinyl_record_by_id(record_id)
    if not success or not data:
        print("❌ Не удалось получить данные для проверки структуры")
        return False
    
    required_fields = ['id', 'price']
    optional_fields = ['description', 'cover_url', 'artist']
    
    missing_required = [field for field in required_fields if field not in data]
    
    # Проверяем наличие названия (name или title)
    if 'name' not in data and 'title' not in data:
        missing_required.append('name/title')
    
    if missing_required:
        print(f"❌ Отсутствуют обязательные поля: {missing_required}")
        return False
    
    print("✅ Все обязательные поля присутствуют")
    print(f"   Поля ответа: {list(data.keys())}")
    
    # Проверяем наличие опциональных полей
    present_optional = [field for field in optional_fields if field in data]
    if present_optional:
        print(f"   Опциональные поля: {present_optional}")
    
    return True

def test_all_vinyl_records():
    """Тест 5: Получение списка всех виниловых пластинок"""
    print("\n🧪 Тест 5: Получение списка всех виниловых пластинок")
    try:
        response = requests.get(PRODUCTS_ENDPOINT, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # API возвращает объект с ключом 'products', который содержит массив
            if isinstance(data, dict) and 'products' in data:
                products = data['products']
                print(f"✅ Получен список из {len(products)} виниловых пластинок")
                if len(products) > 0:
                    print(f"   Первая пластинка: ID={products[0].get('id')}, Название={products[0].get('name') or products[0].get('title', 'N/A')}")
                return True
            elif isinstance(data, list):
                print(f"✅ Получен список из {len(data)} виниловых пластинок")
                if len(data) > 0:
                    print(f"   Первая пластинка: ID={data[0].get('id')}, Название={data[0].get('name') or data[0].get('title', 'N/A')}")
                return True
            else:
                print("⚠️ Ответ не является списком или объектом с products")
                return False
        else:
            print(f"❌ API вернул статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ API ДЛЯ VINYL-DETAIL.JS")
    print("=" * 60)
    
    results = []
    
    # Тест 1: Доступность API
    results.append(("Доступность API", test_api_available()))
    
    # Тест 2: Получение виниловой пластинки по ID
    success, _ = test_get_vinyl_record_by_id(1)
    results.append(("Получение виниловой пластинки по ID", success))
    
    # Тест 3: Несуществующая пластинка
    results.append(("Обработка несуществующей пластинки", test_get_nonexistent_record()))
    
    # Тест 4: Структура ответа
    results.append(("Структура ответа API", test_api_response_structure(1)))
    
    # Тест 5: Список всех пластинок
    results.append(("Получение списка пластинок", test_all_vinyl_records()))
    
    # Сводка
    print("\n" + "=" * 60)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    print(f"\nВсего тестов: {total}")
    print(f"✅ Успешно: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📊 Процент успеха: {round((passed / total) * 100) if total > 0 else 0}%")
    
    return all(result for _, result in results)

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тестирование прервано пользователем")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        exit(1)

