#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полное тестирование сервиса prompts-manager
Проверяет все API endpoints, CORS, обработку ошибок
"""

import requests
import json
import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://127.0.0.1:8007"
TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}[TEST] {name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")

def test_health_check():
    """Тест health check endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("service") == "prompts-manager":
                print_success("Health check прошел успешно")
                return True
            else:
                print_error(f"Неверный формат ответа: {data}")
                return False
        else:
            print_error(f"Ошибка статуса: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Не удалось подключиться к сервису. Убедитесь, что prompts-manager запущен на порту 8007")
        return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_cors_headers():
    """Тест CORS заголовков"""
    print_test("CORS заголовки")
    try:
        # Проверяем CORS заголовки в обычном GET запросе
        response = requests.get(
            f"{BASE_URL}/api/v1/prompts",
            headers={"Origin": "null"},
            timeout=TIMEOUT
        )
        
        # Минимально необходимые CORS заголовки для работы в браузере
        required_headers = ["Access-Control-Allow-Origin"]
        optional_headers = ["Access-Control-Allow-Methods", "Access-Control-Allow-Headers"]
        
        all_required_present = True
        for header in required_headers:
            if header in response.headers:
                print_success(f"{header}: {response.headers[header]}")
            else:
                print_error(f"{header} отсутствует")
                all_required_present = False
        
        # Проверяем опциональные заголовки (добавляются HTTP middleware)
        for header in optional_headers:
            if header in response.headers:
                print_success(f"{header}: {response.headers[header]}")
            else:
                print_warning(f"{header} отсутствует (может быть добавлен middleware)")
        
        return all_required_present
    except Exception as e:
        print_error(f"Ошибка при проверке CORS: {e}")
        return False

def test_get_all_prompts():
    """Тест получения всех промптов"""
    print_test("GET /api/v1/prompts - Получить все промпты")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/prompts", timeout=TIMEOUT)
        
        # Проверяем CORS заголовки
        if "Access-Control-Allow-Origin" in response.headers:
            print_success("CORS заголовки присутствуют в ответе")
        else:
            print_warning("CORS заголовки отсутствуют в ответе")
        
        if response.status_code == 200:
            prompts = response.json()
            if isinstance(prompts, list):
                print_success(f"Получено {len(prompts)} промптов")
                
                # Проверяем структуру первого промпта
                if len(prompts) > 0:
                    prompt = prompts[0]
                    required_fields = ["id", "name", "template"]
                    missing_fields = [f for f in required_fields if f not in prompt]
                    
                    if not missing_fields:
                        print_success("Структура промпта корректна")
                        print(f"   - ID: {prompt['id']}")
                        print(f"   - Name: {prompt['name']}")
                        print(f"   - Template length: {len(prompt['template'])} символов")
                        return True
                    else:
                        print_error(f"Отсутствуют поля: {missing_fields}")
                        return False
                else:
                    print_warning("Список промптов пуст")
                    return True  # Не ошибка, просто нет промптов
            else:
                print_error(f"Неверный тип ответа: {type(prompts)}")
                return False
        else:
            print_error(f"Ошибка статуса: {response.status_code}")
            print_error(f"Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_get_specific_prompt():
    """Тест получения конкретного промпта"""
    print_test("GET /api/v1/prompts/{prompt_id} - Получить конкретный промпт")
    try:
        # Тестируем оба дефолтных промпта
        prompt_ids = ["recommendation_prompt", "description_prompt"]
        
        all_success = True
        for prompt_id in prompt_ids:
            response = requests.get(f"{BASE_URL}/api/v1/prompts/{prompt_id}", timeout=TIMEOUT)
            
            if response.status_code == 200:
                prompt = response.json()
                required_fields = ["id", "name", "template"]
                missing_fields = [f for f in required_fields if f not in prompt]
                
                if not missing_fields and prompt["id"] == prompt_id:
                    print_success(f"Промпт '{prompt_id}' получен успешно")
                    print(f"   - Name: {prompt['name']}")
                    print(f"   - Template length: {len(prompt['template'])} символов")
                else:
                    print_error(f"Ошибка в структуре промпта '{prompt_id}': {missing_fields}")
                    all_success = False
            elif response.status_code == 404:
                print_warning(f"Промпт '{prompt_id}' не найден (возможно не создан)")
            else:
                print_error(f"Ошибка статуса {response.status_code} для '{prompt_id}'")
                print_error(f"Ответ: {response.text[:200]}")
                all_success = False
        
        return all_success
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_get_nonexistent_prompt():
    """Тест получения несуществующего промпта"""
    print_test("GET /api/v1/prompts/{prompt_id} - Несуществующий промпт")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/prompts/nonexistent_prompt_12345", timeout=TIMEOUT)
        
        if response.status_code == 404:
            print_success("Ошибка 404 возвращена корректно")
            # Проверяем, что есть CORS заголовки
            if "Access-Control-Allow-Origin" in response.headers:
                print_success("CORS заголовки присутствуют в ответе ошибки")
            else:
                print_warning("CORS заголовки отсутствуют в ответе ошибки")
            return True
        else:
            print_error(f"Ожидался статус 404, получен {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_update_prompt():
    """Тест обновления промпта"""
    print_test("PUT /api/v1/prompts/{prompt_id} - Обновление промпта")
    try:
        prompt_id = "recommendation_prompt"
        
        # Сначала получаем текущий промпт
        get_response = requests.get(f"{BASE_URL}/api/v1/prompts/{prompt_id}", timeout=TIMEOUT)
        if get_response.status_code != 200:
            print_error(f"Не удалось получить промпт для теста: {get_response.status_code}")
            return False
        
        original_prompt = get_response.json()
        original_template = original_prompt["template"]
        
        # Обновляем промпт с тестовым контентом
        test_template = original_template + "\n\n[Тестовое обновление]"
        update_data = {"template": test_template}
        
        response = requests.put(
            f"{BASE_URL}/api/v1/prompts/{prompt_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        # Проверяем CORS заголовки
        if "Access-Control-Allow-Origin" in response.headers:
            print_success("CORS заголовки присутствуют в ответе PUT запроса")
        else:
            print_warning("CORS заголовки отсутствуют в ответе PUT запроса")
        
        if response.status_code == 200:
            updated_prompt = response.json()
            if updated_prompt["template"] == test_template:
                print_success("Промпт успешно обновлен")
                
                # Восстанавливаем оригинальный контент
                restore_data = {"template": original_template}
                restore_response = requests.put(
                    f"{BASE_URL}/api/v1/prompts/{prompt_id}",
                    json=restore_data,
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
                if restore_response.status_code == 200:
                    print_success("Оригинальный контент восстановлен")
                
                return True
            else:
                print_error("Контент не обновлен корректно")
                return False
        else:
            print_error(f"Ошибка статуса: {response.status_code}")
            print_error(f"Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_update_nonexistent_prompt():
    """Тест обновления несуществующего промпта"""
    print_test("PUT /api/v1/prompts/{prompt_id} - Несуществующий промпт")
    try:
        update_data = {"template": "Тестовый контент"}
        response = requests.put(
            f"{BASE_URL}/api/v1/prompts/nonexistent_prompt_12345",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 404:
            print_success("Ошибка 404 возвращена корректно")
            # Проверяем CORS заголовки
            if "Access-Control-Allow-Origin" in response.headers:
                print_success("CORS заголовки присутствуют в ответе ошибки")
            return True
        else:
            print_error(f"Ожидался статус 404, получен {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def test_error_handling():
    """Тест обработки ошибок с CORS"""
    print_test("Обработка ошибок с CORS заголовками")
    try:
        # Тест на несуществующий промпт (404)
        response = requests.get(
            f"{BASE_URL}/api/v1/prompts/nonexistent_error_test_12345",
            headers={"Origin": "null"},
            timeout=TIMEOUT
        )
        
        # Должна быть ошибка 404
        if response.status_code == 404:
            # Проверяем, что есть CORS заголовки даже при ошибке
            cors_headers = ["Access-Control-Allow-Origin", "Access-Control-Allow-Methods"]
            missing = [h for h in cors_headers if h not in response.headers]
            
            if not missing:
                print_success("CORS заголовки присутствуют в ответе ошибки 404")
                return True
            else:
                print_error(f"CORS заголовки отсутствуют в ответе ошибки: {missing}")
                return False
        else:
            print_warning(f"Неожиданный статус для несуществующего промпта: {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False

def main():
    """Запуск всех тестов"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("[TEST] ПОЛНОЕ ТЕСТИРОВАНИЕ PROMPTS-MANAGER")
    print(f"{'='*60}{Colors.END}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("CORS Headers", test_cors_headers),
        ("Get All Prompts", test_get_all_prompts),
        ("Get Specific Prompt", test_get_specific_prompt),
        ("Get Nonexistent Prompt", test_get_nonexistent_prompt),
        ("Update Prompt", test_update_prompt),
        ("Update Nonexistent Prompt", test_update_nonexistent_prompt),
        ("Error Handling with CORS", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговая статистика
    print(f"\n{Colors.BLUE}{'='*60}")
    print("[RESULTS] РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}[PASSED]{Colors.END}" if result else f"{Colors.RED}[FAILED]{Colors.END}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print(f"{Colors.GREEN}[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}[WARNING] НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

