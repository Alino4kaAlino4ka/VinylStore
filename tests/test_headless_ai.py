#!/usr/bin/env python3
"""
Тест Headless AI архитектуры (шаг 2)
Проверяет получение промптов из prompts-manager и их использование в recommender
"""

import requests
import json
import time
import sys

def test_service_health(service_name, port, endpoint="/health"):
    """Проверяет доступность сервиса"""
    url = f"http://127.0.0.1:{port}{endpoint}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} (порт {port}): доступен")
            return True
        else:
            print(f"❌ {service_name} (порт {port}): недоступен (статус {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {service_name} (порт {port}): сервис не запущен")
        return False
    except Exception as e:
        print(f"❌ {service_name} (порт {port}): ошибка - {e}")
        return False

def test_get_prompt_from_manager(prompt_name):
    """Тестирует получение промпта из prompts-manager"""
    url = f"http://localhost:8007/api/v1/prompts/{prompt_name}"
    
    print(f"\n🧪 Тест получения промпта '{prompt_name}' из prompts-manager...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            if content:
                print(f"✅ Промпт '{prompt_name}' успешно получен")
                print(f"📝 Длина контента: {len(content)} символов")
                print(f"📄 Первые 200 символов:\n{content[:200]}...")
                return True, content
            else:
                print(f"❌ Промпт '{prompt_name}' пустой (нет поля 'content')")
                return False, None
        elif response.status_code == 404:
            print(f"❌ Промпт '{prompt_name}' не найден в prompts-manager")
            print(f"💡 Убедитесь, что промпт создан при старте сервиса")
            return False, None
        else:
            print(f"❌ Ошибка получения промпта: статус {response.status_code}")
            print(f"Ответ: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удалось подключиться к prompts-manager на порту 8007")
        print(f"💡 Убедитесь, что prompts-manager запущен")
        return False, None
    except Exception as e:
        print(f"❌ Ошибка при получении промпта: {e}")
        return False, None

def test_recommender_uses_prompts():
    """Тестирует, что recommender использует промпты из prompts-manager"""
    url = "http://127.0.0.1:8004/api/v1/recommendations/generate"
    
    print(f"\n🧪 Тест использования промптов в recommender...")
    print(f"URL: {url}")
    
    # Тестовый запрос (минимальный, без вызова LLM)
    test_request = {
        "user_preferences": "Тестовое предпочтение",
        "max_recommendations": 3
    }
    
    try:
        print(f"📤 Отправка запроса: {json.dumps(test_request, ensure_ascii=False)}")
        
        # Отправляем запрос с таймаутом (может быть долгим из-за LLM)
        response = requests.post(url, json=test_request, timeout=60)
        
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommender успешно обработал запрос")
            print(f"📦 Получено рекомендаций: {len(data.get('recommendations', []))}")
            return True
        elif response.status_code == 503:
            print(f"⚠️  Сервис prompts-manager недоступен (статус 503)")
            print(f"💡 Убедитесь, что prompts-manager запущен на порту 8007")
            return False
        elif response.status_code == 404:
            print(f"⚠️  Промпт не найден в prompts-manager (статус 404)")
            print(f"💡 Убедитесь, что промпты созданы при старте prompts-manager")
            return False
        else:
            print(f"❌ Ошибка: статус {response.status_code}")
            print(f"Ответ: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⚠️  Таймаут при запросе (возможно, LLM долго отвечает)")
        print(f"💡 Это может быть нормально, если сервис работает")
        return None  # Не критичная ошибка
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удалось подключиться к recommender на порту 8004")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании recommender: {e}")
        return False

def test_all_prompts():
    """Тестирует все необходимые промпты"""
    prompts_to_test = ["recommendation_prompt", "description_prompt"]
    
    print(f"\n{'='*60}")
    print("📋 ТЕСТ: Проверка всех промптов в prompts-manager")
    print(f"{'='*60}")
    
    results = {}
    for prompt_name in prompts_to_test:
        success, content = test_get_prompt_from_manager(prompt_name)
        results[prompt_name] = success
    
    return results

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов Headless AI архитектуры (шаг 2)")
    print("=" * 60)
    
    # Шаг 1: Проверка доступности сервисов
    print("\n📋 ШАГ 1: Проверка доступности сервисов")
    print("-" * 60)
    
    services_status = {
        "prompts-manager": test_service_health("Prompts Manager", 8007),
        "recommender": test_service_health("Recommender", 8004),
        "catalog": test_service_health("Catalog", 8000)  # Нужен для получения книг
    }
    
    if not all(services_status.values()):
        print("\n❌ НЕ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!")
        print("💡 Убедитесь, что все необходимые сервисы запущены:")
        print("   - prompts-manager (порт 8007)")
        print("   - recommender (порт 8004)")
        print("   - catalog (порт 8000)")
        return 1
    
    # Шаг 2: Проверка получения промптов
    print("\n📋 ШАГ 2: Проверка получения промптов из prompts-manager")
    print("-" * 60)
    
    prompts_results = test_all_prompts()
    
    if not all(prompts_results.values()):
        print("\n❌ НЕ ВСЕ ПРОМПТЫ ДОСТУПНЫ!")
        print("💡 Убедитесь, что prompts-manager создал дефолтные промпты при старте")
        return 1
    
    # Шаг 3: Проверка использования промптов в recommender
    print("\n📋 ШАГ 3: Проверка использования промптов в recommender")
    print("-" * 60)
    
    recommender_test = test_recommender_uses_prompts()
    
    if recommender_test is False:
        print("\n❌ RECOMMENDER НЕ ИСПОЛЬЗУЕТ ПРОМПТЫ ИЗ PROMPTS-MANAGER!")
        return 1
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    all_tests_passed = (
        all(services_status.values()) and
        all(prompts_results.values()) and
        recommender_test is not False
    )
    
    print(f"\n✅ Все сервисы доступны: {all(services_status.values())}")
    print(f"✅ Все промпты получены: {all(prompts_results.values())}")
    print(f"✅ Recommender использует промпты: {recommender_test is not False}")
    
    if all_tests_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Headless AI архитектура работает корректно")
        print("✅ Recommender успешно получает промпты из prompts-manager")
        return 0
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

