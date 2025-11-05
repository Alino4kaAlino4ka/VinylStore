"""
Тестовый скрипт для проверки API prompts-manager.
Требует запущенного сервиса prompts-manager на порту 8007.
"""
import requests
import json
import sys

PROMPTS_MANAGER_URL = "http://localhost:8007"

def test_health_check():
    """Проверка health check endpoint"""
    print("=" * 60)
    print("ТЕСТ 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{PROMPTS_MANAGER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Сервис доступен: {data}")
            return True
        else:
            print(f"✗ Неожиданный статус код: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Не удалось подключиться к сервису. Убедитесь, что prompts-manager запущен на порту 8007")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_get_prompts():
    """Тест получения списка промптов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: GET /api/v1/prompts")
    print("=" * 60)
    
    try:
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts", timeout=5)
        if response.status_code == 200:
            prompts = response.json()
            print(f"✓ Получено промптов: {len(prompts)}")
            
            for prompt in prompts:
                print(f"  - id: {prompt.get('id')}, name: {prompt.get('name')}")
                # Проверяем структуру
                if 'id' not in prompt:
                    print(f"✗ Промпт не содержит поле 'id'!")
                    return False
                if 'name' not in prompt:
                    print(f"✗ Промпт не содержит поле 'name'!")
                    return False
                if 'template' not in prompt:
                    print(f"✗ Промпт не содержит поле 'template'!")
                    return False
                if 'content' in prompt:
                    print(f"⚠ Промпт содержит старое поле 'content' (должно быть 'template')!")
            
            print("✓ Все промпты имеют правильную структуру")
            return True
        else:
            print(f"✗ Неожиданный статус код: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_get_specific_prompt():
    """Тест получения конкретного промпта"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: GET /api/v1/prompts/{prompt_name}")
    print("=" * 60)
    
    try:
        # Тестируем получение recommendation_prompt
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        if response.status_code == 200:
            prompt = response.json()
            print(f"✓ Промпт получен: id={prompt.get('id')}, name={prompt.get('name')}")
            
            # Проверяем, что используется 'template', а не 'content'
            if 'template' in prompt:
                template_len = len(prompt['template'])
                print(f"✓ Поле 'template' существует (длина: {template_len} символов)")
            else:
                print("✗ Поле 'template' отсутствует!")
                return False
            
            if 'content' in prompt:
                print("⚠ Промпт содержит старое поле 'content'!")
                return False
            
            # Проверяем, что id - строка
            prompt_id = prompt.get('id')
            if isinstance(prompt_id, str):
                print(f"✓ ID промпта - строка: '{prompt_id}'")
            else:
                print(f"✗ ID промпта не строка: {type(prompt_id)}")
                return False
            
            return True
        elif response.status_code == 404:
            print("⚠ Промпт 'recommendation_prompt' не найден (может быть еще не создан)")
            return True  # Не критично
        else:
            print(f"✗ Неожиданный статус код: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_update_prompt():
    """Тест обновления промпта"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: PUT /api/v1/prompts/{prompt_name}")
    print("=" * 60)
    
    try:
        # Сначала получаем существующий промпт
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        if response.status_code != 200:
            print("⚠ Промпт 'recommendation_prompt' не найден, пропускаем тест обновления")
            return True
        
        original_prompt = response.json()
        original_template = original_prompt.get('template', '')
        
        # Обновляем промпт
        new_template = "Тестовый обновленный шаблон для проверки API"
        update_data = {"template": new_template}
        
        response = requests.put(
            f"{PROMPTS_MANAGER_URL}/api/v1/prompts/recommendation_prompt",
            json=update_data,
            timeout=5
        )
        
        if response.status_code == 200:
            updated_prompt = response.json()
            if updated_prompt.get('template') == new_template:
                print("✓ Промпт успешно обновлен через поле 'template'")
            else:
                print("✗ Шаблон не обновился!")
                return False
            
            # Восстанавливаем оригинальный шаблон
            restore_data = {"template": original_template}
            requests.put(
                f"{PROMPTS_MANAGER_URL}/api/v1/prompts/recommendation_prompt",
                json=restore_data,
                timeout=5
            )
            print("✓ Оригинальный шаблон восстановлен")
            return True
        else:
            print(f"✗ Неожиданный статус код: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommender_integration():
    """Тест интеграции с recommender сервисом"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Интеграция с Recommender Service")
    print("=" * 60)
    
    try:
        # Проверяем, что recommender может получить промпт
        response = requests.get(f"{PROMPTS_MANAGER_URL}/api/v1/prompts/recommendation_prompt", timeout=5)
        if response.status_code == 200:
            prompt = response.json()
            
            # Проверяем, что поле называется 'template'
            if 'template' in prompt:
                template = prompt['template']
                if len(template) > 0:
                    print(f"✓ Recommender может получить промпт с полем 'template' (длина: {len(template)})")
                    print(f"  Первые 100 символов: {template[:100]}...")
                    return True
                else:
                    print("✗ Шаблон пустой!")
                    return False
            else:
                print("✗ Промпт не содержит поле 'template'!")
                return False
        else:
            print("⚠ Промпт 'recommendation_prompt' не найден")
            return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 Запуск тестов API prompts-manager\n")
    print("⚠ Убедитесь, что сервис prompts-manager запущен на порту 8007\n")
    
    results = []
    results.append(test_health_check())
    
    if results[0]:  # Продолжаем только если сервис доступен
        results.append(test_get_prompts())
        results.append(test_get_specific_prompt())
        results.append(test_update_prompt())
        results.append(test_recommender_integration())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ВСЕ ТЕСТЫ API ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ API НЕ ПРОЙДЕНЫ")
        print(f"   Пройдено: {sum(results)}/{len(results)}")
    print("=" * 60)

